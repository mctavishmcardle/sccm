import solid
import solid.utils

from sccm import connector
from sccm.components import component


class Cylinder(component.Component):
    """A cylinder"""

    def __init__(
        self,
        od: float,
        length: float,
        center: bool = False,
        parent: component.Component = None,
    ) -> None:
        """
        Args:
            od: The outside diameter of the cylinder
            length: The cylinder's length
            center: Whether or not to "center" the cylinder's height on the
                origin; if not, the bottom face will be on the XY plane
        """
        super().__init__(parent)

        self.od = od
        self.length = length
        self.center = center

    @property
    def _copy(self) -> "Cylinder":
        return self.__class__(self.od, self.length, self.center)

    @property
    def _end_distance(self) -> float:
        """The distance from the middle plane to a top or bottom face"""
        return self.length / 2.0

    @component.Component.transformed_property
    def top_anchor(self) -> connector.Connector:
        """A connector in the center of the top face"""
        return self.center_anchor.transform(solid.utils.up(self._end_distance))

    @component.Component.transformed_property
    def bottom_anchor(self) -> connector.Connector:
        """A connector in the center of the bottom face"""
        return self.center_anchor.transform(solid.utils.down(self._end_distance))

    @component.Component.transformed_property
    def center_anchor(self) -> connector.Connector:
        """A connector in the center of the middle plane"""
        return connector.Connector.from_components(
            point_z=0.0 if self.center else self._end_distance
        )

    @component.Component.transformed_property
    def _body(self) -> solid.OpenSCADObject:
        return solid.cylinder(d=self.od, h=self.length, center=self.center)

    def __eq__(self, other: object) -> bool:
        return (
            super().__eq__(other)
            and isinstance(other, Cylinder)
            and self.od == other.od
            and self.length == other.length
            and self.center == other.center
        )
