#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Python functions for dealing with with dirty LaTeX ;)
"""


import re
import string
import unicodedata

import bibtexparser.customization as bc
from bibtexparser.latexenc import latex_to_unicode

def latex_to_ascii(tex):
    r""" Transforms LaTeX strings to ascii text ignoring accents

    Args:
        tex (str): LaTeX string

    Returns:
        str: unicode string containing only ascii characters

    Examples:
        >>> latex_to_ascii(r"\^ile")
        'ile'
        >>> latex_to_ascii(r"\^ile") == latex_to_ascii('île')
        True
        >>> latex_to_ascii(r"Bartoszy\'nski Ros\l anowski")
        'Bartoszynski Rosl anowski'
    """
    for pat, sub in latex_to_ascii.dict.items():
        tex = tex.replace(pat, sub)

    uni = latex_to_unicode(tex)
    asc = unicodedata.normalize('NFD', uni)
    asc = asc.encode('ascii', 'ignore').decode('utf-8')
    return asc
latex_to_ascii.dict = {"\\'": '',
                       "\\l": 'l',
                       "\\`": '',
                       "\\^": '',
                       "\\H": '',
                       "\\~": '',
                       "\\c": '',
                       "\\k": '',
                       "\\=": '',
                       "\\b": '',
                       "\\.": '',
                       "\\d": '',
                       "\\r": '',
                       "\\aa": 'å',
                       "\\u": '',
                       "\\v": '',
                       "\\t": '',
                       "\\o": 'ø',
                       "\\ss": 'ß'
                      }

def norm_author(record):
    """ Transforms the author field into an ordered list of last names

    Args:
        record (Dict[str]): record containing an author field

    Returns:
        str: normalized author names

    Examples:
        >>> records = [{'author': 'Siegfried Fischbacher and Uwe Ludwig Horn'},
        ...            {'author': 'Fischbacher, S. and Horn, U.'},
        ...            {'author': 'Fischbacher, Siegfried and Horn, Uwe '
        ...                       'Ludwig'}
        ...           ]
        >>> [norm_author(rec) for rec in records]
        ['Fischbacher Horn', 'Fischbacher Horn', 'Fischbacher Horn']
        >>> norm_author({'author': 'François Augiéras'})
        'Augieras'
        >>> norm_author({'author': 'Avraham (Abraham), Uri and '
        ...              'Ihoda (Haim Judah), Jaime'})
        'Avraham Ihoda'
    """
    authors = record['author'].split(' and ')
    authors = bc.getnames(authors) # Correct "Name, Surname"-format
    authors = [a.split(',')[0] for a in authors]
    authors = list(map(_norm_author, authors))
    authors.sort()
    return ' '.join(authors)


def _norm_author(author):
    author = latex_to_ascii(author)
    author = _norm_author.PAT.sub('', author)
    author = _norm_author.WS.sub('', author)
    return author
_norm_author.WS = re.compile(r'\s|\W|_')
_norm_author.PAT = re.compile(r'\s*\(.*?\)\s*')

def norm_title(record):
    r""" Transforms the title field into a normalized string for matching

    Args:
        record (Dict[str]): record containing a title field

    Returns:
        str: normalized title

    Example:
        >>> norm_title({'title': r'When automorphisms of '
        ...                      r'{$\Cal P(\kappa)/[\kappa]^{<\aleph_0}$} '
        ...                      r'are trivial off a small set'})
        'whenautomorphismsofaretrivialoffasmallset'

    Attributes:
        PAT (_sre.SRE_Pattern):
            precompiled pattern matching LaTeX formulae
        WS (_sre.SRE_Pattern):
            precompiled pattern matching any non-alphanumeric glyph
    """
    title = record['title']
    title = norm_title.PAT.sub('', title)
    title = latex_to_ascii(title)
    title = title.lower()
    title = norm_title.WS.sub('', title)
    return title
norm_title.PAT = re.compile(r'\$[\w\W]*?\$')
norm_title.WS = re.compile(r'\s|\W|_')

def make_key(record, *keys):
    r""" Forms a key from the specified fields of a record

    Args:
        record (Dict[str]): record containing specified fields
        keys (List[str]): keys of the fields used for key generation

    Returns:
        str: key as string

    Example:
        >>> record = dict(author='Siegfried Fischbacher and Uwe Ludwig Horn',
        ...               title=(r'When automorphisms of '
        ...                      r'{$\Cal P(\kappa)/[\kappa]^{<\aleph_0}$} '
        ...                      r'are trivial off a small set'),
        ...               year='2006')
        >>> record['normauthor'] = norm_author(record)
        >>> make_key(record, 'normauthor', 'year')
        'Fischbacher Horn-2006'
    """
    return '-'.join([record.get(key, '') for key in keys])

if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)
