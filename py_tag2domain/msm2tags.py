from __future__ import print_function
import os
import json
import logging
import datetime
import time
from collections import namedtuple

import jsonschema
import pytz

from py_tag2domain.exceptions import (
    InvalidMeasurementException,
    DisallowedTaxonomyModificationException,
    StaleMeasurementException,
    AdapterDBError
)
from py_tag2domain.util import parse_timestamp, calc_changes

DEFAULT_MAX_MEASUREMENT_AGE = None


class MeasurementToTags(object):
    """
    Updates tag2domain entries based on measurements.
    """

    # This named tuple defines the attributes that lead to tags starting and
    # ending. If two tags have the same values associated with the keys named
    # below, they are considered to be the same.
    TagStateTuple = namedtuple(
        "TagStateTuple",
        ["tag_id", "value_id"]
    )

    def __init__(
        self,
        db_adapter,
        logger=logging,
        max_measurement_age=DEFAULT_MAX_MEASUREMENT_AGE
    ):
        self.db_adapter = db_adapter
        self.logger = logger
        self.msm_schema = MeasurementToTags.load_msm_schema(self.logger)
        self.max_measurement_age = max_measurement_age

    def handle_measurement(self, msm, skip_validation=False):
        """
        Handles a single measurement, from validating the measurement to
        writing the resulting tags to the database

        The return looks like this:
        {
            "tag_type": str,  # 'delegation' or 'domain'
            "tagged_id": int,  # ID in domain or delegation table
            "taxonomy_id": int,  # taxonomy ID
            "measured_at": str,  # timestamp of the input measurement
            "tag_changes": {
                "insert": Tuple[TagStateTuple],  # new tags inserted
                "prolong": Tuple[TagStateTuple],  # tags that were extended
                "end": Tuple[TagStateTuple]  # tags that were ended
            }
        }

        The tag TagStateTuple are named tuples defined in MeasurementToTags.
        They have two attributes: .tag_id and .value_id corresponding to IDs
        in the tags and taxonomy_tag_val table.

        Parameters
        ----------
        measurement - dict
            dict that conforms to the measurement_schema
        skip_validation - dict
            skip the validation of msm against the measurement schema. Tis can
            be useful when the validation has already been done.

        Raises
        ------
        InvalidMeasurementException
            the measurement msm is not in the right format or there are keys
            missing or the measurement is for an unknown tag type
        StaleMeasurementException
            the measurement msm is older than max_measurement_age

        Return
        ------
        dict - contains information about the tag changes triggered by the
            measurement
        """
        t_start_total = time.time()

        self.logger.debug("received measurement")
        if not skip_validation:
            # throws InvalidMeasurementException if msm is invalid
            self.validate_measurement(msm)

        self.logger.debug(json.dumps(msm, indent=4))

        msm_timestamp = parse_timestamp(msm["measured_at"])

        if "measurement_id" in msm:
            self.logger.info(
                "received measurement %s:%s measured at %s" % (
                    msm["producer"],
                    msm["measurement_id"],
                    msm["measured_at"]
                )
            )
        else:
            self.logger.info(
                "received measurement from producer %s measured at %s" % (
                    msm["producer"], msm["measured_at"]
                )
            )

        # throw an InvalidMeasurmentException if the tag type is not known
        if not self.db_adapter.is_valid_tag_type(msm["tag_type"]):
            raise InvalidMeasurementException(
                "unknown tag_type '%s'" % msm["tag_type"]
            )

        # throws StaleMeasurementException if msm is invalid
        self.check_max_age(msm_timestamp)

        # throws InvalidMeasurementException if msm does not fit into
        # tag2domain tables
        _t_start = time.time()
        taxonomy_db_info = self.prepare_tag2domain_taxonomy(msm)
        self.logger.debug(
            "finished preparing taxonomy in %5.3f ms",
            1000 * (time.time() - _t_start)
        )

        _t_start = time.time()
        required_intersection_changes = self.calculate_changes(
            msm["tagged_id"],
            msm["tag_type"],
            msm_timestamp,
            msm["producer"],
            taxonomy_db_info
        )
        self.logger.debug(
            "finished calculating intersection changes in %5.3f ms",
            1000 * (time.time() - _t_start)
        )

        _t_start = time.time()
        self.write_intersection_changes(
            taxonomy_db_info["taxonomy"]["id"],
            msm_timestamp,
            required_intersection_changes,
            msm["tag_type"],
            msm["tagged_id"],
            msm["producer"]
        )
        self.logger.debug(
            "finished writing intersection changes in %5.3f ms",
            1000 * (time.time() - _t_start)
        )

        self.logger.debug("committing to DB")
        _t_start = time.time()
        self.db_adapter.commit()
        self.logger.debug(
            "finished committing DB changes in %5.3f ms",
            1000 * (time.time() - _t_start)
        )

        self.logger.info(
            "finished handling measurement in %5.3f ms",
            1000 * (time.time() - t_start_total)
        )

        return {
            "tag_type": msm["tag_type"],
            "tagged_id": msm["tagged_id"],
            "taxonomy_id": taxonomy_db_info["taxonomy"]["id"],
            "measured_at": msm_timestamp,
            "tag_changes": required_intersection_changes
        }

    def calculate_changes(
        self,
        tagged_id,
        tag_type,
        measured_at,
        producer,
        taxonomy_db_info
    ):
        """
        Takes a measurement's data and calculates the tag changes required.

        The producer is checked against the producer that is found associated
        with existing intersections. If an existing intersection is touched
        that was produced by another producer an invalid MeasurementException
        is thrown.

        Parameters
        ----------
        tagged_id - int
            ID the measurement referst to
        tag_type - str
            type of tag (domain or delegation)
        measured_at - datetime.datetime
            timestamp of the measurement
        taxonomy_db_info - dict
            dict that describes the taxonomy, tags, and values that are
            present in the measurement. See prepare_tag2domain_taxonomy
            for the format of this dict.
        producer - str
            name of the producer of the tag

        Throws
        ------
        StaleMeasurementException - if an existing tag with an older
            measured_at than the measured_at given as parameter is found
        InvalidMeasurementException - if an existing tag with another producer
            is found
        AdapterDBError - errors thrown by the DB adapter
        """
        if not isinstance(tagged_id, int):
            raise ValueError("tagged_id must be int")

        if not isinstance(measured_at, datetime.datetime):
            raise ValueError("measured_at must be of type datetime.datetime")

        if not isinstance(taxonomy_db_info, dict):
            raise ValueError("taxonomy_db_info must be a dict")

        if producer is not None and not isinstance(producer, str):
            raise ValueError("expected producer to be str, got %s" % str(
                type(producer)
            ))

        open_tags = self.db_adapter.get_open_tags(
            taxonomy_db_info["taxonomy"]["id"],
            tag_type,
            tagged_id
        )

        tags_by_tag_id_value_id = dict()
        for _tag in open_tags:
            tags_by_tag_id_value_id[(_tag["tag_id"], _tag["value_id"])] = _tag
            if measured_at <= _tag["measured_at"]:
                raise StaleMeasurementException(
                    "received measurement with timestamp %s and found tag that"
                    " has an equal or more recent measured_at with %s" % (
                        measured_at.strftime("%Y-%m-%dT%H:%M:%S"),
                        _tag["measured_at"].strftime("%Y-%m-%dT%H:%M:%S")
                    )
                )

        tag_states_old = frozenset(map(
            lambda x: MeasurementToTags.TagStateTuple(
                x["tag_id"],
                x["value_id"] if "value_id" in x else None
            ),
            open_tags
        ))

        tag_states_new = frozenset(map(
            lambda x: MeasurementToTags.TagStateTuple(
                x["tag_id"],
                x["value_id"] if "value_id" in x else None
            ),
            taxonomy_db_info["tags"]
        ))

        changes = calc_changes(tag_states_old, tag_states_new)

        # check the producers of the modified tags and throw an error
        # if they are modified in a forbidden way
        # the rules implemented are:
        #   + if a producer is set in an intxn then the producer of the
        #       msm has to match, otherwise an error is thrown.
        #   + if no producer is set in the intxn the producer of the msm
        #       can be None or a value. In this case the existing tags are
        #       updated.

        for _tag_state in (changes["prolong"] + changes["end"]):
            _tag = tags_by_tag_id_value_id[(
                _tag_state.tag_id,
                _tag_state.value_id
            )]
            _prod = _tag["producer"]
            if _prod is not None and producer is None:
                raise InvalidMeasurementException(
                    "measurement produced by unnamed producer tried to modify "
                    "intersection produced by %s" % (_prod)
                )

            if _prod is not None:
                if _prod != producer:
                    raise InvalidMeasurementException(
                        "measurement produced by %s tried to modify "
                        "intersection produced by %s" % (producer, _prod)
                    )
        return changes

    def check_max_age(self, ts):
        """
        Checks whether ts is longer ago than max_measurement_age.

        If max_measurment_age is None no check is performed.

        Raise
        -----
        StaleMeasurementException - indicates that a measurement is older
            than max_measurement_age
        """
        now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        if (
            self.max_measurement_age is not None
            and (ts < (now - self.max_measurement_age))
        ):
            raise StaleMeasurementException(
                "received measurement with timestamp %s at time %s" % (
                    ts.strftime("%Y-%m-%dT%H:%M:%S"),
                    now.strftime("%Y-%m-%dT%H:%M:%S")
                )
            )

    def validate_measurement(self, msm):
        """
        Validates the measurement against the measurement_schema and returns
        if successful. Otherwise throws an exception.

        Raises
        ------
        InvalidMeasurementException
            the measurement msm is not in the right format or there are keys
            missing
        """
        self.logger.debug("validating measurement")
        try:
            jsonschema.validate(instance=msm, schema=self.msm_schema)
        except Exception as e:
            raise InvalidMeasurementException(str(e))

        if "autogenerate_tags" in msm and msm["autogenerate_tags"]:
            for item in msm["tags"]:
                if "description" not in item:
                    raise InvalidMeasurementException(
                        "missing tag description in tag required by "
                        "autogenerate_tags"
                    )
                if not isinstance(item["tag"], str):
                    raise InvalidMeasurementException(
                        "Field 'tag' must contain a string if "
                        "autogenerate_tags is true"
                    )

    def prepare_tag2domain_taxonomy(self, msm):
        """
        Prepare the tag2domain taxonomies according to msm.

        The returned dictionary has the following structure:
        {
                "taxonomy": {
                    "id": <taxonomy DB ID>,
                    "allows_auto_tags": <true/false>,
                    "allows_auto_values": <true/false>
                },
                "tags": [
                    {
                        "tag": <tag name or ID as given in msm>,
                        "tag_name": <tag name if given in msm>,
                        "tag_id": <tag DB ID>,
                        "value": <tag value if given in msm>,
                        "value_id": <tag value DB ID if value given in msm>,
                        "tag_description": <tag description if given in msm>,
                        "extras": <tag extras if given in msm>
                    }
                ]
        }
        None tag_id and value_id are guaranteed to contain an integer.

        Returns
        -------
        dict - dictionary that contains the taxonomy, tag and value IDs
            for the update

        Raises
        ------
        DisallowedTaxonomyModificationException
            the measurement required changes to the taxonomy that are forbidden
        InvalidMeasurementException
            the given measurement is incompatible with the taxonomies in the
            database
        """
        db_info = self.fetch_db_information(msm)

        db_info = self.add_missing_tag2domain_taxonomy_entries(db_info)

        return db_info

    def fetch_db_information(self, msm):
        """
        Collect the DB IDs of the database entries that are affected by the
        measurement msm.

        The returned dictionary hase the following structure:
            {
                "taxonomy": {
                    "id": <taxonomy DB ID>,
                    "allows_auto_tags": <true/false>,
                    "allows_auto_values": <true/false>
                },
                "tags": [
                    {
                        "tag": <tag name or ID as given in msm>,
                        "tag_name": <tag name if given in msm>,
                        "tag_id": <tag DB ID>,
                        "value": <tag value if given in msm>,
                        "value_id": <tag value DB ID if value given in msm>,
                        "tag_description": <tag description if given in msm>,
                        "extras": <tag extras if given in msm>
                    }
                ]
            }
        In the tags list, None entries indicate that the associated entry
        does not yet exist. If tag_id and value_id are integers they are
        guaranteed to exist in the database.

        Parameters
        ----------
        msm - dict
            measurement that conforms to the measurement schema

        Returns
        -------
        dict - database information required to change tags.
        """
        db_info = {}

        # fetch the taxonomy ID
        if isinstance(msm["taxonomy"], str):
            try:
                db_info["taxonomy"] = \
                    self.db_adapter.fetch_taxonomy_by_name(msm["taxonomy"])
            except AdapterDBError as e:
                raise InvalidMeasurementException(str(e))
        elif isinstance(msm["taxonomy"], int):
            try:
                db_info["taxonomy"] = \
                    self.db_adapter.fetch_taxonomy_by_id(msm["taxonomy"])
            except AdapterDBError as e:
                raise InvalidMeasurementException(str(e))
        else:
            raise ValueError("msm[taxonomy] should be of type int or str")

        # check taxonomy constraints
        if (
            (not db_info["taxonomy"]["allows_auto_tags"])
            and "autogenerate_tags" in msm
            and msm["autogenerate_tags"]
        ):
            raise DisallowedTaxonomyModificationException(
                "taxonomy with ID %i does not allow tag "
                "automatic tag generation" % (
                    db_info["taxonomy"]["id"]
                )
            )

        if (
            (not db_info["taxonomy"]["allows_auto_values"])
            and "autogenerate_values" in msm
            and msm["autogenerate_values"]
        ):
            raise DisallowedTaxonomyModificationException(
                "taxonomy with ID %i does not allow "
                "automatic value generation" % (
                    db_info["taxonomy"]["id"]
                )
            )

        # Fetch IDs for tags given by name from DB
        _tag_ids = self.db_adapter.fetch_tag_ids_by_name(
            db_info["taxonomy"]["id"],
            [
                _tag["tag"]
                for _tag in msm["tags"]
                if isinstance(_tag["tag"], str)
            ]
        )

        if (
            ("autogenerate_tags" not in msm)
            or (not msm["autogenerate_tags"])
        ):
            for _tag, _id in _tag_ids.items():
                if _id is None:
                    raise InvalidMeasurementException(
                        "tag '%s' is not in taxonomy" % (str(_tag))
                    )

        # Check that the tag IDs given exist
        try:
            self.db_adapter.check_tag_ids_exist(
                db_info["taxonomy"]["id"],
                [
                    _tag["tag"]
                    for _tag in msm["tags"]
                    if isinstance(_tag["tag"], int)
                ]
            )
        except AdapterDBError as e:
            raise InvalidMeasurementException(
                "some tag_ids do no exist: %s" % (
                    ', '.join(map(str, e.missing_ids))
                )
            )

        # Append the IDs of tags given by ID -  whether these exist is checked
        # during the insert
        for _tag in msm["tags"]:
            if isinstance(_tag["tag"], int):
                _tag_ids[_tag["tag"]] = _tag["tag"]

        # Combine this in the db_info list
        db_info["tags"] = []
        for _tag in msm["tags"]:
            _d = {
                "tag": _tag["tag"],
                "tag_id": _tag_ids[_tag["tag"]]
            }
            if "value" in _tag:
                _d["value"] = _tag["value"]
            if isinstance(_tag["tag"], str):
                _d["tag_name"] = _tag["tag"]
            if "description" in _tag:
                _d["tag_description"] = _tag["description"]
            if "extras" in _tag:
                _d["extras"] = _tag["extras"]

            db_info["tags"].append(_d)

        # fetch value IDs for tags where values are given as names
        _value_ids = self.db_adapter.fetch_value_ids_by_value(
            [
                (_tag_ids[_tag["tag"]], _tag["value"])
                for _tag in db_info["tags"]
                if "value" in _tag
                if isinstance(_tag["value"], str)
            ]
        )

        if (
            ("autogenerate_values" not in msm)
            or (not msm["autogenerate_values"])
        ):
            for (_tag_id, _val), _id in _value_ids.items():
                if _id is None:
                    if _tag_id is None:
                        raise InvalidMeasurementException(
                            "value '%s' can not be generated "
                            "in taxonomy '%i' because autogenerating values "
                            "is not allowed" % (
                                _val,
                                db_info["taxonomy"]["id"]
                            )
                        )
                    else:
                        raise InvalidMeasurementException(
                            "value '%s' is not associated with tag ID '%s' "
                            "in taxonomy '%i' and autogenerating values is "
                            "not allowed" % (
                                _val,
                                str(_tag_id),
                                db_info["taxonomy"]["id"]
                            )
                        )

        # Check that the value IDs given exist and are consistent
        try:
            self.db_adapter.check_value_ids_exist(
                [
                    (_tag["tag_id"], _tag["value"])
                    for _tag in db_info["tags"]
                    if "value" in _tag
                    if isinstance(_tag["value"], int)
                ]
            )
        except AdapterDBError as e:
            raise InvalidMeasurementException(
                "some value_ids do no exist: %s" % (
                    ', '.join(map(str, e.missing_ids))
                )
            )

        for _tag in db_info["tags"]:
            if "value" in _tag:
                if isinstance(_tag["value"], int):
                    _tag["value_id"] = _tag["value"]
                elif isinstance(_tag["value"], str):
                    _tag["value_id"] = _value_ids[(
                        _tag["tag_id"],
                        _tag["value"])
                    ]
                else:
                    raise ValueError("value field must be int or str")

        return db_info

    def add_missing_tag2domain_taxonomy_entries(self, db_info):
        taxonomy_id = db_info["taxonomy"]["id"]
        # gather missing tags
        tags_to_add = []
        for _tag in db_info["tags"]:
            if _tag["tag_id"] is None:
                _copy = dict(_tag)
                _copy["taxonomy_id"] = taxonomy_id
                tags_to_add.append(_copy)

        for _tag in tags_to_add:
            self.logger.info("adding new tag '%s' to taxonomy ID %i" % (
                _tag["tag_name"], _tag["taxonomy_id"]
            ))

        if len(tags_to_add) > 0:
            assert db_info["taxonomy"]["allows_auto_tags"]
            new_tag_ids = self.db_adapter.insert_tags(tags_to_add)

        # Update the tag IDs in db_info (required for values below)
        for _tag in db_info["tags"]:
            if _tag["tag_id"] is None:
                _tag["tag_id"] = new_tag_ids[_tag["tag_name"]]

        # gather missing values
        values_to_add = [
            {
                "value": _tag["value"],
                "tag_id": _tag["tag_id"]
            }
            for _tag in db_info["tags"]
            if "value_id" in _tag
            if _tag["value_id"] is None
        ]

        for _value in values_to_add:
            self.logger.info("adding new value '%s' to tag ID %i" % (
                _value["value"],
                _value["tag_id"]
            ))

        if len(values_to_add) > 0:
            assert db_info["taxonomy"]["allows_auto_values"]
            new_value_ids = self.db_adapter.insert_values(values_to_add)

        # Update the value IDs in db_info
        for _tag in db_info["tags"]:
            if "value" in _tag and _tag["value_id"] is None:
                _tag["value_id"] = new_value_ids[(
                    _tag["value"],
                    _tag["tag_id"]
                )]

        return db_info

    def write_intersection_changes(
        self,
        taxonomy_id,
        timestamp,
        changes,
        intxn_type,
        tagged_id,
        producer
    ):
        """
        Calculate and execute the changes to the intersection tables that are
        required to update the state in the DB to the state of the measurement
        msm.

        Parameters
        ----------
        taxonomy_id - int
            taxonomy ID to be written to
        timestamp - datetime.datetime
            timestampt of the measurement. Will be written to measured_at and
            start and end timestamps where appropriate.
        changes - dict
            dict with keys 'insert', 'prolong', and 'end', each associated
            with a list of TagStateTuple. Specifies the changes to be
            applied.
        intxn_type - str (domain or delegation)
            type of intersections to change
        tagged_id - int
            ID of the tagges entity
        """
        if not isinstance(taxonomy_id, int):
            raise ValueError("taxonomy_id must be int")

        if not isinstance(timestamp, datetime.datetime):
            raise ValueError("timestamp must be instance of datetime.datetime")

        if not isinstance(changes, dict):
            raise ValueError("changes must be dict")

        if set(changes.keys()) != set(['insert', 'prolong', 'end']):
            raise ValueError("changes must have keys insert, prolong, and end")

        if not isinstance(tagged_id, int):
            raise ValueError("tagged_id must be int")

        for _intxn in changes["insert"]:
            self.logger.info(
                "%s ID % 8i taxonomy ID % 3i: opening tag-value-pair %s-%s" % (
                    intxn_type,
                    tagged_id,
                    taxonomy_id,
                    str(_intxn.tag_id),
                    str(_intxn.value_id)
                )
            )
        self.db_adapter.insert_intersections(
            taxonomy_id,
            timestamp,
            map(lambda x: x._asdict(), changes["insert"]),
            intxn_type,
            tagged_id,
            producer
        )

        for _intxn in changes["prolong"]:
            self.logger.info(
                "%s ID % 8i taxonomy ID % 3i: prolonging "
                "tag-value-pair %s-%s" % (
                    intxn_type,
                    tagged_id,
                    taxonomy_id,
                    str(_intxn.tag_id),
                    str(_intxn.value_id)
                )
            )
        self.db_adapter.prolong_intersections(
            taxonomy_id,
            timestamp,
            map(lambda x: x._asdict(), changes["prolong"]),
            intxn_type,
            tagged_id,
            producer
        )

        for _intxn in changes["end"]:
            self.logger.info(
                "%s ID % 8i taxonomy ID % 3i: ending "
                "tag-value-pair %s-%s" % (
                    intxn_type,
                    tagged_id,
                    taxonomy_id,
                    str(_intxn.tag_id),
                    str(_intxn.value_id)
                )
            )
        self.db_adapter.end_intersections(
            taxonomy_id,
            timestamp,
            map(lambda x: x._asdict(), changes["end"]),
            intxn_type,
            tagged_id,
            producer
        )

    @staticmethod
    def load_msm_schema(logger=logging):
        """
        Loads the msm schema and returns it
        """
        msm_schema_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "schema",
            "measurement.json"
        )
        logger.debug(
            "Loading measurement schema from %s" % msm_schema_path
        )
        return json.loads(open(msm_schema_path).read())
