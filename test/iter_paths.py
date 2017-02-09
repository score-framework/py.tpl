from score.tpl import init
import os


def test_unconfigured():
    tpl = init({
        'rootdirs': os.path.join(os.path.dirname(__file__), 'templates')
    })
    tpl._finalize()
    assert list(tpl.iter_paths()) == []


def test_tpl_files():
    tpl = init({
        'rootdirs': os.path.join(os.path.dirname(__file__), 'templates')
    })
    tpl.filetypes['text/plain'].extensions.append('tpl')
    tpl._finalize()
    assert set(tpl.iter_paths()) == {'a.tpl', 'b.tpl', 'empty.tpl'}
