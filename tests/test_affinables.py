import typing
import unittest

import solid

from sccm import affinables


class MockAffinable(affinables.Affinable):
    def _transform(
        self, transform: affinables.AffineTransformation
    ) -> affinables.Affinable:
        return self


class TestAffinable(unittest.TestCase):
    def test_eq_affinable(self) -> None:
        self.assertEqual(
            MockAffinable(),
            MockAffinable(),
            msg="Affinable subclass instances should compare equal",
        )

    def test_eq_not_affinable(self) -> None:
        self.assertNotEqual(
            MockAffinable(),
            1,
            msg="Affinable subclass instances should not be equal to non-affinables",
        )


class MockHolonomicTransformable(affinables.HolonomicTransformable):
    def __init__(self) -> None:
        self._rotations: typing.List[solid.rotate] = []
        self._translations: typing.List[solid.translate] = []
        self._scalings: typing.List[solid.scale] = []

    def rotate(self, rotation: solid.rotate) -> affinables.HolonomicTransformable:
        self._rotations.append(rotation)
        return self

    def translate(
        self, translation: solid.translate
    ) -> affinables.HolonomicTransformable:
        self._translations.append(translation)
        return self

    def scale(self, scaling: solid.scale) -> affinables.HolonomicTransformable:
        self._scalings.append(scaling)
        return self


class TestHolonomicTransformable(unittest.TestCase):
    def test_transform_dispatch_rotation(self) -> None:
        holonomic_transformable = MockHolonomicTransformable()

        rotation = solid.rotate([11.0, 12.0, 13.0])
        holonomic_transformable.transform(rotation)

        self.assertEqual(
            holonomic_transformable._rotations,
            [rotation],
            msg="Rotation should be correctly dispatched",
        )

    def test_transform_dispatch_translation(self) -> None:
        holonomic_transformable = MockHolonomicTransformable()

        translation = solid.translate([21.0, 22.0, 23.0])
        holonomic_transformable.transform(translation)

        self.assertEqual(
            holonomic_transformable._translations,
            [translation],
            msg="Translation should be correctly dispatched",
        )

    def test_transform_dispatch_scaling(self) -> None:
        holonomic_transformable = MockHolonomicTransformable()

        scaling = solid.scale([31.0, 32.0, 33.0])
        holonomic_transformable.transform(scaling)

        self.assertEqual(
            holonomic_transformable._scalings,
            [scaling],
            msg="Scaling should be correctly dispatched",
        )

    def test_transform_dispatch_unsuported(self) -> None:
        holonomic_transformable = MockHolonomicTransformable()

        color = solid.color([1.0, 1.0, 1.0])
        with self.assertRaises(
            NotImplementedError, msg="Unsupported transformations should error out"
        ):
            holonomic_transformable.transform(color)


class MockHistoricalTransformable(affinables.HistoricalTransformable):
    def __init__(self) -> None:
        self._transformations: typing.List[affinables.AffineTransformation] = []

    @property
    def transformations(self) -> typing.Iterator[affinables.AffineTransformation]:
        yield from self._transformations

    def _transform(
        self, transform: affinables.AffineTransformation
    ) -> affinables.Affinable:
        self._transformations.append(transform)
        return self

    # `mypy` cannot properly check decorated properties
    @property  # type: ignore
    @affinables.HistoricalTransformable.transformed_object
    def cube(self) -> solid.OpenSCADObject:
        return solid.cube(1)


def flatten_openscad_children(
    parent: solid.OpenSCADObject
) -> typing.List[solid.OpenSCADObject]:
    """Get a recursive list of this object's children, in order of depth

    This object will be last, and its deepest-level children will be first

    Args:
        parent: The object whose children to retrieve

    Raises:
        ValueError:
            If this parent has more than one child
    """
    child_count = len(parent.children)

    if child_count == 0:
        return [parent]
    elif child_count > 1:
        raise ValueError
    else:
        return flatten_openscad_children(parent.children[0]) + [parent]


class TestHistoricalTransformable(unittest.TestCase):
    def test_eq_not_historical_transformable(self) -> None:
        self.assertNotEqual(
            MockHistoricalTransformable(),
            MockHolonomicTransformable(),
            msg="A historical transformable shouldn't be equal to just another affinable",
        )

    def test_eq_different_transformations(self) -> None:
        transformable_1 = MockHistoricalTransformable()
        transformable_1.transform(solid.rotate([11.0, 12.0, 13.0]))

        transformable_2 = MockHistoricalTransformable()
        transformable_2.transform(solid.scale([31.0, 32.0, 33.0]))

        self.assertNotEqual(
            transformable_1,
            transformable_2,
            msg="Two historical transformables with different transformations are not equal",
        )

    def test_eq(self) -> None:
        transformation = solid.rotate([11.0, 12.0, 13.0])

        transformable_1 = MockHistoricalTransformable()
        transformable_1.transform(transformation)

        transformable_2 = MockHistoricalTransformable()
        transformable_2.transform(transformation)

        self.assertEqual(
            transformable_1,
            transformable_2,
            msg="Two historical transformables with the same transformations are equal",
        )

    def test_transformed_affinable(self) -> None:
        transformation = solid.rotate([11.0, 12.0, 13.0])

        transformable_1 = MockHistoricalTransformable()
        transformable_1.transform(transformation)

        transformable_2 = transformable_1.transformed(MockHistoricalTransformable())

        self.assertEqual(
            list(transformable_1.transformations),  # type: ignore
            list(transformable_2.transformations),  # type: ignore
            msg="Transforming a transformable should transfer the transformations",
        )

    def test_transformed_solid_transformation(self) -> None:
        transformations = [
            solid.rotate([11.0, 12.0, 13.0]),
            solid.translate([21.0, 22.0, 23.0]),
            solid.scale([31.0, 32.0, 33.0]),
        ]

        transformable = MockHistoricalTransformable()
        transformable.transform(transformations)

        cube = solid.cube(1)
        transformed_nonaffinable = transformable.transformed(cube)

        self.assertEqual(
            [cube] + transformations,
            flatten_openscad_children(transformed_nonaffinable),
            msg="Transformation application order should be unchanged, and application shouldn't alter transformations",
        )

    def test_transformed_object(self) -> None:
        transformations = [
            solid.rotate([11.0, 12.0, 13.0]),
            solid.translate([21.0, 22.0, 23.0]),
            solid.scale([31.0, 32.0, 33.0]),
        ]

        transformable = MockHistoricalTransformable()
        transformable.transform(transformations)

        transformed_nonaffinable = transformable.cube

        # Exclude the source cube here; OpenSCADObjects don't implement equality,
        # and we don't gain any thing by convolutedly storing the cube instance
        # on the mock historical affinable so it can be compared here
        self.assertEqual(
            transformations,
            flatten_openscad_children(transformed_nonaffinable)[1:],
            msg="The property should be correctly transformed, identically to the parent Affinable",
        )
