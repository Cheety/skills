def up(schema):
    schema.add_column("auftraege", "dunned_at", typ="timestamptz", nullable=True)


def down(schema):
    schema.drop_column("auftraege", "dunned_at")
