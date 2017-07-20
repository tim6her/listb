#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Functions for handling bibliograhic databases
"""

import yaml

import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase

import listb.normalizetex

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

    def __iter__(self):
         return self.data.__iter__()

    def __next__(self):
        return self.data.__next__()

    next = __next__ # python 2 compatibility

    def union(self, other):
        """ Updates `self.data` to the union of the
        data bases

        Args:
            other (Bibliography):
                bibliography to be joined

        Example:
            >>> data1 = [{'ENTRYTYPE': 'article', 'ID': 'test1'},
            ...          {'ENTRYTYPE': 'article', 'ID': 'test2'}]
            >>> data2 = [{'ENTRYTYPE': 'book', 'ID': 'test2'},
            ...         {'ENTRYTYPE': 'article', 'ID': 'test3'}]
            >>> bib1 = Bibliography(data1)
            >>> bib2 = Bibliography(data2)
            >>> bib1.union(bib2)
            >>> bib1.data
            [{'ENTRYTYPE': 'article', 'ID': 'test2'}, {'ENTRYTYPE': 'article',
            'ID': 'test3'}, {'ENTRYTYPE': 'article', 'ID': 'test1'}]
        """

        old_data = {e['ID']: e for e in other}
        for entry in self:
            e_id = entry['ID']
            if entry['ID'] in old_data:
                old_data[e_id].update(entry)
            else:
                old_data[e_id] = entry

        self.data = list(old_data.values())

    def merge(self, other, *keys):
        self.make_key(*keys)
        other.make_key(*keys)

        self_by_key = {e['KEY']: e for e in self}
        other_by_key = {e['KEY']: e for e in other}

        for key, entry in other_by_key.items():
            new_entry = self_by_key.get(key, entry)
            entry.update(new_entry)

        self.data = list(other_by_key.values())


    def add_fields(self, **kargs):
        """ Adds fields to bibliography

        For each entry of `kargs` a field corresponding to the key
        of the entry is added. The value of the entry must be a
        unary function accepting an entry of the bibliography as its
        argument.

        Args:
            kargs (Dict[str: function]):
                Dictionary of field names and construction functions

        Example:
            In this example the author field is concatenated with itself
            and stored in the field 'doubleauthor'.

            >>> data = [{'year': '1981',
            ...          'title': 'Weak compactness and the structure', 
            ...          'author': 'Sageev, G. and Shelah, S.',
            ...          'ENTRYTYPE': 'incollection',
            ...          'ID': 'MR645920'
            ...         },
            ...         {'year': '1981',
            ...          'title': 'Iterated forcing and changing cofinalities',
            ...          'author': 'Shelah, Saharon',
            ...          'ENTRYTYPE': 'article',
            ...          'ID': 'MR636904'
            ...         }
            ...        ]
            >>> bib = Bibliography(data)
            >>> f = lambda entry: entry['author'] * 2
            >>> bib.add_fields(doubleauthor=f)
            >>> [e['doubleauthor'] for e in bib]
            ['Sageev, G. and Shelah, S.Sageev, G. and Shelah, S.',
            'Shelah, SaharonShelah, Saharon']
        """
        for key, func in kargs.items():
            for entry in self:
                entry.update({key: func(entry)})

    def make_key(self, *keys):
        """ Creates a merge key formed out of the fields specified
        in `keys`
        
        Args:
            keys (List[str]): List of field names
        """
        func = lambda r: listb.normalizetex.make_key(r, *keys)
        self.add_fields(KEY=func)

    @staticmethod
    def _test_entry(entry):
        if not isinstance(entry, dict):
            return False

        return 'ENTRYTYPE' in entry and 'ID' in entry

if __name__ == '__main__':
    bib1 = Bibliography()
    bib2 = Bibliography()

    with open('files/msn.bib', 'r') as bibtex:
        bib1.load(bibtex, reader='bibtex')

    with open('files/listb.bib', 'r') as bibtex:
        bib2.load(bibtex, reader='bibtex')

    bib1.add_fields(normauthor=listb.normalizetex.norm_author,
                    normtitle=listb.normalizetex.norm_title)
    bib2.add_fields(normauthor=listb.normalizetex.norm_author,
                        normtitle=listb.normalizetex.norm_title)
    
    bib2.merge(bib1, 'normauthor', 'normtitle', 'year')
    with open('files/merge.bib', 'w') as bibtex:
        bibtex.write(bibtex_dump(bib2.data))