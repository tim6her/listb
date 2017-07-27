#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Functions for handling bibliograhic databases

A workflow of special interest is merging to bibliographies. The example below
creates two :class:`Bibliography` objects from two databases, that are not
disjoint. The first database contains some data we want to keep, but the second
database contains some additional information.


Note how in the first call to :func:`merge` the new dataset contains 3 entries
and the "ID" field remains unchanged. In the second call to :func:`merge` the
resulting bibliography has only two entries, namly its initial ones. However,
the field "url" from the second database is present.

    >>> data1 = [{'year': '1981',
    ...           'title': 'Weak compactness and the structure',
    ...           'author': 'Sageev, G. and Shelah, S.',
    ...           'ENTRYTYPE': 'incollection',
    ...           'ID': 'MR645920'
    ...          },
    ...          {'year': '1981',
    ...           'title': 'Iterated forcing and changing cofinalities',
    ...           'author': 'Shelah, Saharon',
    ...           'ENTRYTYPE': 'article',
    ...           'ID': 'MR636904'
    ...          }
    ...         ]
    >>> data2 = [{'year': '1981',
    ...           'title': 'Iterated forcing and changing cofinalities',
    ...           'author': 'Shelah, Saharon',
    ...           'url': 'http://dx.doi.org/10.1090/proc/13163',
    ...           'ENTRYTYPE': 'article',
    ...           'ID': 'shelah1981'
    ...          },
    ...          {'year': '2016',
    ...           'title': 'Rigidity of continuous quotients',
    ...           'author': 'Shelah, Saharon',
    ...           'ENTRYTYPE': 'article',
    ...           'ID': 'shelah2016'
    ...          }
    ...         ]
    >>> bib1 = Bibliography(data1) # Creating bibliographies
    >>> bib2 = Bibliography(data2)
    >>> bib1.data
    [{'year': '1981', 'title': 'Weak compactness and the structure',
    'author': 'Sageev, G. and Shelah, S.', 'ENTRYTYPE': 'incollection',
    'ID': 'MR645920'}, {'year': '1981',
    'title': 'Iterated forcing and changing cofinalities',
    'author': 'Shelah, Saharon', 'ENTRYTYPE': 'article', 'ID': 'MR636904'}]
    >>> # Creating normalized authors and titles for merging
    >>> bib1.add_fields(normauthor=listb.normalizetex.norm_author,
    ...                 normtitle=listb.normalizetex.norm_title)
    >>> bib2.add_fields(normauthor=listb.normalizetex.norm_author,
    ...                 normtitle=listb.normalizetex.norm_title)
    >>> bib1.data[0]['normtitle']
    'weakcompactnessandthestructure'
    >>> # Let's merge these bibliographies
    >>> m1 = bib1.merge(bib2, 'normauthor', 'year', 'normtitle')
    >>> m1.data
    [{'year': '1981', 'title': 'Weak compactness and the structure',
    'author': 'Sageev, G. and Shelah, S.', 'ENTRYTYPE': 'incollection',
    'ID': 'MR645920', 'normauthor': 'Sageev Shelah',
    'normtitle': 'weakcompactnessandthestructure'},
    {'year': '1981', 'title': 'Iterated forcing and changing cofinalities',
    'author': 'Shelah, Saharon', 'url': 'http://dx.doi.org/10.1090/proc/13163',
    'ENTRYTYPE': 'article', 'ID': 'MR636904', 'normauthor': 'Shelah',
    'normtitle': 'iteratedforcingandchangingcofinalities'},
    {'year': '2016',  'title': 'Rigidity of continuous quotients',
    'author': 'Shelah, Saharon', 'ENTRYTYPE': 'article', 'ID': 'shelah2016',
    'normauthor': 'Shelah', 'normtitle': 'rigidityofcontinuousquotients'}]
    >>> # Now we only want to update the first bibliography and
    >>> # ignore all other entries
    >>> m2 = bib1.merge(bib2, 'normauthor', 'year', 'normtitle', union=False)
    >>> m2.data
    [{'year': '1981', 'title': 'Weak compactness and the structure',
    'author': 'Sageev, G. and Shelah, S.', 'ENTRYTYPE': 'incollection',
    'ID': 'MR645920', 'normauthor': 'Sageev Shelah',
    'normtitle': 'weakcompactnessandthestructure'},
    {'year': '1981', 'title': 'Iterated forcing and changing cofinalities',
    'author': 'Shelah, Saharon', 'ENTRYTYPE': 'article', 'ID': 'MR636904',
    'normauthor': 'Shelah',
    'normtitle': 'iteratedforcingandchangingcofinalities',
    'url': 'http://dx.doi.org/10.1090/proc/13163'}]

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

    READERS = {'bib': bibtex_load_list,
               'yaml': yaml.load
              }
    """ Supported readers
    """

    WRITERS = {'bib': bibtex_dump,
               'yaml': yaml.dump
              }
    """ Supported writers
    """

    MERGEKEY = 'KEY'
    """ Name of the field used for merging in :func:`merge`
    and created in :func:`make_key`.
    """

    def __init__(self, data=None):
        if not data:
            data = []
        self._data = None
        self.data = data

    @property
    def data(self):
        """ Property containing the bibliographic data
        ``data`` must be a list of entries, where each entry
        is a ``dict`` containing the keys "ENTRYTYPE" and "ID".
        These ID-s must be unique.

        Raises:
            RuntimeError:
                if fields are missing or the ID-s are not unique
            TypeError:
                if ``data`` is of incorrect type

        Example:
            The first example raises an error since the argument supplied
            to ``data`` is not of correct type. The second example 
            succeeds.

            >>> bib = Bibliography()
            >>> bib.data
            []
            >>> bib.data = 'Katze'
            Traceback (most recent call last):
              ...
            TypeError: Expected data as list of bibliographic entries got
            <class 'str'>
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
            reader (Optional[str]): name of reader (see :const:`READERS`)

        Example:
            Assuming that the file 'bib.yaml' exists, one can
            load its data into a bibliography as follows.
            >>> bib = Bibliography() # doctest: +SKIP
            >>> with open('bib.yaml', 'r') as handle: # doctest: +SKIP
            ...     bib.load(handle, reader='yaml')
        """
        self.data = self.READERS[reader](handle)

    def dump(self, writer='yaml'):
        """ Serializes :attr:`data` using one of the predefinded writers
        in :const:`WRITERS`

        Args:
            writer (Optional[str]): name of one of the predefined writers

        Returns:
            str: representation of :attr:`data` as a string.

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
            >>> bib = Bibliography(data)
            >>> print(bib.dump(writer='bib'))
            @article{MR3395349,
             author = {Baldwin, John T. and Larson, Paul B. and Shelah,
                       Saharon},
             journal = {J. Symb. Log.},
             number = {3},
             pages = {763--784},
             title = {Almost {G}alois {$\omega$}-stable classes},
             volume = {80},
             year = {2015}
            }
        """
        return self.WRITERS[writer](self.data)

    def __iter__(self):
         return self.data.__iter__()

    def __next__(self):
        return self.data.__next__()

    next = __next__ # python 2 compatibility

    def union(self, other):
        """ Returns the union of two bibliographies.

        This is a special case of :func:`merge` were the merge key is just
        the field 'ID'

        Args:
            other (Bibliography):
                bibliography to be joined

        Returns:
            Bibliography:
                union of the bibliographies entries

        Note:
            ``union`` is *not* commutative. See example below.

        Example:
            >>> data1 = [{'ENTRYTYPE': 'article', 'ID': 'test1'},
            ...          {'ENTRYTYPE': 'article', 'ID': 'test2'}]
            >>> data2 = [{'ENTRYTYPE': 'book', 'ID': 'test2'},
            ...         {'ENTRYTYPE': 'article', 'ID': 'test3'}]
            >>> bib1 = Bibliography(data1)
            >>> bib2 = Bibliography(data2)
            >>> uni = bib1.union(bib2)
            >>> uni.data
            [{'ENTRYTYPE': 'article', 'ID': 'test1'}, {'ENTRYTYPE': 'article',
            'ID': 'test2'}, {'ENTRYTYPE': 'article', 'ID': 'test3'}]
            >>> uni.data == bib2.union(bib1).data
            False
        """
        return self.merge(other, 'ID', union=True)

    def merge(self, other, *keys, **kargs):
        """ Merges two bibliographies using a merge key

        The merge key is made up of the keys specified in the
        argument ``keys`` and a new field called 'KEY' is added to each
        entry of the bibliography. If the merge key is not unique a
        ``RuntimeError`` is raised (see :func:`make_key`).

        Args:
            other (Bibliography):
                The bibliography to be merged
            keys (List[str]):
                Names of the fields to be used to create the merge
                key
            union (Optional[bool]):
                Do you want the new database to contain the union
                of the keys? Otherwise only the entries of the left 
                bibliography will be updated and entries not contained
                in it will be ignored. Defaults to ``True``
                
                For syntactical reasons this parameter is implemented
                as keyword arguments (``**kargs``).

        Returns:
            Bibliography:
                Bibliography containing the merged dataset
        """
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
        For each entry of ``kargs`` a field corresponding to the key
        of the entry is added. The value of the entry must be a
        unary function accepting an entry of the bibliography as its
        argument.

        Args:
            kargs (Dict[str, function]):
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
        in ``keys``

        Args:
            keys (List[str]): List of field names

        Raises:
            RuntimeError: if the merge keys are not unique

        Example:
            Note how the first example produces a ``RuntimeError`` since
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
    print(bib1.data)
    bib2 = Bibliography(data2)
    print(bib1.union(bib2).data)
    print(bib1.data)
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