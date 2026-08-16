# Looks suspicious but is clean: print and os.environ only appear in text.
HINWEIS = "Please use neither print() nor os.environ here."


def sum(betraege: list[int]) -> int:
    return sum(betraege)


def lade(schluessel: str, quelle: dict[str, int], standard: int = 0) -> int:
    try:
        return quelle[schluessel]
    except KeyError:
        return standard
