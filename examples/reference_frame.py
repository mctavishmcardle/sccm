"""An example script demonstrating the visualization of connectors

When run, renders the model into `OpenSCAD` source in `reference_frame.scad`

The source file can be explored interactively, or rendered to an image with:

    openscad \
        --imgsize 540,360 \
        --camera 5,0,1,45,0,-45,30 \
        --colorscheme Starnight \
        --view axes,scales \
        --projection o \
        --preview \
        -o reference_frame.png \
        reference_frame.scad
"""
import solid
import solid.utils

from sccm.components.component import Component
from sccm.components.cylinder import Cylinder
from sccm.components.reference_frame import ReferenceFrame

# A reference frame is a visualization of a connector, and this one will visualize
# the 'default', untransformed connector, and thus will be aligned with the regular
# axes of the `OpenSCAD` coordinate system
universal_rf = ReferenceFrame()

# Construct a cylinder & transform it away from and out of alignment with the origin
cylinder = Cylinder(diameter=2, height=5, color=(1.0, 1.0, 1.0, 0.5))
# Tip the cylinder on its side
cylinder.transform(solid.rotate([0.0, 90.0, 0.0]))
# Rotate it 45 degrees about its central axis
cylinder.transform(solid.rotate([45.0, 0.0, 0.0]))
# Scoot it along X
cylinder.transform(solid.utils.right(5))

# Cylinders (& other components) expose connectors (conventionally called 'anchors')
# at useful positions; these connectors are transformed along with the parent
# components, so they can be
cylinder_top_rf = ReferenceFrame.from_connector(cylinder.top_anchor)
cylinder_bottom_rf = ReferenceFrame.from_connector(cylinder.bottom_anchor)

if __name__ == "__main__":
    # Construct a container so we can easily render the whole scene
    Component(
        children=[universal_rf, cylinder_top_rf, cylinder_bottom_rf, cylinder]
    ).compile("reference_frame.scad", 15)
