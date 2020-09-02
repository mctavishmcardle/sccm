import unittest

import solid

from sccm.components import component
from tests import utils


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


class MockEmbodiedComponent(component.Component):
    """A component subclass that defines a body"""

    @property
    def _copy(self) -> "MockEmbodiedComponent":
        return self.__class__(self.size)

    def __init__(self, size: float = 1.0, color: component.Color = None):
        self.size = size

        super().__init__(color=color)

    @component.Component.transformed_property
    def _body(self) -> solid.OpenSCADObject:
        return solid.cube(self.size)

    def __eq__(self, other: object) -> bool:
        return (
            super().__eq__(other)
            and isinstance(other, MockEmbodiedComponent)
            and self.size == other.size
        )


class TestComponent(unittest.TestCase):
    def test_composition_initializations(self) -> None:
        composee = component.Component()
        composition = (solid.union(), composee)

        composer = component.Component(compositions=[composition])

        self.assertIn(
            composition,
            composer.compositions,
            msg="Compositions should be assigned correctly on initialization",
        )

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

    def test_add_children(self) -> None:
        parent = component.Component()

        child_a = component.Component()
        child_b = component.Component()
        children = [child_a, child_b]

        parent.add_child(children)

        self.assertEqual(
            parent.children, children, msg="Children should be added to a parent"
        )

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

    def test_composed_components(self) -> None:
        parent = component.Component()

        # Transform the operands, so they are nonequal
        operand_a = component.Component()
        operand_a.transform(solid.rotate([1.0, 1.0, 1.0]))
        operand_b = component.Component()
        operand_b.transform(solid.rotate([2.0, 2.0, 2.0]))

        operands = [operand_a, operand_b]

        parent.compose(solid.union(), operands)

        self.assertEqual(
            list(parent.composed_components),
            operands,
            msg="Composed components should contain components which have been composed",
        )

    def test_uncomposed_children(self) -> None:
        parent = component.Component()
        uncomposed_child = component.Component(parent=parent)
        # Transform the children, so they are nonequal
        uncomposed_child.transform(solid.rotate([1.0, 1.0, 1.0]))

        composed_child = component.Component()
        # Transform the children, so they are nonequal
        composed_child.transform(solid.rotate([2.0, 2.0, 2.0]))
        parent.compose(solid.union(), composed_child, make_children=True)

        self.assertEqual(
            list(parent.uncomposed_children),
            [uncomposed_child],
            msg="No composed component should be in the uncomposed children list",
        )

    def test_body_no_uncomposed_children(self) -> None:
        parent = component.Component()
        composed_child = component.Component()
        parent.compose(solid.union(), composed_child, make_children=True)

        self.assertIsNone(
            parent._body,
            msg="The default `_body` of a component with no uncomposed children should be `None`",
        )

    def test_body_with_uncomposed_children(self) -> None:
        parent = component.Component()
        uncomposed_child = MockEmbodiedComponent()
        uncomposed_child.parent = parent

        self.assertTrue(
            utils.compare_flattened_openscad_children(
                parent._body, solid.union()(solid.cube(1.0))
            ),
            msg="Parents with uncomposed children should have defined `_body`s",
        )

    def test_apply_composition_copies(self) -> None:
        composition = solid.union()

        copied_composition = utils.flatten_openscad_children(
            component.Component._apply_composition(composition, [solid.cube(1.0)])
        )[1]

        self.assertTrue(
            utils.compare_openscad_objects(copied_composition, composition),
            msg="A copied, applied composition must be equivalent to the original",
        )
        self.assertIsNot(
            copied_composition,
            composition,
            msg="A copied, applied composition must not be the same instance as the original",
        )

    def test_disembodied_component_raises(self) -> None:
        with self.assertRaises(
            component.DisembodiedComponent,
            msg="Getting the body of a bare component with no children should error",
        ):
            component.Component().body

    def test_body_pure_container(self) -> None:
        parent = component.Component()
        composer_1 = MockEmbodiedComponent(2.0)
        composer_2 = MockEmbodiedComponent(3.0)

        parent.compose(solid.union(), composer_1, make_children=False)
        parent.compose(solid.difference(), composer_2, make_children=False)

        self.assertTrue(
            utils.compare_flattened_openscad_children(
                parent.body,
                solid.difference()(
                    solid.union()(solid.cube(size=2.0)), solid.cube(size=3.0)
                ),
            ),
            msg="The innermost composition on pure containers must first be evaluted on its own",
        )

    def test_compose_not_in_place(self) -> None:
        composer_1 = MockEmbodiedComponent(2.0)
        composer_2 = MockEmbodiedComponent(3.0)

        composed = composer_1.compose(
            solid.union(), composer_2, inplace=False, make_children=True
        )

        self.assertIn(
            composer_1,
            composed.composed_components,
            msg="Not-in-place composition should compose both operands",
        )
        self.assertIn(
            composer_2,
            composed.composed_components,
            msg="Not-in-place composition should compose both operands",
        )

        self.assertIn(
            composer_1,
            composed.children,
            msg="Operands should be children of the result, if requested",
        )
        self.assertIn(
            composer_2,
            composed.children,
            msg="Operands should be children of the result, if requested",
        )

    def test_compose_copy(self) -> None:
        composer_1 = MockEmbodiedComponent(2.0)
        composer_2 = MockEmbodiedComponent(3.0)

        composed = composer_1.compose(
            solid.union(), composer_2, inplace=False, copy=True
        )

        self.assertTrue(
            utils.compare_flattened_openscad_children(
                composed.body, solid.union()(solid.cube(size=3.0), solid.cube(size=2.0))
            ),
            msg="Copied operands should be equal to the originals",
        )

        self.assertTrue(
            all(
                composer_1 is not child and composer_2 is not child
                for child in composed.children
            ),
            msg="Copied operands should be distinct objects",
        )

    def test_copy_composition_all_children_in_operands(self) -> None:
        composer_1 = MockEmbodiedComponent(2.0)
        composer_2 = MockEmbodiedComponent(3.0)

        composed = composer_1.compose(solid.union(), composer_2, inplace=False)

        copy = composed.copy()

        self.assertTrue(
            copy.same_children(composed),
            msg="Copies must share the children of the original",
        )
        self.assertTrue(
            copy.same_compositions(composed),
            msg="Copies must share the compositions of the original",
        )

        self.assertTrue(
            all(
                composer_1 is not child and composer_2 is not child
                for child in copy.children
            ),
            msg="Copied operands should be distinct objects",
        )

    def test_copy_composition_some_uncomposed_children(self) -> None:
        composer_1 = MockEmbodiedComponent(2.0)
        composer_2 = MockEmbodiedComponent(3.0)

        composed = composer_1.compose(
            solid.union(), composer_2, inplace=False, make_children=False
        )
        uncomposed_child = MockEmbodiedComponent(4.0)
        uncomposed_child.parent = composed

        composer_2.parent = composed

        copy = composed.copy()

        self.assertTrue(
            copy.same_children(composed),
            msg="Copies must share the children of the original",
        )
        self.assertTrue(
            copy.same_compositions(composed),
            msg="Copies must share the compositions of the original",
        )

        self.assertTrue(
            all(uncomposed_child is not copy_child for copy_child in copy.children),
            msg="Copied children should be distinct objects",
        )
        self.assertNotIn(
            composer_1,
            copy.children,
            msg="Non-child operands shouldn't be made children of copies",
        )

        self.assertTrue(
            any(composer_1 is operand for operand in copy.composed_components),
            msg="Non-isolated copied non-child operands should be used directly as operands of the copy",
        )
        self.assertTrue(
            all(composer_2 is not operand for operand in copy.composed_components),
            msg="Non-isolated copied child operands should be copied and the copies made operands of the copy",
        )

    def test_copy_composition_isolated_non_child_operands(self) -> None:
        composer_1 = MockEmbodiedComponent(2.0)
        composer_2 = MockEmbodiedComponent(3.0)

        composed = composer_1.compose(
            solid.union(), composer_2, inplace=False, make_children=False
        )
        copy = composed.copy(isolate=True)

        self.assertTrue(
            all(
                composer_1 is not operand and composer_2 is not operand
                for operand in copy.composed_components
            ),
            msg="Isolated copied non-child operands should be copied and the copies made operands of the copy",
        )

    def test_copy_with_color(self) -> None:
        test_component = component.Component(color=(1.0, 1.0, 1.0, 1.0))

        self.assertEqual(
            test_component.color,
            test_component.copy(with_color=True).color,
            msg="Copying with color should make a copy with the same color",
        )

    def test_copy_without_color(self) -> None:
        test_component = component.Component(color=(1.0, 1.0, 1.0, 1.0))
        copy_component = test_component.copy(with_color=False)

        self.assertNotEqual(
            test_component.color,
            copy_component.color,
            msg="Copying without color should make a copy that doesn't have the same color",
        )

        self.assertIsNone(
            copy_component.color, msg="The copy should have the default color"
        )

    def test_body_with_color(self) -> None:
        color_tuple = (1.0, 0.5, 0.25, 0.125)

        self.assertTrue(
            utils.compare_flattened_openscad_children(
                MockEmbodiedComponent(size=2.0, color=color_tuple).body,
                solid.color(color_tuple)(solid.cube(size=2.0)),
            ),
            msg="Color should be applied to the body when being rendered",
        )

    def test_body_without_color(self) -> None:
        self.assertTrue(
            utils.compare_flattened_openscad_children(
                MockEmbodiedComponent(size=2.0, color=None).body, solid.cube(size=2.0)
            ),
            msg="Colorless components' bodies should not have colors applied",
        )
