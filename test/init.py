from score.init import ConfigurationError
from score.tpl import init
import pytest
import os


def test_initialization():
    init({})


def test_nonexistent_rootdir():
    with pytest.raises(ConfigurationError):
        init({
            'rootdir': os.path.join(os.path.dirname(__file__), 'I-Dont-Exist')
        })


def test_rootdir_conflict():
    with pytest.raises(ConfigurationError):
        init({
            'rootdir': 'foo',
            'rootdirs': 'bar',
        })


def test_rootdir():
    init({
        'rootdir': os.path.join(os.path.dirname(__file__), 'templates')
    })


def test_rootdirs():
    init({
        'rootdirs': os.path.join(os.path.dirname(__file__), 'templates')
    })
