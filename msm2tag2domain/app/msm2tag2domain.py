#!/usr/bin/env python
from __future__ import print_function
import sys
import configparser
import argparse
import logging
import traceback
import datetime

import json
from kafka import KafkaConsumer

from py_tag2domain.msm2tags import MeasurementToTags
from py_tag2domain.db import Psycopg2Adapter
from py_tag2domain.util import parse_config
import py_tag2domain.exceptions

LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR
}


def error(s, exit_code=1):
    logging.error(s)
    sys.exit(exit_code)


class KafkaLooper(object):
    def __init__(
        self,
        config,
        msm_handler,
        result_handler=None,
        logger=logging.getLogger()
    ):
        self.logger = logger
        self.msm_handler = msm_handler
        self.result_handler = result_handler

        # check config
        try:
            kafka_config = config["kafka"]
        except KeyError:
            error("could not find 'kafka' section in config file")

        for _option in [
            "topic_name",
            "group_id",
            "bootstrap_servers",
            "client_id"
        ]:
            if not config.has_option("kafka", _option):
                error("could not find required option kafka.%s "
                      "in config file" % str(_option))

        # connect to kafka
        self.logger.info(
            "connecting to kafka (queue=%s, "
            "group=%s, bootstrap_server=%s, client_id=%s)" % (
                kafka_config.get("topic_name"),
                kafka_config.get("group_id"),
                kafka_config.get("bootstrap_servers"),
                kafka_config.get("client_id")
            )
        )
        logging.getLogger("kafka").setLevel(logging.WARNING)
        try:
            self.consumer = KafkaConsumer(
                kafka_config.get("topic_name"),
                group_id=kafka_config.get("group_id"),
                bootstrap_servers=kafka_config.get("bootstrap_servers"),
                client_id=kafka_config.get("client_id"),
                max_poll_records=1,
                enable_auto_commit=False
            )
        except Exception as e:
            error("could not connect to kafka queue (%s) - %s" % (
                type(e), str(e)
            ))

    def loop(self):
        self.logger.info("startup finished, waiting for kafka events")
        for msg in self.consumer:
            self.logger.info("received kafka message")
            if msg.value == 'json failed to parse':
                self.logger.warning("received json failed to parse")
                self.consumer.commit()
                continue
            try:
                msg_decoded = msg.value.decode('utf-8', 'ignore')
            except ValueError:
                self.logger.warning("Could not decode msg: {}".format(msg))
                continue

            try:
                measurement = json.loads(msg_decoded)
            except ValueError:
                self.logger.warning(
                    "could not parse json: {}".format(msg_decoded)
                )
                continue

            success, result = self.msm_handler(measurement)
            if success:
                self.logger.debug(
                    "handled measurement successfully - committing"
                )
                self.consumer.commit()

            if self.result_handler is not None:
                self.result_handler(success, measurement, result)

            if not success:
                continue


class StreamLooper(object):
    KEYSTRING = "--**--SEPARATOR-52579864--**--"

    def __init__(
        self,
        stream,
        msm_handler,
        result_handler=None,
        logger=logging.getLogger()
    ):
        self.logger = logger
        self.msm_handler = msm_handler
        self.stream = stream
        self.result_handler = result_handler

    def get_msms(stream):
        read_string = ""
        char = stream.read(1)
        while char != '':
            read_string += char
            keystring_len = len(__class__.KEYSTRING)
            if (
                (len(read_string) >= keystring_len)
                and (
                    read_string[keystring_len:] == __class__.KEYSTRING
                )
            ):
                msm = read_string[:-len(__class__.KEYSTRING)]
                read_string = ""
                yield msm
            char = stream.read(1)
        yield read_string

    def loop(self):
        self.logger.info("startup finished, reading measurements")
        for msg in __class__.get_msms(self.stream):
            self.logger.info("read message")
            if msg == 'json failed to parse':
                self.logger.warning("received json failed to parse")
                continue
            try:
                measurement = json.loads(msg)
            except ValueError:
                self.logger.warning("Could not parse json: {}".format(msg))
                continue

            success, result = self.msm_handler(measurement)
            if success:
                self.logger.debug("handled measurement successfully")
            else:
                self.logger.debug("handling of measurement failed")

            if self.result_handler is not None:
                self.result_handler(success, measurement, result)


