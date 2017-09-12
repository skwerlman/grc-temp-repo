#!/usr/bin/env python
"""Create a minified, stripped-down database copy."""

from argparse import ArgumentParser

from typing import Any, Dict, List

from grc_mod import Mod

import yaml

from zenlog import log

WANTED_KEYS = [
    'deprecated',
    'gems_category',
    'modid',
    'name',
    'tags',
    # oldrim and sse are special-cased
    # 'oldrim',
    # 'sse',
]

OLDRIM_WANTED_KEYS = [
    'is_oldrim',
]

SSE_WANTED_KEYS = [
    'console_compat',
    'is_sse',
]


def main() -> None:
    """Load, strip, minify, and save the database."""
    parser = ArgumentParser(description='Minify and strip the YAML database')
    parser.add_argument('input', type=str)
    parser.add_argument('output', type=str)

    args = parser.parse_args()
    input_file: str = args.input
    output_file: str = args.output

    log.info('Opening database...')
    with open(input_file, 'r', encoding='utf8') as in_h:
        raw_yaml = in_h.read()
    log.info(f'Opened database (size: {len(raw_yaml.encode("utf8"))})')

    log.info('Reading database...')
    database: List[Dict[str, Any]] = yaml.safe_load(raw_yaml)

    log.info('Stripping database...')
    database_mini: List[Dict[str, Any]] = []
    for mod in database:
        omod: Dict[str, Any] = {}
        omod = {key: value for key, value in mod.items() if key in WANTED_KEYS}
        omod['oldrim'] = {key: value for key, value in mod['oldrim'].items()
                          if key in OLDRIM_WANTED_KEYS}
        omod['sse'] = {key: value for key, value in mod['sse'].items()
                       if key in SSE_WANTED_KEYS}
        database_mini.append(omod)

    log.info('Converting databse back to YAML...')
    yaml_str: str = yaml.dump(database_mini)
    log.info(f'New size: {len(yaml_str.encode("utf8"))}')

    log.info(f'Saving database to {output_file}')
    with open(output_file, 'w', encoding='utf8') as out_h:
        out_h.write(yaml_str)
    log.info('Done')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:  # pylint: disable=W0703
        log.critical(str(exc))
