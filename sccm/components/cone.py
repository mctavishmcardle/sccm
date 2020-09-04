from sccm.components import component, frustum


class Cone(frustum.CircularFrustum):
    """A cone"""

    def __init__(
        self,
        bottom_diameter: float,
        height: float,
        center: bool = False,
        parent: component.Component = None,
        color: component.Color = None,
    ) -> None:
        """
        Args:
            bottom_diameter: The diameter of the cone's base
            height: The cone's height
            center: Whether or not to "center" the cone's height on the
                origin; if not, the bottom face will be on the XY plane
            parent: The cone's parent, if any; this component will be set as
                one of the parent's children
            color: The color to use for this component, if any
        """
        super().__init__(
            bottom_diameter=bottom_diameter,
            top_diameter=0.0,
            height=height,
            center=center,
            parent=parent,
            color=color,
        )

    @property
    def _copy(self) -> "Cone":
        return self.__class__(self.bottom_diameter, self.height, self.center)

    def __eq__(self, other: object) -> bool:
        return (
            super().__eq__(other)
            # Since frustum properties are a superset of cone properties, we
            # only have to check class membership
            and isinstance(other, Cone)
        )
