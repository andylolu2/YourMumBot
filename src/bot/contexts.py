from contextvars import ContextVar


request_id = ContextVar('request_id')
request_id.set(-1)

mute_dict = {}
