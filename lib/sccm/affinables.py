import abc
import functools
import itertools
import typing

import solid

# The subset of OpenSCAD transformations which are linear & which we support
AffineTransformation = typing.Union[solid.translate, solid.rotate, solid.scale]


class Affinable(abc.ABC):
    """An object capable of undergoing affine OpenSCAD transformations"""

    def transform(
        self,
        transform: typing.Union[
            AffineTransformation, typing.Iterable[AffineTransformation]
        ],
    ) -> "Affinable":
        """Apply an affine transformations to this object

        Args:
            transform: One or more transformations to be applied

        Returns:
            The transformed object
        """
        try:
            return functools.reduce(
                lambda connector, transformation: connector._transform(transformation),
                transform,
                self,
            )
        # `reduce` raises a type error if the second argument isn't iterable
        except TypeError:
            return self._transform(transform)

    @abc.abstractmethod
    def _transform(self, transform: AffineTransformation) -> "Affinable":
        """Apply a transformation to this object

        Args:
            transform: The transformation to apply

        Returns:
            This object, appropriately transformed
        """

    def __eq__(self, other: object) -> bool:
        """Is this object equal to another object?"""
        return isinstance(other, Affinable)


# Objects to which affine transformations can be applied
AffineTransformable = typing.Union[Affinable, solid.OpenSCADObject]


class HolonomicTransformable(Affinable, abc.ABC):
    """A transformable object which doesn't keep track of its history"""

    def _transform(self, transform: AffineTransformation) -> "HolonomicTransformable":
        """Apply an affine transformation to this object

        Args:
            transform: One or more transformations to be applied

        Returns:
            The transformed object

        Raises:
            NotImplementedError:
                If the transformation isn't of a supported type
        """
        if isinstance(transform, solid.rotate):
            return self.rotate(transform)
        elif isinstance(transform, solid.translate):
            return self.translate(transform)
        elif isinstance(transform, solid.scale):
            return self.scale(transform)
        else:
            raise NotImplementedError

    @abc.abstractmethod
    def rotate(self, rotation: solid.rotate) -> "HolonomicTransformable":
        """Transform this object to account for a rotation

        Args:
            rotation: The rotation
        """

    @abc.abstractmethod
    def translate(self, translation: solid.translate) -> "HolonomicTransformable":
        """Transform this object to account for a translation

        Args:
            translation: The translation
        """

    @abc.abstractmethod
    def scale(self, scaling: solid.scale) -> "HolonomicTransformable":
        """Transform this object to account for a scaling

        Args:
            scaling: The scaling
        """


HistoricalAffinablePropertyMethod = typing.Callable[
    ["HistoricalTransformable"], AffineTransformable
]


class HistoricalTransformable(Affinable, abc.ABC):
    """A transformable object which keeps track of its history"""

    @property
    @abc.abstractmethod
    def transformations(self) -> typing.Iterator[AffineTransformation]:
        """All of the transformations which have been applied to this object"""

    def transformed(self, target: AffineTransformable) -> AffineTransformable:
        """Apply this object's transformations to another object

        Args:
            target: The object to be transformed

        Returns:
            The transformed object
        """
        if isinstance(target, Affinable):
            return target.transform(self.transformations)
        else:
            return functools.reduce(
                lambda openscad_object, transformation: transformation.copy()(
                    openscad_object
                ),
                self.transformations,
                target,
            )

    @staticmethod
    def transformed_object(
        object_property: HistoricalAffinablePropertyMethod
    ) -> HistoricalAffinablePropertyMethod:
        """Decorate transformable properties so they transform in sync

        The result property will have all of the parent transformable's
        transformations automatically applied to it, when called.

        Note:
            This decorator should be applied below `@property`:

                @property
                @HistoricalTransformable.transformed_object
                def object_property(self) -> AffineTransformable:
                    ...
        """

        @functools.wraps(object_property)
        def transformed_property(self) -> AffineTransformable:
            return self.transformed(object_property(self))

        return transformed_property

    def __eq__(self, other: object) -> bool:
        """Is this object equal to another object?"""
        return (
            super().__eq__(other)
            and isinstance(other, HistoricalTransformable)
            and all(
                self_transform == other_transform
                for self_transform, other_transform in itertools.zip_longest(
                    self.transformations, other.transformations
                )
            )
        )
