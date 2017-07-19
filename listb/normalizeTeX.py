#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Python functions for dealing with with dirty LaTeX ;)
"""


import re

import bibtexparser.customization as bc
from bibtexparser.latexenc import latex_to_unicode
import unicodedata

def latex_to_ascii(tex):
    """ Transforms LaTeX strings to ascii text ignoring accents

    Args:
        tex (str): LaTeX string

    Returns:
        str: unicode string containing only ascii characters

    Examples:
        >>> latex_to_ascii(r"\^ile")
        'ile'
        >>> latex_to_ascii(r"\^ile") == latex_to_ascii('île')
        True
    """
    uni = latex_to_unicode(tex)
    asc = unicodedata.normalize('NFD', uni)
    asc = asc.encode('ascii', 'ignore').decode('utf-8')
    return asc

def norm_authors(record):
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
        >>> [norm_authors(rec) for rec in records]
        ['Fischbacher Horn', 'Fischbacher Horn', 'Fischbacher Horn']
        >>> norm_authors({'author': 'François Augiéras'})
        'Augieras'
    """
    authors = record['author'].split(' and ')
    authors = bc.getnames(authors) # Correct "Name, Surname"-format
    authors = [a.split(',')[0] for a in authors]
    authors = list(map(latex_to_ascii, authors))
    authors.sort()
    return ' '.join(authors)

def norm_title(record):
    """ Transforms the title field into a normalized string for matching

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
    """ Forms a key from the specified fields of a record

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
        >>> record['normauthor'] = norm_authors(record)
        >>> make_key(record, 'normauthor', 'year')
        'Fischbacher Horn-2006'
    """
    return '-'.join([record[key] for key in keys])

if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)
