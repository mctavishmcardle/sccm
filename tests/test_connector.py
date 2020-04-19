import unittest

import solid

from sccm import connector, vector


class TestConnector(unittest.TestCase):
    def test_roll_preserved(self) -> None:
        self.assertAlmostEqual(
            connector.Connector.from_components(roll=45.0).roll,
            45.0,
            msg="Ordinary rolls should be preserved",
        )

    def test_roll_preserved_180(self) -> None:
        self.assertAlmostEqual(
            connector.Connector.from_components(roll=180.0).roll,
            180.0,
            msg="Half-circle rolls should come out to 180",
        )

    def test_roll_preserved_360(self) -> None:
        self.assertAlmostEqual(
            connector.Connector.from_components(roll=360.0).roll,
            0.0,
            msg="Full-circle rolls should come out to 0",
        )

    def test_roll_preserved_negative(self) -> None:
        self.assertAlmostEqual(
            connector.Connector.from_components(roll=-45.0).roll,
            -45.0,
            msg="Negative rolls should be preserved",
        )

    def test_roll_preserved_complex(self) -> None:
        self.assertAlmostEqual(
            connector.Connector.from_components(
                axis_x=1.0, axis_y=-2.0, axis_z=3.0, roll=-45.0
            ).roll,
            -45.0,
            msg="The roll should be preserved with a complicated primary alignment axis",
        )

    def test_roll_preserved_from_vectors(self) -> None:
        self.assertAlmostEqual(
            connector.Connector(
                normal=vector.AXIS_X.rotate(123.0, normal=vector.AXIS_Z)
            ).roll,
            123.0,
            msg="The roll should be preserved when constructing from vectors",
        )

    def test_translate(self) -> None:
        translation_vector_raw = [1, 2, 3]
        original_connector = connector.Connector()
        translated_connector = original_connector.translate(
            solid.translate(translation_vector_raw)
        )

        self.assertEqual(
            translated_connector.point,
            original_connector.point + vector.Vector.from_raw(translation_vector_raw),
            msg="The connector point should be transformed as expected",
        )

        self.assertEqual(
            translated_connector.axis,
            original_connector.axis,
            msg="The primary alignment axis should be unchanged under translation",
        )

        self.assertEqual(
            translated_connector.normal,
            original_connector.normal,
            msg="The secondary alignment axis should be unchanged under translation",
        )

    def test_rotate_about(self) -> None:
        rotated_connector = connector.Connector(
            point=vector.Vector.from_raw([0, 0, 1]),
            axis=vector.Vector.from_raw([0, 0, 1]),
            normal=vector.Vector.from_raw([1, 0, 0]),
        ).rotate_about(90, vector.AXIS_Y)

        self.assertEqual(
            rotated_connector.point,
            vector.Vector.from_raw([1, 0, 0]),
            msg="The point should be rotated as expected",
        )

        self.assertEqual(
            rotated_connector.axis,
            vector.Vector.from_raw([1, 0, 0]),
            msg="The primary alignment axis should be rotated as expected",
        )

        self.assertEqual(
            rotated_connector.normal,
            vector.Vector.from_raw([0, 0, -1]),
            msg="The secondary alignment axis should be rotated as expected",
        )

    def test_rotate_about_at_origin(self) -> None:
        rotated_connector = connector.Connector(
            point=vector.Vector.from_raw([0, 0, 0]),
            axis=vector.Vector.from_raw([0, 0, 1]),
            normal=vector.Vector.from_raw([1, 0, 0]),
        ).rotate_about(90, vector.AXIS_Y)

        self.assertEqual(
            rotated_connector.point,
            vector.Vector.from_raw([0, 0, 0]),
            msg="The point should remain at the origin",
        )

        self.assertEqual(
            rotated_connector.axis,
            vector.Vector.from_raw([1, 0, 0]),
            msg="The primary alignment axis should be rotated as expected",
        )

        self.assertEqual(
            rotated_connector.normal,
            vector.Vector.from_raw([0, 0, -1]),
            msg="The secondary alignment axis should be rotated as expected",
        )

    def test_scaling(self) -> None:
        original_connector = connector.Connector(
            point=vector.Vector.from_raw([2, 2, 2])
        )
        translated_connector = original_connector.scale(solid.scale([1, 2, 3]))

        self.assertEqual(
            translated_connector.point,
            vector.Vector.from_raw([2, 4, 6]),
            msg="The connector point should be scaled as expected",
        )

        self.assertEqual(
            translated_connector.axis,
            original_connector.axis,
            msg="The primary alignment axis should be unchanged under scaling",
        )

        self.assertEqual(
            translated_connector.normal,
            original_connector.normal,
            msg="The secondary alignment axis should be unchanged under scaling",
        )

    def test_rotate_angle_no_axis(self) -> None:
        original_connector = connector.Connector(
            point=vector.Vector.from_raw([1, 1, 1]),
            axis=vector.Vector.from_raw([0, 0, 1]),
            normal=vector.Vector.from_raw([1, 0, 0]),
        )
        rotated_connector = original_connector.rotate(solid.rotate(a=90.0))

        self.assertEqual(
            rotated_connector.point,
            vector.Vector.from_raw([-1, 1, 1]),
            msg="If no pole is specified, rotation should be about the Z axis",
        )

        self.assertEqual(
            rotated_connector.axis,
            vector.Vector.from_raw([0, 0, 1]),
            msg="The primary alignment axis should not be rotated because it's parallel to Z",
        )

        self.assertEqual(
            rotated_connector.normal,
            vector.Vector.from_raw([0, 1, 0]),
            msg="The secondary alignment axis should be rotated as expected",
        )

    def test_rotate_angle_with_axis(self) -> None:
        original_connector = connector.Connector(
            point=vector.Vector.from_raw([1, 1, 1]),
            axis=vector.Vector.from_raw([0, 0, 1]),
            normal=vector.Vector.from_raw([1, 0, 0]),
        )
        rotated_connector = original_connector.rotate(solid.rotate(a=90.0, v=[0, 1, 0]))

        self.assertEqual(
            rotated_connector.point,
            vector.Vector.from_raw([1, 1, -1]),
            msg="The point should rotate about the input axis",
        )

        self.assertEqual(
            rotated_connector.axis,
            vector.Vector.from_raw([1, 0, 0]),
            msg="The primary alignment axis should be rotated as expected",
        )

        self.assertEqual(
            rotated_connector.normal,
            vector.Vector.from_raw([0, 0, -1]),
            msg="The secondary alignment axis should be rotated as expected",
        )

    def test_rotate_multiangle(self) -> None:
        original_connector = connector.Connector(
            point=vector.Vector.from_raw([1, 1, 1]),
            axis=vector.Vector.from_raw([0, 0, 1]),
            normal=vector.Vector.from_raw([1, 0, 0]),
        )
        rotated_connector = original_connector.rotate(solid.rotate(a=[90, 90, 90]))

        self.assertEqual(
            rotated_connector.point,
            vector.Vector.from_raw([1, 1, -1]),
            msg="The point should rotate the specified angles around X, Y, & Z",
        )

        self.assertEqual(
            rotated_connector.axis,
            vector.Vector.from_raw([1, 0, 0]),
            msg="The primary alignment axis should be rotated as expected",
        )

        self.assertEqual(
            rotated_connector.normal,
            vector.Vector.from_raw([0, 0, -1]),
            msg="The secondary alignment axis should be rotated as expected",
        )

    def test_rotate_multiangle_equivalent_successive_multiangle(self) -> None:
        original_connector = connector.Connector(
            point=vector.Vector.from_raw([1, 1, 1]),
            axis=vector.Vector.from_raw([0, 0, 1]),
            normal=vector.Vector.from_raw([1, 0, 0]),
        )

        self.assertEqual(
            original_connector.rotate(solid.rotate(a=[90, 90, 90])),
            original_connector.rotate(solid.rotate(a=[90, 0, 0]))
            .rotate(solid.rotate(a=[0, 90, 0]))
            .rotate(solid.rotate(a=[0, 0, 90])),
            msg="Multiangle rotation should be equiavelent to successive rotations about each axis",
        )

    def test_rotate_multiangle_equivalent_successive_pole(self) -> None:
        original_connector = connector.Connector(
            point=vector.Vector.from_raw([1, 1, 1]),
            axis=vector.Vector.from_raw([0, 0, 1]),
            normal=vector.Vector.from_raw([1, 0, 0]),
        )

        self.assertEqual(
            original_connector.rotate(solid.rotate(a=[90, 90, 90])),
            original_connector.rotate(solid.rotate(a=90, v=[1, 0, 0]))
            .rotate(solid.rotate(a=90, v=[0, 1, 0]))
            .rotate(solid.rotate(a=90, v=[0, 0, 1])),
            msg="Multiangle rotation should be equiavelent to successive rotations about each axis",
        )

    def test_rotate_malformed(self) -> None:
        with self.assertRaises(
            connector.MalformedRotation,
            msg="Rotation with a vector parameter but no angle is malformed",
        ):
            connector.Connector().rotate(solid.rotate(v=[1, 0, 0]))

    def test_transform_equivalent(self) -> None:
        original_connector = connector.Connector(
            point=vector.Vector.from_raw([1, 1, 1]),
            axis=vector.Vector.from_raw([0, 0, 1]),
            normal=vector.Vector.from_raw([1, 0, 0]),
        )

        self.assertEqual(
            original_connector.rotate(solid.rotate(a=[90, 90, 90]))
            .translate(solid.translate([1, 1, 1]))
            .scale(solid.scale([2, 2, 2])),
            original_connector.transform(
                [
                    solid.rotate(a=90, v=[1, 0, 0]),
                    solid.rotate(a=90, v=[0, 1, 0]),
                    solid.rotate(a=90, v=[0, 0, 1]),
                    solid.translate([1, 1, 1]),
                    solid.scale([2, 2, 2]),
                ]
            ),
            msg="Transform should accept & correctly dispatch multiple transformations",
        )

    def test_align_to_origin(self) -> None:
        original_connector = connector.Connector.from_components(
            point_x=123,
            point_y=631,
            point_z=62,
            axis_x=172,
            axis_y=15,
            axis_z=125,
            roll=214,
        )

        self.assertEqual(
            original_connector.transform(original_connector.align()),
            connector.Connector(),
            msg="Should align complex connector with origin",
        )

    def test_align_from_origin(self) -> None:
        original_connector = connector.Connector()
        target_connector = connector.Connector.from_components(
            point_x=123,
            point_y=631,
            point_z=62,
            axis_x=172,
            axis_y=15,
            axis_z=125,
            roll=214,
        )

        self.assertEqual(
            original_connector.transform(original_connector.align(target_connector)),
            target_connector,
            msg="Should align origin connector with complex vector",
        )

    def test_align_both_non_origin(self) -> None:
        original_connector = connector.Connector.from_components(
            point_x=136,
            point_y=-61,
            point_z=-151,
            axis_x=-12,
            axis_y=0.135,
            axis_z=15,
            roll=-15,
        )
        target_connector = connector.Connector.from_components(
            point_x=123,
            point_y=631,
            point_z=62,
            axis_x=172,
            axis_y=15,
            axis_z=125,
            roll=214,
        )

        self.assertEqual(
            original_connector.transform(original_connector.align(target_connector)),
            target_connector,
            msg="Should align two complex connectors",
        )

    def test_align_noop(self) -> None:
        original_connector = connector.Connector()
        target_connector = connector.Connector()

        self.assertEqual(
            original_connector.transform(original_connector.align(target_connector)),
            target_connector,
            msg="Connectors that don't need to be altered for alignment shouldn't be",
        )

    def test_eq_wrong_type(self) -> None:
        with self.assertRaises(
            NotImplementedError,
            msg="Should error out if the comparison value has the wrong type",
        ):
            connector.Connector() == "test"

    def test_string_repr(self) -> None:
        self.assertEqual(
            repr(connector.Connector()),
            "{<0.0, 0.0, 0.0>; <0.0, 0.0, 1.0>; <1.0, 0.0, 0.0>}",
            msg="Should have the correct string representation",
        )
