import sys, pickle
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ShapeTool, XCAFDoc_ColorTool, XCAFDoc_ColorType
from OCP.TDF import TDF_LabelSequence, TDF_Label
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDataStd import TDataStd_Name
from OCP.TopLoc import TopLoc_Location
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepTools import BRepTools
from OCP.Quantity import Quantity_ColorRGBA
doc=TDocStd_Document(TCollection_ExtendedString("d")); r=STEPCAFControl_Reader(); r.SetNameMode(True); r.SetColorMode(True); r.ReadFile(sys.argv[1]); r.Transfer(doc)
st=XCAFDoc_DocumentTool.ShapeTool_s(doc.Main()); ct=XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
def name(l):
    a=TDataStd_Name(); return a.Get().ToExtString() if l.FindAttribute(TDataStd_Name.GetID_s(),a) else '?'
def col(l):
    c=Quantity_ColorRGBA()
    for t in (XCAFDoc_ColorType.XCAFDoc_ColorSurf, XCAFDoc_ColorType.XCAFDoc_ColorGen):
        if XCAFDoc_ColorTool.GetColor_s(l,t,c): rgb=c.GetRGB(); return (rgb.Red(),rgb.Green(),rgb.Blue())
    return None
out=[]
def walk(lab,loc,path):
    if XCAFDoc_ShapeTool.IsReference_s(lab):
        ref=TDF_Label(); XCAFDoc_ShapeTool.GetReferredShape_s(lab,ref); l2=loc.Multiplied(XCAFDoc_ShapeTool.GetLocation_s(lab))
        if XCAFDoc_ShapeTool.IsAssembly_s(ref): walk(ref,l2,path+'/'+name(ref))
        else:
            s=XCAFDoc_ShapeTool.GetShape_s(ref); t=l2.Multiplied(s.Location()).Transformation()
            w=BRepBuilderAPI_Transform(s.Located(TopLoc_Location()),t,True).Shape(); i=len(out)
            BRepTools.Write_s(w,f'stn/{i:03d}.brep'); out.append((path+'/'+name(ref), col(ref) or col(lab)))
        return
    if XCAFDoc_ShapeTool.IsAssembly_s(lab):
        cs=TDF_LabelSequence(); XCAFDoc_ShapeTool.GetComponents_s(lab,cs)
        for i in range(1,cs.Length()+1): walk(cs.Value(i),loc,path)
    else:
        s=XCAFDoc_ShapeTool.GetShape_s(lab); i=len(out); BRepTools.Write_s(s,f'stn/{i:03d}.brep'); out.append((path+'/'+name(lab), col(lab)))
roots=TDF_LabelSequence(); st.GetFreeShapes(roots)
for i in range(1,roots.Length()+1): walk(roots.Value(i),TopLoc_Location(),name(roots.Value(i)))
pickle.dump(out,open('stn/names.pkl','wb')); print(len(out)); [print(o) for o in out[:40]]
