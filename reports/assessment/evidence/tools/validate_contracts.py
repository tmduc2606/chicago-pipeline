import yaml
import json

yaml.safe_load(open("contracts/openapi.yaml"))
print("openapi.yaml: VALID")

d = json.load(open("contracts/dbt-manifest.json"))
print("dbt-manifest.json: VALID")
print(f"nodes: {len(d.get('nodes', {}))}, sources: {len(d.get('sources', {}))}")
