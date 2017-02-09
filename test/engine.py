from score.init import ConfigurationError
from score.tpl import init
import os
import unittest.mock
import pytest


def test_missing_engine_filetypes():
    tpl = init({
        'rootdirs': os.path.join(os.path.dirname(__file__), 'templates')
    })
    engine = unittest.mock.Mock()
    tpl.engines['tpl'] = engine
    with pytest.raises(ConfigurationError):
        tpl._finalize()


def test_factory_call():
    tpl = init({
        'rootdirs': os.path.join(os.path.dirname(__file__), 'templates')
    })
    engine = unittest.mock.Mock()
    tpl.engines['tpl'] = engine
    tpl.filetypes['text/plain'].extensions.append('tpl')
    tpl._finalize()
    tpl.render('a.tpl')
    engine.assert_called_once_with(tpl, tpl.filetypes['text/plain'])


def test_render_file_call():
    tpl = init({
        'rootdirs': os.path.join(os.path.dirname(__file__), 'templates')
    })
    renderer = unittest.mock.Mock()
    renderer.render_file.return_value = 'foo'
    tpl.engines['tpl'] = lambda *_: renderer
    tpl.filetypes['text/plain'].extensions.append('tpl')
    tpl._finalize()
    renderer.render_file.assert_not_called()
    assert tpl.render('a.tpl') == 'foo'
    renderer.render_file.assert_called_once_with(
        os.path.join(tpl.rootdirs[0], 'a.tpl'), {}, path='a.tpl')


def test_embedded_extension():
    tpl = init({
        'rootdirs': os.path.join(os.path.dirname(__file__), 'templates')
    })
    loader = unittest.mock.Mock()
    loader.load.return_value = (False, 'foo')
    renderer = unittest.mock.Mock()
    renderer.render_string.return_value = 'bar'
    tpl.loaders['xml'].append(loader)
    tpl.engines['tpl'] = lambda *_: renderer
    tpl.filetypes['text/plain'].extensions.append('tpl')
    tpl.filetypes['text/xml'].extensions.append('xml')
    tpl._finalize()
    renderer.render_string.assert_not_called()
    assert tpl.render('path/to/file.tpl.xml') == 'bar'
    renderer.render_string.assert_called_once_with('foo', {},
                                                   path='path/to/file.tpl.xml')
