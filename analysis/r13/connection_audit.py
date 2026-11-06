"""Read-only R13 geometry extraction; FreeCAD Python. Units mm and mm^3."""
import FreeCAD as A, Part, json, csv, hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2]
out=root/'reports/connection_study';out.mkdir(parents=True,exist_ok=True)
src=root/'cad/r13/RescU_R13_Layout_Candidate.FCStd'
d=A.openDocument(str(src));items=[]
for o in d.Objects:
 if o.TypeId!='PartDesign::Feature':continue
 s=o.Shape;b=s.BoundBox
 c=sum((v.CenterOfMass*v.Volume for v in s.Solids),A.Vector())/sum(v.Volume for v in s.Solids)
 items.append({'name':o.Name,'label':o.Label,'volume_mm3':s.Volume,'centroid_x_mm':c.x,'centroid_y_mm':c.y,'centroid_z_mm':c.z,'xmin':b.XMin,'xmax':b.XMax,'ymin':b.YMin,'ymax':b.YMax,'zmin':b.ZMin,'zmax':b.ZMax,'solids':len(s.Solids)})
with (out/'cad_component_locations.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,items[0].keys());w.writeheader();w.writerows(items)
names=['R13_Forward_Bonded_Wing_Socket_PosY','R13_Aft_Bonded_Wing_Socket_PosY','CFRP_motor_rib_nominal_2mm_PosY','Rebuilt_Swept_TaperedSpar_PosY','R13_Aft_Torque_Tube_PosY','Wing_Skin_PosY','Bonded_spar_sleeve_PosY','R13_Aft_Spar_Bond_Collar_265_PosY']
pairs=[]
for i,n in enumerate(names):
 for m in names[i+1:]:
  a=d.getObject(n).Shape;b=d.getObject(m).Shape
  pairs.append({'a':n,'b':m,'minimum_gap_mm':a.distToShape(b)[0],'overlap_mm3':a.common(b).Volume})
(out/'interface_audit.json').write_text(json.dumps({'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'pairs':pairs},indent=2))
print(json.dumps({'locations':len(items),'selected':[i for i in items if any(t in i['name'] for t in ['envelope','Battery','Avionics','Camera','Payload','Servo','rib_bolt','rib_nut'])],'pairs':pairs},indent=2),flush=True)
