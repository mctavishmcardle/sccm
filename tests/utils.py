import itertools
import typing

import solid


def flatten_openscad_children(
    parent: solid.OpenSCADObject
) -> typing.List[solid.OpenSCADObject]:
    """Get a reversed, breadth-first recursive list of this object's children

    This object will be last, and its deepest-level children will be first

    Note:
        Preserves the order of an object's children

    Args:
        parent: The object whose children to retrieve
    """
    return list(
        itertools.chain(
            *(flatten_openscad_children(child) for child in parent.children), [parent]
        )
    )


def compare_openscad_objects(
    left: solid.OpenSCADObject, right: solid.OpenSCADObject
) -> bool:
    """Are two OpenSCAD objects equal?

    Note:
        Ignores children!

    Args:
        left: One of the OpenSCAD objects to compare
        right: The other OpenSCAD object to compare
    """
    return type(left) == type(right) and left.params == right.params


def compare_flattened_openscad_children(
    left: solid.OpenSCADObject, right: solid.OpenSCADObject
) -> bool:
    """Recursively naively compare an object & its children to another object

    Args:
        left: One of the OpenSCAD objects to compare
        right: The other OpenSCAD object to compare
    """
    return all(
        compare_openscad_objects(left_object, right_object)
        for left_object, right_object in itertools.zip_longest(
            flatten_openscad_children(left), flatten_openscad_children(right)
        )
    )
