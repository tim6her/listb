#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Small command line tools for accessing bibliographic data from 'MathSciNet'.
"""

import requests
import yaml

import click

import listb.mrtools as mrtools

def chunk_list(l, n):
    """ Chops a list into tuples (chunks) of maximal size `n`
    
    Args:
        l (List[Any]): the list to be resized
        n (int): maximal size of the chunks
    
    Example:
        >>> chunk_list([1, 2, 3, 4, 5], 2)
        [(1, 2), (3, 4), (5,)]
    """
    assert n > 0
    
    nl = len(l)
    if n > nl:
        return [tuple(l)]
    
    l_ = list(zip(*[l[i::n] for i in range(n)]))
    
    if nl % n > 0:
        l_.append(tuple(l[-(nl % n):]))
    return l_

@click.group()
def cli():
    """ Small command line tool for crawling search pages on
    MathSciNet, requesting MR-numbers and obtaining BibTex-databases
    """
    pass

@click.command('crawl',
               short_help='Prints the URL and all suceeding URLs.')
@click.option('--url',
              prompt='Please enter URL',
              help='URL pointing to MathSciNet search result')
def crawl(url):
    """ Prints the URL and all suceeding URLs.
    
    If the search result is split into 5 pages and the URL to page
    3 is passed then the URLs of pages 3, 4, and 5 are printed.
    """
    _, urls = mrtools.crawl(url)
    click.echo('\n'.join(urls))

@click.command('mrnumbers',
               short_help='Prints the MR-numbers of the entries')
@click.option('--url',
              prompt='Please enter URL',
              help='URL pointing to MathSciNet search result')
@click.option('--crawl/--no-crawl',
              default=False,
              help='Crawl page and return all MR-numbers')
@click.option('--dump',
              type=click.File('w'),
              help='path to yaml file for output')
def mrnumbers(url, crawl, dump):
    if crawl:
        sites, _ = mrtools.crawl(url)
    else:
        req = requests.get(url)
        sites = [req.text]
    
    mmrn = [mrtools.msn_to_mrnumbers(s) for s in sites]
    mmrn = [n for sublist in mmrn for n in sublist] # flattens the list
    
    if dump:
        mrtools.yaml_dumps(mmrn, dump)
    else:
        click.echo('\n'.join(mmrn))

@click.command('bib',
                short_help='Retrieves BibTeX file for MR-numbers')
@click.option('--load',
               type=click.File('r'),
               help='path to yaml file storing the MR-numbers')
@click.option('--dump',
              type=click.File('w'),
              help='Path to BibTeX file for output')
@click.argument('mrnumbers',
                nargs=-1)
def bib(load, dump, mrnumbers):
    """ Fetches BibTeX entries for MR-numbers from MathSciNet.
    
    If both `--load` and `mrnumbers` are specified, only the numbers
    stored in the yaml file are used.
    """
    if load:
        mrnumbers = yaml.load(load)
    elif mrnumbers:
        pass
    else:
        raise click.UsageError('Please specify yaml file or mrnumbers.')
    
    chunks = chunk_list(mrnumbers, 20)
    with click.progressbar(chunks) as bar:
        bibs = [mrtools.get_bibtex_from_msn(c) for c in bar]
    
    if not all(bibs):
        err_bibs = filter(lambda x: x[1] == None, enumerate(bibs))
        err_chunks = [', '.join(chunks[i]) for i, _ in err_bibs]
        raise click.UsageError('There seems to be something wrong with '
                                 'at least one of the following MR-numbers.'
                                 '\n\n%s' % '\n'.join(err_chunks))
    
    if dump:
        dump.write('\n'.join(bibs))
    else:
        click.echo('\n'.join(bibs))

cli.add_command(crawl)
cli.add_command(mrnumbers)
cli.add_command(bib)

if __name__ == '__main__':
    cli()