def get_msm_looper(args, config, msm_handler, result_handler=None):
    if args.stdin:
        logging.info("reading measurements from stdin")
        looper = StreamLooper(
            sys.stdin,
            msm_handler,
            result_handler=result_handler
        )
    elif args.file:
        logging.info("opening measurement file %s" % args.file)
        try:
            f = open(args.file, encoding="utf-8")
        except IOError as e:
            error("could not open measurement file %s - %s" % (
                config.file,
                str(e)
            ))
        looper = StreamLooper(f, msm_handler, result_handler=result_handler)
    elif args.kafka:
        looper = KafkaLooper(
            config,
            msm_handler,
            result_handler=result_handler
        )
    else:
        error("no measurement source specified")

    return looper


def run(args, config):
    # set up database connection
    db_logger = logging.getLogger()
    db_config, intxn_table_mappings = parse_config(config)
    db_pars = Psycopg2Adapter.to_psycopg_args(db_config)

    if db_config is None:
        error("could not read DB configuration")

    if intxn_table_mappings is None:
        error("table mappings are not defined")

    try:
        db_adapter = Psycopg2Adapter(
            db_pars,
            intxn_table_mappings,
            logger=db_logger
        )
    except py_tag2domain.exceptions.AdapterConnectionException as e:
        error("could not connect to database - %s" % str(e))

    # create MeasruementToTags object
    msm2tags_logger = logging.getLogger()
    max_measurement_age_int = config.getint(
        "tag2domain",
        "max_measurement_age",
        fallback=None
    )
    if max_measurement_age_int is None:
        max_measurement_age = None
        logging.info(
            "setting up MeasurementToTags without a max measurement age"
        )
    else:
        max_measurement_age = datetime.timedelta(
            minutes=max_measurement_age_int
        )
        logging.info(
            "setting up MeasurementToTags with max measurement "
            "age of %i minutes" % (
                max_measurement_age_int
            )
        )
    msm2tags = MeasurementToTags(
        db_adapter,
        logger=msm2tags_logger,
        max_measurement_age=max_measurement_age
    )

    def msm_handler(msm):
        try:
            result = msm2tags.handle_measurement(msm)
        except py_tag2domain.exceptions.InvalidMeasurementException as e:
            logging.warning("invalid measurement - %s" % str(e))
            raise
        except py_tag2domain.exceptions.StaleMeasurementException as e:
            logging.warning("stale measurement - %s" % str(e))
            return True, None
        except Exception as e:
            bt = traceback.format_exc()
            error("unknown exception - %s\n%s" % (str(e), bt))

        return True, result

    msm_looper = get_msm_looper(args, config, msm_handler)

    msm_looper.loop()

    logging.info("all measurements consumed - exiting")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="measurement to tag2domain script"
    )

    parser.add_argument(
        "config",
        type=str,
        help="path of config file"
    )

    input_group = parser.add_mutually_exclusive_group(required=True)

    input_group.add_argument(
        "-in",
        "--stdin",
        action="store_true"
    )

    input_group.add_argument(
        "-f",
        "--file",
        type=str,
        help="read measurements from a file",
        default=False
    )

    input_group.add_argument(
        "-k",
        "--kafka",
        action="store_true"
    )

    logging.basicConfig(level=logging.INFO)

    args = parser.parse_args()

    logging.info("reading config file %s" % args.config)

    config = configparser.ConfigParser()
    try:
        keys = config.read(args.config)
        if len(keys) == 0:
            error("could not read config")
    except Exception as e:
        error("could not read config file - %s" % (str(e)))

    loglevel_str = config.get("logging", "level", fallback="info").lower()
    try:
        loglevel = LOG_LEVELS[loglevel_str]
    except KeyError:
        error("unknown logging level '%s' configured" % loglevel_str)
    logging.getLogger().setLevel(loglevel)

    run(args, config)
