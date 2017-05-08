import doctest
import unittest
import os.path

import listb.mrtools
import listb.normalizetex

suite = unittest.TestSuite()

flags = doctest.NORMALIZE_WHITESPACE
suite.addTest(doctest.DocTestSuite(listb.mrtools,
                                   optionflags=flags))
suite.addTest(doctest.DocTestSuite(listb.normalizetex,
                                   optionflags=flags))

runner = unittest.TextTestRunner(verbosity=2)
runner.run(suite)