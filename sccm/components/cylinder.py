from sccm.components import component, frustum


class Cylinder(frustum.CircularFrustum):
    """A cylinder"""

    def __init__(
        self,
        diameter: float,
        height: float,
        center: bool = False,
        parent: component.Component = None,
        color: component.Color = None,
    ) -> None:
        """
        Args:
            diameter: The outside diameter of the cylinder
            height: The cylinder's height
            center: Whether or not to "center" the cylinder's height on the
                origin; if not, the bottom face will be on the XY plane
            parent: The cylinder's parent, if any; this component will be set as
                one of the parent's children
            color: The color to use for this component, if any
        """
        super().__init__(
            bottom_diameter=diameter,
            height=height,
            center=center,
            parent=parent,
            color=color,
        )

    @property
    def diameter(self) -> float:
        """The diameter of the cylinder"""
        return self.bottom_diameter

    @diameter.setter
    def diameter(self, diameter: float) -> None:
        """Set the diameter of the cylinder

        Args:
            diameter: The new diameter
        """
        self.bottom_diameter = diameter

    @property
    def _copy(self) -> "Cylinder":
        return self.__class__(self.diameter, self.height, self.center)

    def __eq__(self, other: object) -> bool:
        return (
            super().__eq__(other)
            # Since frustum properties are a superset of cylinder properties, we
            # only have to check
            and isinstance(other, Cylinder)
        )
