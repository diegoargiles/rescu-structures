import cadquery as cq, glob, os, json
rho={'GFRP':1.85,'G10':1.85,'M3':7.85}
def dens(n):
    if 'Nutplates' in n or 'Screws' in n: return 7.85
    return 1.85
add=0; mom=0; rows=[]
for f in sorted(glob.glob('p164/*.brep')):
    n=os.path.basename(f)[:-5]; s=cq.Shape.importBrep(f); v=s.Volume(); c=cq.Shape.centerOfMass(s); m=v*dens(n)/1000
    rows.append((n,round(v,1),round(m,2),round(c.x,1),round(c.y,1),round(c.z,1))); 
for r in rows: print(r)
new=sum(r[2] for r in rows); newm=sum(r[2]*r[3] for r in rows)
# removed from R16.3: Nose_Shell 22.35@104.5, band 4.31@179, shelf 16.45@82, frames_lower total 22.11@? -> replaced whole Frames_Lower row (old 22.11)
old=[(22.35,104.5),(4.31,179.0),(16.45,82.0),(22.11,None)]
import pickle
fl=cq.Shape.importBrep('new3/Frames_Lower_and_Battery_Saddles_GFRP_Fuselage.brep'); flm=fl.Volume()*1.85/1000; flx=cq.Shape.centerOfMass(fl).x
rem=22.35+4.31+16.45+flm; remm=22.35*104.5+4.31*179+16.45*82.0+flm*flx
d=new-rem; dm=newm-remm
M0=3699.9; X0=380.8  # R16.3 estimate
M=M0+d; X=(M0*X0+dm)/M
print(f'structure delta {d:+.1f} g; new total {M:.0f} g; CG x {X:.1f}')
json.dump(dict(rows=rows,delta=d,total=M,cgx=X),open('mass164.json','w'),indent=1)
