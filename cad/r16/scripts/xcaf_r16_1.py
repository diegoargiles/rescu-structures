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
names = pickle.load(open('orig/names.pkl', 'rb')); idx = {n.split('/')[-1]: i for i, n in enumerate(names)}
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
    return BRepBuilderAPI_Transform(shape, loc.Transformation(), True).Shape()
# 1) nose parts: replace referred shape (local coords = global moved by inverse location)
for f in sorted(os.listdir('new')):
    i = int(f[:3]); nm = names[i].split('/')[-1]; lab, ref, par, loc = comps[nm]
    s = cq.Shape.importBrep(f'new/{f}')
    c = Quantity_ColorRGBA(); hasc = False
    for ctype in (XCAFDoc_ColorType.XCAFDoc_ColorSurf, XCAFDoc_ColorType.XCAFDoc_ColorGen):
        if XCAFDoc_ColorTool.GetColor_s(ref, ctype, c): hasc = ctype; break
    cloc = XCAFDoc_ShapeTool.GetLocation_s(lab)
    st.RemoveComponent(lab); st.RemoveShape(ref, True)
    sl = st.AddShape(bake(s.wrapped, loc.Inverted()), False)
    TDataStd_Name.Set_s(sl, TCollection_ExtendedString(nm))
    cl = st.AddComponent(par, sl, cloc); TDataStd_Name.Set_s(cl, TCollection_ExtendedString(nm))
    if hasc is not False: ct.SetColor(sl, c, hasc)
    comps[nm] = (cl, sl, par, loc)
    print('replaced', nm)
# 2) remove superseded placeholders
for nm in list(comps):
    if any(k in nm for k in ('REF_MT4008_Envelope', 'REF_Pusher_Prop_13in_Disk', 'REF_Prop_Disk_10in')):
        lab, ref, par, loc = comps.pop(nm); st.RemoveComponent(lab); ok = st.RemoveShape(ref, True); print('removed', nm, ok)
# 3) add new parts into the matching sub-assembly
parent_of = {}
for nm, (lab, ref, par, loc) in comps.items():
    g = next(g for g in ('Fuselage', 'Wing_R', 'Wing_L', 'Boom_R', 'Boom_L', 'VTail_R', 'VTail_L') if nm.endswith('_' + g))
    parent_of.setdefault(g, (par, loc.Multiplied(XCAFDoc_ShapeTool.GetLocation_s(lab).Inverted())))
COL = {'Tarot': (0.15, 0.15, 0.17), 'Adapter': (0.75, 0.75, 0.78), 'APC_13x8': (0.12, 0.12, 0.12), 'APC_10x3': (0.12, 0.12, 0.12)}
for f in sorted(os.listdir('add')):
    if not f.endswith('.brep'): continue
    nm = f[:-5]; g = 'Fuselage' if nm.endswith('_Fuselage') else ('Boom_R' if nm.endswith('_Boom_R') else 'Boom_L')
    par, ploc = parent_of[g]
    s = bake(cq.Shape.importBrep(f'add/{f}').wrapped, ploc.Inverted())
    sl = st.AddShape(s, False)
    TDataStd_Name.Set_s(sl, TCollection_ExtendedString(nm))
    cl = st.AddComponent(par, sl, TopLoc_Location())
    TDataStd_Name.Set_s(cl, TCollection_ExtendedString(nm))
    rgb = next(v for k, v in COL.items() if k in nm)
    ct.SetColor(sl, Quantity_Color(*rgb, Quantity_TOC_RGB), XCAFDoc_ColorType.XCAFDoc_ColorSurf)
    print('added', nm, 'to', g)
st.UpdateAssemblies()
Interface_Static.SetCVal_s("write.step.schema", "AP214IS"); Interface_Static.SetCVal_s("write.step.unit", "MM")
w = STEPCAFControl_Writer(); w.SetNameMode(True); w.SetColorMode(True)
w.Transfer(doc, STEPControl_AsIs); w.Write(DST)
print('written', DST, round(time.time()-t0))
