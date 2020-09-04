import unittest

import solid

from sccm import connector
from sccm.components import sphere
from tests import utils


class TestSphere(unittest.TestCase):
    def test_body(self) -> None:
        self.assertTrue(
            utils.compare_openscad_objects(
                sphere.Sphere(diameter=15.0).body, solid.sphere(d=15.0)
            ),
            msg="Should produce the expected OpenSCAD object",
        )

    def test_eq(self) -> None:
        self.assertEqual(
            sphere.Sphere(diameter=15.0),
            sphere.Sphere(diameter=15.0),
            msg="Equivalent cylinders should be equal",
        )

        self.assertNotEqual(
            sphere.Sphere(diameter=15.0),
            sphere.Sphere(diameter=20.0),
            msg="Equivalent cylinders should be equal",
        )

    def test_copy(self) -> None:
        test_sphere = sphere.Sphere(diameter=15.0)
        copy_sphere = test_sphere.copy()

        self.assertEqual(
            test_sphere,
            copy_sphere,
            msg="Copied spheres should be equivalent to the originals",
        )

    def test_radius(self) -> None:
        self.assertEqual(
            sphere.Sphere(diameter=20.0).radius,
            10.0,
            msg="Radius should be as expected",
        )

    def test_center_anchor_position(self) -> None:
        self.assertEqual(
            sphere.Sphere(diameter=20.0).center_anchor,
            connector.Connector(),
            msg="Center connector should be positioned as expected",
        )

        self.assertEqual(
            sphere.Sphere(diameter=20.0).transform(solid.utils.up(10.0)).center_anchor,
            connector.Connector.from_components(point_z=10.0),
            msg="Center connector should move with translation",
        )
