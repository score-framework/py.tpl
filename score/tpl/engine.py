# Copyright © 2015,2016 STRG.AT GmbH, Vienna, Austria
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


class Engine(metaclass=ABCMeta):
    """
    Abstract base class for :term:`template engines <template engine>`. The
    sole duty of this class is to create :class:`EngineRenderers
    <.EngineRenderer>` for specific
    :term:`template formats <template format>`.
    """

    @abstractmethod
    def create_subrenderer(format, rootdir, cachedir):
        """
        Creates a new :class:`.EngineRenderer` object for given
        :term:`template format`. The :class:`Renderer <score.tpl.Renderer>`
        will call this only once for each file format.
        """
        return


class EngineRenderer(metaclass=ABCMeta):
    """
    Abstract base class for sub-renderers created by
    :meth:`Engine.create_subrenderer`. This class is only relevant when
    implementing a new :term:`template engine`.

    Instances of this class can make these assumptions:

    - All registered entities (i.e. functions, filters and globals) will only
      be registered once.
    - The :class:`Renderer <score.tpl.Renderer>` will further ensure there are
      no name collisions.
    - There will be only one instance per engine/format combination.
    """

    @abstractmethod
    def add_function(self, name, callback, escape_output=True):
        """
        Adds a function that shall be available globally.
        """
        return

    @abstractmethod
    def add_filter(self, name, callback, escape_output=True):
        """
        Adds a :term:`filter` that shall be available globally.
        """
        return

    @abstractmethod
    def add_global(self, name, value):
        """
        Adds a variable that shall be available globally.
        """
        return

    @abstractmethod
    def render_file(self, file, variables):
        """
        Renders given template *file* with the given *variables* dict.
        """
        return

    @abstractmethod
    def render_string(self, string, variables):
        """
        Renders given template *string* with the given *variables* dict.
        """
        return
