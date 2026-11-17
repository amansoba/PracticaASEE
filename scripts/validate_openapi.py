"""Validate canonical contracts and their checked-in mirrors."""
from pathlib import Path

import yaml
from openapi_spec_validator import validate

ROOT = Path(__file__).resolve().parents[1]
METHODS = {"get", "post", "put", "patch", "delete", "options", "head", "trace"}


class UniqueLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ValueError(f"Duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def load(path):
    return yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueLoader)


def main():
    for path in sorted(ROOT.glob("*-service/openapi.yaml")):
        spec = load(path)
        validate(spec)
        mirror = load(path.parent / "generated/openapi.yaml")
        validate(mirror)
        assert spec == mirror, f"Contract mirror out of date: {path.parent.name}"
        ids = [op["operationId"] for item in spec["paths"].values()
               for method, op in item.items() if method in METHODS]
        assert len(ids) == len(set(ids)), f"Duplicate operationId: {path}"
        print(f"{path.parent.name}: {len(ids)} operations validated")


if __name__ == "__main__":
    main()
