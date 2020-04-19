import functools
import math
import typing

import numpy
import vg

NumpyVector = typing.Type[numpy.array]
RawVector = typing.Union[typing.Tuple[float, float, float], typing.Sequence[float]]


class NaNVector(Exception):
    """Raised when a vector is with a NaN magnitude"""

    def __init__(self, components: NumpyVector) -> None:
        """
        Args:
            components: The components of the problematic vector
        """
        self.components = components


class UndefinedNormal(Exception):
    """Raised when no normal can be found for a pair of vectors"""

    def __init__(self, left: "Vector", right: "Vector") -> None:
        """
        Args:
            left: The 'left' vector in the normal calculation; this should be
                the vector on which the `normal` method was called
            right: The 'right' vector in the normal calculation; this should be
                the vector that was passed into the `normal` method

        """
        self.left = left
        self.right = right


class NoNormalForNulls(UndefinedNormal):
    """Raised if a normal to a 0-magnitude vector is sought"""

    def __init__(self, null_vector: "Vector", other_vector: "Vector") -> None:
        """
        Args:
            null_vector: The 0-magnitude vector in the normal calculation
            other_vector: The other vector in the normal calculation
        """

        self.null_vector = null_vector
        self.other_vector = other_vector

        super().__init__(self.null_vector, self.other_vector)


class NoNormalForColineals(UndefinedNormal):
    """Raised if two vectors have alignment such that that normal is undefined"""

    pass


class NoNormalForParallels(NoNormalForColineals):
    """Raised if a normal for two parallel vectors is sought"""

    pass


class NoNormalForAntiparallels(NoNormalForColineals):
    """Raised if a normal for two antiparallel vectors is sought"""

    pass


class NoArbitraryNormal(Exception):
    """Raised when no arbitrary normal can be found for a vector"""

    def __init__(self, vector: "Vector") -> None:
        """
        Args:
            vector: The vector for which we cannot find an arbitrary normal
        """
        self.vector = vector


