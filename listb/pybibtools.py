#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Functions for handling bibliograhic databases
"""

import yaml

import bibtexparser
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
    return writer.write(db)

class Bibliography(object):
    """ Class for handling bibliographic data
    """

    READERS = {'bib': lambda handle: bibtexparser.load(handle).get_entry_list(),
               'yaml': yaml.load
              }
    """ Supported readers
    """

    WRITERS = {'bib': bibtex_dump,
               'yaml': yaml.dump
              }
    """ Supported writers
    """

    def __init__(self, data=None):
        if not data:
            data = []

        self._data = None

        self.data = data

    @property
    def data(self):
        """ Property containing the bibliographic data

        `data` must be a list of entries, where each entry
        is a `dict` containing the keys "ENTRYTYPE" and "ID".

        Example:
            >>> bib = Bibliography()
            >>> bib.data
            []
            >>> bib.data = 'Katze'
            Traceback (most recent call last):
              ...
            TypeError: Expected data as list of bibliographic entries got <class 'str'>
            >>> bib.data = [{'ENTRYTYPE': 'article', 'ID': 'test'}]
        """
        return self._data

    @data.setter
    def data(self, data):
        if not isinstance(data, list):
            raise TypeError('Expected data as list of bibliographic entries '
                            'got %s' % type(data))

        if not all(map(self._test_entry, data)):
            raise RuntimeError('There is something wrong with your data. '
                               'Either one of your entries is not a '
                               'dictionary or does not contain both '
                               'keys "ENTRYTYPE" and "ID".')
        self._data = data

    @data.deleter
    def data(self):
        del self._data

    def load(self, handle, reader='yaml'):
        """ Loads bibliography from handle

        Args:
            handle (handle):        file handle of biblography
            reader (Optional[str]): name of reader
        """
        self.data = self.READERS[reader](handle)

    @staticmethod
    def _test_entry(entry):
        if not isinstance(entry, dict):
            return False

        return 'ENTRYTYPE' in entry and 'ID' in entry
