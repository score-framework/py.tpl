# Copyright © 2015-2017 STRG.AT GmbH, Vienna, Austria
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

from abc import ABCMeta, abstractmethod


class Renderer(metaclass=ABCMeta):

    def __init__(self, tpl_conf, filetype):
        self._tpl_conf = tpl_conf
        self.filetype = filetype

    @abstractmethod
    def render_file(self, file, variables, path=None):
        """
        Renders given template *file* with the given *variables* dict.
        """
        return

    @abstractmethod
    def render_string(self, string, variables, path=None):
        """
        Renders given template *string* with the given *variables* dict.
        """
        return
