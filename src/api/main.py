from prometheus_fastapi_instrumentator import Instrumentator

from api.app import create_app

app = create_app()

Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=["/metrics"],
).instrument(app).expose(app)
