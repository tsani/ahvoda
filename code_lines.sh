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
    |
    xargs wc -l |
    sort -n
