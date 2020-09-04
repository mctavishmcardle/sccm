import unittest

import solid

from sccm.components import cone, frustum
from tests import utils


class TestCone(unittest.TestCase):
    def test_body(self) -> None:
        self.assertTrue(
            utils.compare_openscad_objects(
                cone.Cone(bottom_diameter=15.0, height=7.5, center=True).body,
                solid.cylinder(d1=15.0, d2=0.0, h=7.5, center=True),
            ),
            msg="Should produce the expected OpenSCAD object",
        )

    def test_eq(self) -> None:
        self.assertEqual(
            cone.Cone(bottom_diameter=15.0, height=7.5, center=True),
            cone.Cone(bottom_diameter=15.0, height=7.5, center=True),
            msg="Equivalent cones should be equal",
        )

        self.assertNotEqual(
            cone.Cone(bottom_diameter=15.0, height=7.5, center=True),
            frustum.CircularFrustum(
                bottom_diameter=15.0, top_diameter=0.0, height=7.5, center=True
            ),
            msg="A cone & equivalent circular frustum should not be equal",
        )

    def test_copy(self) -> None:
        test_cone = cone.Cone(bottom_diameter=15.0, height=7.5, center=True)
        copy_cone = test_cone.copy()

        self.assertEqual(
            test_cone,
            copy_cone,
            msg="Copied cones should be equivalent to the originals",
        )
