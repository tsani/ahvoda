#!/bin/bash

cat \
    <(find app \
        -path 'app/bower_components' -prune \
        -o -name '*.py' -print \
        -o -name '*.html' -print \
        -o -name '*.json' -print \
        -o -name '*.js' -print \
        -o -name '*.less' -print \
    ) \
    <(find tests \
        -name '*.py' \
    ) \
    <(echo "create_test_data.py") \
    <(echo "create_base_data.py") \
    |
    xargs wc -l |
    sort -n
