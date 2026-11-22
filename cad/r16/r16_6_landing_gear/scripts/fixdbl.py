import cadquery as cq, lg, math
from cadquery import Vector as V
TILT=0.4
def T_T(s): return s.rotate(V(0,0,0),V(0,0,1),180).rotate(V(0,0,0),V(0,1,0),-TILT).translate(V(*lg.P_T))
def R_fus(x): return 44.3 - 0.0275 * (x - 450.0)
x0,x1=884.0,931.0
outer=cq.Solid.makeCone(R_fus(x0)-0.33,R_fus(x1)-0.33,x1-x0,V(x0,0,0),V(1,0,0))
inner=cq.Solid.makeCone(R_fus(x0)-1.33,R_fus(x1)-1.33,x1-x0,V(x0,0,0),V(1,0,0))
seam=cq.Shape.importBrep('out_deployed/MOD__Fuselage_Seam_Strips_GFRP_Fuselage.brep')
dbl=outer.cut(inner).intersect(lg.box(x0,x1,-16,16,-60,-20)).cut(T_T(lg.box(-9.5,45,-7.0,7.0,-30,0))).cut(seam)
dbl=max(dbl.Solids(),key=lambda s:s.Volume())
print(dbl.isValid(), round(dbl.Volume(),1), len(dbl.Solids()))
for d in ['out_deployed','out_retracted']: dbl.exportBrep(f'{d}/Belly_Doubler_CFRP_LG_Tail.brep')
import ctx
print('seam ov', ctx.ov(dbl,seam))
for p in [-15,-22,-30,-37,-45]:
    m,dd,th=lg.moving_parts(p,359.49); print(p, round(ctx.ov(T_T(m['Leg_Rod']),dbl),3), round(ctx.ov(T_T(m['Knuckle']),dbl),3), round(ctx.ov(T_T(m['Foot']),dbl),3))
