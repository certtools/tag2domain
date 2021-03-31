# Example tag2domain measurements
## Contents
The json files found in this directory contain example measurements that
can be used together with the example database that is created by the
all-in-one examples.

A measurement contains the following keys:
+ _version_ - the version of the measurement format used (at this time "1" is
the only valid value)
+ _tag_type_ - the type of the tag to be set. This type must correspond to one
of the intersection tables that has been configured for the tag2domain
components.
+ _tagged_id_ - the ID of the entity to be tagged. This could be the ID of a
domain or of a cluster.
+ _taxonomy_ - ID (as integer) or name (as string) of the taxonomy the tags
refer to.
+ _producer_ - a string that identifies who or which program has produced the
measurement. Note, that at this time only the same producer can modify a tag.
If a measurement from producer _A_ sets a tag and producer _B_ tries to end it,
the measurement will be rejected.
+ _measured_at_ - a timestamp that reflects the time at which the measurement
was taken. The format is `YYYY-mm-ddTHH:MM:SS`.
+ _measurement_id_ (optional) - an ID that identifies the measurement.
+ _tags_ - contains a list of tags to be set Each tag has the following keys:
    + _tag_ - ID (as integer) or name (as string) of the tag to be set.
    + _value_ (optional) - ID (as integer) or value (as string) to be set.
    + _description_ (required if autogenerate_tags = true) - a dsecription of the tag. If a tag is newly
    generated this description is set with the tag. If the tag already exists
    this value is ignored.
    + _extras_ (required if autogenerate_tags = true) - a JSON object that contains further information
    about the tag.
+ _autogenerate_tags_ - set to true to automatically insert tags that are not
yet defined in the taxonomy. This requires that the taxonomy allows automatic
insertion of tags.
+ _autogenerate_values_ - set to true to automatically insert values that are
not yet defined in the taxonomy. This requires that the taxonomy allows
automatic insertion of values.

Example (`measurement_flavor_salty_strongly.json`):

``` json
{
    "version": "1",
    "tag_type": "domain",
    "tagged_id": 3,
    "taxonomy": "flavors",
    "producer": "test",
    "measured_at": "2020-12-23T10:30:51",
    "measurement_id": "test/1",
    "tags": [
      {
        "tag": "salty",
        "value": "strongly"
      }
    ]
}
```

## Submitting measurements to the REST interface (all-in-one example)
This example assumes that there is a tag2domain-api available where the
MSM2TAG functionality is enabled. To send the `flavor_salty_strongly`
measurement execute the following command (replace `<API HOST>` with the
address where tag2domain API is running):
``` bash
API_HOST=<TAG2DOMAIN API HOST>
cat measurement_flavor_strongly_salty.json \
    | sed "s/{MEASURED_AT}/$(date +"%Y-%m-%dT%T")/" \
    | curl \
        -X POST "${API_HOST}/api/v1/msm2tag/" \
        -H  "accept: application/json" \
        -H  "Content-Type: application/json" \
        --data @-
```

The sed command sets the _measured_at_ field of the measurement to the current
time. The resulting tag can be fetched by running
``` bash
curl \
    -X GET "${API_HOST}/api/v1/bydomain/domain_test3.at?limit=1000" \
    -H  "accept: application/json"
```

Alternatively you can test the REST interface in your browser by visiting
`\<API HOST\>/docs`.

## Submitting measurements to a kafka topic (all-in-one-kafka example)
For this method of submitting measurements a [kafka](https://kafka.apache.org/)
setup must be configured and the `kafka-console-producer.sh` must be accessible
in the _PATH_ environment. The tools are included in the `bin/` folder of the
kafka package.

To send a measurement, first configure the kafka broker and topic to send to:
``` bash
export KAFKA_BROKER=<YOUR KAFKA BROKERS URL>
export KAFKA_TOPIC=<THE KAFKA TOPIC TO SEND TO>
```
These options should match the broker and topic that the msm2tag2domain
service is listening to. The measurement can then be submitted using the
script
``` bash
submit_measurement-kafka.sh measurement_flavor_strongly_salty.json
```

 The resulting tag can be fetched by running this command:
``` bash
API_HOST=<TAG2DOMAIN API HOST>
curl \
    -X GET "${API_HOST}/api/v1/bydomain/domain_test3.at?limit=1000" \
    -H  "accept: application/json"
```