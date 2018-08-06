import urllib.request
import json
import os
import sqlite3
import hashlib
from sqlite_utils import Database


def flatten_targeting(targeting, prefix=''):
    # Convert targeting nested dictionary into list of strings
    # e.g. people_who_match:interests:Martin Luther King
    if isinstance(targeting, list) and all(isinstance(s, str) for s in targeting):
        return ["{}:{}".format(prefix, item) for item in targeting]
    elif isinstance(targeting, str):
        return ["{}:{}".format(prefix, targeting)]
    elif isinstance(targeting, dict):
        items = []
        for key, value in targeting.items():
            new_prefix = "{}:{}".format(prefix, key) if prefix else key
            items.extend(flatten_targeting(value, new_prefix))
        return items


def fetch_ads(url):
    return json.load(urllib.request.urlopen(url))


def hash_id(s):
    return hashlib.md5(s.encode("utf8")).hexdigest()[:5]


def main(dbfile, url):
    raw_ads = fetch_ads(url)
    db = Database(sqlite3.connect(dbfile))
    ads = db["ads"]
    targets = db["targets"]
    ad_targets = db["ad_targets"]
    ads_to_upsert = []
    targets_to_upsert = []
    ad_targets_to_insert = []
    for ad in raw_ads:
        ad_id = ad["id"]
        record = {
            "id": ad_id,
            "pdf": ad["pdf"],
            "image": ad["image"],
            "clicks": ad["clicks"],
            "impressions": ad["impressions"],
            "text": ad["text"],
            "url": (ad["url"] or "").replace("httpszll", "https://").replace("https:l/", "https://"),
            "spend_amount": ad["spend"]["amount"],
            "spend_currency": ad["spend"]["currency"] or "USD",
            "created": ad["created"],
            "ended": ad["ended"],
        }
        ads_to_upsert.append(record)
        for target in flatten_targeting(ad["targeting"]):
            target_id = hash_id(target)
            targets_to_upsert.append({
                "id": target_id,
                "name": target,
                "category": target.split(":")[0],
                "prefix": target.rsplit(":", 1)[0],
            })
            ad_targets_to_insert.append({
                "target_id": target_id,
                "ad_id": ad_id,
            })
    ads.upsert_all(ads_to_upsert, pk="id")
    targets.upsert_all(targets_to_upsert, pk="id")
    ad_targets.insert_all(ad_targets_to_insert, foreign_keys=(
        ("ad_id", "INTEGER", "ads", "id"),
        ("target_id", "TEXT", "targets", "id"),
    ))
    ad_targets.create_index(["target_id"])
    ad_targets.create_index(["ad_id"])
    # Enable full-text search
    ads.enable_fts(["text"])
    db.create_view("top_targets", """
        select id, name,
            json_object(
                "href", "/russian-ads-ae17624/display_ads?_target=" || urllib_quote_plus(id),
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
        order by count(*) desc
    """)
    db.create_view("display_ads", """
        select ads.id,
            case when image is not null then
                json_object("img_src", "https://raw.githubusercontent.com/edsu/irads/03fb4b/site/" || image, "width", 200)
            else
                "no image"
            end as img,
            json_group_array(
                json_object(
                    "label", targets.name,
                    "href", "/russian-ads/display_ads?_target="
                        || urllib_quote_plus(targets.id)
                )
            ) as targeting,
            ads.impressions, ads.clicks, ads.url, ads.text,
            cast(case
                when ads.spend_currency == "RUB" then ads.spend_amount * 0.016
                else ads.spend_amount
            end as float) as spend_usd,
            ads.spend_amount, ads.spend_currency,
            ads.created, ads.ended
        from ads
            join ad_targets on ads.id = ad_targets.ad_id
            join targets on ad_targets.target_id = targets.id
        group by ads.id
        order by ads.id
    """)


if __name__ == "__main__":
    import sys
    url = sys.argv[-2]
    dbfile = sys.argv[-1]
    assert dbfile.endswith(".db")
    assert url.startswith("http")
    main(dbfile, url)
