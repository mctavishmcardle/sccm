"""An example script that generates a model of a pin spanner

The issue with this example is that while it makes a workable solid model of the
entire assembly, the individual components are not completely usable for the
purposes of machining: specifically, the spanner body is, at the end of the
construction process, still a solid cylinder, rather than one with holes for the
insertion of the pins & handle.

When run, renders the model into `OpenSCAD` source in `Spanner.scad`

The source file can be explored interactively, or rendered to an image with:

    openscad \
        --imgsize 540,540 \
        --camera 0,0,0.45,245,0,135,5 \
        --colorscheme Nature \
        --view axes,scales \
        --projection o \
        --render \
        -o Spanner.png \
        Spanner.scad
"""

import solid
import solid.utils

from sccm.components.component import Component
from sccm.components.cylinder import Cylinder

# Parent component for the whole thing
wrench = Component()

# The main 'body' of the wrench, to which the other things attach
spanner_body = Cylinder(od=3 / 4, length=1.0, parent=wrench)

# The handle of the wrench
handle = Cylinder(od=1 / 4, length=1.5, center=True, parent=wrench)
handle_rotation = solid.rotate([90.0, 0.0, 0.0])
handle.transform(handle_rotation)
handle.transform(
    # The center anchor has to be transformed first, in the same manner as the
    # whole handle was, so the alignment works correctly - otherwise, the primary
    # alignment axis of the center anchor, which is parallel to the axis of the
    # cylinder, would be aligned with that of the body's top anchor (ditto)
    handle.center_anchor.transform(handle_rotation).align(spanner_body.top_anchor)
)
handle.transform(solid.utils.down(3 / 8))
# Subtract the space occupied by the handle from the body
spanner_body.compose(solid.difference(), handle, make_children=False)

# The pin that actually engages in the hole in the nut (which this wrench is
# designed to turn) is made from a 1/8" pin, but the part that engages in the
# hole must be turned down to fit the hole's size
protruding_pin = Cylinder(od=0.110, length=0.1)
inside_pin = Cylinder(od=1 / 8, length=3 / 8)

inside_pin.transform(inside_pin.bottom_anchor.align(spanner_body.bottom_anchor))
protruding_pin.transform(protruding_pin.top_anchor.align(inside_pin.bottom_anchor))


# There are two pins in the nut, so we make an assembly & then clone it
pin_assembly_a = protruding_pin.compose(solid.union(), inside_pin, inplace=False)
pin_assembly_b = pin_assembly_a.copy()

# The holes in the nut are .472" (12mm) apart, so the pins are located half that
# distance on either side of the body's axis
pin_assembly_a.transform(solid.utils.left(0.472 / 2))
pin_assembly_b.transform(solid.utils.right(0.472 / 2))
pin_assemblies = [pin_assembly_a, pin_assembly_b]

# Subtract the space occupied by the pins from the body
spanner_body.compose(solid.difference(), pin_assemblies, make_children=False)
wrench.add_child(pin_assemblies)

wrench.compile("Spanner.scad", 15)
