from fastapi.testclient import TestClient

import pprint
import psycopg2.extras
import datetime

from .db_test_classes import APIWriteTest
from tests.util import parse_test_db_config

from tag2domain_api.app.main import app

pprinter = pprint.PrettyPrinter(indent=4)
client = TestClient(app)


_, INTXN_TABLE_MAPPINGS = parse_test_db_config()


class MSM2TagEndpointMSM2TAGTest(APIWriteTest):
    def test_post_measurement(self):
        msm = {
            "version": "1",
            "tag_type": "intersection",
            "tagged_id": 3,
            "taxonomy": "tax_test1",
            "producer": "test",
            "measured_at": "2020-12-22T12:35:32",
            "measurement_id": "test/12345",
            "tags": [
                {
                    "tag": "test_tag_1_tax_1",
                    "value": "value_1_tag_1"
                },
                {
                    "tag": "test_tag_3_tax_1"
                },
            ]
        }
        response = client.post(
            "/api/v1/msm2tag/",
            json=msm
        )
        pprinter.pprint(response.json())
        assert response.status_code == 200
        assert response.json() == {"message": "OK"}

        cursor = self.db_connection.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        )

        sql = (
            """
            SELECT
                %(id)s AS id,
                %(taxonomy_id)s AS taxonomy_id,
                %(tag_id)s AS tag_id,
                %(value_id)s AS value_id,
                %(measured_at)s AS measured_at,
                %(producer)s AS producer,
                %(start_date)s AS start_date,
                %(end_date)s AS end_date,
                %(start_ts)s AS start_ts,
                %(end_ts)s AS end_ts
            FROM %(table_name)s
            WHERE
                %(id)s = 3
                AND (%(taxonomy_id)s = 1)
                AND (%(id)s = 3)
            """ % INTXN_TABLE_MAPPINGS["intersection"]
        )

        cursor.execute(sql)

        rows = cursor.fetchall()

        assert len(rows) == 2

        rows = [
            {key: val for key, val in _d.items()}
            for _d in rows
        ]
        pprinter.pprint(rows)
        assert rows == [
            {
                'end_date': None,
                'end_ts': None,
                'id': 3,
                'measured_at': datetime.datetime(2020, 12, 22, 12, 35, 32, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None)),
                'producer': 'test',
                'start_date': 20201222,
                'start_ts': datetime.datetime(2020, 12, 22, 12, 35, 32, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None)),
                'tag_id': 1,
                'taxonomy_id': 1,
                'value_id': 1
            },
            {
                'end_date': None,
                'end_ts': None,
                'id': 3,
                'measured_at': datetime.datetime(2020, 12, 22, 12, 35, 32, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None)),
                'producer': 'test',
                'start_date': 20201222,
                'start_ts': datetime.datetime(2020, 12, 22, 12, 35, 32, tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None)),
                'tag_id': 3,
                'taxonomy_id': 1,
                'value_id': None
            }
        ]

    def test_post_measurement_fail_empty_msm(self):
        msm = {}
        response = client.post(
            "/api/v1/msm2tag/",
            json=msm
        )
        pprinter.pprint(response.json())
        assert response.status_code == 422

    def test_post_measurement_fail_invalid_tag_type(self):
        msm = {
            "version": "1",
            "tag_type": "phantasy_tag_type",
            "tagged_id": 3,
            "taxonomy": "tax_test1",
            "producer": "test",
            "measured_at": "2020-12-22T12:35:32",
            "measurement_id": "test/12345",
            "tags": [
                {
                    "tag": "test_tag_1_tax_1",
                    "value": "value_1_tag_1"
                },
                {
                    "tag": "test_tag_3_tax_1"
                },
            ]
        }
        response = client.post(
            "/api/v1/msm2tag/",
            json=msm
        )
        pprinter.pprint(response.json())
        assert response.status_code == 400
