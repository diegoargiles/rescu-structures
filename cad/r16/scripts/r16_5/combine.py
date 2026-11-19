import sys, pickle
from OCP.STEPCAFControl import STEPCAFControl_Reader, STEPCAFControl_Writer
from OCP.STEPControl import STEPControl_AsIs
from OCP.TDocStd import TDocStd_Document
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ShapeTool, XCAFDoc_ColorType
from OCP.TDF import TDF_LabelSequence
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDataStd import TDataStd_Name
from OCP.TopLoc import TopLoc_Location
from OCP.gp import gp_Trsf, gp_Vec
from OCP.BRepTools import BRepTools
from OCP.BRep import BRep_Builder
from OCP.TopoDS import TopoDS_Shape
from OCP.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCP.Interface import Interface_Static
doc=TDocStd_Document(TCollection_ExtendedString("d")); r=STEPCAFControl_Reader(); r.SetNameMode(True); r.SetColorMode(True)
r.ReadFile(sys.argv[1]); r.Transfer(doc)
st=XCAFDoc_DocumentTool.ShapeTool_s(doc.Main()); ct=XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
roots=TDF_LabelSequence(); st.GetFreeShapes(roots); air=roots.Value(1)
top=st.NewShape(); TDataStd_Name.Set_s(top, TCollection_ExtendedString('RescU_R16_5_Seated_on_Landing_Station'))
t=gp_Trsf(); t.SetTranslation(gp_Vec(0,0,300))
c=st.AddComponent(top, air, TopLoc_Location(t)); TDataStd_Name.Set_s(c, TCollection_ExtendedString('RescU_R16_Full_Aircraft'))
stn=st.NewShape(); TDataStd_Name.Set_s(stn, TCollection_ExtendedString('RescU_Landing_Station'))
names=pickle.load(open('stn/names.pkl','rb'))
for i,(nm,col) in enumerate(names):
    s=TopoDS_Shape(); BRepTools.Read_s(s, f'stn/{i:03d}.brep', BRep_Builder())
    lab=st.AddShape(s, False); n=nm.split('/')[-1]; TDataStd_Name.Set_s(lab, TCollection_ExtendedString(n))
    if col: ct.SetColor(lab, Quantity_Color(*col, Quantity_TOC_RGB), XCAFDoc_ColorType.XCAFDoc_ColorSurf)
    cc=st.AddComponent(stn, lab, TopLoc_Location()); TDataStd_Name.Set_s(cc, TCollection_ExtendedString(n))
cs=st.AddComponent(top, stn, TopLoc_Location()); TDataStd_Name.Set_s(cs, TCollection_ExtendedString('RescU_Landing_Station'))
st.UpdateAssemblies()
fr=TDF_LabelSequence(); st.GetFreeShapes(fr); print('free shapes', fr.Length())
Interface_Static.SetCVal_s('write.step.schema','AP214IS')
w=STEPCAFControl_Writer(); w.SetNameMode(True); w.SetColorMode(True); w.Transfer(doc, STEPControl_AsIs); print('write', w.Write(sys.argv[2]))
