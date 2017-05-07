#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TODO:
* book or chapter
"""
from os.path import join
import re
import requests
import yaml

from bs4 import BeautifulSoup
import bibtexparser as bibtex

import listb.normalizeTeX as norm

def yaml_dump(data, path):
    with open(path, 'w') as fout:
        yaml_dumps(data, fout)

def yaml_dumps(data, handle):
    yaml.dump(data, handle,
                  default_flow_style=False,
                  allow_unicode=True)

def get_mrnumber(doc):
    """ Extracts MR-number from the "headlineText" of the search result
    
    Args:
        doc (bs4.element.Tag): headlineText
    
    Returns:
        str: MR-number
    """
    mrnumber = doc.find(class_='mrnum').strong.string
    grp = get_mrnumber.PAT.match(mrnumber)
    return grp[1]
get_mrnumber.PAT = re.compile(r'MR(\d+)', re.IGNORECASE)

def msn_to_mrnumbers(msn, outfile=None):
    """ Retrieves MR-numbers from the source code of a search page
    
    Args:
        msn (str OR file handle): source code of the search result
        outfile Optional[str]:
            if specified the MR-numbers get written to a yaml file located at
            the path
    
    Returns:
        List[str]: List of MR-numbers found on page
    """
    msn_soup = BeautifulSoup(msn, 'html.parser')

    docs = msn_soup.find_all('div', class_='headlineText')
    mrnumbers = [get_mrnumber(doc) for doc in docs]

    if outfile:
        yaml_dump(mrnumbers, outfile)
    return mrnumbers

def get_bibtex_from_msn(mrnumbers, outfile=None):
    """ Fetches BibTeX file from MathSciNet server using the MR-numbers
    
    Args:
        mrnumbers (List[str]):
            the BibTeX entries for these MR-numbers are retrieved
        outfile (Opitonal[str]): path to output file
    
    Returns:
        str: BibTeX file as string
    
    Example:
        >>> print(get_bibtex_from_msn(['0241312']))
        @article {MR0241312,
            AUTHOR = {Shelah, Saharon},
             TITLE = {Note on a min-max problem of {L}eo {M}oser},
           JOURNAL = {J. Combinatorial Theory},
            VOLUME = {6},
              YEAR = {1969},
             PAGES = {298--300},
           MRCLASS = {05.04},
          MRNUMBER = {0241312},
        MRREVIEWER = {G. F. Clements},
        }
        
        
    """
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

def crawl(url):
    """ Crawls specified URL on MathSciNet
    
    If the search result is split into 5 pages and the URL to page
    3 is passed then the source codes and URLs of pages 3, 4, and 5
    are returned.
    
    Args:
        url (str): URL pointing to a search page on MathSciNet
    
    Returns:
        (List[str], List[str]): List of page source codes and list of URLs
    """
    sites = []
    urls = [url]
    while True:
        req = requests.get(url)
        site = req.text
        sites.append(site)
        soup = BeautifulSoup(site, 'html.parser')
        a = soup.find('a', string='Next')
        if not a:
            break
        urls.append(a['href'])
        # Links on MathSciNet are relative
        url = 'http://www.ams.org/%s' % a['href']
    return sites, urls

if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)
    """
    
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
    """