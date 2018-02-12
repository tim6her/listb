#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os.path import join
import yaml

import bibtexparser as bibtex

from . import  normalizetex as norm

def listb(infile, outfile=None):
    with open(infile, 'r') as listb:
        bib = bibtex.load(listb)

    entries = bib.entries
    for doc in entries:
        doc.update({'normtitle': norm.norm_title(doc),
                    'normauthor': norm.norm_authors(doc)})

    if outfile:
        with open(outfile, 'w') as fout:
            yaml.dump(entries, fout,
                      default_flow_style=False,
                      allow_unicode=True)

    return entries

if __name__ == '__main__':
    ddoc = listb(join('files', 'listb.bib'),
                 join('files', 'listb.yaml'))
