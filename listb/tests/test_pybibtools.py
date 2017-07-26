import unittest

from listb.pybibtools import *

class TestPybibtools(unittest.TestCase):

    def test_load_yaml(self):
        import io

        s_yaml = """
- ENTRYTYPE: article
  ID: MR3523657
  author: Matet, Pierre and P\'ean, C\'edric and Shelah, Saharon
  title: Cofinality of normal ideals on {$[\lambda]^{<\kappa}$} {I}
  year: '2016'
        """

        bib = Bibliography()
        with io.StringIO(s_yaml) as handle:
            bib.load(handle, reader='yaml')
        
        asserted_data = [{'ENTRYTYPE': 'article',
                          'ID': 'MR3523657',
                          'author': "Matet, Pierre and P'ean, "
                                    "C'edric and Shelah, Saharon",
                          'title': 'Cofinality of normal ideals '
                                   'on {$[\\lambda]^{<\\kappa}$} {I}',
                          'year': '2016'}]
        self.assertEqual(bib.data, asserted_data)

    def test_load_bibtex(self):
        import io

        s_bibtex = """
@article{MR3523657,
 author = {Matet, Pierre and P\'ean, C\'edric and Shelah, Saharon},
 title  = {Cofinality of normal ideals on {$[\lambda]^{<\kappa}$} {I}},
 year   = {2016}
}
        """

        bib = Bibliography()
        with io.StringIO(s_bibtex) as handle:
            bib.load(handle, reader='bibtex')
    
        asserted_data = [{'ENTRYTYPE': 'article',
                          'ID': 'MR3523657',
                          'author': "Matet, Pierre and P'ean, "
                                    "C'edric and Shelah, Saharon",
                          'title': 'Cofinality of normal ideals '
                                   'on {$[\\lambda]^{<\\kappa}$} {I}',
                          'year': '2016'}]
        self.assertEqual(bib.data, asserted_data)

    def test_union(self):
        import copy

        data1 = [{'ENTRYTYPE': 'article', 'ID': 'test1'},
                 {'ENTRYTYPE': 'article', 'ID': 'test2'}]
        data2 = [{'ENTRYTYPE': 'book', 'ID': 'test2'},
                {'ENTRYTYPE': 'article', 'ID': 'test3'}]

        data1_c = copy.deepcopy(data1)
        data2_c = copy.deepcopy(data2)

        bib1 = Bibliography(data1_c)
        bib2 = Bibliography(data2_c)
        self.assertEqual(bib1.data, data1_c)
        self.assertEqual(bib2.data, data2_c)

        uni = bib1.union(bib2)
        self.assertEqual(uni.data,
                         [{'ENTRYTYPE': 'article', 'ID': 'test1'},
                          {'ENTRYTYPE': 'article', 'ID': 'test2'},
                          {'ENTRYTYPE': 'article', 'ID': 'test3'}]
                        )

        # `union` should not change the initial bibliographies
        self.assertEqual(bib1.data, data1_c)
        self.assertEqual(bib2.data, data2_c)

if __name__ == '__main__':
    unittest.main()