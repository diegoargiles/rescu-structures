import sys, pickle, time
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ShapeTool
from OCP.TDF import TDF_LabelSequence, TDF_Label
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDataStd import TDataStd_Name
from OCP.TopLoc import TopLoc_Location
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepTools import BRepTools
t0=time.time()
doc = TDocStd_Document(TCollection_ExtendedString("doc"))
r = STEPCAFControl_Reader(); r.SetNameMode(True); r.ReadFile(sys.argv[1]); r.Transfer(doc)
print('read', round(time.time()-t0), flush=True)
def name(l):
    a = TDataStd_Name(); return a.Get().ToExtString() if l.FindAttribute(TDataStd_Name.GetID_s(), a) else '?'
out=[]
def walk(lab, loc, path):
    if XCAFDoc_ShapeTool.IsReference_s(lab):
        ref = TDF_Label(); XCAFDoc_ShapeTool.GetReferredShape_s(lab, ref)
        l2 = loc.Multiplied(XCAFDoc_ShapeTool.GetLocation_s(lab))
        if XCAFDoc_ShapeTool.IsAssembly_s(ref): walk(ref, l2, path+'/'+name(ref))
        else:
            s = XCAFDoc_ShapeTool.GetShape_s(ref)
            t = l2.Multiplied(s.Location()).Transformation()
            w = BRepBuilderAPI_Transform(s.Located(TopLoc_Location()), t, True).Shape()
            i=len(out); BRepTools.Write_s(w, f'orig/{i:03d}.brep'); out.append(path+'/'+name(ref))
        return
    if XCAFDoc_ShapeTool.IsAssembly_s(lab):
        cs = TDF_LabelSequence(); XCAFDoc_ShapeTool.GetComponents_s(lab, cs)
        for i in range(1, cs.Length()+1): walk(cs.Value(i), loc, path)
roots = TDF_LabelSequence(); XCAFDoc_DocumentTool.ShapeTool_s(doc.Main()).GetFreeShapes(roots)
for i in range(1, roots.Length()+1): walk(roots.Value(i), TopLoc_Location(), name(roots.Value(i)))
pickle.dump(out, open('orig/names.pkl','wb')); print(len(out), 'parts', round(time.time()-t0))
