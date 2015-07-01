#!/bin/bash

cat \
    <(find app \
        -path 'app/bower_components' -prune \
        -o -name '*.py' -print \
        -o -name '*.html' -print \
        -o -name '*.json' -print \
        -o -name '*.js' -print \
    ) \
    <(find less -name '*.less') |
    xargs wc -l |
    sort -n
