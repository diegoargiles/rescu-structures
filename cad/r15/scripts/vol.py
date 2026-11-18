from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
def pvol(shape):
    w = shape.wrapped if hasattr(shape, 'wrapped') else shape
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(w, g, 1e-5); return g.Mass()
