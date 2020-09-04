import unittest

import solid

from sccm import connector
from sccm.components import reference_frame


class TestReferenceFrame(unittest.TestCase):
    def test_eq(self) -> None:
        self.assertEqual(
            reference_frame.ReferenceFrame.from_connector(
                connector.Connector()
                .translate(solid.translate([1.0, 2.0, 3.0]))
                .rotate(solid.rotate([15.0, 45.0, 90.0]))
            ),
            reference_frame.ReferenceFrame.from_connector(
                connector.Connector()
                .translate(solid.translate([1.0, 2.0, 3.0]))
                .rotate(solid.rotate([15.0, 45.0, 90.0]))
            ),
            msg="Equivalent frames should be equal",
        )

    def test_copy(self) -> None:
        reference_connector = (
            connector.Connector()
            .translate(solid.translate([1.0, 2.0, 3.0]))
            .rotate(solid.rotate([15.0, 45.0, 90.0]))
        )

        test_rf = reference_frame.ReferenceFrame.from_connector(reference_connector)
        copy_rf = test_rf.copy()

        self.assertEqual(
            test_rf, copy_rf, msg="Copied frames should be equivalent to the originals"
        )
