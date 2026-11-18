import cadquery as cq, numpy as np, math, time, sys
from cadquery import Vector as V
sys.path.insert(0,'.'); from cove import XC, ZOFF, ZTOP
from r164a_lib import nin
t0=time.time(); XJ=179.0
def box(x0,x1,y0,y1,z0,z1): return cq.Solid.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def R(x): return 45*math.sqrt(max(0,1-(1-x/200)**2))
def sv(s,n): s.exportBrep(f'p164/{n}.brep'); b=s.BoundingBox(); print(f'{n:40s} valid {s.isValid()} solids {len(s.Solids())} vol {s.Volume():9.1f} x {b.xmin:6.1f}..{b.xmax:6.1f} z {b.zmin:6.1f}..{b.zmax:6.1f}  t={time.time()-t0:.0f}', flush=True); return s
K=cq.Shape.importBrep('K.brep'); N=cq.Shape.importBrep('N.brep'); O=cq.Shape.importBrep('Nf_8.brep')
Kb=cq.Shape.importBrep('Kbig.brep'); Kf=cq.Shape.importBrep('Kfl.brep'); Kbs=cq.Shape.importBrep('Kbs.brep'); I66=cq.Shape.importBrep('I66.brep')
N33=nin(0.33,187); N63=nin(0.63,187); N93=nin(0.93,187); N99=nin(0.99,187); N633=nin(6.33,187)
# --- liner -----------------------------------------------------------
PCD=32.0; HOLES=[(XC+PCD/2*math.cos(math.radians(a)), PCD/2*math.sin(math.radians(a))) for a in (45,135,225,315)]
liner=O.cut(I66).intersect(Kb).fuse(N33.cut(N99).intersect(Kf.cut(Kbs))).fuse(cq.Solid.makeCylinder(21.21,0.39,V(XC,0,ZTOP+0.60)))
ZS0=ZTOP+0.99; ZS1=ZS0+2.0
def holes(z0,h):
    s=cq.Solid.makeCylinder(6.0,h,V(XC,0,z0))
    for x,y in HOLES: s=s.fuse(cq.Solid.makeCylinder(1.7,h,V(x,y,z0)))
    return s
liner=sv(liner.cut(holes(ZTOP-1,4)),'Nose_Cove_Liner_GFRP_Fuselage')
# --- shell halves -------------------------------------------------------
shell=N.cut(nin(0.33,180)).cut(Kb)
# joint screw holes: x 171.5, angles from top +-60, +-120
XS=171.5; ANG=(60,120,-60,-120)
def rdir(a): return (math.sin(math.radians(a)), math.cos(math.radians(a)))
def radial_cyl(a, r0, r1, d):
    sy,sz=rdir(a); return cq.Solid.makeCylinder(d/2, r1-r0, V(XS, r0*sy, r0*sz), V(0,sy,sz))
SH=None
for a in ANG:
    c=radial_cyl(a,30,50,3.4); SH=c if SH is None else SH.fuse(c)
shell=shell.cut(SH)
sv(shell.intersect(box(-5,XJ+1,-60,0,-60,60)),'Nose_Shell_Left_GFRP_Fuselage')
sv(shell.intersect(box(-5,XJ+1,0,60,-60,60)),'Nose_Shell_Right_GFRP_Fuselage')
# --- seam strips (0.30 under the skin, 12 wide) -------------------------
lay=N33.cut(N63).intersect(box(3,164,-6,6,-60,60))
strips=lay.cut(Kf)
keep=[s for s in strips.Solids() if s.Volume()>2]
strips=sv(cq.Compound.makeCompound(keep),'Nose_Seam_Strips_GFRP_Fuselage')
# --- joiner band (bonded in fuselage x179-186, nose side x164-179 removable) ----
band=N33.cut(N93).intersect(box(164,186,-60,60,-60,60)).cut(Kf).cut(SH)
band=sv(band,'Nose_Joiner_Band_GFRP_Fuselage')
# --- frames ---------------------------------------------------------------
cut_all=K.fuse(liner).fuse(strips).fuse(band)
def frame(x0,x1,name,zmax=None,lighten=False):
    s=box(x0,x1,-60,60,-60,60 if zmax is None else zmax).intersect(N33).cut(cut_all)
    if lighten: s=s.cut(box(x0-1,x1+1,-60,60,ZS1+6,60).intersect(N633))
    s=max(s.Solids(), key=lambda q:q.Volume()); return sv(s,name)
