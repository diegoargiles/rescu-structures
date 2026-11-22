import sys
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ShapeTool
from OCP.TDF import TDF_LabelSequence, TDF_Label
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDataStd import TDataStd_Name
doc=TDocStd_Document(TCollection_ExtendedString("doc"))
r=STEPCAFControl_Reader(); r.SetNameMode(True); r.ReadFile(sys.argv[1]); r.Transfer(doc)
st=XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
def nm(l):
    a=TDataStd_Name(); return a.Get().ToExtString() if l.FindAttribute(TDataStd_Name.GetID_s(),a) else '?'
n=[0]; tree=[]
def walk(lab,depth,show):
    if XCAFDoc_ShapeTool.IsReference_s(lab):
        ref=TDF_Label(); XCAFDoc_ShapeTool.GetReferredShape_s(lab,ref)
        if XCAFDoc_ShapeTool.IsAssembly_s(ref):
            s=show or nm(ref).startswith('LG_')
            if s: tree.append('  '*depth+nm(ref)+'/')
            walk(ref,depth+1,s)
        else:
            n[0]+=1
            if show: tree.append('  '*depth+nm(ref))
        return
    cs=TDF_LabelSequence(); XCAFDoc_ShapeTool.GetComponents_s(lab,cs)
    for i in range(1,cs.Length()+1): walk(cs.Value(i),depth,show)
roots=TDF_LabelSequence(); st.GetFreeShapes(roots)
for i in range(1,roots.Length()+1): print('ROOT',nm(roots.Value(i))); walk(roots.Value(i),1,len(sys.argv)>2)
print('parts',n[0]); print('\n'.join(tree[:80]))
