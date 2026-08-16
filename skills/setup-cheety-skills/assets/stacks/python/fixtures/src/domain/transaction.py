def arbeite(db, queue) -> None:
    with db.transaction():
        db.speichere()
        queue.enqueue("mail")   # !! TRANSACTION_SIDE_EFFECT
