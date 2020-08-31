import typing
import unittest

import solid

from sccm import affinables
from tests import utils


class MockAffinable(affinables.Affinable):
    def _transform(self, transform: affinables.AffineTransformation) -> "MockAffinable":
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

    def test_same_transformations_equivalent(self) -> None:
        self.assertTrue(
            affinables.Affinable._same_transformations(
                [
                    solid.rotate([11.0, 12.0, 13.0]),
                    solid.translate([21.0, 22.0, 23.0]),
                    solid.scale([31.0, 32.0, 33.0]),
                ],
                [
                    solid.rotate([11.0, 12.0, 13.0]),
                    solid.translate([21.0, 22.0, 23.0]),
                    solid.scale([31.0, 32.0, 33.0]),
                ],
            ),
            msg="Identical transformations should be considered the same",
        )

    def test_same_transformations_nonequivalent_params(self) -> None:
        self.assertFalse(
            affinables.Affinable._same_transformations(
                [
                    solid.rotate([11.0, 12.0, 13.0]),
                    solid.translate([21.0, 22.0, 23.0]),
                    solid.scale([31.0, 32.0, 33.0]),
                ],
                [
                    solid.rotate([11.1, 12.1, 13.1]),
                    solid.translate([21.1, 22.1, 23.1]),
                    solid.scale([31.1, 32.1, 33.1]),
                ],
            ),
            msg="Similar transformations with different params are not the same",
        )

    def test_same_transformations_nonequivalent_types(self) -> None:
        self.assertFalse(
            affinables.Affinable._same_transformations(
                [
                    solid.rotate([11.0, 12.0, 13.0]),
                    solid.translate([21.0, 22.0, 23.0]),
                    solid.scale([31.0, 32.0, 33.0]),
                ],
                [
                    solid.translate([11.0, 12.0, 13.0]),
                    solid.scale([21.0, 22.0, 23.0]),
                    solid.rotate([31.0, 32.0, 33.0]),
                ],
            ),
            msg="Similar transformations with different types are not the same",
        )

    def test_same_transformations_different_order(self) -> None:
        self.assertFalse(
            affinables.Affinable._same_transformations(
                [
                    solid.rotate([11.0, 12.0, 13.0]),
                    solid.translate([21.0, 22.0, 23.0]),
                    solid.scale([31.0, 32.0, 33.0]),
                ],
                [
                    solid.scale([31.0, 32.0, 33.0]),
                    solid.translate([21.0, 22.0, 23.0]),
                    solid.rotate([11.0, 12.0, 13.0]),
                ],
            ),
            msg="Identical transformations in different orders should not be considered the same",
        )

    def test_same_transformations_different_lengths(self) -> None:
        self.assertFalse(
            affinables.Affinable._same_transformations(
                [
                    solid.rotate([11.0, 12.0, 13.0]),
                    solid.translate([21.0, 22.0, 23.0]),
                    solid.scale([31.0, 32.0, 33.0]),
                ],
                [solid.rotate([11.0, 12.0, 13.0]), solid.translate([21.0, 22.0, 23.0])],
            ),
            msg="Transformation lists of different lengths are not the same",
        )


class MockHolonomicTransformable(affinables.HolonomicTransformable):
    def __init__(self) -> None:
        self._rotations: typing.List[solid.rotate] = []
        self._translations: typing.List[solid.translate] = []
        self._scalings: typing.List[solid.scale] = []

    def rotate(self, rotation: solid.rotate) -> "MockHolonomicTransformable":
        self._rotations.append(rotation)
        return self

    def translate(self, translation: solid.translate) -> "MockHolonomicTransformable":
        self._translations.append(translation)
        return self

    def scale(self, scaling: solid.scale) -> "MockHolonomicTransformable":
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
    ) -> "MockHistoricalTransformable":
        self._transformations.append(transform)
        return self

    @affinables.HistoricalTransformable.transformed_property
    def cube(self) -> solid.OpenSCADObject:
        return solid.cube(1)


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

        self.assertTrue(
            affinables.Affinable._same_transformations(
                transformations,
                # Just extract the transformations to compare
                utils.flatten_openscad_children(transformed_nonaffinable)[1:],
            ),
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

        self.assertTrue(
            affinables.Affinable._same_transformations(
                transformations,
                # Just extract the transformations to compare
                utils.flatten_openscad_children(transformed_nonaffinable)[1:],
            ),
            msg="The property should be correctly transformed, identically to the parent Affinable",
        )
