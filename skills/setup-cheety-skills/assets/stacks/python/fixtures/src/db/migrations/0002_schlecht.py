def up(schema):
    schema.rename_column("auftraege", "amount", "amount_cents")   # !! MIGRATION_RENAME
    schema.drop_column("auftraege", "old_status")                # !! MIGRATION_DROP
    schema.add_column("auftraege", "shipping_method")                 # !! MIGRATION_NOT_NULL
    schema.add_column("auftraege", "sent_at", typ="timestamp", nullable=True)   # !! MIGRATION_TIMEZONE
    schema.update("auftraege", shipping_method="standard")            # !! MIGRATION_BULK_UPDATE
# !! MIGRATION_DOWN
