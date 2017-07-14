import json


def load_plain_json(path):
    with open(path, 'r') as fp:
        return json.load(fp)


def load_json(luigi_target):
    with luigi_target.open('r') as fp:
        return json.load(fp)


def load_jsonl(luigi_target):
    objs = []
    with luigi_target.open('r') as fp:
        for line in fp:
            objs.append(json.loads(line))
    return objs


def dump_json(luigi_target, obj):
    with luigi_target.open('w') as fp:
        json.dump(obj, fp, indent=4, sort_keys=True)
