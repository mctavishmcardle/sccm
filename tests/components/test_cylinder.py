import unittest

import solid

from sccm.components import cylinder
from tests import utils


class TestCylinder(unittest.TestCase):
    def test_body(self) -> None:
        self.assertTrue(
            utils.compare_openscad_objects(
                cylinder.Cylinder(od=15.0, length=7.5, center=True).body,
                solid.cylinder(d=15.0, h=7.5, center=True),
            ),
            msg="Should produce the expected OpenSCAD object",
        )

    def test_eq(self) -> None:
        self.assertEqual(
            cylinder.Cylinder(od=15.0, length=7.5, center=True),
            cylinder.Cylinder(od=15.0, length=7.5, center=True),
            msg="Equivalent cylinders should be equal",
        )

        self.assertNotEqual(
            cylinder.Cylinder(od=15.0, length=7.5, center=True),
            cylinder.Cylinder(od=15.0, length=100, center=True),
            msg="Different cylinders should not be equal",
        )

        self.assertNotEqual(
            cylinder.Cylinder(od=15.0, length=7.5, center=True),
            cylinder.Cylinder(od=15.0, length=7.5, center=False),
            msg="Equality depends on dimensions & position",
        )

    def test_copy(self) -> None:
        test_cylinder = cylinder.Cylinder(od=15.0, length=7.5, center=True)
        copy_cylinder = test_cylinder.copy()

        self.assertEqual(
            test_cylinder,
            copy_cylinder,
            msg="Copied cylinders should be equivalent to the originals",
        )

    def test_anchor_positions_uncentered(self) -> None:
        test_cylinder = cylinder.Cylinder(od=15.0, length=7.5)

        self.assertAlmostEqual(
            test_cylinder.center_anchor.point.z,
            3.75,
            msg="Uncentered cylinders' midpoint Z should be half the height",
        )

        self.assertAlmostEqual(
            test_cylinder.bottom_anchor.point.z,
            0,
            msg="Uncentered cylinders' bottom Z should be at the origin",
        )

        self.assertAlmostEqual(
            test_cylinder.top_anchor.point.z,
            7.5,
            msg="Uncentered cylinders' bottom Z should be at the origin",
        )

    def test_anchor_positions_centered(self) -> None:
        test_cylinder = cylinder.Cylinder(od=15.0, length=7.5, center=True)

        self.assertAlmostEqual(
            test_cylinder.center_anchor.point.z,
            0,
            msg="Centered cylinders' midpoint Z should be at the origin",
        )

        self.assertAlmostEqual(
            test_cylinder.bottom_anchor.point.z,
            -3.75,
            msg="Centered cylinders' bottom Z should be half the height below the origin",
        )

        self.assertAlmostEqual(
            test_cylinder.top_anchor.point.z,
            3.75,
            msg="Centered cylinders' bottom Z should be half the height above the origin",
        )
