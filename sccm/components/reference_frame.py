from sccm import connector, vector
from sccm.components import component, cone, cylinder, sphere


class ReferenceFrame(component.Component):
    """A visualization of a Connector's internal frame of reference"""

    def __init__(self, parent: component.Component = None) -> None:
        """
        Args:
            parent: The frame's parent, if any; this component will be set as
                one of the parent's children
        """
        # A central sphere corresponding to the connector's location
        self.origin = sphere.Sphere(diameter=1.0)

        # Three arms representing the connector's orientation
        self.x_arm = self._arm(axis=vector.AXIS_X, color=(1.0, 0.0, 0.0))
        self.y_arm = self._arm(axis=vector.AXIS_Y, color=(0.0, 1.0, 0.0))
        self.z_arm = self._arm(axis=vector.AXIS_Z, color=(0.0, 0.0, 1.0))

        # need to get this to work without making them children, because
        # otherwise copying doesn't work, i think
        super().__init__(
            parent=parent, children=[self.origin, self.x_arm, self.y_arm, self.z_arm]
        )

    @classmethod
    def from_connector(
        cls,
        intrinsic_connector: connector.Connector = connector.Connector(),
        parent: component.Component = None,
    ):
        """Construct a reference frame corresponding to an existing connector

        Args:
            intrinsic_connector: The connector that this refrence frame embodies
            parent: The frame's parent, if any; this component will be set as
                one of the parent's children
        """
        return cls(parent).transform(connector.Connector().align(intrinsic_connector))

    def _arm(self, axis: vector.Vector, color: component.Color) -> component.Component:
        """Construct an arm for representing the frame's alignment

        Args:
            axis: The axis with which the arm should be aligned
            color: The color the arm should have
        """
        arm_cylinder = cylinder.Cylinder(diameter=0.2, height=2.0)
        tip_cone = cone.Cone(bottom_diameter=0.3, height=0.3)

        # Put the cone on top of the cylinder and construct a container for them
        tip_cone.transform(tip_cone.bottom_anchor.align(arm_cylinder.top_anchor))
        arm = component.Component(children=[arm_cylinder, tip_cone], color=color)

        # Align the arm with the desired axis
        arm.transform(
            arm_cylinder.bottom_anchor.align(
                connector.Connector.from_components(
                    axis_x=axis.x, axis_y=axis.y, axis_z=axis.z
                )
            )
        )

        return arm

    def __eq__(self, other: object) -> bool:
        return super().__eq__(other) and isinstance(other, ReferenceFrame)
