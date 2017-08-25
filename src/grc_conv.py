#!/usr/bin/env python3
"""Convert the GEMS HTML index to YAML."""

import re

from argparse import ArgumentParser
from typing import List

from bs4 import BeautifulSoup
from bs4.element import Tag

from grc_mod import Media, Mod, Oldrim, Requirement, Sse, Webpages

import yaml

from zenlog import log

REQ_MAP = {
    'DG': (1, 'Dawnguard'),
    'HF': (2, 'Hearthfire'),
    'DB': (3, 'Draonborn'),
    'SKSE': (None, 'SKSE'),
}


class BadEntryException(Exception):
    """Thrown when a table entry is invalid."""


def get_media_from_tag(tag: Tag) -> Media:
    """Create a Media object from one or more <a> tags."""
    media_tags = tag.select('a')
    images = []
    videos = []
    for media_tag in media_tags:
        url = media_tag.get('href')
        if re.search(r'(?:png|jpe?g|gif|resizedimage)$', url):
            images.append(url)
        elif re.search(r'(?:youtube|youtu\.be|ajax%2Fmodvideo)', url):
            videos.append(url)
        else:
            log.warn(f'Unknown media type for url {url}')
    return Media(images, videos)


def get_name_from_tag(tag: Tag) -> str:
    """Get the name of the mod."""
    link = tag.find('a')
    if link is None:
        raise BadEntryException(f'No link in tag:\n{tag}')
    return link.get_text()


def get_webpages_from_tag(tag: Tag) -> Webpages:
    """Get the mod's linked homepage."""
    link = tag.find('a')
    if link is None:
        raise BadEntryException(f'No link in tag:\n{tag}')
    url = link.get('href')
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
    return ''  # TODO


def get_notes_from_tag(tag: Tag) -> List[str]:
    return []  # TODO


def get_requirements_from_tag(tag: Tag) -> List[Requirement]:
    """Get a list of requirements from the mod's description."""
    spans = tag.find_all('span')
    requirements = []
    for span in spans:
        class_ = span.get('class')
        if class_ is not None:
            class_ = class_[0]
        if class_ in REQ_MAP:
            requirements.append(Requirement(*REQ_MAP[class_]))
    return requirements


def table_to_list(table: Tag, section: str, id_base: int) -> List[Mod]:
    """Convert an HTML table into a list of Mods."""
    mods = []
    modid = id_base + 1
    for row in table.find_all('tr'):
        try:
            tag_column_1 = row.find('td', 'col1')
            tag_column_2 = row.find('td', 'col2')
            tag_column_3 = row.find('td', 'col3')
            if tag_column_1 is not None \
               and tag_column_2 is not None \
               and tag_column_3 is not None:
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
                    [], False, False
                )

                mods.append(mod)

                modid += 1
        except BadEntryException as exc:
            log.error(exc)

    return mods


def get_data_from_html(html: str) -> List[Mod]:
    """Convert the HTML tables in the index to a single list of Mods."""
    soup = BeautifulSoup(html, 'html.parser')

    sections = [x.getText().strip() for x in soup.find_all('h5')]
    id_bases = []
    for section in sections:
        id_bases.append(int(section[:3]) * 1000)

    tables = []
    section_number = 0
    for table in soup.select('#acc2 > div.inner.shown > div.inner > table'):
        tables += table_to_list(
            table,
            sections[section_number],
            id_bases[section_number])
        section_number += 1

    return tables


def convert(input_file: str, output_file: str) -> None:
    """Actually do the conversion from HTML to YAML."""
    with open(input_file, 'r') as in_h:
        html = in_h.read()

    data = get_data_from_html(html)

    yaml_str = yaml.dump(data)

    yaml_str = yaml_str.replace('- !!python/object:grc_mod.Wrapper\n ', '-')
    yaml_str = yaml_str.replace(' !!python/object:grc_mod.Wrapper', '')

    with open('dlc.yml', 'r') as dlc_h:
        dlc_str = dlc_h.read()

    with open(output_file, 'w') as out_h:
        out_h.write(dlc_str + '\n' + yaml_str)


def main() -> None:
    """Handle program logic."""
    parser = ArgumentParser(description='Convert HTML to YAML')
    parser.add_argument('input', type=str)
    parser.add_argument('output', type=str)

    args = parser.parse_args()
    convert(args.input, args.output)


if __name__ == '__main__':
    main()
