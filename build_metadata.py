import json
import yaml

open("russian-ads-metadata.json", "w").write(
    json.dumps(yaml.load(open("russian-ads-metadata.yaml")), indent=4)
)
