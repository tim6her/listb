#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import yaml

import bibtexparser.customization as bc
from bibtexparser.latexenc import latex_to_unicode
import unicodedata

def latex_to_ascii(s):
    s = latex_to_unicode(s)
    s = unicodedata.normalize('NFD',
                    s).encode('ascii', 'ignore').decode('utf-8')
    return s

def norm_authors(record):
    authors = record['author'].split(' and ')
    authors = bc.getnames(authors) # Correct "Name, Surname"-format
    authors = [a.split(',')[0] for a in authors]
    authors = list(map(latex_to_ascii, authors))
    authors.sort()
    return ' '.join(authors)

def norm_title(record):
    title = record['title']
    title = norm_title.PAT.sub('', title)
    title = latex_to_ascii(title)
    title = title.lower()
    title = norm_title.WS.sub('', title)
    return title
norm_title.PAT = re.compile(r'\$[\w\W]*?\$')
norm_title.WS = re.compile(r'\s|\W|_')
