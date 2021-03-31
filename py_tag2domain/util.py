import datetime
import configparser
import re
import logging
from psycopg2.tz import FixedOffsetTimezone

logger = logging.getLogger(__file__)

RE_INTERSECTION_TABLE_MAPPING_SECTION = r"db\.intxn_table\.(.+)"
INTXN_TABLE_MAPPING_KEYS_REQUIRED = [
    "table_name",
    "id",
    "taxonomy_id",
    "tag_id",
    "value_id",
    "measured_at",
    "producer",
    "start_date",
    "end_date",
    "start_ts",
    "end_ts"
]


def _parse_db_connection(config_object):
    try:
        db_config = config_object["db"]
        print(db_config)
        tag2domain_db_config = dict(
            DBUSER=db_config["user"],
            DBHOST=db_config["host"],
            DATABASE=db_config["dbname"],
            DBPASSWORD=db_config["password"],
            DBPORT=db_config.getint("port", fallback=5432),
            DBSSLMODE=db_config.get("sslmode", fallback="require"),
            DBSCHEMA=db_config.get(
                "schema",
                fallback="public"
            ),
            DBTAG2DOMAIN_SCHEMA=db_config.get(
                "schema",
                fallback="public"
            ),
            DBAPPLICATION_NAME=db_config.get(
                "application_name",
                fallback="tag2domain_test"
            )
        )
    except KeyError as e:
        tag2domain_db_config = None
        logger.error(
            "could not find required key '%s' in db config" % (str(e))
        )
    return tag2domain_db_config


def _part_intxn_table_mapping(config_object):
    mapping = {}
    try:
        for key in INTXN_TABLE_MAPPING_KEYS_REQUIRED:
            mapping[key] = config_object[key]
    except KeyError as e:
        raise ValueError(
            "could not find required key '%s' in intxn table mapping" % str(e)
        )
    return mapping


def _parse_intxn_table_mappings(config_object):
    intxn_table_mappings = {}
    for _section in config_object.keys():
        m = re.match(RE_INTERSECTION_TABLE_MAPPING_SECTION, _section)
        if m:
            intxn_table_mappings[m.group(1).strip()] = \
                _part_intxn_table_mapping(config_object[_section])
    return intxn_table_mappings


def parse_config(configfile):
    if isinstance(configfile, str):
        print("reading configfile " + configfile)
        config = configparser.ConfigParser()
        config.read(configfile)
    elif isinstance(configfile, configparser.ConfigParser):
        config = configfile
    if len(config.keys()) > 0:
        tag2domain_db_config = _parse_db_connection(config)
        intxn_table_mappings = _parse_intxn_table_mappings(config)
    else:
        tag2domain_db_config = None
        intxn_table_mappings = None

    return tag2domain_db_config, intxn_table_mappings


def calc_changes(from_, to):
    """
    Calculate the label changes required to change from the set of labels from_
    to the set of labels to.

    For use with function :func:`tag2domain_execute_changes`.

    Returns
    -------
    dict : keys 'insert', 'prolong', 'end' -> list
        keys indicate the action that is required and the lists contain the
        tags the action has to be applied to.
    """
    changes = {
        'insert': tuple(sorted(to - from_)),
        'prolong': tuple(sorted(to & from_)),
        'end': tuple(sorted(from_ - to)),
    }
    return changes


def parse_timestamp(ts):
    """
    Takes a timestamp in format "%Y-%m-%dT%H:%M:%S(.$d)" with or
    without microseconds and returns the time as datetime.datetime.
    """
    try:
        dt = datetime.datetime.strptime(
            ts,
            "%Y-%m-%dT%H:%M:%S.%f"
        )
    except ValueError:
        try:
            # Retry without microseconds
            dt = datetime.datetime.strptime(
                ts,
                "%Y-%m-%dT%H:%M:%S"
            )
        except ValueError as e:
            raise ValueError("could not parse timestamp - %s" % str(e))

    return dt.replace(tzinfo=FixedOffsetTimezone(offset=0, name=None))
