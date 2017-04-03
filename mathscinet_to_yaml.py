#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import yaml

import bibtexparser as bibtex
from bs4 import BeautifulSoup
import requests
from os.path import join

import normalizeTeX as norm

def get_mrnumber(doc):
    mrnumber = doc.find(attrs={'class': 'mrnum'}).strong.string
    grp = get_mrnumber.PAT.match(mrnumber)
    return grp[1]
get_mrnumber.PAT = re.compile(r'MR(\d+)', re.IGNORECASE)
    

def get_article_link(doc):
    menu = doc.find('div', class_='headlineMenu')
    if menu:
        article = doc.find('a', string='Article')
        if article:
            return get_article_link.PAT.split(article['href'], maxsplit=1)[-1]
    return None
get_article_link.PAT = re.compile(r'=')

def msn_to_mrnumbers(infile, outfile=None):
    with open(infile, 'r') as mathscinet:
        msn = mathscinet.read()

    msn_soup = BeautifulSoup(msn, 'html.parser')

    docs = msn_soup.find_all('div', class_='headlineText')

    ddocs = []
    d = {}
    for doc in docs:
    
        d['mrnumber'] = get_mrnumber(doc)
        d['msnarticle'] = get_article_link(doc)
        d = {k: str(v) for k, v in d.items()}
        ddocs.append(d)
        d = {}
    
    if outfile:
        with open(outfile, 'w') as msn:
            yaml.dump(ddocs, msn,
                      default_flow_style=False,
                      allow_unicode=True)
    return ddocs

def get_bibtex_from_msn(mrnumbers, outfile=None):
    params = dict(
        bdl="",
        batch_title="Selected+Matches+for%3A+Author%3D%28Shelah%29",
        pg7="ALLF",
        yrop="eq",
        s8="All",
        pg4="AUCN",
        co7="AND",
        co5="AND",
        s6="",
        s5="",
        co4="AND",
        pg5="TI",
        co6="AND",
        pg6="PC",
        s4="Shelah",
        dr="all",
        arg3="",
        yearRangeFirst="",
        pg8="ET",
        s7="",
        review_format="html",
        yearRangeSecond="",
        fmt="bibtex",
        sort="newest",
        searchin="",
        agg_itemtype_Reviewed="Reviewed",
        agg_author_160185="160185"
    )
    params['b'] = mrnumbers
    req = requests.get('http://www.ams.org/mathscinet/search/publications.html',
                       params=params)
    dirty_bib = req.text
    soup = BeautifulSoup(dirty_bib, 'html.parser')
    pre_bib = soup.find('div', class_='doc')
    entries = pre_bib.find_all('pre')
    bib = '\n'.join([str(e.string) for e in entries])
    
    if outfile:
        with open(outfile, 'w') as msn_bib:
            msn_bib.write(bib)
    
    return bib

if __name__ == '__main__':
    ddocs = msn_to_mrnumbers('publications.html',
                     join('files', 'mrnumbers.yaml'))
    mrnumbers = [d['mrnumber'] for d in ddocs]
    
    bib = get_bibtex_from_msn(mrnumbers,
                              join('files', 'msn.bib'))
    
    bibliography = bibtex.loads(bib)
    bib_dict = bibliography.get_entry_dict()
    for doc in ddocs:
        bibentry = bib_dict['MR%s' % doc['mrnumber']]
        doc.update(bibentry)
        doc.update({'normtitle': norm.norm_title(doc),
                    'normauthor': norm.norm_authors(doc)})
    with open(join('files', 'msn.yaml'), 'w') as msn:
        yaml.dump(ddocs, msn,
                  default_flow_style=False,
                  allow_unicode=True)