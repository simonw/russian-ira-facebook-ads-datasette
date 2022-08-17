from datasette import hookimpl
from urllib.parse import quote_plus


@hookimpl
def prepare_connection(conn):
    conn.create_function("urllib_quote_plus", 1, quote_plus)
