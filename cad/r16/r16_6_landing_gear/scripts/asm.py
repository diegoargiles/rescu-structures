"""Write STEP assemblies (names, colours, nested sub-assemblies) with XCAF.
  python3 asm.py full  <src_step> <state_dir> <dst_step>    full aircraft, original tree kept, modified parts swapped,
                                                             gear added as LG_* sub-assemblies (Fixed / Leg / Tendon / Servo_Arm)
  python3 asm.py module <state_dir> <dst_step> <tag> [ctx]   one gear module (+ optional airframe context parts)
"""
import sys, os, json, time, pickle
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
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform

COL = {'Knuckle': (0.62, 0.64, 0.68), 'Knee_Shaft': (0.25, 0.25, 0.27), 'Fork_Pin': (0.25, 0.25, 0.27),
       'Leg_Rod': (0.08, 0.08, 0.09), 'Foot': (0.85, 0.35, 0.10), 'Tendon_Plate': (0.20, 0.45, 0.80),
       'Tendon_Bracket': (0.20, 0.45, 0.80), 'Servo_Arm': (0.85, 0.75, 0.15), 'Servo_Arm_Pin': (0.25, 0.25, 0.27),
       'Knee_Block': (0.70, 0.72, 0.76), 'Guide_Pin': (0.25, 0.25, 0.27), 'Guide_Tab': (0.82, 0.60, 0.16),
       'REF_Servo': (0.12, 0.30, 0.55), 'Servo_Mount': (0.82, 0.60, 0.16), 'Trough': (0.12, 0.12, 0.13),
       'Belly_Doubler': (0.12, 0.12, 0.13)}
def colour_for(n): return next((v for k, v in COL.items() if n.startswith(k)), (0.6, 0.6, 0.6))
def nm(l):
    a = TDataStd_Name(); return a.Get().ToExtString() if l.FindAttribute(TDataStd_Name.GetID_s(), a) else '?'
def setname(l, s): TDataStd_Name.Set_s(l, TCollection_ExtendedString(s))
def bake(shape, loc):
    t = loc.Multiplied(shape.Location()).Transformation()
    return BRepBuilderAPI_Transform(shape.Located(TopLoc_Location()), t, True).Shape()
def write(doc, dst):
    Interface_Static.SetCVal_s("write.step.schema", "AP214IS"); Interface_Static.SetCVal_s("write.step.unit", "MM")
    w = STEPCAFControl_Writer(); w.SetNameMode(True); w.SetColorMode(True)
    w.Transfer(doc, STEPControl_AsIs); w.Write(dst)

def add_gear(st, ct, parent, state_dir, tags=None):
    meta = json.load(open(f'{state_dir}/meta.json'))['parts']
    groups = {}
    for n, (g, sub) in meta.items():
        tag = sub.rsplit('_', 1)[0] if not sub.endswith('Servo_Arm') else sub[:-len('_Servo_Arm')]
        if tags and tag not in tags: continue
        groups.setdefault(tag, {}).setdefault(sub, []).append(n)
    for tag, subs in groups.items():
        asm = st.NewShape(); setname(asm, tag)
        for sub, parts in sorted(subs.items()):
            sa = st.NewShape(); setname(sa, sub)
            for n in sorted(parts):
                s = cq.Shape.importBrep(f'{state_dir}/{n}.brep')
                pl = st.AddShape(s.wrapped, False, False); setname(pl, n)
                ct.SetColor(pl, Quantity_Color(*colour_for(n), Quantity_TOC_RGB), XCAFDoc_ColorType.XCAFDoc_ColorSurf)
                c = st.AddComponent(sa, pl, TopLoc_Location()); setname(c, n)
            c = st.AddComponent(asm, sa, TopLoc_Location()); setname(c, sub)
        c = st.AddComponent(parent, asm, TopLoc_Location()); setname(c, tag)
        print('added', tag, {k: len(v) for k, v in subs.items()})

mode = sys.argv[1]
t0 = time.time()
doc = TDocStd_Document(TCollection_ExtendedString("doc"))
if mode == 'full':
    SRC, SD, DST = sys.argv[2:5]
    r = STEPCAFControl_Reader(); r.SetNameMode(True); r.SetColorMode(True); r.ReadFile(SRC); r.Transfer(doc)
    st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main()); ct = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
    print('read', round(time.time() - t0))
    comps = {}
    def walk(lab, loc, parent):
        if XCAFDoc_ShapeTool.IsReference_s(lab):
            ref = TDF_Label(); XCAFDoc_ShapeTool.GetReferredShape_s(lab, ref)
            l2 = loc.Multiplied(XCAFDoc_ShapeTool.GetLocation_s(lab))
            if XCAFDoc_ShapeTool.IsAssembly_s(ref): walk(ref, l2, ref)
            else: comps[nm(ref)] = (lab, ref, parent, l2)
            return
        if XCAFDoc_ShapeTool.IsAssembly_s(lab):
            cs = TDF_LabelSequence(); XCAFDoc_ShapeTool.GetComponents_s(lab, cs)
            for i in range(1, cs.Length() + 1): walk(cs.Value(i), loc, lab)
    roots = TDF_LabelSequence(); st.GetFreeShapes(roots); root = roots.Value(1)
    walk(root, TopLoc_Location(), root)
    for f in sorted(os.listdir(SD)):
        if not f.startswith('MOD__'): continue
        n = f[5:-5]; s = cq.Shape.importBrep(f'{SD}/{f}')
        lab, ref, par, loc = comps[n]
        c = Quantity_ColorRGBA(); hasc = False
        for ctype in (XCAFDoc_ColorType.XCAFDoc_ColorSurf, XCAFDoc_ColorType.XCAFDoc_ColorGen):
            if XCAFDoc_ColorTool.GetColor_s(ref, ctype, c): hasc = ctype; break
        cloc = XCAFDoc_ShapeTool.GetLocation_s(lab)
        st.RemoveComponent(lab); st.RemoveShape(ref, True)
        sl = st.AddShape(bake(s.wrapped, loc.Inverted()), False, False); setname(sl, n)
        cl = st.AddComponent(par, sl, cloc); setname(cl, n)
        if hasc is not False: ct.SetColor(sl, c, hasc)
        print('replaced', n)
    add_gear(st, ct, root, SD)
    setname(root, 'RescU_R16_6_Full_Aircraft')
else:
    SD, DST, TAG = sys.argv[2:5]
    st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main()); ct = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
    root = st.NewShape(); setname(root, f'RescU_R16_6_{TAG}_Module')
    add_gear(st, ct, root, SD, tags=[TAG])
    if len(sys.argv) > 5:                      # airframe context parts (brep files, global coords)
        ca = st.NewShape(); setname(ca, f'{TAG}_Airframe_Context')
        for f in sys.argv[5].split(','):
            s = cq.Shape.importBrep(f); n = os.path.basename(f)[:-5].replace('MOD__', '').replace('ctxR_', '')
            pl = st.AddShape(s.wrapped, False, False); setname(pl, n)
            ct.SetColor(pl, Quantity_Color(0.88, 0.88, 0.86, Quantity_TOC_RGB), XCAFDoc_ColorType.XCAFDoc_ColorSurf)
            c = st.AddComponent(ca, pl, TopLoc_Location()); setname(c, n)
        c = st.AddComponent(root, ca, TopLoc_Location()); setname(c, f'{TAG}_Airframe_Context')
st.UpdateAssemblies()
write(doc, DST)
print('written', DST, round(time.time() - t0))
