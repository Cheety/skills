import os
from flask import request       # !! BOUNDARY_ACTION_HTTP
import psycopg                  # !! BOUNDARY_ACTION_DB


def execute() -> None:
    limit = os.environ.get("LIMIT")   # !! ENV_OUTSIDE_CONFIG
    try:
        _ = int(limit)
    except ValueError:
        pass                          # !! ERROR_SWALLOWED
    _ = request  # type: ignore       # !! HYGIENE_TYPE_IGNORE
