import unittest

import solid

from sccm.components import component


class MockChildSpecifyingComponent(component.Component):
    """A component subclass that has a specific role for a child"""

    def __init__(
        self,
        parent: component.Component = None,
        special_child: component.Component = None,
    ):
        if not special_child:
            special_child = component.Component()
        self.special_child = special_child

        super().__init__(parent=parent, children=[self.special_child])

    @property
    def _copy(self) -> component.Component:
        return self.__class__(special_child=self.special_child.copy(isolate=True))


class TestComponent(unittest.TestCase):
    def test_parent_child_initialization(self) -> None:
        parent = component.Component()
        child_a = component.Component()
        child_b = component.Component()

        test_component = component.Component(parent=parent, children=[child_a, child_b])

        self.assertIs(
            test_component.parent,
            parent,
            msg="Parenthood should be correctly assigned on initialization",
        )
        self.assertIn(
            child_a,
            test_component.children,
            msg="Children should be correctly assigned on initialization",
        )
        self.assertIn(
            child_b,
            test_component.children,
            msg="Children should be correctly assigned on initialization",
        )

    def test_reparent_raise(self) -> None:
        parent = component.Component()
        child = component.Component(parent=parent)

        with self.assertRaises(
            component.ReparentException,
            msg="Should error if we attempt to add a parent to a child that has one",
        ):
            child.parent = component.Component()

    def test_reparent_to_parent(self) -> None:
        """Redundantly assigning parenthood should not cause an issue"""
        parent = component.Component()
        child = component.Component(parent=parent)

        child.parent = parent

    def test_grandparent(self) -> None:
        grandparent = component.Component()
        parent = component.Component(parent=grandparent)
        test_component = component.Component(parent=parent)

        self.assertEqual(
            list(test_component.parents),
            [parent, grandparent],
            msg="The parents iterator should contain all parents in order",
        )

    def test_copy_family_no_isolation(self) -> None:
        grandparent = component.Component()
        parent = component.Component(parent=grandparent)
        test_component = component.Component(parent=parent)
        child = component.Component()
        test_component.add_child(child)

        copy_component = test_component.copy()

        self.assertIs(
            copy_component.parent,
            parent,
            msg="Parenthood should be correctly assigned on non-isolated copying",
        )
        self.assertEqual(
            list(copy_component.parents),
            [parent, grandparent],
            msg="All parent relationships should be preserved on non-isolated copying",
        )

        self.assertIsNot(
            child,
            copy_component.children[0],
            msg="Children should be copied, not reparented",
        )
        self.assertTrue(
            test_component.same_children(copy_component),
            msg="Copied components should have equal children",
        )

        self.assertEqual(
            test_component, copy_component, msg="Copied components must be equal"
        )

    def test_copy_children_no_isolation_with_transformaton(self) -> None:
        test_component = component.Component()
        child = component.Component()
        test_component.add_child(child)

        rotation = solid.rotate([11.0, 12.0, 13.0])
        test_component.transform(rotation)

        copy_component = test_component.copy()

        self.assertTrue(
            test_component.same_children(copy_component),
            msg="Copied components should have equal children",
        )
        self.assertEqual(
            test_component, copy_component, msg="Copied components must be equal"
        )

    def test_copy_family_in_isolation(self) -> None:
        grandparent = component.Component()
        parent = component.Component(parent=grandparent)
        test_component = component.Component(parent=parent)
        child = component.Component()
        test_component.add_child(child)

        copy_component = test_component.copy(isolate=True)

        self.assertEqual(
            list(copy_component.parents),
            [],
            msg="An isolated copy should have no parents",
        )
        self.assertTrue(
            test_component.same_children(copy_component),
            msg="Copied components should have equal children",
        )
        self.assertEqual(
            test_component,
            copy_component,
            msg="Isolated copied components should be equal unless the original's parents have been transformed",
        )

    def test_copy_children_in_isolation_with_transformaton(self) -> None:
        test_component = component.Component()
        child = component.Component()
        test_component.add_child(child)

        rotation = solid.rotate([11.0, 12.0, 13.0])
        test_component.transform(rotation)

        copy_component = test_component.copy(isolate=True)

        self.assertTrue(
            test_component.same_children(copy_component),
            msg="Copied components should have equal children",
        )
        self.assertEqual(
            test_component, copy_component, msg="Copied components must be equal"
        )

    def test_copy_family_in_isolation_with_transformaton(self) -> None:
        parent = component.Component()
        test_component = component.Component(parent=parent)
        child = component.Component()
        test_component.add_child(child)

        rotation = solid.rotate([11.0, 12.0, 13.0])
        parent.transform(rotation)

        copy_component = test_component.copy(isolate=True)

        self.assertNotEqual(
            test_component,
            copy_component,
            msg="Because the original component is transformed through a parent, the isolated copy is not equal",
        )
        self.assertFalse(
            test_component.same_children(copy_component),
            msg="Children of isolated copies do not retain parent transformations and so are unequal",
        )

    def test_copy_with_specific_child(self) -> None:
        test_component = MockChildSpecifyingComponent()
        copy_component = test_component.copy()

        self.assertTrue(
            test_component.same_children(copy_component),
            msg="The copy's self-specified children should be copied over",
        )
