from datasette import hookimpl
from datasette.utils import TableFilter
import json


@hookimpl
def table_filter():
    async def inner(view, name, table, request):
        # Hacky thing for ?_target=
        extra_human_descriptions = []
        where_clauses = []
        params = {}
        # They can come in as JSON or as _target=foo&_target=bar
        _targets_json = request.raw_args.get("_targets_json" or "")
        if _targets_json:
            try:
                targets = json.loads(_targets_json)
            except ValueError:
                pass
        else:
            try:
                targets = request.args["_target"]
            except KeyError:
                return None
        i = 0
        for target in targets:
            target_name = (
                await view.ds.execute(name, "select name from targets where id = :id", {
                    "id": target
                })
            ).rows[0][0]
            param = "target_{}".format(i)
            i += 1
            where_clauses.append("""
                display_ads.id in (
                    select ad_targets.ad_id from ad_targets
                    where ad_targets.target_id = :{}
                )
            """.format(param))
            extra_human_descriptions.append(
                "an ad_target was {}".format(target_name)
            )
            params[param] = target

        return TableFilter(
            human_description_extras=extra_human_descriptions,
            where_clauses=where_clauses,
            params=params,
        )
    return inner
