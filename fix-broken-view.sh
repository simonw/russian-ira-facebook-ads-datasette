#!/bin/bash
sqlite-utils create-view russian-ads.db top_targets '
select id, name,
    json_object(
        "href", "/russian-ads/display_ads?_target=" || urllib_quote_plus(id),
        "label", count(*) || " ads"
    ) as num_ads,
    json_object(
        "href", "/russian-ads/faceted-targets?targets=" || urllib_quote_plus(
            json_array(id)
        ),
        "label", "Faceted browse"
    ) as apply_this_facet,
    category, prefix
from targets
    join ad_targets on targets.id = ad_targets.target_id
group by ad_targets.target_id
order by count(*) desc;
' --replace
