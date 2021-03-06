#!/usr/bin/env python
"""Convert the GEMS HTML index to YAML."""

import copy
import re

from argparse import ArgumentParser
from typing import List, Tuple

from bs4 import BeautifulSoup
from bs4.element import Tag

from grc_mod import Media, Mod, Oldrim, Requirement, Sse, Webpages

import yaml

from zenlog import log

REQ_MAP = {
    'DG': (1, 'Dawnguard'),
    'HF': (2, 'Hearthfire'),
    'DB': (3, 'Dragonborn'),
    'SKSE': (None, 'SKSE'),
}

REQ_VARIANTS = [
    '',
    'DB',
    'DG',
    'DG + DB',
    'DG + HF',
    'DG + HF + DB',
    'HF',
    'HF + DB',
    'SKSE',
    'SKSE + DB',
    'SKSE + DG',
    'SKSE + DG + DB',
    'SKSE + DG + HF',
    'SKSE + DG + HF + DB',
    'SKSE + HF',
    'SKSE + HF + DB',
]


class BadEntryException(Exception):
    """Thrown when a table entry is invalid."""


def strip_reqs(string: str) -> str:
    """Remove all requirement tags from a string."""
    for req in REQ_VARIANTS:
        string = string.replace(f'[{req}]', '')
    return string.strip()


def get_media_from_tag(tag: Tag) -> Media:
    """Create a Media object from one or more <a> tags."""
    media_tags: List[Tag] = tag.select('a')
    images = []
    videos = []
    for media_tag in media_tags:
        url: str = media_tag.get('href')
        if re.search(r'(?:png|jpe?g|gif|resizedimage)$', url):
            images.append(url)
        elif re.search(r'(?:youtube|youtu\.be|ajax%2Fmodvideo)', url):
            videos.append(url)
        else:
            log.warn(f'Unknown media type for url {url}')
    return Media(images, videos)


def get_name_from_tag(tag: Tag) -> str:
    """Get the name of the mod."""
    link: Tag = tag.find('a')
    if link is None:
        raise BadEntryException(f'No link in tag:\n{tag}')
    return link.get_text()


def get_webpages_from_tag(tag: Tag) -> Webpages:
    """Get the mod's linked homepage."""
    link: Tag = tag.find('a')
    if link is None:
        raise BadEntryException(f'No link in tag:\n{tag}')
    url: str = link.get('href')
    steam_link = None
    nexus_link = None
    bethesda_link = None
    other_links = []
    if 'steamcommunity.com' in url:
        steam_link = url
    elif 'nexusmods.com' in url:
        nexus_link = url
    elif 'bethesda.net' in url:
        bethesda_link = url
    else:
        other_links.append(url)
    return Webpages(steam_link, nexus_link, bethesda_link, other_links)


def get_description_from_tag(tag: Tag) -> str:
    """Get the mod's description."""
    tag = copy.copy(tag)  # deepcopy tag since we're gonna edit it
    spans: List[Tag] = tag.find_all('span')
    for span in spans:
        span.extract()  # remove the span and its content from tag
    description: str = strip_reqs(tag.get_text())
    return description


def get_notes_from_tag(tag: Tag) -> List[str]:
    """Get a list of notes from the mod's description."""
    spans: List[Tag] = tag.find_all('span')
    notes: List[str] = []
    for span in spans:
        span_text: str = span.get_text()
        if span_text in REQ_VARIANTS:
            continue
        note = span_text.replace('**', '').strip()
        notes.append(note)
    return notes


def get_requirements_from_tag(tag: Tag) -> List[Requirement]:
    """Get a list of requirements from the mod's description."""
    spans: List[Tag] = tag.find_all('span')
    requirements: List[Requirement] = []
    for span in spans:
        clss: str = span.get('class')
        if clss is not None:
            clss = clss[0]
        if clss in REQ_MAP:
            requirements.append(Requirement(*REQ_MAP[clss], False))
    return requirements


def get_deprecated_status_from_tag(tag: Tag) -> bool:
    """Determine if a mod has been deprecated based on its description."""
    is_deprecated = False
    tag_text: str = tag.get_text().replace('\n', ' ')
    if (re.search(r'[Uu]se .*? instead(?! of)(?! if)', tag_text) is not None or
            re.search(r'[Nn]o longer supported', tag_text) is not None):
        is_deprecated = True
    return is_deprecated


def table_to_list(table: Tag, section: str,
                  id_base: int) -> Tuple[List[Mod], int]:
    """Convert an HTML table into a list of Mods."""
    mods: List[Mod] = []
    modid = id_base
    row: Tag
    for row in table.find_all('tr'):
        try:
            tag_column_1: Tag = row.find('td', 'col1')
            tag_column_2: Tag = row.find('td', 'col2')
            tag_column_3: Tag = row.find('td', 'col3')
            if tag_column_1 and tag_column_2 and tag_column_3:
                webpages = get_webpages_from_tag(tag_column_2)
                requirements = get_requirements_from_tag(tag_column_3)

                mod = Mod(
                    modid,
                    get_name_from_tag(tag_column_2),
                    get_description_from_tag(tag_column_3),
                    get_notes_from_tag(tag_column_3),
                    section,
                    get_media_from_tag(tag_column_1),
                    Oldrim(True, webpages, requirements),
                    Sse(False, Webpages(None, None, None, []), []),
                    [],
                    get_deprecated_status_from_tag(tag_column_3),
                    False
                )

                mods.append(mod)

                modid += 1
        except BadEntryException as exc:
            log.error(str(exc))

    return (mods, modid)


def get_data_from_html(html: str) -> List[Mod]:
    """Convert the HTML tables in the index to a single list of Mods."""
    soup = BeautifulSoup(html, 'html.parser')

    sections = [x.get_text().strip() for x in soup.find_all('h5')]

    tables: List[Mod] = []
    section_number = 0
    id_base = 4
    table: Tag
    for table in soup.select('div.inner > table'):
        data = table_to_list(
            table,
            sections[section_number],
            id_base)
        tables += data[0]
        id_base = data[1]
        section_number += 1

    return tables


def convert(input_file: str, output_file: str) -> None:
    """Actually do the conversion from HTML to YAML."""
    log.info(f'Reading HTML from {input_file}')
    with open(input_file, 'r', encoding='utf8') as in_h:
        html = in_h.read()

    log.info('Extracting mod data')
    data = get_data_from_html(html)
    log.info(f'Loaded {len(data)} mods.')

    log.info('Building YAML database from mod data')
    yaml_str: str = yaml.dump(data)
    yaml_str = yaml_str.replace('- !!python/object:grc_mod.Wrapper\n ', '-')
    yaml_str = yaml_str.replace(' !!python/object:grc_mod.Wrapper', '')

    log.info('Injecting DLC info')
    with open('dlc.yml', 'r', encoding='utf8') as dlc_h:
        dlc_str = dlc_h.read()
    yaml_str = dlc_str + '\n' + yaml_str
    log.info(f'Built database. (size: {len(yaml_str.encode("utf8"))})')

    log.info(f'Saving database to {output_file}')
    with open(output_file, 'w', encoding='utf8') as out_h:
        out_h.write(yaml_str)
    log.info('Done.')


def main() -> None:
    """Handle program logic."""
    parser = ArgumentParser(description='Convert HTML to YAML')
    parser.add_argument('input', type=str)
    parser.add_argument('output', type=str)

    args = parser.parse_args()
    input_file: str = args.input
    output_file: str = args.output
    convert(input_file, output_file)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:  # pylint: disable=W0703
        log.critical(str(exc))
