#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase


def bibtex_dump(data):
    """ Turns dict into BibTex string
    
    Args:
        data (List[dict]): data to be transformed
    
    Returns:
        str: BibTex representation of dict data
    
    Example:
        >>> data = [{"ENTRYTYPE": "article",
        ...          "ID": "MR3395349",
        ...          "author":
        ...             ("Baldwin, John T. and "
        ...              "Larson, Paul B. and "
        ...              "Shelah, Saharon"),
        ...          "journal": "J. Symb. Log.",
        ...          "number": "3",
        ...          "pages": "763--784",
        ...          "title": r"Almost {G}alois {$\omega$}-stable classes",
        ...          "volume": "80",
        ...          "year": "2015",
        ...        }]
        >>> print(bibtex_dump(data))
        @article{MR3395349,
         author = {Baldwin, John T. and Larson, Paul B. and Shelah, Saharon},
         journal = {J. Symb. Log.},
         number = {3},
         pages = {763--784},
         title = {Almost {G}alois {$\omega$}-stable classes},
         volume = {80},
         year = {2015}
        }
    """
    db = BibDatabase()
    db.entries = data
    writer = BibTexWriter()
    indent = '  '
    return writer.write(db)
    

