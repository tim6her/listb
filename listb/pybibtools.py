#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Functions for handling bibliograhic databases
"""
import copy
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
    MERGEKEY = 'KEY'
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
            >>> bib1.union(bib2).data
            [{'ENTRYTYPE': 'article', 'ID': 'test1'}, {'ENTRYTYPE': 'article',
            'ID': 'test2'}, {'ENTRYTYPE': 'article', 'ID': 'test3'}]
        """
        # TODO: docstring
        return self.merge(other, 'ID', union=True)
    def merge(self, other, *keys, **kargs):
        """ Overwrites the bibliography with the merge of both
        bibliographies
        Args:
            other (Bibliography):
                The bibliography to be merged
            keys (List[str]):
                Names of the fields to be used to create the merge
                key
            union (Optional[bool]):
                Do you want the new database to contain the union
                of the keys? Defaults to `True`
                For syntactical reasons this parameter is implemented
                as keyword arguments (`**kargs`).
        """
        # TODO: docstring
        union = kargs.get('union', True)
        self.make_key(*keys)
        other.make_key(*keys)
        self_by_key = {e[self.MERGEKEY]: e for e in self}
        other_by_key = {e[self.MERGEKEY]: e for e in other}
        joined = copy.deepcopy(self_by_key)
        if union:
            joined.update(other_by_key)
            # Creates the union of both keys
        for key, entry in joined.items():
            if key in other_by_key:
                entry.update(other_by_key[key])
            if key in self_by_key:
                entry.update(self_by_key[key])
        bib = Bibliography(list(joined.values()))
        bib.del_fields(self.MERGEKEY)
        return bib
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
    def del_fields(self, *fields):
        """ Deletes the specified fields from the database
        Args:
            fields (List[str]):
                names of fields to be deleted. If an entry does not
                contain a field with the specified name, nothing happens.
        Example:
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
            >>> bib.del_fields('title', 'year')
            >>> bib.data
            [{'author': 'Sageev, G. and Shelah, S.', 'ENTRYTYPE':
            'incollection', 'ID': 'MR645920'}, {'author': 'Shelah, Saharon',
            'ENTRYTYPE': 'article', 'ID': 'MR636904'}]
        """
        for e in self:
            for k in fields:
                if k in e.keys():
                    del e[k]
    def make_key(self, *keys):
        """ Creates a merge key formed out of the fields specified
        in `keys`
        Args:
            keys (List[str]): List of field names
        Raises:
            RuntimeError: if the merge keys are not unique
        Example:
            Note how the first example produces a `RuntimeError` since
            the years coincide. Using a combination of author and year
            fixes this.
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
            >>> bib.make_key('year')
            Traceback (most recent call last):
              ...
            RuntimeError: The following merge keys are duplicates: ['1981',
            '1981']
            >>> bib.make_key('author', 'year')
            >>> [e['KEY'] for e in bib]
            ['Sageev, G. and Shelah, S.-1981', 'Shelah, Saharon-1981']
        """
        func = lambda r: listb.normalizetex.make_key(r, *keys)
        self.add_fields(**{self.MERGEKEY: func})
        keys = [e[self.MERGEKEY] for e in self]
        duplicates = [k for k in keys if keys.count(k) > 1]
        if duplicates:
            raise RuntimeError('The following merge keys '
                               'are duplicates: %s' % duplicates)
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
    bib1 = Bibliography(data1)
    bib2 = Bibliography(data2)
    bib1.union(bib2).data
    """
    bib1 = Bibliography()
    bib2 = Bibliography()
    with open('files/test1.bib', 'r') as bibtex:
        bib1.load(bibtex, reader='bibtex')
    with open('files/test2.bib', 'r') as bibtex:
        bib2.load(bibtex, reader='bibtex')
    bib1.add_fields(normauthor=listb.normalizetex.norm_author,
                    normtitle=listb.normalizetex.norm_title)
    bib2.add_fields(normauthor=listb.normalizetex.norm_author,
                        normtitle=listb.normalizetex.norm_title)
    bib1.merge(bib2, 'normauthor', 'normtitle', 'year', union=False)
    bib1.del_fields('normauthor', 'normtitle')
    with open('files/merge.bib', 'w') as bibtex:
        bibtex.write(bibtex_dump(bib1.data))
    """