import sys, pickle, time
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.XCAFDoc import XCAFDoc_DocumentTool
from OCP.TDF import TDF_LabelSequence
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDataStd import TDataStd_Name
from OCP.TopLoc import TopLoc_Location
import cadquery as cq
t=time.time()
doc=TDocStd_Document(TCollection_ExtendedString("doc"))
r=STEPCAFControl_Reader(); r.SetNameMode(True); r.SetColorMode(True)
r.ReadFile(sys.argv[1]); r.Transfer(doc)
st=XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
print('read',round(time.time()-t))
def name(l):
    a=TDataStd_Name()
    return a.Get().ToExtString() if l.FindAttribute(TDataStd_Name.GetID_s(),a) else '?'
out={}
def walk(lab, loc, path):
    from OCP.XCAFDoc import XCAFDoc_ShapeTool
    if XCAFDoc_ShapeTool.IsReference_s(lab):
        ref=lab.__class__(); XCAFDoc_ShapeTool.GetReferredShape_s(lab, ref)
        l2=loc.Multiplied(XCAFDoc_ShapeTool.GetLocation_s(lab))
        walk(ref, l2, path+[name(lab)]); return
    comps=TDF_LabelSequence()
    if XCAFDoc_ShapeTool.IsAssembly_s(lab):
        XCAFDoc_ShapeTool.GetComponents_s(lab, comps)
        for i in range(1, comps.Length()+1): walk(comps.Value(i), loc, path)
    else:
        s=XCAFDoc_ShapeTool.GetShape_s(lab).Moved(loc)
        out['/'.join(path+[name(lab)])]=cq.Shape.cast(s)
roots=TDF_LabelSequence(); st.GetFreeShapes(roots)
for i in range(1, roots.Length()+1): walk(roots.Value(i), TopLoc_Location(), [name(roots.Value(i))])
print(len(out))
for k in out: print(k)
import os; os.makedirs('/home/claude/work/orig',exist_ok=True)
for i,(k,v) in enumerate(out.items()):
    v.exportBrep(f'/home/claude/work/orig/{i:03d}.brep')
pickle.dump(list(out.keys()),open('/home/claude/work/orig/names.pkl','wb'))
print('done',round(time.time()-t))
