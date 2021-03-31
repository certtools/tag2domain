from __future__ import print_function
import logging
from collections import OrderedDict, defaultdict
import psycopg2
import psycopg2.extras
import json
import copy

from .exceptions import (
    AdapterConnectionException,
    AdapterDBError,
    InconsistentTaxonomyException
)

from .db_statements import db_statements as db_stmts


class Psycopg2Adapter(object):
    # This dictionary defines the default mappings for measurement tag_types
    # to intersection tables
    @classmethod
    def _compile(cls, stmt, mapping):
        return stmt % mapping

    @classmethod
    def compile_all(cls, mappings):
        compiled = {}

        mappings_copy = copy.deepcopy(mappings)

        for type, mapping in mappings_copy.items():
            mapping["__all_fields__"] = ','.join([
                "%s AS %s" % (value, key)
                for key, value in mapping.items()
                if key != 'table_name'
            ])
            _stmts = {}
            for key, stmt in db_stmts.items():
                _stmts[key] = cls._compile(stmt, mapping)
            compiled[type] = _stmts
        return compiled

    @classmethod
    def to_psycopg_args(cls, config):
        if config is None:
            return None
        try:
            options = ""
            options += "-c search_path=%s" % config["DBTAG2DOMAIN_SCHEMA"]
            psycopg_args = dict(
                user=config["DBUSER"],
                host=config["DBHOST"],
                dbname=config["DATABASE"],
                password=config["DBPASSWORD"],
                port=config["DBPORT"],
                sslmode=config["DBSSLMODE"],
                application_name=config["DBAPPLICATION_NAME"],
                options=options
            )
        except KeyError as e:
            raise ValueError("could not generate psycopg args. Required "
                             "key '%s' not found in config" % str(e))
        return psycopg_args

    def __init__(
        self,
        connect_params,
        tag_type_intxn_table_mappings,
        logger=logging.getLogger()
    ):
        """
        Constructor

        Parameters
        ----------
        connect_params - str, dict or psycopg2.connect
            database connection string, dict of parameters or connection object
        logger - logging.Logger
            Logger used for logging

        Raises
        ------
        AdapterConnectionException
            indicates that the connection to the backend failed
        """
        self.tag_type_intxn_table_mappings = tag_type_intxn_table_mappings
        self.compiled_db_statements = self.__class__.compile_all(
            self.tag_type_intxn_table_mappings
        )
        self.tag_types = list(self.tag_type_intxn_table_mappings.keys())

        self.connect_params = connect_params
        self.logger = logger
        try:
            if isinstance(connect_params, str):
                self.db_connection = psycopg2.connect(connect_params)
            elif isinstance(connect_params, dict):
                self.db_connection = psycopg2.connect(**connect_params)
            elif isinstance(connect_params, psycopg2.extensions.connection):
                self.db_connection = connect_params
                if self.db_connection.autocommit:
                    raise ValueError(
                        "DB connection used must not be in in autocommit mode"
                    )
            else:
                raise ValueError(
                    "unknown datatype for connect_params -"
                    " expect dict or str, got %s" % type(connect_params)
                )
        except psycopg2.Warning as e:
            self.logger.warning(str(e))
        except psycopg2.Error as e:
            raise AdapterConnectionException(str(e))

        self.db_cursor = self.db_connection.cursor()

    def is_valid_tag_type(self, tag_type):
        return tag_type in self.tag_types

    def get_compiled_stmt(self, stmt_name, type):
        if type not in self.compiled_db_statements:
            raise AdapterDBError("unknown intersection type '%s'" % type)

        if stmt_name not in self.compiled_db_statements[type]:
            raise ValueError(
                "invalid db statement name - Bad Programmer Error"
            )

        return self.compiled_db_statements[type][stmt_name]

    def fetch_tag_ids(self, taxonomy_id):
        """
        Fetch the available tags under taxonomy with id taxonomy_id

        Return
        -------
        dict: tag_name -> tag_id
        """

        self.db_cursor.execute(
            "SELECT tag_name,tag_id FROM tags WHERE taxonomy_id = %s",
            [taxonomy_id, ]
        )
        tag_id_tuples = self.db_cursor.fetchall()
        tag_ids = OrderedDict(tag_id_tuples)

        return tag_ids

    def get_taxonomies(self):
        """
        Return all taxonomies

        Return
        ------
        List[Dict] - list of taxonomies with DB columns as key
        """
        dict_cursor = self.db_connection.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        dict_cursor.execute("SELECT * FROM taxonomies")
        return dict_cursor.fetchall()

    def get_taxonomy_tags(self, taxonomy_id):
        """
        Return all tags that are found in the given taxonomy.

        Return
        ------
        List[Dict] - list of tags with DB columns as keys
        """
        dict_cursor = self.db_connection.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        dict_cursor.execute(
            """
                SELECT
                    *
                FROM tags
                WHERE (taxonomy_id = %s)
            """,
            (taxonomy_id,),
        )
        return dict_cursor.fetchall()

    def get_tag_values(self, tag_id):
        """
        Return all values associated with the given tag_id.

        Return
        ------
        List[Dict] - list of tags with DB columns as keys
        """
        if not isinstance(tag_id, int):
            raise ValueError("tag_id must be int")

        dict_cursor = self.db_connection.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        dict_cursor.execute(
            """
                SELECT
                    *
                FROM taxonomy_tag_val
                WHERE (tag_id = %s)
            """,
            (tag_id,),
        )
        return dict_cursor.fetchall()

    def get_taxonomy_intersections(self, taxonomy_id, type):
        """
        Return all intersections found in taxonomy with ID taxonomy_id that
        are of type.

        Parameters
        ----------
        type - str
            domain or delegation

        Return
        ------
        List[Dict] - list of tags with DB columns as keys
        """
        dict_cursor = self.db_connection.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        dict_cursor.execute(
            self.get_compiled_stmt("get_taxonomy_intersections", type),
            (taxonomy_id,),
        )
        return dict_cursor.fetchall()

    def get_open_tags(self, taxonomy_id, type, id_):
        """
        Get open tags (end_date and end_ts NULL) that belong to the taxonomy
        with ID taxonomy_id from the table that corresponds to tag_type type
        and that are linked to id id_.

        Return
        -------
        list : int
            List of tag IDs that are open
        """
        self.db_cursor.execute(
            self.get_compiled_stmt("get_open_tags", type),
            [id_, taxonomy_id]
        )

        return [
            {
                "tag_id": _tag_id,
                "value_id": _value_id,
                "measured_at": _measured_at,
                "producer": _producer
            }
            for (_tag_id, _value_id, _measured_at, _producer) in self.db_cursor
        ]

    def get_all_tags(self, taxonomy_id, type, id_):
        """
        Get all tags that belong to the taxonomy with
        ID taxonomy_id from the table that corresponds to tag_type type and
        that are linked to id id_.

        Return
        -------
        list : int
            List of tag IDs that are open
        """
        self.db_cursor.execute(
            self.get_compiled_stmt("get_all_tags", type),
            [id_, taxonomy_id]
        )

        return [
            {
                "tag_id": _tag_id,
                "value_id": _value_id,
                "start_ts": _start_ts,
                "measured_at": _measured_at,
                "end_ts": _end_ts,
                "producer": _producer
            }
            for (
                _tag_id,
                _value_id,
                _start_ts,
                _measured_at,
                _end_ts,
                _producer
            ) in self.db_cursor
        ]

    def _format_as_date(ts):
        return ts.strftime("%Y%m%d")

    def insert_intersections(
        self,
        taxonomy_id,
        timestamp,
        tag_list,
        type,
        id_,
        producer=None
    ):
        """
        Inserts intersections between entitientities with id id_ and the tags
        in tag_list in a given taxonomy.
        """

        if producer is not None and not isinstance(producer, str):
            raise ValueError("expected producer to be a string, got %s" % (
                str(type(producer))
            ))

        if not self.is_valid_tag_type(type):
            raise ValueError("unknown tag type '%s' encountered" % type)

        try:
            stmt = self.get_compiled_stmt("insert_intersections", type)
            params = []
            for _tag in tag_list:
                self.logger.debug("Inserting %s intersection %s" % (
                    type, str(_tag)
                ))
                params.append((
                    id_,
                    _tag["tag_id"],
                    Psycopg2Adapter._format_as_date(timestamp),  # start_date
                    None,  # end_date
                    taxonomy_id,
                    _tag["value_id"],
                    timestamp,  # measured_at
                    timestamp,  # start_ts
                    None,  # end_ts,
                    producer
                ))

            psycopg2.extras.execute_batch(
                self.db_cursor,
                stmt,
                params
            )

        except psycopg2.Error as e:
            raise AdapterDBError(str(e))

    def prolong_intersections(
        self,
        taxonomy_id,
        timestamp,
        tag_list,
        type,
        id_,
        producer=None
    ):
        """
        Prolongs intersections between entities with id id_ and the tags in
        tag_list in a given taxonomy.
        """

        if not self.is_valid_tag_type(type):
            raise ValueError("unknown tag type '%s' encountered" % type)

        stmt_no_value = \
            self.get_compiled_stmt("prolong_intersections_no_value", type)
        stmt_w_value = \
            self.get_compiled_stmt("prolong_intersections_w_value", type)

        params_no_value = []
        params_w_value = []
        for _tag in tag_list:
            if _tag["value_id"] is None:
                self.logger.debug(
                    "prolonging %s intersection %s with value_id null" % (
                        type, str(_tag)
                    )
                )
                params_no_value.append(
                    (
                        timestamp,  # measured_at
                        producer,
                        id_,
                        taxonomy_id,
                        _tag["tag_id"]
                    )
                )
            else:
                self.logger.debug("prolonging %s intersection %s" % (
                    type, str(_tag)
                ))
                params_w_value.append(
                    (
                        timestamp,  # measured_at
                        producer,
                        id_,
                        taxonomy_id,
                        _tag["tag_id"],
                        _tag["value_id"]
                    )
                )
        try:
            psycopg2.extras.execute_batch(
                self.db_cursor,
                stmt_no_value,
                params_no_value
            )

            psycopg2.extras.execute_batch(
                self.db_cursor,
                stmt_w_value,
                params_w_value
            )
        except psycopg2.Error as e:
            raise AdapterDBError(str(e))

    def end_intersections(
        self,
        taxonomy_id,
        timestamp,
        tag_list,
        type,
        id_,
        producer=None
    ):
        """
        Ends intersections between entities with id id_ and the tags in
        tag_list in a given taxonomy.
        """
        if not self.is_valid_tag_type(type):
            raise ValueError("unknown tag type '%s' encountered" % type)

        stmt_no_value = \
            self.get_compiled_stmt("end_intersection_no_value", type)
        stmt_w_value = \
            self.get_compiled_stmt("end_intersection_w_value", type)

        params_no_value = []
        params_w_value = []

        for _tag in tag_list:
            if _tag["value_id"] is None:
                self.logger.debug(
                    "ending %s intersection %s with value_id null" % (
                        type, str(_tag)
                    )
                )
                params_no_value.append(
                    (
                        timestamp,  # measured_at
                        Psycopg2Adapter._format_as_date(timestamp),  # end_date
                        timestamp,  # end_ts
                        producer,
                        id_,
                        taxonomy_id,
                        _tag["tag_id"]
                    )
                )
            else:
                self.logger.debug("ending %s intersection %s" % (
                    type, str(_tag)
                ))
                params_w_value.append(
                    (
                        timestamp,  # measured_at
                        Psycopg2Adapter._format_as_date(timestamp),  # end_date
                        timestamp,  # end_ts
                        producer,
                        id_,
                        taxonomy_id,
                        _tag["tag_id"],
                        _tag["value_id"]
                    )
                )

        try:
            psycopg2.extras.execute_batch(
                self.db_cursor,
                stmt_no_value,
                params_no_value
            )

            psycopg2.extras.execute_batch(
                self.db_cursor,
                stmt_w_value,
                params_w_value
            )
        except psycopg2.Error as e:
            raise AdapterDBError(str(e))

    def fetch_taxonomy_by_id(self, taxonomy_id):
        """
        Return information about the taxonomy with ID taxonomy_id

        Return
        -------
        dict - taxonomy information. Has keys 'id', 'is_allows_autotags', and
                'is_allows_autovalues'

        Raise
        -----
        AdapterDBError
            indicates that taxonomy with that name does not exist
        InconsistentTaxonomyException
            found multiple taxonomies with the same name
        """
        self.logger.debug("fetching taxonomy by ID %i" % taxonomy_id)
        self.db_cursor.execute(
            """
                SELECT
                    id,
                    allows_auto_tags,
                    allows_auto_values
                FROM taxonomy
                WHERE id = %s
            """,
            (taxonomy_id,)
        )
        rows = self.db_cursor.fetchall()
        if len(rows) == 0:
            raise AdapterDBError(
                "taxonomy with id '%s' does not exist" % taxonomy_id
            )
        elif len(rows) > 1:
            raise InconsistentTaxonomyException(
                "encountered multiple taxonomies with the same name"
            )

        (id, allows_auto_tags, allows_auto_values) = rows[0]
        self.logger.debug("found taxonomy with id %i" % taxonomy_id)
        return {
            "id": id,
            "allows_auto_tags": allows_auto_tags,
            "allows_auto_values": allows_auto_values
        }

    def fetch_taxonomy_by_name(self, taxonomy_name):
        """
        Return information about the taxonomy with name taxonomy_name

        Return
        -------
        dict - taxonomy information. Has keys 'id', 'is_allows_autotags', and
                'is_allows_autovalues'

        Raise
        -----
        AdapterDBError
            indicates that taxonomy with that name does not exist
        InconsistentTaxonomyException
            found multiple taxonomies with the same name
        """
        self.logger.debug("fetching taxonomy by name %s" % taxonomy_name)
        self.db_cursor.execute(
            """
                SELECT
                    id,
                    allows_auto_tags,
                    allows_auto_values
                FROM taxonomy
                WHERE name = %s
            """,
            (taxonomy_name,)
        )
        rows = self.db_cursor.fetchall()
        if len(rows) == 0:
            raise AdapterDBError(
                "taxonomy with name '%s' does not exist" % taxonomy_name
            )
        elif len(rows) > 1:
            raise InconsistentTaxonomyException(
                "encountered multiple taxonomies with the same name"
            )

        (id, allows_auto_tags, allows_auto_values) = rows[0]
        self.logger.debug("found taxonomy with id %i" % id)
        return {
            "id": id,
            "allows_auto_tags": allows_auto_tags,
            "allows_auto_values": allows_auto_values
        }

    def check_tag_ids_exist(self, taxonomy_id, tag_id_list):
        """
        Check that the given tag_ids exist and are associated with taxonomy_id.

        Parameters
        ----------
        taxonomy_id - int
            ID of the taxonomy
        tag_id_list - List[int]
            tag IDs to  be checked

        Raises
        ------
        AdapterDBError - indicates that some of the IDs do not exist. The
                         .missing_ids attribute contains the missing IDs.
        """

        if len(tag_id_list) == 0:
            self.logger.debug(
                "checking empty tag_id_list exist on taxonomy %i" % taxonomy_id
            )
            return
        else:
            self.logger.debug("checking tag_ids %s exist in taxonomy %i" % (
                ', '.join(list(map(str, tag_id_list))), taxonomy_id
            ))

        not_found_ids = []

        for _id in tag_id_list:
            self.db_cursor.execute(
                """
                SELECT
                    tag_id
                FROM tags
                WHERE (taxonomy_id = %s) and (tag_id = %s)
                """,
                (
                    taxonomy_id,
                    _id
                )
            )
            _found_ids = self.db_cursor.fetchall()
            if len(_found_ids) == 0:
                self.logger.debug("could not find tag ID %i" % _id)
                not_found_ids.append(_id)
            elif len(_found_ids) == 1:
                self.logger.debug("found tag ID %i" % _id)
            elif len(_found_ids) > 1:
                raise InconsistentTaxonomyException(
                    "multiple tags with the same ID in the same taxonomy found"
                )
        if len(not_found_ids) > 0:
            e = AdapterDBError(
                "IDs %s not found" % ', '.join(map(str, not_found_ids))
            )
            e.missing_ids = not_found_ids
            raise e

    def fetch_tag_ids_by_name(self, taxonomy_id, tag_name_list):
        """
        Return the IDs of the tags in tag_name_list that belong to the
        taxonomy with ID taxonomy_id.

        If no tag could be found for a given name, the ID returned is None.

        Parameters
        ----------
        taxonomy_id - int
            ID of the taxonomy
        tag_name_list - List[str]
            names of the tags to be looked up

        Return
        -------
        dict[str->int or None] - dict that maps names to tag IDs
        """
        if len(tag_name_list) == 0:
            self.logger.debug(
                "checking empty tag_name_list exist "
                "on taxonomy %i" % taxonomy_id
            )
            return {}
        else:
            self.logger.debug("looking for tags %s in taxonomy %i" % (
                ', '.join(map(str, tag_name_list)), taxonomy_id
            ))

        sql = (
            """
            SELECT
                tag_name, tag_id
            FROM tags
            WHERE (taxonomy_id = %%s)
            AND tag_name IN (%s)
            """ % ','.join(["%s"] * len(tag_name_list))
        )

        self.db_cursor.execute(sql, [taxonomy_id, ] + tag_name_list)

        tag_ids_db = defaultdict(list)
        for _tag_name, _tag_id in self.db_cursor.fetchall():
            tag_ids_db[_tag_name].append(_tag_id)

        tag_ids = {}
        for _tag_name in tag_name_list:
            _found_ids = tag_ids_db[_tag_name]
            if len(_found_ids) == 0:
                self.logger.debug(
                    "could not find tag with name %s" % _tag_name
                )
                tag_ids[_tag_name] = None
            elif len(_found_ids) == 1:
                _tag_id = _found_ids[0]
                self.logger.debug(
                    "found tag with name %s under ID %i" % (_tag_name, _tag_id)
                )
                tag_ids[_tag_name] = _tag_id
            elif len(_found_ids) > 1:
                raise InconsistentTaxonomyException(
                    "multiple tags with the same name found "
                    "in the same taxonomy"
                )
        return tag_ids

    def check_value_ids_exist(self, value_id_list):
        """
        Check that the given tag_ids exist and are associated with taxonomy_id.

        Parameters
        ----------
        value_id_list - List[Tuple[int, int]]
            list of tag_id, value_id pairs

        Raises
        ------
        AdapterDBError - indicates that some of the IDs do not exist. The
                         .missing_ids attribute contains the missing IDs.
        """
        if len(value_id_list) == 0:
            self.logger.debug(
                "checking empty value_id_list exists"
            )
            return
        else:
            self.logger.debug("checking value_ids %s exist" % (
                ', '.join(map(str, value_id_list))
            ))

        not_found_ids = []

        for _tag_id, _value_id in value_id_list:
            self.db_cursor.execute(
                """
                SELECT
                    id
                FROM taxonomy_tag_val
                WHERE (tag_id = %s) AND (id = %s)
                """,
                (
                    _tag_id,
                    _value_id
                )
            )
            _found_ids = self.db_cursor.fetchall()
            if len(_found_ids) == 0:
                self.logger.debug(
                    "could not find value ID %i for "
                    "tag ID %i" % (_value_id, _tag_id)
                )
                not_found_ids.append((_tag_id, _value_id))
            elif len(_found_ids) == 1:
                self.logger.debug(
                    "found value ID %i for "
                    "tag ID %i" % (_value_id, _tag_id)
                )
            elif len(_found_ids) > 1:
                raise InconsistentTaxonomyException(
                    "values tags with the same tag and the same value ID found"
                )
        if len(not_found_ids) > 0:
            e = AdapterDBError(
                "IDs %s not found" % ', '.join(map(str, not_found_ids))
            )
            e.missing_ids = not_found_ids
            raise e

    def fetch_value_ids_by_value(self, value_list):
        """
        Return the IDs of the values given in value_list that belong to the
        taxonomy with ID taxonomy_id.

        If a value could not be found in the database, None is returned.

        Parameters
        ----------
        value_list - List[Tuple[int, str]]
            list of tag_id, value pairs

        Return
        -------
        dict[Tuple[tag_id, value]->int or None] - dict that maps values
                                                  to value IDs
        """
        if len(value_list) == 0:
            self.logger.debug(
                "checking empty value_list exists"
            )
            return {}
        else:
            self.logger.debug("looking for values %s" % (
                ', ' % list(map(str, value_list))
            ))

        sql = (
            """
            SELECT
                tag_id, value, id
            FROM taxonomy_tag_val
            WHERE (tag_id, value) IN (%s)
            """ % ','.join(
                ["(%s,%s)"] * len(value_list)
            )
        )

        params = [
            value
            for _tuples in value_list
            for value in _tuples
        ]

        self.db_cursor.execute(sql, params)

        db_value_ids = defaultdict(list)
        for _tag_id, _value, _id in self.db_cursor.fetchall():
            db_value_ids[(_tag_id, _value)].append(_id)

        value_ids = {}

        for _tag_id, _value in value_list:
            _found_ids = db_value_ids[(_tag_id, _value)]
            if len(_found_ids) == 0:
                self.logger.debug("could not find value %s" % _value)
                value_ids[(_tag_id, _value)] = None
            elif len(_found_ids) == 1:
                _value_id = _found_ids[0]
                self.logger.debug(
                    "found value %s for tag ID %i under value ID %i" % (
                        _value,
                        _tag_id,
                        _value_id
                    )
                )
                value_ids[(_tag_id, _value)] = _value_id
            elif len(_found_ids) > 1:
                raise InconsistentTaxonomyException(
                    "multiple values entries with the same entry and the same "
                    "tag ID found"
                )
        return value_ids

    def insert_tags(self, tag_list):
        """
        Insert the tags in tag_list into the database.

        Each tag is given as a dictionary with the structure
            {
                "tag_name": <new tag name>,
                "tag_description": <new tag description>,
                "taxonomy_id": <ID of the taxonomy the tag belongs to>,
                "extras": <additional information, optional>
            }

        No consistency checking beyond the checks done by the database is
        done here. The caller must make sure that the resulting state is
        consistent.

        Parameters
        ----------
        tag_list - List[Dict]
            list of tags to add

        Return
        ------
        dict[str->int] - maps tag_name to new tag_id
        """
        # replace extras by empty dict where none is present
        tag_ids = {}
        tag_list_of_lists = []
        for _tag in tag_list:
            try:
                _tag_list = [
                    _tag["tag_name"],
                    _tag["tag_description"],
                    _tag["taxonomy_id"],
                    json.dumps(_tag["extras"]) if "extras" in _tag else "{}"
                ]
                tag_list_of_lists.append(_tag_list)
            except KeyError as e:
                raise AdapterDBError("missing field '%s' in "
                                     "tag definition" % str(e))
        try:
            for _tag in tag_list_of_lists:
                self.db_cursor.execute(
                    """
                    INSERT INTO tags
                        (tag_name, tag_description, taxonomy_id, extras)
                        VALUES
                        (%s, %s, %s, %s)
                    RETURNING tag_id
                    """,
                    _tag
                )
                tag_ids[_tag[0]] = self.db_cursor.fetchone()[0]
        except psycopg2.Error as e:
            raise AdapterDBError(str(e))
        except psycopg2.Warning as e:
            self.logger.debug(str(e))

        return tag_ids

    def insert_values(self, value_list):
        """
        Insert the values in value_list into the database.

        Each tag is given as a dictionary with the structure
            {
                "value": <value to insert>,
                "tag_id": <ID of the tag the value is associated with>
            }

        No consistency checking beyond the checks done by the database is
        done here. The caller must make sure that the resulting state is
        consistent.

        Parameters
        ----------
        tag_list - List[Dict]
            list of values to add

        Return
        ------
        dict[Tuple[str,int]->int] - maps value/tag_id pairs to new value ID
        """
        value_ids = {}
        value_list_of_lists = []
        for _value in value_list:
            try:
                _value_list = [
                    _value["value"],
                    _value["tag_id"]
                ]
                value_list_of_lists.append(_value_list)
            except KeyError as e:
                raise AdapterDBError(
                    "missing field '%s' in value definition" % str(e)
                )
        try:
            for _value in value_list_of_lists:
                self.logger.debug("inserting value '%s' for tag %i" % (
                    _value[0],
                    _value[1]
                ))
                self.db_cursor.execute(
                    """
                    INSERT INTO taxonomy_tag_val
                        (value, tag_id) VALUES (%s, %s)
                    RETURNING id
                    """,
                    _value
                )
                value_ids[(_value[0], _value[1])] = \
                    self.db_cursor.fetchone()[0]

        except psycopg2.Error as e:
            raise AdapterDBError(e.pgerror)
        except psycopg2.Warning as e:
            self.logger.debug(str(e))

        return value_ids

    def commit(self):
        self.db_connection.commit()

    def rollback(self):
        self.db_connection.rollback()

    def close_connection(self):
        self.db_connection.close()
