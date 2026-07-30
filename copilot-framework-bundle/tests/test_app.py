
"""Smoke tests for the endpoints the CodeNow platform depends on.

These cover the contract in `.claude/rules/codenow.md`, so a change that
breaks deployment fails here first.
"""


def test_index_responds(client):
    """`/` answers, which means the app boots and routing is wired."""
    response = client.get('/')

    assert response.status_code == 200


def test_index_propagates_b3_tracing_headers(client):
    """CodeNow expects the B3 trace headers echoed back on responses."""
    response = client.get(
        '/', headers={'X-B3-TraceId': 'trace-1', 'X-B3-SpanId': 'span-1'}
    )

    assert response.headers['X-B3-TraceId'] == 'trace-1'
    assert response.headers['X-B3-SpanId'] == 'span-1'


def test_health_reports_up(client):
    """CI and traffic routing depend on this exact response."""
    response = client.get('/health')

    assert response.status_code == 200
    assert response.get_json() == {'status': 'UP'}
