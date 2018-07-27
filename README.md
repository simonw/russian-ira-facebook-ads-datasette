# Converting irads JSON to Datasette

The House Intelligence Committee released 3,517 Facebook ads that were
reported to have been bought by the Russian Internet Research Agency as a set
of redacted PDF files.

Ed Summers wrote a parser that converts those PDFs into a JSON file:
https://github.com/edsu/irads

The script in this repository downloads that JSON file and converts it into a
SQLite database for use with Datasette. Use it like this:

    python pull_ads_json_and_convert_to_sqlite.py \
        https://raw.githubusercontent.com/edsu/irads/master/ads.json \
        ads.db

This will produce a SQLite database called `ads.db`. You can then explore it
locally with [Datasette](https://github.com/simonw/datasette) like so:

    pip3 install datasette
    datasette ads.db

I published it using Datasette Publish by running this command:

    datasette publish now ads.db \
        -n irads-with-targeting-as-json \
        --source="edsu/irads" \
        --source_url="https://github.com/edsu/irads" \
        --install=datasette-vega

The resulting Datasette instance can be browsed here:
https://irads-with-targeting-as-json.now.sh/
