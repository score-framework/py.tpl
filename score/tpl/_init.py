# Copyright © 2015 STRG.AT GmbH, Vienna, Austria
#
# This file is part of the The SCORE Framework.
#
# The SCORE Framework and all its parts are free software: you can redistribute
# them and/or modify them under the terms of the GNU Lesser General Public
# License version 3 as published by the Free Software Foundation which is in the
# file named COPYING.LESSER.txt.
#
# The SCORE Framework and all its parts are distributed without any WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. For more details see the GNU Lesser General Public
# License.
#
# If you have not received a copy of the GNU Lesser General Public License see
# http://www.gnu.org/licenses/.
#
# The License-Agreement realised between you as Licensee and STRG.AT GmbH as
# Licenser including the issue of its valid conclusion and its pre- and
# post-contractual effects is governed by the laws of Austria. Any disputes
# concerning this License-Agreement including the issue of its valid conclusion
# and its pre- and post-contractual effects are exclusively decided by the
# competent court, in whose district STRG.AT GmbH has its registered seat, at
# the discretion of STRG.AT GmbH also the competent court, in whose district the
# Licensee has his registered seat, an establishment or assets.

"""
This module handles :term:`templates <template>`, i.e. files that need to be
pre-processed before they can be put to their actual use. The module
initialization yields a :class:`.Renderer` object, which is the central hub
for rendering templates.
"""


import logging
import os
from .renderer import Renderer
from score.init import (
    extract_conf, init_cache_folder,
    init_object, ConfiguredModule, ConfigurationError
)


log = logging.getLogger('score.tpl')
defaults = {
    'rootdir': None,
    'cachedir': None,
    'default_format': None,
}


def init(confdict, webassets=None):
    """
    Initializes this module acoording to :ref:`our module initialization
    guidelines <module_initialization>` with the following configuration keys:

    :confkey:`rootdir` :faint:`[default=None]`
        Denotes the root folder containing all templates. When a new format is
        created via :meth:`.Renderer.register_format`, it will have a
        sub-folder of this folder as its default root (unless, of course, the
        `rootdir` parameter of that function is provided). If this value is
        omitted, all calls to :meth:`.Renderer.register_format` must provide a
        format-specific root folder.

    :confkey:`cachedir` :faint:`[default=None]`
        A cache folder that will be used to cache rendered templates. Will
        fall back to a sub-folder (called ``tpl``) of the cachedir in the
        *webassets*, if one was provided.

        Although this module will work without a cache folder, it is highly
        recommended that it is either initialized with a ``cachedir`` or a
        *webassets* with a valid ``cachedir``, even if the value points
        to the system's temporary folder.

    :confkey:`default_format` :faint:`[default=None]`
        The default format of files where the :term:`template format` could
        not be determined automatically. This must be the name of another,
        registered format.

    :confkey:`engine.*`
        All keys starting with ``engine.`` will be registered as engines. For
        example, if the key ``engine.php`` is provided, the engine will be
        instantiated via :func:`score.init.init_object` and registered for the
        extension ``php``.
    """
    conf = dict(defaults.items())
    conf.update(confdict)
    if not conf['cachedir'] and webassets and webassets.cachedir:
        conf['cachedir'] = os.path.join(webassets.cachedir, 'tpl')
    if conf['cachedir']:
        init_cache_folder(conf, 'cachedir', autopurge=True)
    if conf['rootdir']:
        if not os.path.isdir(conf['rootdir']):
            import score.tpl
            raise ConfigurationError(score.tpl, 'Given rootdir is not a folder')
    renderer = Renderer(conf['rootdir'], conf['cachedir'],
                        conf['default_format'])
    extensions = set()
    for key in extract_conf(conf, 'engine.'):
        extensions.add(key.split('.', 1)[0])
    for ext in extensions:
        engine = init_object(conf, 'engine.' + ext)
        renderer.register_engine(ext, engine)
    return ConfiguredTplModule(renderer, conf['rootdir'],
                               conf['cachedir'], conf['default_format'])


class ConfiguredTplModule(ConfiguredModule):
    """
    This module's :class:`configuration class
    <score.init.ConfiguredModule>`.
    """

    def __init__(self, renderer, rootdir, cachedir, default_format):
        super().__init__(__package__)
        self.renderer = renderer
        self.rootdir = rootdir
        self.cachedir = cachedir
        self.default_format = default_format
