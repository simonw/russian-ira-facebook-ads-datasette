from datasette import hookimpl
from datasette.utils import TableFilter
import re


def regexp(pattern, value):
    if value is None:
        return False
    return bool(re.search(pattern, value))


@hookimpl
def table_filter():
    async def inner(view, name, table, request):
        # Hacky thing for ?_target=
        try:
            regexp = request.args["_regexp"][0]
        except (KeyError, IndexError):
            return None
        # They can come in as JSON or as _target=foo&_target=bar
        return TableFilter(
            human_description_extras=[
                'regexp matches "{}"'.format(regexp),
            ],
            where_clauses=[
                "text regexp :regexp"
            ],
            params={
                "regexp": regexp
            },
        )
    return inner


@hookimpl
def prepare_connection(conn):
    conn.create_function("regexp", 2, regexp)
