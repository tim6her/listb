#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Small command line tools for manipulating bibliographies.
"""


from functools import reduce
import os.path
import requests
import yaml

import click
import bibtexparser

import listb.normalizetex as normalizetex
import listb.pybibtools as bibtools

READERS = bibtools.Bibliography.READERS.keys()
WRITERS = bibtools.Bibliography.WRITERS.keys()

def load(reader, fil):
    """ Common interface for loading with all readers
    
    Args:
        reader (str):   name of reader
        fil (str):      path to input file
    
    Returns:
        (Bibliography): :class:`Bibliography`-object
    """
    bib = bibtools.Bibliography()
    with open(fil, 'r') as handle:
        bib.load(handle, reader=reader)
    return bib

def get_formats(f, t, o, files):
    """ Chooses reader and writer based on user options
    
    Args:
        f (str):            name of reader
        t (str):            name of writer
        o (click.File):     filehandle pointing to output file
        files (List[str]):  paths to input files
    
    Returns:
        (str, str): Name of reader and name of writer
    """
    if not files:
        raise click.UsageError('At least one file must be specified.')

    if not f:
        exts_f = [os.path.splitext(fil)[-1].replace('.', '') for fil in files]
        ext_f = exts_f[0]
        if not all(map(lambda x: x == ext_f, exts_f)):
            raise click.UsageError('You did not explicitely specify a reader '
                                   'and implicite deduction failed since not '
                                   'all files share the same extension.')

        if not ext_f in READERS:
            raise click.UsageError('I implicitely deduced that you want to '
                                   'use the %s reader. Unfortunately, this '
                                   'reader is not supported. The available '
                                   'readers are:\n%s' % (ext_f,
                                                         ', '.join(READERS))
                                   )
        f = ext_f

    if not t:
        if not o:
            raise click.UsageError('Cannot implicitely deduce writer. '
                                   'specify writer "-t" or output file "-o".')

        fn_o = o.name
        ext_t = os.path.splitext(fn_o)[-1].replace('.', '')
        if not ext_t in WRITERS:
            raise click.UsageError('I implicitely deduced that you want to '
                                   'use the %s writer. Unfortunately, this '
                                   'writer is not supported. The available '
                                   'writers are:\n%s' % (ext_t,
                                                         ', '.join(WRITERS))
                                   )
        t = ext_t

    return f, t

@click.group()
def cli():
    """ Small command line tool for combining and converting
    bibliographic data
    """
    pass

@click.command('union',
               short_help='creates the union of multiple databases')
@click.option('-f',
              type=click.Choice(READERS),
              help='from file format')
@click.option('-t',
              type=click.Choice(WRITERS),
              help='to file format')
@click.option('-o',
              type=click.File('w'),
              help='path to file for output')
@click.argument('files', nargs=-1,
                type=click.Path(exists=True))
def union(f, t, o, files):
    """ Creates the union of multiple bibliograhpies
    
    If some IDs/cite keys are contained in both bibliographies data from the
    left bibliography overwrites data from the right one.
    """
    f, t = get_formats(f, t, o, files)

    with click.progressbar(files, label='Loading bibliographies') as ff:
        bibs = [load(f, fin) for fin in ff]
    
    with click.progressbar(bibs, label='Unioning bibliographies') as bb:
        bib = reduce(bibtools.Bibliography.union, bb)

    datastring = bib.dump(writer=t)
    if o:
        o.write(datastring)
    else:
        click.echo(datastring)

@click.command('merge',
               short_help='merge databases')
@click.option('-f',
              type=click.Choice(READERS),
              help='from file format')
@click.option('-t',
              type=click.Choice(WRITERS),
              help='to file format')
@click.option('-o',
              type=click.File('w'),
              help='path to file for output')
@click.option('--union/--left',
              default=True,
              help=('Do you want the union of entries or '
                    'just update the left-most bibliography?'))
@click.option('--keep-key/--del-key',
              default=False,
              help='Do you want to keep the merge key?')
@click.argument('files', nargs=-1,
                type=click.Path(exists=True))
def merge(f, t, o, union, keep_key, files):
    """ Merges multiple bibliographies
    """
    f, t = get_formats(f, t, o, files)

    with click.progressbar(files, label='Loading bibliographies') as ff:
        bibs = [load(f, fin) for fin in ff]
    
    f = lambda b1, b2 : b1.merge(b2, union=union, keep_key=keep_key)
    with click.progressbar(bibs, label='Merging bibliographies') as bb:
        bib = reduce(f, bb)

    datastring = bib.dump(writer=t)
    if o:
        o.write(datastring)
    else:
        click.echo(datastring)
    

@click.command('make-key',
               short_help='create merge key')
@click.option('-f',
              type=click.Choice(READERS),
              help='from file format')
@click.option('-t',
              type=click.Choice(WRITERS),
              help='to file format')
@click.option('-o',
              type=click.File('w'),
              help='path to file for output')
@click.option('-k',
              type=click.STRING,
              multiple=True,
              help='name of field for key creation')
@click.argument('fil', nargs=1, metavar='FILE',
                type=click.Path(exists=True))
def make_key(k, f, t, o, fil):
    """ Adds a merge key to your database
    """
    f, t = get_formats(f, t, o, [fil])

    bib = load(f, fil)

    if 'normauthor' in k:
        bib.add_fields(normauthor=normalizetex.norm_author)
    if 'normtitle' in k:
        bib.add_fields(normtitle=normalizetex.norm_title)

    bib.make_key(*k)

    if 'normauthor' in k:
        bib.del_fields('normauthor')
    if 'normtitle' in k:
        bib.del_fields('normtitle')

    datastring = bib.dump(writer=t)
    if o:
        o.write(datastring)
    else:
        click.echo(datastring)

cli.add_command(union)
cli.add_command(merge)
cli.add_command(make_key)

if __name__ == '__main__':
    cli()