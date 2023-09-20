"""Test our parser"""
import os

from ..parser import parser


def get_filepath(name):
    """Helper function to get the text file contents"""
    basedir = os.path.dirname(__file__)
    return "%s/../../../examples/%s" % (basedir, name)


def test_parser():
    """Can we parse it, yes we can"""
    with open(get_filepath("data.bin"), "rb") as fh:
        leftover, res = parser(fh)
    assert len(res) == 3
    assert not leftover
