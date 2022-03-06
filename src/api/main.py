from prometheus_fastapi_instrumentator import Instrumentator, metrics

from api.app import create_app

app = create_app()

Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=["/metrics"],
).add(
    metrics.requests(should_include_method=False)
).add(
    metrics.latency(
        should_include_method=False,
        buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10)
    )
).instrument(app).expose(app)
