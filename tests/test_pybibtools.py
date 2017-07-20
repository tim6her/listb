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

if __name__ == '__main__':
    unittest.main()