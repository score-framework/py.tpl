from score.tpl import init, TemplateNotFound
import pytest
import os


def test_unconfigured():
    tpl = init({
        'rootdirs': os.path.join(os.path.dirname(__file__), 'templates')
    })
    tpl._finalize()
    with pytest.raises(TemplateNotFound):
        tpl.render('empty.tpl')


def test_empty_template():
    tpl = init({
        'rootdirs': os.path.join(os.path.dirname(__file__), 'templates')
    })
    tpl.filetypes['text/plain'].extensions.append('tpl')
    tpl._finalize()
    assert tpl.render('empty.tpl') == ''


def test_a_tpl():
    tpl = init({
        'rootdirs': os.path.join(os.path.dirname(__file__), 'templates')
    })
    tpl.filetypes['text/plain'].extensions.append('tpl')
    tpl._finalize()
    assert tpl.render('a.tpl') == 'a\n'


def test_b_tpl():
    tpl = init({
        'rootdirs': os.path.join(os.path.dirname(__file__), 'templates')
    })
    tpl.filetypes['text/plain'].extensions.append('tpl')
    tpl._finalize()
    assert tpl.render('b.tpl') == 'b\n'


def test_consecutive_renderings():
    tpl = init({
        'rootdirs': os.path.join(os.path.dirname(__file__), 'templates')
    })
    tpl.filetypes['text/plain'].extensions.append('tpl')
    tpl._finalize()
    assert tpl.render('a.tpl') == 'a\n'
    assert tpl.render('b.tpl') == 'b\n'
