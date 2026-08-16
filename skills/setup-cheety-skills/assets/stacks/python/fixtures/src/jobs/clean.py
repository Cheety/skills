PROCESSED: set[str] = set()


def handle(event_id: str) -> bool:
    if event_id in PROCESSED:
        return False
    PROCESSED.add(event_id)
    return True
