
"""Module providing an entry point to application."""

import json
import logging.config
import os
import sys

from flask import Flask, request, Response, jsonify

# CodeNow's runtime imports this file as the top-level module `app`, with this
# directory (src/) as the path root. Local runs and tests instead import it as
# `src.app`, with the repo root on the path. Putting this directory on
# sys.path keeps any `core.*` imports added later resolving the same way in
# both cases - see flask.instructions.md.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

_config_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', 'codenow', 'config', 'log-config.json',
)
with open(_config_path, 'rt', encoding='utf-8') as f:
    config = json.load(f)

logging.config.dictConfig(config)


@app.route('/')
def root_route():
    """Function for serving route /."""
    headers = {
        'X-B3-TraceId': request.headers.get('X-B3-TraceId'),
        'X-B3-SpanId': request.headers.get('X-B3-SpanId'),
        'X-B3-ParentSpanId': request.headers.get('X-B3-ParentSpanId'),
        'X-B3-Sampled': request.headers.get('X-B3-Sampled'),
        'X-B3-Flags': request.headers.get('X-B3-Flags')
    }
    app.logger.info('INFO log message')
    result = "Hello World!"
    resp = Response(result)
    resp.headers['X-B3-TraceId'] = headers.get('X-B3-TraceId')
    resp.headers['X-B3-SpanId'] = headers.get('X-B3-SpanId')
    return resp


@app.route('/health')
def health_check():
    """Function for serving route /health."""
    return jsonify(status='UP'), 200


if __name__ == '__main__':
    app.run(port=8080)