@functools.total_ordering
class Vector:
    """A 3-dimensional vector"""

    def __init__(self, components: NumpyVector = numpy.zeros(3)):
        """
        Args:
            components: The components of the vector

        Raises:
            NaNVector: If the magnitude of the resulting vector would be
                undefined
        """
        self.array = components.astype(float)

        if math.isnan(self.magnitude):
            raise NaNVector(self.array)

    @property
    def magnitude(self) -> float:
        """This vector's length"""
        if (self.x == 0) and (self.y == 0) and (self.z == 0):
            return 0.0

        return vg.magnitude(self.array)

    @classmethod
    def from_components(cls, components: NumpyVector) -> "Vector":
        """Construct a vector from components

        Args:
            components: The components of the vector
        """
        return cls(components)

    @classmethod
    def from_raw(cls, raw: RawVector) -> "Vector":
        """Construct a vector from an iterable of values

        Args:
            raw: The three vector components
        """
        if not isinstance(raw, tuple):
            raw = (raw[0], raw[1], raw[2])

        return cls.from_components(numpy.array(raw))

    @property
    def raw(self) -> RawVector:
        """Get the 'raw' version of the vector"""
        return (self.array[0], self.array[1], self.array[2])

    def normal(self, other: "Vector") -> "Vector":
        """Compute the vector normal to this vector & another vector

        Note:
            This is equivalent to computing the normalized cross product
            between this vector & the other vector, and so is anticommutative.

        Args:
            other: The vector with respect to which to compute the normal

        Raises:
            NoNormalForParallels: If the input vectors are parallel
            NoNormalForAntiparallels: If the input vectors are antiparallel
            NoNormalForNulls: If one of the vectors has 0 magnitude
        """
        try:
            return self.from_components(vg.perpendicular(self.array, other.array))
        except NaNVector:
            if self.magnitude and other.magnitude:
                if self.normalized == other.normalized:
                    raise NoNormalForParallels(self, other)
                else:
                    raise NoNormalForAntiparallels(self, other)
            else:
                raise NoNormalForNulls(min(self, other), max(self, other))

    def rotate(self, angle: float, normal: "Vector") -> "Vector":
        """Rotate through an angle in the plane normal to an given vector

        Args:
            angle: The signed angle through which to rotate this vector
            normal: The normal vector of the plane through which to rotate this
                vector
        """
        return self.from_components(
            vg.rotate(
                self.array,
                angle=angle,
                around_axis=normal.array,
                assume_normalized=True,
            )
        )

    def rotate_to_alignment(self, inclined: "Vector", reference: "Vector") -> "Vector":
        """Rotate the angle it takes to align an given vector with the reference

        The rotation will be in the same 'direction' as that reuqired to align
        the two vectors, and in the plane normal to them.

        Note:
            Swapping the inclined & reference vectors is equivalent to reversing
            the sign of the rotation.

        Note:
            If the vectors to align are antiparallel, this vector's reverse will
            be returned, arbitrarily

        Args:
            inclined: The vector that needs to be rotated to align with the
                reference
            reference: The vector to which the inclined vector will be aligned
        """
        return self.rotate(*self.alignment_rotation_parameters(inclined, reference))

    def alignment_rotation_parameters(
        self, inclined: "Vector", reference: "Vector" = None
    ) -> typing.Tuple[float, "Vector"]:
        """Get the angle and rotation axis an alignment rotation

        See `rotate_to_alignment` for details.

        Args:
            inclined: The vector that needs to be rotated to align with the
                reference
            reference: The vector to which the inclined vector will be aligned;
                if not provided, this vectore will be used as a reference

        Returns:
            The angle through which to rotate and the vector about which to
            rotate
        """
        if reference is None:
            reference = self

        try:
            normal = inclined.normal(reference)
        # If the vectors are either parallel or antiparalle, we have to pick a
        # a different normal
        except NoNormalForColineals:
            try:
                normal = self.normal(reference)
            # If all three vectors are colinear, we have to pick an arbitrary
            # normal
            except NoNormalForColineals:
                normal = self.arbitrary_normal

        return inclined.angle_between(reference, normal), normal

    @property
    def arbitrary_normal(self) -> "Vector":
        """An arbitrary vector normal to this one

        Raises:
            NoArbitraryNormal: If one cannot be found
        """
        for axis in [AXIS_X, AXIS_Y, AXIS_Z]:
            try:
                return self.normal(axis)
            except NoNormalForColineals:
                continue

        raise NoArbitraryNormal(self)

    def angle_between(self, other: "Vector", normal: "Vector" = None) -> float:
        """Get the angle between this vector & another

        This is the angle necessary to rotate this vector into alignment with
        the other vector, about the normal

        Note:
            If the vectors are antiparallel, 180.0 will be arbitrarily returned
            (as -180.0 would be equally correct).

        Args:
            other: The other angle, to which to calculate the angle
            normal: An optional, specified normal; if not privided, the
                cross product between this vector & the other vector will be
                used (which will ensure that the result is positive)
        """
        try:
            return vg.signed_angle(
                self.array, other.array, look=(normal or self.normal(other)).array
            )
        except NoNormalForParallels:
            return 0.0
        except NoNormalForAntiparallels:
            return 180.0

    @property
    def normalized(self) -> "Vector":
        """A vector parallel to this one, with a magnitude of 1.0"""
        return self.from_components(vg.normalize(self.array))

    def __neg__(self) -> "Vector":
        """This vector reflected through the origin"""
        return self.from_components(-self.array)

    def __add__(self, other: "Vector") -> "Vector":
        """Add another vector to this one

        Args:
            other: The other vector which should be added this one
        """
        return self.from_components(self.array + other.array)

    def __sub__(self, other: "Vector") -> "Vector":
        """Subtract another vector from this one

        Args:
            other: The other vector which should be subtracted from this one
        """
        return self + (-other)

    def __mul__(self, other: "Vector") -> "Vector":
        """Element-wise multiplication of this vector by another

        Args:
            other: The other vector, whose elements should be multiplied by
                this vector's elements
        """
        return self.from_components(self.array * other.array)

    def __eq__(self, other: object) -> bool:
        """Is this vector equal to another?

        Args:
            other: The other vector, to check for equality

        Raises:
            NotImplementedError: If the other object is not a vector
        """
        if not isinstance(other, Vector):
            raise NotImplementedError

        return vg.almost_equal(self.array, other.array)

    @property
    def x(self) -> float:
        """The X component of this vector"""
        return self.array[0]

    @property
    def y(self) -> float:
        """The Y component of this vector"""
        return self.array[1]

    @property
    def z(self) -> float:
        """The Z component of this vector"""
        return self.array[2]

    def __repr__(self) -> str:
        return f"<{self.x:.3}, {self.y:.3}, {self.z:.3}>"

    def __lt__(self, other: "Vector") -> bool:
        """Is this vector's magnitude less than another's?

        Args:
            other: The other vector, with which to compare magnitude
        """
        return self.magnitude < other.magnitude


ORIGIN = Vector()
AXIS_X = Vector(vg.basis.x)
AXIS_Y = Vector(vg.basis.y)
AXIS_Z = Vector(vg.basis.z)
