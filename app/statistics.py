from app import app

from flask import g, request

import time

@app.before_request
def before_request():
    g.request_start_time = time.perf_counter()

@app.after_request
def after_request(response):
    g.status_code = response.status_code
    return response

@app.teardown_request
def teardown_request(exc):
    try:
        response_time = (time.perf_counter() - g.request_start_time) * 1000
    except AttributeError:
        pass
    else:
        app.logger.info(
                "%(method)s %(path)s %(code)d processed in %(time)d ms.",
                dict(
                    method=request.method,
                    path=request.path,
                    time=response_time,
                    code=g.status_code
                ),
        )
