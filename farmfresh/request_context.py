from contextvars import ContextVar


current_request_id: ContextVar[str] = ContextVar("current_request_id", default="-")




