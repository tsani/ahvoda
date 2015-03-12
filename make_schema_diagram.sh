#!/bin/bash

if test -n "$1" ; then
    FMT="$1"
else
    FMT="svg"
fi

grep -e 'CREATE TABLE' -e 'REFERENCES' docs/schema.sql | grep -v '^--' | python make_schema_diagram.py | dot "-T$FMT" > "docs/schema.$FMT"
