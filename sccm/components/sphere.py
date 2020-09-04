import solid
import solid.utils

from sccm import connector
from sccm.components import component


class Sphere(component.Component):
    """A sphere

    Note:
        Until transformed, the sphere's center will be at the origin
    """

    def __init__(
        self,
        diameter: float,
        parent: component.Component = None,
        color: component.Color = None,
    ) -> None:
        """
        Args:
            diamteter: The sphere's diameter
            parent: The sphere's parent, if any; this component will be set as
                one of the parent's children
            color: The color to use for this component, if any
        """
        super().__init__(parent=parent, color=color)

        self.diameter = diameter

    @property
    def radius(self) -> float:
        """The radius of the sphere"""
        return self.diameter / 2.0

    @component.Component.transformed_property
    def center_anchor(self) -> connector.Connector:
        """A connector in the center of the sphere"""
        return connector.Connector()

    @property
    def _copy(self) -> "Sphere":
        return self.__class__(self.diameter)

    def __eq__(self, other: object) -> bool:
        return (
            super().__eq__(other)
            and isinstance(other, Sphere)
            and self.diameter == other.diameter
        )

    @component.Component.transformed_property
    def _body(self) -> solid.OpenSCADObject:
        return solid.sphere(d=self.diameter)
