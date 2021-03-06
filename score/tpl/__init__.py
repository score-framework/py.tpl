# Copyright © 2015-2018 STRG.AT GmbH, Vienna, Austria
# Copyright © 2020 Necdet Can Ateşman, Vienna, Austria
#
# This file is part of the The SCORE Framework.
#
# The SCORE Framework and all its parts are free software: you can redistribute
# them and/or modify them under the terms of the GNU Lesser General Public
# License version 3 as published by the Free Software Foundation which is in
# the file named COPYING.LESSER.txt.
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
# the discretion of STRG.AT GmbH also the competent court, in whose district
# the Licensee has his registered seat, an establishment or assets.


"""
This module handles :term:`templates <template>`, i.e. files that need to be
pre-processed before they can be put to their actual use. The module
initialization yields a :class:`.Renderer` object, which is the central hub
for rendering templates.
"""

from ._init import init, ConfiguredTplModule, FileType
from ._exc import TemplateNotFound
from .renderer import Renderer
from .loader import Loader, FileSystemLoader, ChainLoader, PrefixedLoader

__all__ = (
    'init', 'ConfiguredTplModule', 'FileType', 'TemplateNotFound', 'Renderer',
    'Loader', 'FileSystemLoader', 'ChainLoader', 'PrefixedLoader')
