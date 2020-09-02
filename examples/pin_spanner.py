"""An example script that generates a model of a pin spanner

The issue with this example is that while it makes a workable solid model of the
entire assembly, the individual components are not completely usable for the
purposes of machining: specifically, the spanner body is, at the end of the
construction process, still a solid cylinder, rather than one with holes for the
insertion of the pins & handle.

When run, renders the model into `OpenSCAD` source in `pin_spanner.scad`

The source file can be explored interactively, or rendered to an image with:

    openscad \
        --imgsize 540,540 \
        --camera 0,0,0.45,245,0,135,5 \
        --colorscheme Nature \
        --view axes,scales \
        --projection o \
        --preview \
        -o pin_spanner.png \
        pin_spanner.scad
"""

import solid
import solid.utils

from sccm.components.component import Component
from sccm.components.cylinder import Cylinder

# The main 'body' of the spanner, to which the other things attach; this is
# made out of a stubby cylinder of aluminum
spanner_body = Cylinder(
    od=3 / 4,
    length=1.0,
    # We want to be able to see the other parts embedded inside the body, so it
    # should be transparent
    color=(1.0, 0.0, 0.0, 0.8),
)

# The handle of the spanner, for which we'll just use a 1/4" dowel pin
handle = Cylinder(
    od=1 / 4,
    length=1.5,
    # Cylinders are created with their height axis along Z; since we need to
    # rotate the handle so it's perpendicular to the handle, it's most
    # convenient to "center" it, so its center point is at the origin, rather
    # than the default, which puts its bottom at the origin
    center=True,
    # We want the handle to be fully opaque, so we can omit the optional alpha
    color=(0.0, 0.0, 1.0),
)

# We need to position the handle inside the body; first, rotate it about X, so
# it's perpendicular to the handle
handle_rotation = solid.rotate([90.0, 0.0, 0.0])
handle.transform(handle_rotation)
# Then, we need to move it, so it's in the same orientation but sitting at the
# top of the body
handle.transform(
    # The center anchor has to be transformed first, in the same manner as the
    # whole handle was, so the alignment works correctly - otherwise, the primary
    # alignment axis of the center anchor, which is parallel to the axis of the
    # cylinder, would be aligned with that of the body's top anchor (ditto)
    handle.center_anchor.transform(handle_rotation).align(spanner_body.top_anchor)
)
# From there, we can move it down 3/8", so it's captured inside the body
handle.transform(solid.utils.down(3 / 8))
# Subtract the space occupied by the handle from the body
spanner_body.compose(solid.difference(), handle, make_children=False)

# The pin that actually engages in the hole in the nut (which this spanner is
# designed to turn) is made from a 1/8" pin, but the part that engages in the
# hole must be turned down to fit the hole's size
protruding_pin = Cylinder(od=0.110, length=0.1)
# The "inside" pin is the unmodified portion that sits inside the spanner body
inside_pin = Cylinder(od=1 / 8, length=3 / 8)
# Then, we need to align the two portions of the pin model, such that
protruding_pin.transform(protruding_pin.top_anchor.align(inside_pin.bottom_anchor))

# There are two pins in the nut, so we make an assembly & then clone it
pin_assembly_a = protruding_pin.compose(solid.union(), inside_pin, inplace=False)
# Then, move the whole assembly such that the bottom of the inside pin is aligned
# with the bottom of the spanner body. Note that while the two portions of the pin
# have been composed into a single component, the individual portions exist, and
# we still have access to them.
pin_assembly_a.transform(inside_pin.bottom_anchor.align(spanner_body.bottom_anchor))
# Not-in-place composition produces a new component (here, the pin assembly),
# so we have to assign the desired color to it after instantiation; it will be
# assigned to the other pin assembly during the copy operation by default
pin_assembly_a.color = (0.0, 1.0, 0.0)
pin_assembly_b = pin_assembly_a.copy()

# The holes in the nut are .472" (12mm) apart, so the pins are located half that
# distance on either side of the body's axis
pin_assembly_a.transform(solid.utils.left(0.472 / 2))
pin_assembly_b.transform(solid.utils.right(0.472 / 2))
pin_assemblies = [pin_assembly_a, pin_assembly_b]

# Subtract the space occupied by the pins from the body
spanner_body.compose(solid.difference(), pin_assemblies, make_children=False)

# Now, we need a parent component for the whole spanner, so we can render it.
pin_spanner = Component(
    # Ordering is actually significant here because of a quirk in `OpenSCAD`: if
    # we want an object "inside" another, transparent object to be visible, it
    # has to be drawn first. Because rendering a pure container (a component that
    # only contains other components, and doesn't define a body of its own)
    # automatically creates a `union` of the contained child components, with the
    # children listed in order of their appearance in the container's `children`
    # list, the order we specify these children here directly maps to the order
    # with which they'll be drawn. Because the spanner body is transparent and
    # we want to see the driving pins & handle through it, it has to be last.
    children=[*pin_assemblies, handle, spanner_body]
)

if __name__ == "__main__":
    pin_spanner.compile("pin_spanner.scad", 15)
