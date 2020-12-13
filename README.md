# Status

This project is no longer under active development: I've discovered `cadquery`,
which is sufficient for my purposes.

# `sccm`: Solid Component (& Constraint\*) Modeling
> \* (constraint-based modeling coming before version `1.0`)

`sccm` is a `python` toolkit for solid modelling CAD - it aims to replicate a
workflow similar to one familiar to users of `Fusion 360` (in some ways) while
leveraging the flexibility & power of source-code-based object definition. It
uses `OpenSCAD` as its rendering and interactive engine: objects in `sccm` can
be rendered to `OpenSCAD` code, which itself can be rendered visually or explored
interactively.

<p align="center">
    <img
        src="examples/pin_spanner.png"
        alt="Example pin spanner model rendering"
    >
</p>

# Example models

Example models, `OpenSCAD` source files, and rendered images are stored in the
`examples/` directory; each set of associated files shares the same base name:
* the `<model>.py` file contains the `sccm` source code for that model
* the `<model>.scad` contains the to "compiled" `OpenSCAD` source of that model,
  which can be regenerated by executing the source file
* the `<model>.png` file contains an image generated by rendering the compiled
  `OpenSCAD` source, which can be regenerated by executing the command provided
  in the `sccm` source file's module-level docstring.

# Versions

Releases commits are tagged with their appropriate semantic version.

# Development

This project uses `pipenv` for managing the development environment, and
`pre-commit` to ensure code standards are met. Branches should be squashed before
being merged into the `master` branch.
