#!/bin/bash

cat \
    <(find app -name '*.py' \
        -o -name '*.html' \
        -o -name '*.json' \
        -o -name '*.js') \
    <(find less -name '*.less') |
    xargs wc -l |
    sort -n
