#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml

from bs4 import BeautifulSoup
from os.path import join

def get_title(doc):
    title = doc.find(attrs={'class': 'title'})
    if title.find('span'):
        title.script.extract()
        tex = title.span.string
        title.span.replace_with(tex)
        return get_title(doc)
    return ''.join(title.contents).strip('.')

def get_article_link(headline):
    menu = headline.find(attrs={'class': 'headlineMenu'})
    if menu:
        article = headline.find('a', string='Article')
        if article:
            return article['href'].split('=')[1]
    return 'No linked document found'

with open('publdoc.html', 'r') as mathscinet:
    msn = mathscinet.read()

msn_soup = BeautifulSoup(msn, 'html.parser')

docs = msn_soup.find_all(attrs={'class': 'doc'})

ddocs = []
d = {}
for doc in docs:
    headline = doc.find(attrs={'class': 'headline'})
    
    d['mrnumber'] = headline.find('strong').string
    d['title'] = get_title(headline)
    d['journal'] = headline.find('em').string
    d['link'] = get_article_link(headline)
    d = {k: str(v) for k, v in d.items()}
    ddocs.append(d)
    d = {}

with open(join('files', 'msn.yaml'), 'w') as msn:
    yaml.dump(ddocs, msn,
              default_flow_style=False,
              allow_unicode=True)