import math
import unittest
from unittest import mock

import numpy

from sccm import vector


class TestVector(unittest.TestCase):
    xy_45 = (vector.AXIS_X + vector.AXIS_Z).normalized

    def test_nan_magnitude_any(self) -> None:
        with self.assertRaises(vector.NaNVector, msg="Any NaN components should fail"):
            vector.Vector(numpy.array([1, 1, numpy.nan]))

    def test_nan_magnitude_all(self) -> None:
        with self.assertRaises(vector.NaNVector, msg="All-NaN components should fail"):
            vector.Vector(numpy.array([numpy.nan, numpy.nan, numpy.nan]))

    def test_zero_magnitude(self) -> None:
        self.assertAlmostEqual(
            vector.Vector.from_raw((0, 0, 0)).magnitude,
            0.0,
            msg="Should correctly determine 0 magnitude",
        )

    def test_unit_magnitude(self) -> None:
        self.assertAlmostEqual(
            vector.Vector.from_raw((1, 0, 0)).magnitude,
            1.0,
            msg="Should correctly evaluate unit vector magnitudes",
        )

    def test_magnitude(self) -> None:
        self.assertAlmostEqual(
            vector.Vector.from_raw((1, 1, 0)).magnitude,
            math.sqrt(2),
            msg="Should correctly determine other magnitudes",
        )

    def test_normal(self) -> None:
        self.assertEqual(
            vector.AXIS_X.normal(vector.AXIS_Y),
            vector.AXIS_Z,
            msg="Normals should follow right hand rule",
        )

    def test_normal_swap(self) -> None:
        self.assertEqual(
            vector.AXIS_Y.normal(vector.AXIS_X),
            -vector.AXIS_Z,
            msg="Swapping vectors should reverse the normal",
        )

    def test_normal_null(self) -> None:
        with self.assertRaises(
            vector.NoNormalForNulls, msg="0-length vectors have undefined normals"
        ):
            vector.AXIS_X.normal(vector.Vector())

    def test_normal_parallel(self) -> None:
        with self.assertRaises(
            vector.NoNormalForParallels, msg="Parallel vectors have undefined normals"
        ):
            vector.AXIS_X.normal(vector.AXIS_X)

    def test_normal_antiparallel(self) -> None:
        with self.assertRaises(
            vector.NoNormalForAntiparallels,
            msg="Antiparallel vectors have undefined normals",
        ):
            vector.AXIS_X.normal(-vector.AXIS_X)

    def test_rotate(self) -> None:
        self.assertEqual(
            vector.AXIS_X.rotate(90.0, vector.AXIS_Y),
            -vector.AXIS_Z,
            msg="Rotation should follow right hand rule",
        )

    def test_rotate_reverse(self) -> None:
        self.assertEqual(
            vector.AXIS_Y.rotate(90.0, vector.AXIS_X),
            vector.AXIS_Z,
            msg="Swapping vectors should reverse direction of rotation",
        )

    def test_rotate_undo(self) -> None:
        self.assertEqual(
            vector.AXIS_X.rotate(90.0, vector.AXIS_Y).rotate(-90.0, vector.AXIS_Y),
            vector.AXIS_X,
            msg="Rotating and then reverse-rotating in the same plane should result in the original vector",
        )

    def test_rotate_full(self) -> None:
        self.assertEqual(
            vector.AXIS_X.rotate(360, vector.AXIS_Y),
            vector.AXIS_X,
            msg="Rotating through a full circle should result in the original vector",
        )

    def test_rotate_about_self(self) -> None:
        self.assertEqual(
            vector.AXIS_X.rotate(45.0, vector.AXIS_X),
            vector.AXIS_X,
            msg="Rotating a vector about itself should result in no change",
        )

    def test_rotate_about_opposite(self) -> None:
        self.assertEqual(
            vector.AXIS_X.rotate(45.0, -vector.AXIS_X),
            vector.AXIS_X,
            msg="Rotating a vector about its reverse should result in no change",
        )

    def test_rotate_to_alignment(self) -> None:
        self.assertEqual(
            vector.AXIS_X.rotate_to_alignment(self.xy_45, vector.AXIS_Z),
            self.xy_45,
            msg="The vector should rotate in the same direction as the alignment",
        )

    def test_rotate_to_alignment_on_normal(self) -> None:
        self.assertEqual(
            vector.AXIS_Y.rotate_to_alignment(self.xy_45, vector.AXIS_Z),
            vector.AXIS_Y,
            msg="A vector perpendicular to the inclined & reference vector should be unchanged",
        )

    def test_rotate_to_alignment_on_parallel(self) -> None:
        self.assertEqual(
            vector.AXIS_Y.rotate_to_alignment(self.xy_45, self.xy_45),
            vector.AXIS_Y,
            msg="The vector should be unchanged if the inclined & reference vectors are parallel",
        )

    def test_rotate_to_alignment_on_antiparallel(self) -> None:
        self.assertEqual(
            vector.AXIS_Z.rotate_to_alignment(-vector.AXIS_X, vector.AXIS_X),
            -vector.AXIS_Z,
            msg="Antiparallel vectors to align should result in an inverted input",
        )

    def test_rotate_to_alignment_parallel_to_reference(self) -> None:
        self.assertEqual(
            vector.AXIS_X.rotate_to_alignment(-vector.AXIS_X, vector.AXIS_X),
            -vector.AXIS_X,
            msg="Vectors parallel to the reference vector should be transformed appropriately",
        )

    def test_rotate_to_alignment_parallel_to_inclined(self) -> None:
        self.assertEqual(
            (-vector.AXIS_X).rotate_to_alignment(-vector.AXIS_X, vector.AXIS_X),
            vector.AXIS_X,
            msg="Vectors parallel to the inclined vector should be transformed appropriately",
        )

    def test_angle_between(self) -> None:
        self.assertAlmostEqual(
            vector.AXIS_Z.angle_between(vector.AXIS_X),
            90.0,
            msg="Should rotate about cross product",
        )

    def test_angle_between_normal(self) -> None:
        self.assertAlmostEqual(
            vector.AXIS_X.angle_between(vector.AXIS_Z, normal=vector.AXIS_Y),
            -90.0,
            msg="Should follow the right hand rule with a specified normal",
        )

    def test_angle_between_antiparallel(self) -> None:
        self.assertAlmostEqual(
            vector.AXIS_X.angle_between(-vector.AXIS_X),
            180.0,
            msg="Antiparallel vectors' angles are arbitrarily positive",
        )

    def test_angle_between_parallel(self) -> None:
        self.assertAlmostEqual(
            vector.AXIS_X.angle_between(vector.AXIS_X),
            0.0,
            msg="Parallel vectors have no angle between them",
        )

    @unittest.mock.patch.object(
        vector.Vector,
        "normal",
        mock.Mock(
            side_effect=vector.NoNormalForColineals(vector.Vector(), vector.Vector())
        ),
    )
    def test_arbitrary_normal_error(self) -> None:
        with self.assertRaises(
            vector.NoArbitraryNormal,
            msg="Should raise the correct error if no normals can be found",
        ):
            self.xy_45.arbitrary_normal

    def test_eq_wrong_type(self) -> None:
        with self.assertRaises(
            NotImplementedError,
            msg="Should error out if the comparison value has the wrong type",
        ):
            vector.ORIGIN == "test"

    def test_string_repr(self) -> None:
        self.assertEqual(
            repr(vector.Vector.from_raw((1.0000001, 2.2, 30003.0))),
            "<1.0, 2.2, 3e+04>",
            msg="Should have the correct string representation",
        )
