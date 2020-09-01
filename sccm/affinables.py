import abc
import functools
import itertools
import typing

import solid

# The subset of OpenSCAD transformations which are linear & which we support
AffineTransformation = typing.Union[solid.translate, solid.rotate, solid.scale]

GenericAffinable = typing.TypeVar("GenericAffinable", bound="Affinable")


class Affinable(abc.ABC):
    """An object capable of undergoing affine OpenSCAD transformations"""

    def transform(
        self: GenericAffinable,
        transform: typing.Union[
            AffineTransformation, typing.Iterable[AffineTransformation]
        ],
    ) -> GenericAffinable:
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
    def _transform(
        self: GenericAffinable, transform: AffineTransformation
    ) -> GenericAffinable:
        """Apply a transformation to this object

        Args:
            transform: The transformation to apply

        Returns:
            This object, appropriately transformed
        """

    def __eq__(self, other: object) -> bool:
        """Is this object equal to another object?"""
        return isinstance(other, Affinable)

    @staticmethod
    def _same_transformations(
        left_transformations: typing.Iterable[AffineTransformation],
        right_transformations: typing.Iterable[AffineTransformation],
    ) -> bool:
        """Are these two lists of transformations equivalent?

        Args:
            left_transformations: One of the two lists of transformations to
                compare
            right_transformations: The other list of transformations to compare
        """
        return all(
            # Transformations instances, like all OpenSCAD objects, are
            # non-comparable, but we can compare their types and their
            # parameters to determine equivalency
            type(self_transform) == type(other_transform)
            and self_transform.params == other_transform.params
            for self_transform, other_transform in itertools.zip_longest(
                left_transformations, right_transformations
            )
        )


# Objects to which affine transformations can be applied
AffineTransformable = typing.Union[GenericAffinable, solid.OpenSCADObject]

GenericHolonomicTransformable = typing.TypeVar(
    "GenericHolonomicTransformable", bound="HolonomicTransformable"
)


class HolonomicTransformable(Affinable, abc.ABC):
    """A transformable object which doesn't keep track of its history"""

    def _transform(
        self: GenericHolonomicTransformable, transform: AffineTransformation
    ) -> GenericHolonomicTransformable:
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
    def rotate(
        self: GenericHolonomicTransformable, rotation: solid.rotate
    ) -> GenericHolonomicTransformable:
        """Transform this object to account for a rotation

        Args:
            rotation: The rotation
        """

    @abc.abstractmethod
    def translate(
        self: GenericHolonomicTransformable, translation: solid.translate
    ) -> GenericHolonomicTransformable:
        """Transform this object to account for a translation

        Args:
            translation: The translation
        """

    @abc.abstractmethod
    def scale(
        self: GenericHolonomicTransformable, scaling: solid.scale
    ) -> GenericHolonomicTransformable:
        """Transform this object to account for a scaling

        Args:
            scaling: The scaling
        """


GenericHistoricalTransformable = typing.TypeVar(
    "GenericHistoricalTransformable", bound="HistoricalTransformable"
)

HistoricalTransformablePropertyMethod = typing.Callable[
    [GenericHistoricalTransformable], AffineTransformable
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
    def transformed_property(
        object_property: HistoricalTransformablePropertyMethod
    ) -> AffineTransformable:
        """Decorate transformable properties so they transform in sync

        The result property will have all of the parent transformable's
        transformations automatically applied to it, when called.

        Note:
            The `property` decoration is applied within this decorator, so it
            should not be applied independently to target methods.
        """
        # `mypy` cannot properly check decorated properties
        @property  # type: ignore
        @functools.wraps(object_property)
        def transformed_property(
            self: GenericHistoricalTransformable
        ) -> AffineTransformable:
            return self.transformed(object_property(self))

        return transformed_property

    def same_transformations(
        self: GenericHistoricalTransformable, other: GenericHistoricalTransformable
    ) -> bool:
        """Does this component have the same transformations as another?

        Args:
            other: The other component, to whose transformations this component's
                transformations should be compared
        """
        return self._same_transformations(self.transformations, other.transformations)

    def __eq__(self, other: object) -> bool:
        """Is this object equal to another object?"""
        return (
            super().__eq__(other)
            and isinstance(other, HistoricalTransformable)
            and self.same_transformations(other)
        )
