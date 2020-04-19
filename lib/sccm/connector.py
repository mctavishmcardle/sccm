import functools
import typing

import solid

from sccm import vector

Transformation = typing.Union[solid.translate, solid.rotate, solid.scale]


class MalformedRotation(Exception):
    """Raised if the rotation does not have the expected properties"""

    def __init__(
        self,
        angle: typing.Optional[typing.Union[float, vector.RawVector]],
        axis: typing.Optional[vector.RawVector],
    ) -> None:
        """
        Args:
            angle: The rotation's "angle" (its 'a' argument)
            axis: The rotation's "axis" (its 'v' argument)
        """
        self.angle = angle
        self.axis = axis


class Connector:
    """A connector, for aligning components"""

    def __init__(
        self,
        point: vector.Vector = vector.ORIGIN,
        axis: vector.Vector = vector.AXIS_Z,
        normal: vector.Vector = vector.AXIS_X,
    ) -> None:
        """
        Args:
            point: The location of the attachment point
            axis: The primary alignment axis of the attachment point
            normal: The secondary alignment axis of the attachment point,
                perpendicular to the primary axis
        """
        self.point = point
        self.axis = axis
        self.normal = normal

    @classmethod
    def from_vectors(
        cls,
        point: vector.Vector = vector.ORIGIN,
        axis: vector.Vector = vector.AXIS_Z,
        normal: vector.Vector = vector.AXIS_X,
    ) -> "Connector":
        """
        Args:
            point: The location of the attachment point
            axis: The primary alignment axis of the attachment point
            normal: The secondary alignment axis of the attachment point,
                perpendicular to the primary axis
        """
        return cls(point, axis, normal)

    def copy(
        self,
        point: vector.Vector = None,
        axis: vector.Vector = None,
        normal: vector.Vector = None,
    ) -> "Connector":
        """
        Args:
            point: The location of the attachment point; if not provided, this
                connector's point will be used
            axis: The primary alignment axis of the attachment point; if not
                provided, this connector's primary alignment axis will be
                used
            normal: The secondary alignment axis of the attachment point,
                perpendicular to the primary axis; if not provided, this
                connector's secondary alignment axis will be used
        """
        return self.from_vectors(
            point or self.point, axis or self.axis, normal or self.normal
        )

    @classmethod
    def from_components(
        cls,
        point_x: float = 0.0,
        point_y: float = 0.0,
        point_z: float = 0.0,
        axis_x: float = 0.0,
        axis_y: float = 0.0,
        axis_z: float = 1.0,
        roll: float = 0.0,
    ) -> "Connector":
        """Construct a connector from vector components

        Args:
            point_x: The X component of the connector's position
            point_y: The Y component of the connector's position
            point_z: The Z component of the connector's position
            axis_x: The X component of the connector's primary alignment axis
            axis_y: The Y component of the connector's primary alignment axis
            axis_z: The Z component of the connector's primary alignment axis
            roll: The angle between the X axis and the connector's secondary
                alignment axis, when the primary axis is aligned with Z
        """
        axis = vector.Vector.from_raw([axis_x, axis_y, axis_z]).normalized

        return cls(
            vector.Vector.from_raw([point_x, point_y, point_z]),
            axis,
            vector.AXIS_X.rotate(roll, vector.AXIS_Z).rotate_to_alignment(
                vector.AXIS_Z, axis
            ),
        )

    @property
    def roll(self) -> float:
        """This connector's roll

        The roll is the angle between the X axis and the secondary alignment
        axis, when the primary alignment axis is aligned with Z
        """
        return vector.AXIS_X.angle_between(
            self.normal.rotate_to_alignment(self.axis, vector.AXIS_Z),
            normal=vector.AXIS_Z,
        )

    def translate(self, translation: solid.translate) -> "Connector":
        """Transform this connector to account for a translation

        Args:
            translation: The translation object
        """
        return self.copy(
            point=self.point + vector.Vector.from_raw(translation.params["v"])
        )

    def rotate_about(self, angle: float, axis: vector.Vector) -> "Connector":
        """Rotate this connector about an axis running through the origin

        Args:
            angle: The signed angle through which to rotate
            axis: The axis about which to rotate
        """
        return self.from_vectors(
            point=self.point.rotate(angle, axis),
            axis=self.axis.rotate(angle, axis),
            normal=self.normal.rotate(angle, axis),
        )

    def rotate(self, rotation: solid.rotate) -> "Connector":
        """Transform this connector to account for a rotation

        Args:
            rotation: The rotation object

        Raises:
            MalformedRotation: If the rotation's arguments do not have the
                expected structure
        """
        angle = rotation.params["a"]
        pole = rotation.params["v"]

        if isinstance(angle, (float, int)):
            if not pole:
                pole = vector.AXIS_Z
            else:
                pole = vector.Vector.from_raw(pole).normalized

            return self.rotate_about(angle, pole)

        elif angle:
            return (
                self.rotate_about(angle[0], vector.AXIS_X)
                .rotate_about(angle[1], vector.AXIS_Y)
                .rotate_about(angle[2], vector.AXIS_Z)
            )

        raise MalformedRotation(angle, pole)

    def scale(self, scaling: solid.scale) -> "Connector":
        """Transform this connector to account for a scaling

        Args:
            scaling: The scaling object
        """
        return self.copy(self.point * vector.Vector.from_raw(scaling.params["v"]))

    def transform(
        self, transform: typing.Union[Transformation, typing.List[Transformation]]
    ) -> "Connector":
        """Apply transformations to this connector

        Args:
            transform: Either a single transformation or a list of transformations
                which will be applied
        """
        if isinstance(transform, solid.rotate):
            return self.rotate(transform)
        elif isinstance(transform, solid.translate):
            return self.translate(transform)
        elif isinstance(transform, solid.scale):
            return self.scale(transform)
        else:
            return functools.reduce(
                lambda connector, transformation: connector.transform(transformation),
                transform,
                self,
            )

    def align(self, other: "Connector" = None) -> typing.Iterator[Transformation]:
        """Emit the transformations necessary to align this connector with another

        Args:
            other: The other connector; if not supplied, it defaults to the
                default connector (see the initializer)

        Yields:
            The necessary transformations for alignment
        """
        if other is None:
            other = self.from_vectors()

        working_connector = self.copy()

        # Cancel axis alignment, if necessary
        if working_connector.axis != other.axis:
            angle, axis = working_connector.axis.alignment_rotation_parameters(
                other.axis
            )

            transformation = solid.rotate(a=-angle, v=axis.raw)
            working_connector = working_connector.transform(transformation)
            yield transformation

        # Cancel roll, if necessary
        if working_connector.normal != other.normal:
            angle, axis = working_connector.normal.alignment_rotation_parameters(
                other.normal
            )

            transformation = solid.rotate(a=-angle, v=axis.raw)
            working_connector = working_connector.transform(transformation)
            yield transformation

        # Move to the origin, if necessary
        if working_connector.point != other.point:
            transformation = solid.translate(
                (-(working_connector.point - other.point)).raw
            )
            working_connector = working_connector.transform(transformation)
            yield transformation

    def __repr__(self) -> str:
        return f"{{{self.point}; {self.axis}; {self.normal}}}"

    def __eq__(self, other: object) -> bool:
        """Is this connector equal to another?

        Args:
            other: The other connector

        Raises:
            NotImplementedError: If the other object is not a connector
        """
        if not isinstance(other, Connector):
            raise NotImplementedError

        return (
            self.point == other.point
            and self.axis == other.axis
            and self.normal == other.normal
        )
