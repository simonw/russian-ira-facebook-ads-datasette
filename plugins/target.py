from datasette import hookimpl
from datasette.filters import FilterArguments
import json


@hookimpl
def filters_from_request(request, datasette, database):
    db = datasette.get_database(database)
    async def inner():
        human_descriptions = []
        where_clauses = []
        params = {}
        # They can come in as JSON or as _target=foo&_target=bar
        _targets_json = request.args.get("_targets_json") or ""
        if _targets_json:
            try:
                targets = json.loads(_targets_json)
            except ValueError:
                pass
        else:
            try:
                targets = request.args.getlist("_target")
            except KeyError:
                return None

        i = 0
        for target in targets:
            result = await db.execute("select name from targets where id = :id", {
                "id": target
            })
            target_name = result.first()["name"]
            param = "target_{}".format(i)
            i += 1
            where_clauses.append("""
                display_ads.id in (
                    select ad_targets.ad_id from ad_targets
                    where ad_targets.target_id = :{}
                )
            """.format(param))
            human_descriptions.append(
                "an ad_target was {}".format(target_name)
            )
            params[param] = target

        return FilterArguments(
            where_clauses=where_clauses,
            params=params,
            human_descriptions=human_descriptions,
        )
    return inner
