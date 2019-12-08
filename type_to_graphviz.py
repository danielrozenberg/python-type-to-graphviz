# python3
import inspect
import types

from typing import Sequence


def generate_hierarchy_groups(*modules: types.ModuleType) -> Sequence[str]:
    """Returns a Graphviz-compatible list of grouped edges from type hierarchy.

    Args:
        *modules: Python modules to generate type hierarchies from.
    Returns: list of edges in the format `"x"->"y"`. Edges may contain
        additional attributes. e.g., `"x"->"y" [group="z"]`
    """
    processed = set()
    edges = []

    for module in modules:
        for _, cls in inspect.getmembers(
                module, lambda cls: inspect.isclass(cls) and cls is not type):
            nodes = inspect.getclasstree(cls.mro(), unique=True)
            nodes.pop(0)  # remove the (object, ()) tuple.
            while nodes:
                node = nodes.pop(0)
                if type(node) is tuple:
                    child, parents = node
                    edges.extend(
                        '"%s"->"%s" [group="%s"]' %
                        (parent.__name__, child.__name__, module.__name__)
                        for parent in parents
                        if child.__name__ not in processed)
                    processed.add(child.__name__)
                elif type(node) is list:
                    nodes.extend(node)
                else:
                    raise NotImplementedError()

    return edges


def generate_graphviz(*modules: types.ModuleType) -> str:
    """Returns a Graphviz-compatible formatted graph.

    Args:
        *modules: Python modules to generate type hierarchies from.
    """
    return '''digraph G {
  rankdir=LR
  splines=ortho

  %s
}''' % '\n  '.join(generate_hierarchy_groups(*modules))


if __name__ == '__main__':
    import collections
    import datetime

    print(
        generate_graphviz(__builtins__, collections, collections.abc,
                          datetime))
