from sqlalchemy import create_engine   # !! BOUNDARY_DOMAIN_PURE


def rechne(werte: list[int] = []) -> float:   # !! STATE_MUTABLE_DEFAULT
    amount: float = 0.0                        # !! STATE_MONEY_FLOAT
    print("debug", werte)                      # !! DEBUG_OUTPUT
    try:
        amount = sum(werte)
    except:                                    # !! ERROR_BARE_EXCEPT
        pass
    return amount
