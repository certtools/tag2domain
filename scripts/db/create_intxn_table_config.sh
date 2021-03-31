#!/bin/bash
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$SCRIPT_DIR"

function error_exit {
    >&2 echo "ERROR: $1"
    exit 1
}

if [ -z "$TAG2DOMAIN_TAG_TYPE" ]; then
    error_exit "TAG2DOMAIN_TAG_TYPE is not set"
fi

if [ -z "$TAG2DOMAIN_INTXN_TABLE_NAME" ]; then
    error_exit "TAG2DOMAIN_INTXN_TABLE_NAME is not set"
fi

if [[ $TAG2DOMAIN_TAG_TYPE == *"."* ]]; then
  error_exit "<TAG TYPE> can not contain a ."
fi

ESCAPED_TAG_TYPE="$(printf '%s\n' "$TAG2DOMAIN_TAG_TYPE" | sed -e 's/[\/&]/\\&/g')"
ESCAPED_INTXN_TABLE_NAME="$(printf '%s\n' "$TAG2DOMAIN_INTXN_TABLE_NAME" | sed -e 's/[\/&]/\\&/g')"

cat "intersection_table_config.template" \
    | sed "s/{TAG2DOMAIN_INTXN_TABLE_NAME}/$ESCAPED_INTXN_TABLE_NAME/g" \
    | sed "s/{TAG TYPE}/$ESCAPED_TAG_TYPE/g"