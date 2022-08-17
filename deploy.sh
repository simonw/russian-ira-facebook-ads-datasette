#!/bin/bash
datasette publish vercel russian-ads.db \
  --scope datasette \
  --project russian-ads \
  -m russian-ads-metadata.yaml \
  --plugins-dir plugins \
  --install datasette-publish-vercel \
  --install datasette-json-html \
  --install datasette-block-robots \
  --install datasette-hashed-urls
