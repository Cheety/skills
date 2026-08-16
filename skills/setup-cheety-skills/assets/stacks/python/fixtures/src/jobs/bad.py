def handle(event_id: str) -> None:
    # no safeguard against duplicate delivery   !! IDEMPOTENCY_HANDLER
    _ = event_id
