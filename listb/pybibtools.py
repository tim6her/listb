#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Functions for handling bibliograhic databases
"""

import yaml

import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase

def bibtex_dump(data):
    r""" Turns dict into BibTex string

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

def bibtex_load_list(handle):
    """ Loads bibtex data from handle

    Args:
        handle (handle): file handle of bibliography

    Returns:
        List[dict]: entry list of bibliography
    """
    return bibtexparser.load(handle).get_entry_list()

class Bibliography(object):
    """ Class for handling bibliographic data
    """

    READERS = {'bibtex': bibtex_load_list,
               'yaml': yaml.load
              }
    """ Supported readers
    """

    WRITERS = {'bibtex': bibtex_dump,
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
        These ID-s must be unique.

        Raises:
            RuntimeError:
                if fields are missing or the ID-s are not unique
            TypeError:
                if `data` is of incorrect type

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

        ids = [e['ID'] for e in data]
        if len(ids) > len(set(ids)):
            raise RuntimeError('Your bibliography contains duplicate '
                               'ID-s.')

        self._data = data

    @data.deleter
    def data(self):
        del self._data

    def load(self, handle, reader='yaml'):
        """ Loads bibliography from handle

        Args:
            handle (handle):        file handle of biblography
            reader (Optional[str]): name of reader

        Example:
            Assuming that the file 'bib.yaml' exists, one can
            load its data into a bibliography as follows.

            >>> bib = Bibliography() # doctest: +SKIP
            >>> with open('bib.yaml', 'r') as handle: # doctest: +SKIP
            ...     bib.load(handle, reader='yaml')
        """
        self.data = self.READERS[reader](handle)


    def union(self, other, keep_left=True):
        """ Updates `self.data` to the union of the
        data bases

        Args:
            other (Bibliography):
                bibliography to be joined
            keep_left (Optional[bool]):
                If both data bases contain the same ID,
                should the left data base overwrite the
                right or vice versa? Default: `True`

        Examples:
            Note how the entry type is overwritten in the second example.

            >>> data1 = [{'ENTRYTYPE': 'article', 'ID': 'test1'},
            ...          {'ENTRYTYPE': 'article', 'ID': 'test2'}]
            >>> data2 = [{'ENTRYTYPE': 'book', 'ID': 'test2'},
            ...         {'ENTRYTYPE': 'article', 'ID': 'test3'}]
            >>> data3 = [{'ENTRYTYPE': 'misc', 'ID': 'test2'}]
            >>> bib1 = Bibliography(data1)
            >>> bib2 = Bibliography(data2)
            >>> bib3 = Bibliography(data3)
            >>> bib1.union(bib2)
            >>> bib1.data
            [{'ENTRYTYPE': 'article', 'ID': 'test2'}, {'ENTRYTYPE': 'article', 'ID': 'test3'}, {'ENTRYTYPE': 'article', 'ID': 'test1'}]
            >>> bib1.union(bib3, keep_left=False)
            >>> bib1.data
            [{'ENTRYTYPE': 'misc', 'ID': 'test2'}, {'ENTRYTYPE': 'article', 'ID': 'test3'}, {'ENTRYTYPE': 'article', 'ID': 'test1'}]
        """
        if keep_left:
            data = other.data
            new_data = self.data
        else:
            data = self.data
            new_data = other.data

        old_data = {e['ID']: e for e in data}
        for entry in new_data:
            e_id = entry['ID']
            if entry['ID'] in old_data:
                old_data[e_id].update(entry)
            else:
                old_data[e_id] = entry

        self.data = list(old_data.values())

    @staticmethod
    def _test_entry(entry):
        if not isinstance(entry, dict):
            return False

        return 'ENTRYTYPE' in entry and 'ID' in entry

if __name__ == '__main__':
    data1 = [{'ENTRYTYPE': 'article', 'ID': 'test1'},
             {'ENTRYTYPE': 'article', 'ID': 'test2'}]
    data2 = [{'ENTRYTYPE': 'book', 'ID': 'test2'},
             {'ENTRYTYPE': 'article', 'ID': 'test3'}]
    data3 = [{'ENTRYTYPE': 'misc', 'ID': 'test2'}]
    bib1 = Bibliography(data1)
    bib2 = Bibliography(data2)
    bib3 = Bibliography(data3)

    bib1.union(bib2)
    print(bib1.data)
    bib1.union(bib3, keep_left=False)
    print(bib1.data)