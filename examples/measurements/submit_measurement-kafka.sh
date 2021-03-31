#!/bin/bash

infile="$1"

if [ -z "$infile" ]; then
  >&2 echo "ERROR: not enough arguments. Usage: $0 <MEASUREMENT FILE>"
  exit 1
fi

if [ -z "$KAFKA_BROKER" ]; then
  >&2 echo "KAFKA_BROKER is not set"
  exit 3
fi

if [ -z "$KAFKA_BROKER" ]; then
  >&2 echo "KAFKA_TOPIC is not set"
  exit 4
fi

KAFKA_PRODUCER_BIN="$(which kafka-console-producer.sh)"
KAFKA_PRODUCER_ARGS="--broker-list $KAFKA_BROKER --topic $KAFKA_TOPIC"

if [ ! -x "$KAFKA_PRODUCER_BIN" ]; then
  >&2 echo "ERROR: could not find kafka producer script or it is not executable"
  exit 2
fi

t=$(date +"%Y-%m-%dT%T")

cat "$infile" | sed "s/{MEASURED_AT}/$t/"  | tr '\n' ' ' | "$KAFKA_PRODUCER_BIN" $KAFKA_PRODUCER_ARGS
