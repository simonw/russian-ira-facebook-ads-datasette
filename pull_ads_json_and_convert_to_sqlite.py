import urllib
import json
import os
import sqlite3


def init_db(filename):
    if os.path.exists(filename):
        return

    conn = sqlite3.connect(filename)
    conn.executescript(
        """
    CREATE TABLE ads (
        id VARCHAR(40) NOT NULL,
        file TEXT,
        text TEXT,
        url TEXT,
        impressions INTEGER,
        clicks INTEGER,
        spend_amount REAL,
        spend_currency TEXT,
        created TEXT,
        ended TEXT,
        targeting TEXT,
        PRIMARY KEY (id)
    );
    """
    )
    conn.close()


def best_fts_version():
    "Discovers the most advanced supported SQLite FTS version"
    conn = sqlite3.connect(":memory:")
    for fts in ("FTS5", "FTS4", "FTS3"):
        try:
            conn.execute(
                "CREATE VIRTUAL TABLE v USING {} (t TEXT);".format(
                    fts
                )
            )
            return fts

        except sqlite3.OperationalError:
            continue

    return None


def create_and_populate_fts(conn):
    create_sql = """
        CREATE VIRTUAL TABLE "ads_fts"
        USING {fts_version} (text, url, content="ads")
    """.format(
        fts_version=best_fts_version()
    )
    conn.executescript(create_sql)
    conn.executescript(
        """
        INSERT INTO "ads_fts" (rowid, text, url)
        SELECT ads.rowid, ads.text, ads.url
        FROM ads;
    """
    )


def insert_or_replace(conn, table, record):
    pairs = record.items()
    columns = [p[0] for p in pairs]
    params = [p[1] for p in pairs]
    sql = "INSERT OR REPLACE INTO {table} ({column_list}) VALUES ({value_list});".format(
        table=table,
        column_list=", ".join(columns),
        value_list=", ".join(["?" for p in params]),
    )
    conn.execute(sql, params)


def parse_and_load(url, db):
    data = json.load(urllib.urlopen(url))
    for ad in data:
        insert_or_replace(
            db,
            "ads",
            {
                "id": ad["id"],
                "file": ad["file"],
                "text": ad["text"],
                "url": ad["url"],
                "impressions": ad["impressions"],
                "clicks": ad["clicks"],
                "spend_amount": ad["spend"]["amount"],
                "spend_currency": ad["spend"]["currency"],
                "created": ad["created"],
                "ended": ad["ended"],
                "targeting": json.dumps(ad["targeting"]),
            },
        )


if __name__ == "__main__":
    import sys

    dbfile = sys.argv[-1]
    assert dbfile.endswith(".db")
    init_db(dbfile)
    db = sqlite3.connect(dbfile)
    for arg in sys.argv:
        if arg.startswith("https://"):
            parse_and_load(arg, db)
            print(arg)
    create_and_populate_fts(db)
    db.close()
