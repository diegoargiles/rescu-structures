"""Recompute retained P06 splice screens after P07 relief/skin-cap changes."""
import json
from pathlib import Path
import FreeCAD as A,Part,Assembly
R=Path(__file__).resolve().parents[1];B=R.parent
d=A.openDocument(str(R/'cad/RescU_P07_Wing_Arm_Integration.FCStd'))
g=json.loads((B/'rib-saddle-p06/reports/geometry_checks.json').read_text())
build=json.loads((R/'reports/build.json').read_text())
def gs(o):
 q=o.Shape.copy();q.Placement=o.getGlobalPlacement()*o.Placement.inverse()*q.Placement;q.tessellate(.3);return q
def contact(a,b):
 area=0.
 for fa in a.Faces:
  if type(fa.Surface).__name__!='Plane':continue
  for fb in b.Faces:
   if type(fb.Surface).__name__!='Plane':continue
   if abs(abs(fa.normalAt(0,0).dot(fb.normalAt(0,0)))-1)<1e-5 and fa.distToShape(fb)[0]<1e-5:area+=fa.common(fb).Area
 return area
def union_names(ns):
 extra=[row['name'] for row in build['new_components'] if any(row['name'].startswith(n+'_P07Segment') for n in ns)]
 return Part.makeCompound([gs(d.getObject(n)) for n in ns+extra])
out=[]
for side in ['PosY','NegY']:
 for station,force in [('Spar',84.7248134328358),('Rear',96.15055970149255)]:
  for ri in [1,2]:
   records=[]
   for group in [q for q in g['bond_interfaces'] if q['side']==side and q['station']==station and q['rib_index']==ri]:
    bond=union_names(group['bond_parts']);areas=[]
    for neighbor in group['contacts']:
     ns=neighbor['parts'][:]
     if any(n.startswith('Wing_Spar_Rib') for n in ns):
      ns += [r['name'] for r in build['new_components'] if r['name'].startswith('RibForwardSegment_'+side+'_Rib'+str(ri)+'_')]
     areas.append(contact(bond,union_names(ns)))
    records.append(dict(bond_parts=group['bond_parts'],actual_planar_contact_areas_mm2=areas))
   area=min(a for row in records for a in row['actual_planar_contact_areas_mm2'])
   t=2. if station=='Spar' else 1.5
   plate=union_names(['SplicePlate_'+side+'_'+station+'_Rib'+str(ri)])
   widths=[]
   for i in range(25):
    z=5+i*.25
    plane=Part.Face(Part.makePolygon([A.Vector(330,-320,z),A.Vector(440,-320,z),A.Vector(440,320,z),A.Vector(330,320,z),A.Vector(330,-320,z)]))
    widths.append(plate.common(plane).Area/t)
   net=min(widths) if station=='Spar' else 24.
   eccentricity=3.2+t/2
   stress=force/(max(net,1e-9)*t)+6*force*eccentricity/(max(net,1e-9)*t*t)
   tau=force/(.5*max(area,1e-9));lap=area/24
   out.append(dict(side=side,station=station,rib_index=ri,full_station_reaction_N=force,bond_groups=records,minimum_actual_planar_contact_mm2=area,effective_area_factor_assumption=.5,average_shear_MPa=tau,assumed_shear_screen_MPa=2.,shear_utilization=tau/2,sampled_plate_net_width_mm=net,plate_strip_combined_MPa=stress,assumed_plate_screen_MPa=70.,plate_utilization=stress/70,peel_proxy_MPa=6*force*eccentricity/(24*max(lap,1e-9)**2),peel_allowable=None))
 print('Updated splice screens',side,flush=True)
result=dict(status='Screening only; no peel/fatigue or process qualification',checks=out,max_shear_utilization=max(q['shear_utilization'] for q in out),max_plate_utilization=max(q['plate_utilization'] for q in out),all_assumed_screens_below_one=all(q['shear_utilization']<1 and q['plate_utilization']<1 for q in out))
(R/'reports/splice_checks.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='checks'},indent=2))
