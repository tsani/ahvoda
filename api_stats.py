#!/usr/bin/env python

from app.api_spec import _artistic_endpoints
from app.api import endpoints

if __name__ == '__main__':
    print(_artistic_endpoints(endpoints))
