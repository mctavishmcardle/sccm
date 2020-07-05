import typing

from sccm import affinables


class ReparentException(Exception):
    """Raised when we attempt to assign a parent to a child that already has one"""

    def __init__(self, child: "Component", parent: "Component") -> None:
        self.child = child
        self.parent = parent


class Component(affinables.HistoricalTransformable):
    """A component part

    Components form the basic structure of an `sccm` design: they can represent
    both atomic, physical parts & assemblies of those parts which are transformed
    together.
    """

    def __init__(
        self, parent: "Component" = None, children: typing.List["Component"] = None
    ) -> None:
        """
        Args:
            parent: The component's parent, if any; this component will be set
                as one of the parent's children
            children: The component's children, if any; this component will be
                set as the children's parent
        """
        # The transformations that affect this component & its children, but not
        # its parents
        self.direct_transformations: typing.List[affinables.AffineTransformation] = []

        self._parent: typing.Optional["Component"] = None
        if parent:
            self.parent = parent

        self.children: typing.List["Component"] = []
        if children is not None:
            for child in children:
                self.add_child(child)

    def add_child(self, child: "Component") -> None:
        """Make a component this component's child

        Args:
            child: The child to add
        """
        self.children.append(child)

        if child.parent is not self:
            child.parent = self

    @property
    def parent(self) -> typing.Optional["Component"]:
        """This component's parent"""
        return self._parent

    @parent.setter
    def parent(self, parent: "Component") -> None:
        """Assign a parent to the component

        Args:
            parent: The parent to assign

        Raises:
            ReparentException:
                If this component already has a parent
        """
        if self.parent and self.parent is not parent:
            raise ReparentException(self, parent)

        self._parent = parent
        if self not in parent.children:
            parent.add_child(self)

    @property
    def parents(self) -> typing.Iterator["Component"]:
        """The parents of this component, if any, in ascending order of closeness

        The component's direct parent (if any) will be yielded first, then that
        component's parent, and so on.
        """
        if self.parent:
            yield self.parent
            yield from self.parent.parents

    @property
    def transformations(self) -> typing.Iterator[affinables.AffineTransformation]:
        """All of the transformations applied to this component

        Note:
            This includes the transformations applied to all parents and also
            those applied directly to this component
        """
        yield from self.direct_transformations

        if self.parent:
            yield from self.parent.transformations

    def _transform(self, transform: affinables.AffineTransformation) -> "Component":
        """Apply a transformation to this object

        Args:
            transform: The transformation to apply

        Returns:
            This object, appropriately transformed
        """
        self.direct_transformations.append(transform)

        return self

    def same_children(self, other: "Component") -> bool:
        """Does this component have the same children as another?

        This allows the comparison of children without respect to order

        Args:
            other: The other component, to whose children this component's
                children should be compared
        """

        return len(self.children) == len(other.children) and all(
            child in other.children for child in self.children
        )

    def __eq__(self, other: object) -> bool:
        """Is this component equal to enother object?

        Parenthood per se is not taken into account, but transformations
        (both direct & inherited from parents) are (by virtue of parent
        class equality); children are considered 'part' of the component,
        and so are compared.

        Essentially: two components are equal if their bodies would be
        identical, except when their transformations are equivalent but
        different.
        """
        return (
            super().__eq__(other)
            and isinstance(other, Component)
            and self.same_children(other)
        )

    @property
    def _copy(self) -> "Component":
        """Create a new, orphan copy of this component

        This should include important parameters and any children fulfilling
        specific roles (if e.g. a child is associated with a named property
        of the component, it should probably be copied here).
        """
        return self.__class__()

    def copy(self, isolate: bool = False) -> "Component":
        """Copy this component, optionally with family relationships

        Args:
            isolate: Should this copy be created without the parent & child
                relationships that the original has?
        """
        copy = self._copy

        # Only make the copy a child of this object's parent if we aren't
        # isolating (and this object has a parent in the first place)
        if self.parent and not isolate:
            copy.parent = self.parent

        # All children are copied
        for child in self.children:
            # Chidren fulfilling specific roles in the component should be
            # copied by `_copy`, so they shouldn't be copied here
            if child not in copy.children:
                # Isolate & then reparent them
                copy.add_child(child.copy(isolate=True))

        # Copies should have identical direct transformations
        for transformation in self.direct_transformations:
            copy.transform(transformation)

        return copy
