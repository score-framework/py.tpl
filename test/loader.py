from score.tpl import init, TemplateNotFound
from score.tpl.loader import FileSystemLoader
import os
import pytest
import unittest.mock


def test_filesystem_loader_existence():
    tpl = init({
        'rootdirs': os.path.join(os.path.dirname(__file__), 'templates')
    })
    found = False
    for loader in tpl.loaders['tpl']:
        if isinstance(loader, FileSystemLoader):
            assert loader.rootdirs == tpl.rootdirs
            found = True
            break
    assert found


def test_basic_loader():
    tpl = init({
        'rootdirs': os.path.join(os.path.dirname(__file__), 'templates')
    })
    loader = unittest.mock.Mock()
    loader.load.return_value = (False, 'foo')
    tpl.loaders['tpl'].insert(0, loader)
    assert loader in tpl.loaders['tpl']
    tpl.filetypes['text/plain'].extensions.append('tpl')
    tpl._finalize()
    loader.load.assert_not_called()
    assert tpl.render('a.tpl') == 'foo'
    loader.load.assert_called_once_with('a.tpl')


def test_filesystem_fallback():
    tpl = init({
        'rootdirs': os.path.join(os.path.dirname(__file__), 'templates')
    })
    loader = unittest.mock.Mock()
    loader.load.side_effect = TemplateNotFound
    tpl.loaders['tpl'].insert(0, loader)
    tpl.filetypes['text/plain'].extensions.append('tpl')
    tpl._finalize()
    loader.load.assert_not_called()
    assert tpl.render('a.tpl') == 'a\n'
    loader.load.assert_called_once_with('a.tpl')


def test_disabling_filesystem_loader():
    tpl = init({
        'rootdirs': os.path.join(os.path.dirname(__file__), 'templates')
    })
    loader = unittest.mock.Mock()
    loader.load.side_effect = TemplateNotFound
    tpl.loaders['tpl'] = [loader]
    tpl.filetypes['text/plain'].extensions.append('tpl')
    tpl._finalize()
    loader.load.assert_not_called()
    with pytest.raises(TemplateNotFound):
        tpl.render('a.tpl')
    loader.load.assert_called_once_with('a.tpl')
