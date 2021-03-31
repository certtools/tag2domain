import logging
import time
import re
import copy
import random

import psycopg2
import psycopg2.extras

_db_conn = None
_db_config = None
_config = None

logger = logging.getLogger(__name__)

RE_FILTER = (
    "^(?:(?P<taxonomy>[A-Za-z\-0-9 ]+):)?(?:(?P<category>[A-Za-z\-0-9:]+)::)?(?P<tag>[A-Za-z0-9-]+)?(?:=(?P<value>[A-Za-z0-9. ?:_=\\/]+))?$"  # noqa:W605
)
COMPILED_RE_FILTER = re.compile(RE_FILTER)


def get_db():
    """
    Returns an already opened database connection or None
    """
    return _db_conn


def get_db_cursor():
    """
    Returns a cursor
    """
    if _db_conn is None:
        raise RuntimeError("no DB connected")
    return _db_conn.cursor()


def get_db_dict_cursor():
    """
    Returns a psycopg2.extras.RealDictCursor instance
    """
    if _db_conn is None:
        raise RuntimeError("no DB connected")
    return _db_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


def execute_db(query, params=None, dict_=False, handle_failure=True):
    """
    Executes a DB statement and returns the results
    """

    _log_id = random.randint(0, 32768)
    try:
        if dict_:
            cursor = get_db_dict_cursor()
        else:
            cursor = get_db_cursor()

        if params is None:
            logger.debug(query)
        else:
            if isinstance(params, dict):
                logger.debug(query, params)
            else:
                logger.debug(query, *params)

        logger.debug(str(_log_id) + " - executing query...")
        start = time.time()
        cursor.execute(query, params)
        logger.debug(str(_log_id) + " - done - %f s", time.time() - start)
        logger.debug(str(_log_id) + " - fetching result...")
        start = time.time()
        rows = cursor.fetchall()
        get_db().commit()  # immediately end transaction
        logger.debug(str(_log_id) + " - done - %f s", time.time() - start)
    except (psycopg2.Error, RuntimeError) as e:
        if handle_failure:
            logger.debug("failed DB stmt (%s) - reconnecting", str(e))
            time.sleep(2)
            connect_db()
            rows = execute_db(query, params, dict_=dict_, handle_failure=False)
        else:
            raise RuntimeError("could not execute statement - %s" % str(e))
    return rows


def connect_db(config=None):
    """Connects to the specific database.
    :rtype: psycopg2 connection"""
    global _db_conn
    global _db_config
    global _config
    if _db_conn is not None:
        logger.debug("closing previous DB connection")
        try:
            _db_conn.rollback()
            _db_conn.close()
        except psycopg2.Error as e:
            logger.debug(
                "encountered error in close before connect: %s", str(e.pgerror)
            )
        _db_conn = None

    if config is None:
        if _db_config is None:
            raise ValueError("No config given")
        logger.debug("reusing previous DB config")
        db_config = _db_config
    else:
        db_config = dict(
            dbname=config['DATABASE'],
            user=config['DBUSER'],
            password=config['DBPASSWORD'],
            host=config['DBHOST'],
            port=config['DBPORT'],
            application_name="tag2domain_api",
            sslmode=config['DBSSLMODE'],
            options='-c search_path=%s' % config['DBTAG2DOMAIN_SCHEMA']
        )
        _config = copy.deepcopy(config)

    def filter(key, value):
        if key in ["password", ]:
            return "<REDACTED>"
        else:
            return value
    logger.debug(
        "DB config: " + str({
            key: filter(key, value)
            for key, value in db_config.items()
        })
    )
    try:
        conn = psycopg2.connect(**db_config)
    except Exception as ex:
        time.sleep(2)
        raise RuntimeError(
            "could not connect to the DB. Reason: %s" % (str(ex))
        )

    # Disable transactions and set to read only if ENABLE_MSM2TAG is disabled
    if (
        ("ENABLE_MSM2TAG" not in _config)
        or (not _config["ENABLE_MSM2TAG"] is True)
    ):
        logger.info("accessing DB in read-only mode")
        conn.set_session(readonly=True)
    else:
        logger.info("accessing DB in read-write mode")

    logger.info(
        "connected to DB '%s' on '%s'" % (
            db_config['dbname'],
            db_config['host']
        )
    )
    _db_conn = conn
    _db_config = db_config

    return _db_conn


def set_db(db_conn):
    global _db_conn
    global _db_config
    global _config
    _db_conn = db_conn
    _db_config = None
    _config = None


def disconnect_db():
    global _db_conn
    _db_conn.close()
    _db_conn = None


def get_sql_base_table(at_time, filter=None, domain=None):
    if filter is not None and domain is not None:
        raise ValueError(
            "filtering by domain and by filter is not implemented"
        )
    if filter is not None:
        m = COMPILED_RE_FILTER.match(filter)
        if not m:
            raise ValueError("invalid filter clause - '%s'" % filter)
        else:
            taxonomy, category, tag, value = \
                m.group('taxonomy', 'category', 'tag', 'value')
            logger.debug(','.join(map(str, [taxonomy, category, tag, value])))
            if taxonomy is not None:
                raise ValueError("filtering by tags is not implemented")
            if value is None:
                raise ValueError("value is required for filtering by non-tags")
            params = {
                '__tag_type': tag,
                '__value': value
            }
            if at_time is not None:
                s = (
                    'tag2domain_get_tags_at_time_filtered'
                    '(%(__at_time)s, %(__tag_type)s, %(__value)s)'
                )
                params['__at_time'] = at_time
            else:
                s = (
                    'tag2domain_get_open_tags_filtered'
                    '(%(__tag_type)s, %(__value)s)'
                )
            return s, params
    elif domain is not None:
        params = {'__domain': domain}
        if at_time is not None:
            params['__at_time'] = at_time
            s = (
                'tag2domain_get_tags_at_time_domain'
                '(%(__at_time)s, %(__domain)s)'
            )
        else:
            s = 'tag2domain_get_open_tags_domain(%(__domain)s)'
        return s, params
    else:
        if at_time is not None:
            params = {'__at_time': at_time}
            return 'tag2domain_get_tags_at_time(%(__at_time)s)', params
        else:
            return 'tag2domain_get_open_tags()', {}
