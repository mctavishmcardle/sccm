import unittest

import solid

from sccm.components import cylinder, frustum
from tests import utils


class TestCylinder(unittest.TestCase):
    def test_body(self) -> None:
        self.assertTrue(
            utils.compare_openscad_objects(
                cylinder.Cylinder(diameter=15.0, height=7.5, center=True).body,
                solid.cylinder(d1=15.0, d2=15.0, h=7.5, center=True),
            ),
            msg="Should produce the expected OpenSCAD object",
        )

    def test_eq(self) -> None:
        self.assertEqual(
            cylinder.Cylinder(diameter=15.0, height=7.5, center=True),
            cylinder.Cylinder(diameter=15.0, height=7.5, center=True),
            msg="Equivalent cylinders should be equal",
        )

        self.assertNotEqual(
            cylinder.Cylinder(diameter=15.0, height=7.5, center=True),
            frustum.CircularFrustum(bottom_diameter=15.0, height=7.5, center=True),
            msg="A cylinder & equivalent circular frustum should not be equal",
        )

    def test_copy(self) -> None:
        test_cylinder = cylinder.Cylinder(diameter=15.0, height=7.5, center=True)
        copy_cylinder = test_cylinder.copy()

        self.assertEqual(
            test_cylinder,
            copy_cylinder,
            msg="Copied cylinders should be equivalent to the originals",
        )

    def test_diameter_modification(self) -> None:
        test_cylinder = cylinder.Cylinder(diameter=15.0, height=7.5, center=True)
        test_cylinder.diameter = 30.0

        self.assertEqual(
            test_cylinder.diameter,
            30.0,
            msg="Should be able to modify the diameter of an existing cylinder",
        )
