#!/usr/bin/env bash

MODULE_NAME=$1
CONFIG_FILE=$2

CMD="python -m brain.services.${MODULE_NAME}.run"

if [ -n "$CONFIG_FILE" ]
then
    CMD+=" --config=${CONFIG_FILE}"
fi

eval ${CMD}
