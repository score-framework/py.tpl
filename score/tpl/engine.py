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
