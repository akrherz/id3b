"""Test our parser"""
import unittest
import os

from ..parser import parser


def get_filepath(name):
    ''' Helper function to get the text file contents '''
    basedir = os.path.dirname(__file__)
    return "%s/../../../examples/%s" % (basedir, name)


class ParserTest(unittest.TestCase):
    """Run tests"""

    def test_parser(self):
        """Can we parse it, yes we can"""
        data = open(get_filepath('data.bin'), 'rb')
        leftover, res = parser(data)
        self.assertEquals(len(res), 3)
        self.assertTrue(len(leftover) == 0)
