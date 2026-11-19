"""Edit the R16 STEP assembly in place (names, colours, structure kept): swap nose parts, drop superseded REF
placeholders, add Tarot 4008 pusher + REF adapter + APC props. Writes RescU_R16_Full_Aircraft.step (R16.1)."""
import sys, os, pickle, time
import cadquery as cq
from OCP.STEPCAFControl import STEPCAFControl_Reader, STEPCAFControl_Writer
from OCP.STEPControl import STEPControl_AsIs
from OCP.TDocStd import TDocStd_Document
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ShapeTool, XCAFDoc_ColorType, XCAFDoc_ColorTool
from OCP.TDF import TDF_LabelSequence, TDF_Label
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDataStd import TDataStd_Name
from OCP.TopLoc import TopLoc_Location
from OCP.Quantity import Quantity_Color, Quantity_TOC_RGB, Quantity_ColorRGBA
from OCP.Interface import Interface_Static
t0 = time.time()
SRC, DST = sys.argv[1], sys.argv[2]
doc = TDocStd_Document(TCollection_ExtendedString("doc"))
r = STEPCAFControl_Reader(); r.SetNameMode(True); r.SetColorMode(True); r.ReadFile(SRC); r.Transfer(doc)
st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main()); ct = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
print('read', round(time.time()-t0))
def name(l):
    a = TDataStd_Name(); return a.Get().ToExtString() if l.FindAttribute(TDataStd_Name.GetID_s(), a) else '?'

comps = {}   # part name -> (component label, parent assembly label, accumulated location incl. component)
def walk(lab, loc, parent):
    if XCAFDoc_ShapeTool.IsReference_s(lab):
        ref = TDF_Label(); XCAFDoc_ShapeTool.GetReferredShape_s(lab, ref)
        l2 = loc.Multiplied(XCAFDoc_ShapeTool.GetLocation_s(lab))
        if XCAFDoc_ShapeTool.IsAssembly_s(ref): walk(ref, l2, ref)
        else: comps[name(ref)] = (lab, ref, parent, l2)
        return
    if XCAFDoc_ShapeTool.IsAssembly_s(lab):
        cs = TDF_LabelSequence(); XCAFDoc_ShapeTool.GetComponents_s(lab, cs)
        for i in range(1, cs.Length()+1): walk(cs.Value(i), loc, lab)
roots = TDF_LabelSequence(); st.GetFreeShapes(roots)
for i in range(1, roots.Length()+1): walk(roots.Value(i), TopLoc_Location(), roots.Value(i))
print('parts', len(comps))
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
def bake(shape, loc):
    t = loc.Multiplied(shape.Location()).Transformation()
    return BRepBuilderAPI_Transform(shape.Located(TopLoc_Location()), t, True).Shape()
# R16.2: replace by name (new2/ and add2/), add parts that do not exist yet
parent_of = {}
for nm, (lab, ref, par, loc) in comps.items():
    g = next((g for g in ('Fuselage', 'Wing_R', 'Wing_L', 'Boom_R', 'Boom_L', 'VTail_R', 'VTail_L') if nm.endswith('_' + g)), None)
    if g is None:
        g = 'Boom_R' if nm.endswith('Boom_R') else 'Boom_L' if nm.endswith('Boom_L') else None
    if g: parent_of.setdefault(g, (par, loc.Multiplied(XCAFDoc_ShapeTool.GetLocation_s(lab).Inverted())))
COL = {'Root_Block': (0.15, 0.15, 0.16), 'Fairings': (0.92, 0.92, 0.90), 'Pads': (0.82, 0.60, 0.16), 'Inserts': (0.80, 0.62, 0.25), 'Plug': (0.78, 0.79, 0.81), 'Retention_Screws': (0.10, 0.10, 0.11), 'Nose_Shell': (0.91, 0.90, 0.87), 'Cove_Liner': (0.86, 0.85, 0.80), 'Seam': (0.91, 0.90, 0.87), 'Frame': (0.82, 0.60, 0.16), 'Shelf': (0.82, 0.60, 0.16), 'Nutplates': (0.75, 0.76, 0.78), 'Screws': (0.10, 0.10, 0.11), 'Joiner_Band': (0.91, 0.90, 0.87)}
files = [(f'out/{f}', f[:-5]) for f in sorted(os.listdir('out')) if f.endswith('.brep')]
for path, nm in files:
    s = cq.Shape.importBrep(path)
    if nm in comps:
        lab, ref, par, loc = comps[nm]
        c = Quantity_ColorRGBA(); hasc = False
        for ctype in (XCAFDoc_ColorType.XCAFDoc_ColorSurf, XCAFDoc_ColorType.XCAFDoc_ColorGen):
            if XCAFDoc_ColorTool.GetColor_s(ref, ctype, c): hasc = ctype; break
        cloc = XCAFDoc_ShapeTool.GetLocation_s(lab)
        st.RemoveComponent(lab); st.RemoveShape(ref, True)
        sl = st.AddShape(bake(s.wrapped, loc.Inverted()), False, False); print("   label", nm, XCAFDoc_ShapeTool.IsSimpleShape_s(sl), XCAFDoc_ShapeTool.IsReference_s(sl), XCAFDoc_ShapeTool.IsAssembly_s(sl), sl.Tag(), sl.Father().Tag())
        TDataStd_Name.Set_s(sl, TCollection_ExtendedString(nm))
        cl = st.AddComponent(par, sl, cloc); TDataStd_Name.Set_s(cl, TCollection_ExtendedString(nm))
        if hasc is not False: ct.SetColor(sl, c, hasc)
        comps[nm] = (cl, sl, par, loc); print('replaced', nm)
    else:
        g = next(g for g in ('Fuselage','Wing_R','Wing_L','VTail_R','VTail_L','Boom_R','Boom_L') if nm.endswith('_'+g))
        par, ploc = parent_of[g]
        sl = st.AddShape(bake(s.wrapped, ploc.Inverted()), False)
        TDataStd_Name.Set_s(sl, TCollection_ExtendedString(nm))
        cl = st.AddComponent(par, sl, TopLoc_Location()); TDataStd_Name.Set_s(cl, TCollection_ExtendedString(nm))
        rgb = next(v for k, v in COL.items() if k in nm)
        ct.SetColor(sl, Quantity_Color(*rgb, Quantity_TOC_RGB), XCAFDoc_ColorType.XCAFDoc_ColorSurf)
        print('added', nm, 'to', g)
st.UpdateAssemblies()
# make sure every part definition carries its component's name
comps2 = {}
for i in range(1, roots.Length()+1): pass
def fixnames(lab):
    cs = TDF_LabelSequence(); XCAFDoc_ShapeTool.GetComponents_s(lab, cs)
    for i in range(1, cs.Length()+1):
        c = cs.Value(i); ref = TDF_Label(); XCAFDoc_ShapeTool.GetReferredShape_s(c, ref)
        if XCAFDoc_ShapeTool.IsAssembly_s(ref): fixnames(ref); continue
        if name(ref) != name(c) and name(c) != '?':
            TDataStd_Name.Set_s(ref, TCollection_ExtendedString(name(c))); print('named', name(c))
fr = TDF_LabelSequence(); st.GetFreeShapes(fr)
for i in range(1, fr.Length()+1): fixnames(fr.Value(i))
Interface_Static.SetCVal_s("write.step.schema", "AP214IS"); Interface_Static.SetCVal_s("write.step.unit", "MM")
w = STEPCAFControl_Writer(); w.SetNameMode(True); w.SetColorMode(True)
w.Transfer(doc, STEPControl_AsIs); w.Write(DST)
print('written', DST, round(time.time()-t0))
