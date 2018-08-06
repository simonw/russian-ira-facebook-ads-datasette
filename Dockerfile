FROM python:3.6-slim-stretch
RUN apt update
RUN apt install -y python3-dev gcc wget
ADD russian-ads-metadata.yaml russian-ads-metadata.yaml
ADD build_metadata.py build_metadata.py
ADD fetch_and_build_russian_ads.py fetch_and_build_russian_ads.py
ADD static static
ADD plugins plugins
RUN pip install pyyaml
RUN python build_metadata.py
RUN pip install https://github.com/simonw/datasette/archive/filter-plugin-hook.zip
RUN pip install datasette-vega
RUN pip install datasette-json-html
RUN pip install sqlite-utils
RUN python fetch_and_build_russian_ads.py https://raw.githubusercontent.com/edsu/irads/master/site/index.json russian-ads.db
RUN datasette inspect russian-ads.db --inspect-file inspect-data.json

EXPOSE 8001

CMD datasette serve russian-ads.db --host 0.0.0.0 --cors --port 8001 \
  --inspect-file inspect-data.json -m russian-ads-metadata.json \
  --config default_page_size:50 --config sql_time_limit_ms:3000 \
  --config num_sql_threads:10 --config facet_time_limit_ms:3000 \
  --config allow_sql:off --config force_https_urls:1 \
  --plugins-dir=plugins --static static:static
