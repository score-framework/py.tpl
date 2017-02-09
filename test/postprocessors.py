from score.tpl import init
import os


def test_working():
    tpl = init({
        'rootdirs': os.path.join(os.path.dirname(__file__), 'templates')
    })
    tpl.filetypes['text/plain'].extensions.append('tpl')
    tpl.filetypes['text/plain'].postprocessors.append(lambda a: a + 'foo')
    tpl._finalize()
    assert tpl.render('a.tpl') == 'a\nfoo'


def test_replacement():
    tpl = init({
        'rootdirs': os.path.join(os.path.dirname(__file__), 'templates')
    })
    tpl.filetypes['text/plain'].extensions.append('tpl')
    tpl.filetypes['text/plain'].postprocessors.append(lambda *_: 'foo')
    tpl._finalize()
    assert tpl.render('a.tpl') == 'foo'


def test_removing_postprocessor():
    tpl = init({
        'rootdirs': os.path.join(os.path.dirname(__file__), 'templates')
    })
    tpl.filetypes['text/plain'].extensions.append('tpl')
    tpl.filetypes['text/plain'].postprocessors.append(lambda *_: 'foo')
    tpl.filetypes['text/plain'].postprocessors.pop()
    tpl._finalize()
    assert tpl.render('a.tpl') == 'a\n'
