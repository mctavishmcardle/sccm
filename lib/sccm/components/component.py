import functools
import itertools
import typing

import solid

from sccm import affinables

Composition = typing.Union[solid.union, solid.difference, solid.intersection]
CompositionAndOperands = typing.Tuple[Composition, typing.List["Component"]]


class ReparentException(Exception):
    """Raised when we attempt to assign a parent to a child that already has one"""

    def __init__(self, child: "Component", parent: "Component") -> None:
        self.child = child
        self.parent = parent


class DisembodiedComponent(Exception):
    """Raised when a body cannot be constructed for a component"""

    def __init__(self, component: "Component") -> None:
        """
        Args:
            component: The disembodied component
        """
        self.component = component


class Component(affinables.HistoricalTransformable):
    """A component part

    Components form the basic structure of an `sccm` design: they can represent
    both atomic, physical parts & assemblies of those parts which are transformed
    together.
    """

    def __init__(
        self,
        parent: "Component" = None,
        children: typing.List["Component"] = None,
        compositions: typing.List[CompositionAndOperands] = None,
    ) -> None:
        """
        Args:
            parent: The component's parent, if any; this component will be set
                as one of the parent's children
            children: The component's children, if any; this component will be
                set as the children's parent
            compositions: The component's compositions, if any
        """
        # The transformations that affect this component & its children, but not
        # its parents
        self.direct_transformations: typing.List[affinables.AffineTransformation] = []

        self._parent: typing.Optional["Component"] = None
        self.children: typing.List["Component"] = []

        if parent:
            self.parent = parent

        if children is not None:
            for child in children:
                self.add_child(child)

        self.compositions: typing.List[CompositionAndOperands] = []
        if compositions:
            self.compositions = compositions

    def add_child(
        self, children: typing.Union["Component", typing.List["Component"]]
    ) -> None:
        """Make one or more components this component's child

        Args:
            children: The child or children to add
        """
        if isinstance(children, list):
            for child in children:
                self.add_child(child)
        else:
            child = children

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
        if not any(self is child for child in parent.children):
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

    def same_compositions(self, other: "Component") -> bool:
        """Does this component have the same compositions as another?

        This allows the comparison of compositions without respect to operand
        order

        Args:
            other: The other component, to whose compositions this component's
                compositions should be compared
        """
        return all(
            # Composition instances, like all OpenSCAD objects, are
            # non-comparable, but their types are
            type(self_composition) == type(other_composition)
            and len(self_operands) == len(other_operands)
            and all(operand in other_operands for operand in self_operands)
            for (self_composition, self_operands), (
                other_composition,
                other_operands,
            ) in zip(self.compositions, other.compositions)
        )

    def __eq__(self, other: object) -> bool:
        """Is this component equal to another object?

        Parenthood per se is not taken into account, but transformations
        (both direct & inherited from parents) are (by virtue of parent
        class equality); children are considered 'part' of the component,
        and so are compared, as are compositions

        Essentially: two components are equal if their bodies would be
        identical, except when their transformations are equivalent but
        different (e.g. a 10x scale followed by a 2x scale, which would not be
        considered equal to a 2x scale compared to a 10x scale)
        """
        return (
            super().__eq__(other)
            and isinstance(other, Component)
            and self.same_children(other)
            and self.same_compositions(other)
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
        """Copy this component

        Args:
            isolate: If true, the copied component will not retain the parent
                relationships of the original
        """
        copy = self._copy

        # Only make the copy a child of this object's parent if we aren't
        # isolating (and this object has a parent in the first place)
        if self.parent and not isolate:
            copy.parent = self.parent

        # Copy components involved in composition
        for composition, operands in self.compositions:
            copied_child_operands = []
            all_operands = []

            # Operands that are children must be copied to avoid reparenting
            for operand in operands:
                if operand in self.children:
                    operand = operand.copy(isolate=True)
                    copied_child_operands.append(operand)
                elif isolate:
                    operand = operand.copy(isolate=True)

                all_operands.append(operand)

            copy.compose(
                composition,
                all_operands,
                # To avoid double-copying child operands, we have to do the copy
                # manually, above
                copy=False,
                inplace=True,
                # Since some operands might not be children, we have to parent
                # the copied children on their own, after the composition
                make_children=False,
            )

            for copied_child_operand in copied_child_operands:
                copy.add_child(copied_child_operand)

        # All children are copied, because we can't reparent
        for child in self.uncomposed_children:
            # Children fulfilling specific roles in the component should be
            # copied by `_copy`, so they shouldn't be copied here
            if child not in copy.children:
                # Isolate & then reparent them
                copy.add_child(child.copy(isolate=True))

        # Copies should have identical direct transformations
        for transformation in self.direct_transformations:
            copy.transform(transformation)

        return copy

    def compose(
        self,
        composition: Composition,
        operands: typing.Union["Component", typing.List["Component"]],
        copy: bool = False,
        inplace: bool = True,
        make_children: bool = True,
    ) -> "Component":
        """Compose this component with one or more other components

        Args:
            composition: The type of composition to apply
            operands: The component or components to compose with
            copy: If true, the operands will be copied in isolation before the
                composition is applied
            inplace: If true, the composition will be applied to this component;
                otherwise, a new component will be constructed with the
                components being composed as children
            make_children: Should the components involved in the composition be
                made children of the result component?

        Returns:
            The 'parent' of the composition: either this component, if the
            composition is performed in place, or a newly-constructed component
            if not
        """
        if not isinstance(operands, list):
            operands = [operands]

        if copy:
            operands = [operand.copy(isolate=True) for operand in operands]

        if inplace:
            self.compositions.append((composition, operands))
            component = self
            children = operands
        else:
            # This object is only copied (conditionally) if the composition is
            # not in place; otherwise, it wouldn't be an in-place composition,
            # since the result object would be distinct from this one.
            operands += [self.copy(isolate=True) if copy else self]
            component = Component(compositions=[(composition, operands)])
            children = operands

        if make_children:
            component.add_child(
                [child for child in children if child not in component.children]
            )

        return component

    @property
    def composed_components(self) -> typing.Iterator["Component"]:
        """All of the operand components composed with this component"""
        if self.compositions:
            operands = tuple(zip(*self.compositions))[1]
        else:
            operands = []

        yield from itertools.chain(*operands)

    @property
    def uncomposed_children(self) -> typing.Iterator["Component"]:
        """All of the children of this component not composed with it"""
        composed_components = list(self.composed_components)
        for child in self.children:
            if child not in composed_components:
                yield child

    @property
    def _body(self) -> typing.Optional[solid.OpenSCADObject]:
        """The transformed object that embodies the base of this component

        This should not include any components that are included in compositions
        """
        uncomposed_children = list(self.uncomposed_children)

        if uncomposed_children:
            return solid.union()([child.body for child in uncomposed_children])
        else:
            return None

    @staticmethod
    def _apply_composition(
        composition: Composition, operands: typing.List[solid.OpenSCADObject]
    ) -> solid.OpenSCADObject:
        """Apply a composition to a set of operands

        Args:
            composition: The composition to apply
            operands: The operands to apply the composition to

        Returns:
            The object that results from applying the composition to the operands
        """
        # The composition must be copied first because application mutates the
        # composition object
        return composition.copy()(operands)

    @property
    def body(self) -> solid.OpenSCADObject:
        """The fully transformed object that embodies this component

        Raises:
            DisembodiedComponent:
                If this component cannot be rendered as a body
        """
        body_reduction = functools.partial(
            functools.reduce,
            lambda body, composition_and_operands: self._apply_composition(
                composition_and_operands[0],
                [body] + [operand.body for operand in composition_and_operands[1]],
            ),
        )

        if self._body:
            return body_reduction(self.compositions, self._body)
        else:
            if not self.compositions:
                raise DisembodiedComponent(self)

            # If this component is a pure container (without a defined `_body`),
            # we must extract an initial body to compose onto from the first
            # composition & its operands - otherwise, there would be nothing at
            # the "root" of the compositions
            first_composition, first_operands = self.compositions[0]
            return body_reduction(
                self.compositions[1:],
                self._apply_composition(
                    first_composition, [operand.body for operand in first_operands]
                ),
            )

    def scad_source(self, fn: int = None) -> str:  # pragma: no cover
        """The OpenSCAD source code that this component corresponds to"""
        header = ""
        if fn:
            header = f"$fn = {fn};"

        return solid.scad_render(self.body, header)

    def compile(self, filename: str = None, fn: int = None) -> None:  # pragma: no cover
        """Write OpenSCAD source corresponding to this component

        Args:
            filename: The path to which to write the file; if not provided, the
                file will be written to the working directory & given the same
                name as this class
            fn: The number of facets to render curved surfaces with; if not
                provided, the `OpenSCAD` default will be used
        """
        if filename is None:
            filename = f"{self.__class__.__name__}.scad"

        with open(filename, "w") as file_contents:
            file_contents.write(self.scad_source(fn))
