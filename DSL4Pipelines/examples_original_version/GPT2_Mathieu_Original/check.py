#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "pyyaml",
#   "jsonschema",
# ]
# ///
# PYTHON_ARGCOMPLETE_OK
import argparse
import json

import yaml
import jsonschema


def load_data(filename):
    with open(filename) as f:
        if filename.endswith('.yaml'):
            data = yaml.safe_load(f)
        elif filename.endswith('json'):
            data = json.load(f)
        else:
            assert False, 'Unknown file type'
    return data


def check(schema, llm):
    jsonschema.validate(llm, schema)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--schema', default='schema2.yaml')
    parser.add_argument('--llm', default='gpt2.yaml')
    args = parser.parse_args()

    schema = load_data(args.schema)
    llm = load_data(args.llm)

    check(schema, llm)

main()
