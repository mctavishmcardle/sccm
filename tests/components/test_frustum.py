import unittest

import solid

from sccm.components import frustum
from tests import utils


class TestFrustum(unittest.TestCase):
    def test_body(self) -> None:
        self.assertTrue(
            utils.compare_openscad_objects(
                frustum.Frustum(
                    bottom_circumscribed_circle_diameter=15.0,
                    top_circumscribed_circle_diameter=25.0,
                    height=7.5,
                    center=True,
                    segments=7,
                ).body,
                solid.cylinder(d1=15.0, d2=25.0, h=7.5, center=True, segments=7),
            ),
            msg="Should produce the expected OpenSCAD object",
        )

    def test_anchor_positions_uncentered(self) -> None:
        test_frustum = frustum.Frustum(
            bottom_circumscribed_circle_diameter=15.0, height=7.5
        )

        self.assertAlmostEqual(
            test_frustum.center_anchor.point.z,
            3.75,
            msg="Uncentered frustums' midpoint Z should be half the height",
        )

        self.assertAlmostEqual(
            test_frustum.bottom_anchor.point.z,
            0,
            msg="Uncentered frustums' bottom Z should be at the origin",
        )

        self.assertAlmostEqual(
            test_frustum.top_anchor.point.z,
            7.5,
            msg="Uncentered frustums' bottom Z should be at the origin",
        )

    def test_anchor_positions_centered(self) -> None:
        test_frustum = frustum.Frustum(
            bottom_circumscribed_circle_diameter=15.0, height=7.5, center=True
        )

        self.assertAlmostEqual(
            test_frustum.center_anchor.point.z,
            0,
            msg="Centered frustums' midpoint Z should be at the origin",
        )

        self.assertAlmostEqual(
            test_frustum.bottom_anchor.point.z,
            -3.75,
            msg="Centered frustums' bottom Z should be half the height below the origin",
        )

        self.assertAlmostEqual(
            test_frustum.top_anchor.point.z,
            3.75,
            msg="Centered frustums' bottom Z should be half the height above the origin",
        )

    def test_copy(self) -> None:
        test_frustum = frustum.Frustum(
            bottom_circumscribed_circle_diameter=15.0,
            top_circumscribed_circle_diameter=25.0,
            height=7.5,
            center=True,
            segments=7,
        )
        copy_frustum = test_frustum.copy()

        self.assertEqual(
            test_frustum,
            copy_frustum,
            msg="Copied frusta should be equivalent to the originals",
        )

    def test_eq(self) -> None:
        self.assertEqual(
            frustum.Frustum(
                bottom_circumscribed_circle_diameter=15.0,
                top_circumscribed_circle_diameter=25.0,
                height=7.5,
                center=True,
                segments=7,
            ),
            frustum.Frustum(
                bottom_circumscribed_circle_diameter=15.0,
                top_circumscribed_circle_diameter=25.0,
                height=7.5,
                center=True,
                segments=7,
            ),
            msg="Equivalent frusta should be equal",
        )

        self.assertNotEqual(
            frustum.Frustum(
                bottom_circumscribed_circle_diameter=15.0,
                top_circumscribed_circle_diameter=25.0,
                height=7.5,
                center=True,
                segments=7,
            ),
            frustum.Frustum(
                bottom_circumscribed_circle_diameter=15.0,
                top_circumscribed_circle_diameter=25.0,
                height=11.5,
                center=True,
                segments=7,
            ),
            msg="Different frusta should not be equal",
        )

        self.assertNotEqual(
            frustum.Frustum(
                bottom_circumscribed_circle_diameter=15.0,
                top_circumscribed_circle_diameter=25.0,
                height=7.5,
                center=True,
                segments=7,
            ),
            frustum.Frustum(
                bottom_circumscribed_circle_diameter=15.0,
                top_circumscribed_circle_diameter=25.0,
                height=7.5,
                center=False,
                segments=7,
            ),
            msg="Equality depends on dimensions & position",
        )


class TestCircularFrustum(unittest.TestCase):
    def test_bottom_diameter_assignment(self) -> None:
        test_circular_frustum = frustum.CircularFrustum(
            bottom_diameter=5.0, height=1.0, top_diameter=6.0
        )
        test_circular_frustum.bottom_diameter = 6.0

        self.assertEqual(
            test_circular_frustum.bottom_diameter,
            6.0,
            msg="Should be able to modify the bottom diameter of a frustum",
        )

    def test_top_diameter_assignment(self) -> None:
        test_circular_frustum = frustum.CircularFrustum(
            bottom_diameter=5.0, height=1.0, top_diameter=6.0
        )
        test_circular_frustum.top_diameter = 5.0

        self.assertEqual(
            test_circular_frustum.top_diameter,
            5.0,
            msg="Should be able to modify the top diameter of a frustum",
        )

    def test_copy(self) -> None:
        test_circular_frustum = frustum.CircularFrustum(
            bottom_diameter=5.0, height=1.0, top_diameter=6.0, center=True
        )
        copy_circular_frustum = test_circular_frustum.copy()

        self.assertEqual(
            test_circular_frustum,
            copy_circular_frustum,
            msg="Copied frusta should be equivalent to the originals",
        )

    def test_eq(self) -> None:
        self.assertEqual(
            frustum.CircularFrustum(
                bottom_diameter=5.0, height=1.0, top_diameter=6.0, center=True
            ),
            frustum.CircularFrustum(
                bottom_diameter=5.0, height=1.0, top_diameter=6.0, center=True
            ),
            msg="Equivalent circular frusta should be equal",
        )

        self.assertNotEqual(
            frustum.CircularFrustum(
                bottom_diameter=15.0, top_diameter=25.0, height=7.5, center=True
            ),
            frustum.Frustum(
                bottom_circumscribed_circle_diameter=15.0,
                top_circumscribed_circle_diameter=25.0,
                height=7.5,
                center=True,
            ),
            msg="A circular frustum & equivalent generic frustum should not be equal",
        )