F1=frame(55.5,57.0,'Nose_Frame_NF1_G10_Fuselage',lighten=True)
F2=frame(104.0,105.5,'Nose_Frame_NF2_G10_Fuselage',lighten=True)
F3=frame(135.0,136.5,'Nose_Frame_NF3_G10_Fuselage',zmax=-5.0)
F4=frame(162.5,164.0,'Nose_Frame_NF4_G10_Fuselage',zmax=-5.0)
# --- camera shelf 2 mm ------------------------------------------------------
shelf=box(57.2,103.8,-60,60,ZS0,ZS1).intersect(N33).cut(holes(ZS0-1,4)).cut(liner)
shelf=sv(shelf,'Camera_Shelf_G10_Fuselage')
# --- mount nutplates (2-lug, M3) on shelf top, lugs tangential ------------
def nutplate(L=12.0, W=5.0, t=1.0, bh=3.0):
    base=box(-L/2,L/2,-W/2,W/2,0,t).cut(cq.Solid.makeCylinder(1.05,t+1,V(-4.0,0,-0.5))).cut(cq.Solid.makeCylinder(1.05,t+1,V(4.0,0,-0.5)))
    barrel=cq.Solid.makeCylinder(3.0,bh,V(0,0,t)).fuse(cq.Solid.makeCylinder(2.4,0.0001+0.0,V(0,0,t))) 
    s=base.fuse(cq.Solid.makeCylinder(3.0,bh,V(0,0,t))).cut(cq.Solid.makeCylinder(1.25,t+bh+1,V(0,0,-0.5)))
    return s.clean()
NP=nutplate(); parts=[]
for (x,y),a in zip(HOLES,(45,135,225,315)):
    s=NP.rotate(V(0,0,0),V(0,0,1),a+90).translate(V(x,y,ZS1)); parts.append(s)
sv(cq.Compound.makeCompound(parts),'Camera_Mount_Nutplates_M3_Fuselage')
# --- joint nutplates (lugs along x) on band inner face + ISO 7380 M3x6 screws ---
jn=[]; js=[]
r_in=R(XS)-0.93
for a in ANG:
    sy,sz=rdir(a); ang=math.degrees(math.atan2(sz,sy))
    # nutplate local: z up = toward axis; place base outer face at r_in-0.12
    s=NP.rotate(V(0,0,0),V(0,1,0),180)   # flip so barrel points to -z (toward axis after mapping)
    s=s.translate(V(0,0,0))
    # map local z -> -radial, local x -> x, local y -> tangential
    s=s.rotate(V(0,0,0),V(1,0,0), -(90-ang) ).translate(V(XS, (r_in-0.25)*sy, (r_in-0.25)*sz))
    jn.append(s)
    head=cq.Solid.makeCylinder(2.85,1.65,V(0,0,0)); 
    try: head=head.fillet(1.0,[e for e in head.Edges() if e.Center().z>1.6])
    except Exception: pass
    hexs=cq.Workplane('XY').polygon(6,2.0/math.cos(math.pi/6)).extrude(1.0).val().translate(V(0,0,0.65))
    scr=head.cut(hexs).fuse(cq.Solid.makeCylinder(1.5,6.0,V(0,0,-6.0)))
    scr=scr.rotate(V(0,0,0),V(1,0,0), -(90-ang)).translate(V(XS, (R(XS)+0.05)*sy, (R(XS)+0.05)*sz))
    js.append(scr)
sv(cq.Compound.makeCompound(jn),'Nose_Joint_Nutplates_M3_Fuselage')
sv(cq.Compound.makeCompound(js),'Nose_Joint_Screws_M3x6_ISO7380_Fuselage')
