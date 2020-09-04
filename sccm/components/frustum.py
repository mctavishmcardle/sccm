import solid
import solid.utils

from sccm import connector
from sccm.components import component


class Frustum(component.Component):
    """A frustum

    In degenerate cases, this is equivalent to a prism or a pyramid (or, if the
    top & bottom faces are circular, a cylinder or cone).

    Note:
        Before transformations, one of the vertices of the top & bottom faces
        will be on the X axis
    """

    def __init__(
        self,
        bottom_circumscribed_circle_diameter: float,
        height: float,
        top_circumscribed_circle_diameter: float = None,
        center: bool = False,
        segments: int = None,
        parent: component.Component = None,
        color: component.Color = None,
    ) -> None:
        """
        Args:
            bottom_circumscribed_circle_diameter: The diameter of the circle
                circumscribing the bottom face of the frustum
            height: The height of the frustum
            top_circumscribed_circle_diameter: The diameter of the circle
                circumscribing the top face of the frustum; if not provided, the
                top diameter will be the same as the bottom diameter, and if the
                top diameter is zero, the sides will all meet at a point at the
                top
            center: Whether or not to "center" the frustum's height on the origin;
                if not, the bottom face will be on the XY plane
            segments: The number of segments the top & bottom faces should have,
                which is equivalent to the number of sides the frustum should have
                (discounting the top & bottom)
            parent: The frustum's parent, if any; this component will be set as
                one of the parent's children
            color: The color to use for this component, if any
        """
        super().__init__(parent=parent, color=color)

        self.bottom_circumscribed_circle_diameter = bottom_circumscribed_circle_diameter
        # `OpenSCAD`'s rendering works stangely if `d1` is passed in but `d2`
        # isn't (which happens if it's `None` in `solid`), so we ensure it always
        # has a value; this could also be handled by just using `d` for prisms
        # / cylinders
        self.top_circumscribed_circle_diameter = (
            top_circumscribed_circle_diameter
            if top_circumscribed_circle_diameter is not None
            else bottom_circumscribed_circle_diameter
        )

        self.height = height
        self.segments = segments

        self.center = center

    @property
    def _end_distance(self) -> float:
        """The distance from the middle plane to a top or bottom face"""
        return self.height / 2.0

    @component.Component.transformed_property
    def top_anchor(self) -> connector.Connector:
        """A connector in the center of the top face"""
        return self._center_anchor.transform(solid.utils.up(self._end_distance))

    @component.Component.transformed_property
    def bottom_anchor(self) -> connector.Connector:
        """A connector in the center of the bottom face"""
        return self._center_anchor.transform(solid.utils.down(self._end_distance))

    @component.Component.transformed_property
    def center_anchor(self) -> connector.Connector:
        """A connector in the center of the middle plane"""
        return self._center_anchor

    @property
    def _center_anchor(self) -> connector.Connector:
        """An untransformed center anchor

        This is necessary since the top & bottom anchors are produced by
        transforming the center anchor, and since they themselves are
        transformed, referencing the transformed center anchor would result
        in the double application of transformations.
        """
        return connector.Connector.from_components(
            point_z=0.0 if self.center else self._end_distance
        )

    @property
    def _copy(self) -> "Frustum":
        return self.__class__(
            self.bottom_circumscribed_circle_diameter,
            self.height,
            self.top_circumscribed_circle_diameter,
            self.center,
            self.segments,
        )

    def __eq__(self, other: object) -> bool:
        return (
            super().__eq__(other)
            and isinstance(other, Frustum)
            and self.bottom_circumscribed_circle_diameter
            == other.bottom_circumscribed_circle_diameter
            and self.top_circumscribed_circle_diameter
            == other.top_circumscribed_circle_diameter
            and self.height == other.height
            and self.center == other.center
            and self.segments == other.segments
        )

    @component.Component.transformed_property
    def _body(self) -> solid.OpenSCADObject:
        return solid.cylinder(
            d1=self.bottom_circumscribed_circle_diameter,
            d2=self.top_circumscribed_circle_diameter,
            h=self.height,
            center=self.center,
            segments=self.segments,
        )


class CircularFrustum(Frustum):
    """A frustum where the top & bottom faces are circles (or points, for a cone)

    Note:
        When rendered, the actual number of faces this component will have depends
        on the global circle-approximation properties set (e.g. `$fn`), if any.
    """

    def __init__(
        self,
        bottom_diameter: float,
        height: float,
        top_diameter: float = None,
        center: bool = False,
        parent: component.Component = None,
        color: component.Color = None,
    ) -> None:
        """
        Args:
            bottom_diameter: The diameter of the top face
            height: The height of the frustum
            top_diameter: The diameter of the top face if not provided, the top
                diameter will be the same as the bottom diameter, and if the top
                diameter is zero, the sides will all meet at a point at the top
            center: Whether or not to "center" the frustum's height on the origin;
                if not, the bottom face will be on the XY plane
            parent: The frustum's parent, if any; this component will be set as
                one of the parent's children
            color: The color to use for this component, if any
        """
        super().__init__(
            bottom_circumscribed_circle_diameter=bottom_diameter,
            height=height,
            top_circumscribed_circle_diameter=top_diameter,
            center=center,
            parent=parent,
            color=color,
        )

    @property
    def bottom_diameter(self) -> float:
        """The diameter of the bottom face"""
        return self.bottom_circumscribed_circle_diameter

    @bottom_diameter.setter
    def bottom_diameter(self, bottom_diameter: float) -> None:
        """Set the diameter of the bottom face

        Args:
            bottom_diameter: The new bottom diameter
        """
        self.bottom_circumscribed_circle_diameter = bottom_diameter

    @property
    def top_diameter(self) -> float:
        """The diameter of the top face"""
        return self.top_circumscribed_circle_diameter

    @top_diameter.setter
    def top_diameter(self, top_diameter: float) -> None:
        """Set the diameter of the top face

        Args:
            top_diameter: The new top diameter
        """
        self.top_circumscribed_circle_diameter = top_diameter

    @property
    def _copy(self) -> "CircularFrustum":
        return self.__class__(
            self.bottom_diameter, self.height, self.top_diameter, self.center
        )

    def __eq__(self, other: object) -> bool:
        return (
            super().__eq__(other)
            # Since generic frustum properties are a superset of circular frustum
            # properties, we only have to check class membership
            and isinstance(other, CircularFrustum)
        )
