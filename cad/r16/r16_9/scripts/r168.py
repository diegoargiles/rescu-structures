"""R16.8 = R16.6 + smooth nose / Z30 removed / ELP camera placeholder (from R16.7, no plug) + wing moved 35 mm aft.
Moves with the wing: both wing panels, both booms (motors, props, nuts), both front gear modules, the joiner and its
receiver sleeves, axial stop, root side rails, pin bushing pads, root fairings and ring frames F282/F320; the shell
holes for the joiner, wire conduit and anti-rotation pin are filled and re-cut 35 mm aft. The rear battery module (with
its tray / stop / pad halves and saddles) moves 35 mm aft, and the ESC deck group 5 mm aft: otherwise the joiner and F320 would pass through it.
Writes breps to out/ and ops.json."""
import pickle, json, os
import cadquery as cq
from cadquery import Vector as V

DXW = 35.0
N = [x.split('/')[-1] for x in pickle.load(open('rt166/names.pkl', 'rb'))]
O2 = [x.split('/')[-1] for x in pickle.load(open('../r162/orig/names.pkl', 'rb'))]
def S(n): return cq.Shape.importBrep(f'rt166/{N.index(n):03d}.brep')
def S2(n): return cq.Shape.importBrep(f'../r162/orig/{O2.index(n):03d}.brep')
def box(x0, x1, y0=-1000, y1=1000, z0=-1000, z1=1000): return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))
def comp(l):
    l = [x for x in l if x is not None]
    return l[0] if len(l) == 1 else cq.Compound.makeCompound(l)
def clip(s, x0, x1):
    r = s.intersect(box(x0, x1)); return r if [q for q in r.Solids() if q.Volume() > 1e-3] else None
T = V(DXW, 0, 0)
TB = V(35.0, 0, 0)          # rear battery keeps its 3 mm gap to F320 (now x 355)
TE = V(5.0, 0, 0)           # ESC deck, pads and ESCs 5 mm aft so the rear battery end stop clears the deck
os.makedirs('out', exist_ok=True)
replace, add, remove = {}, {}, []

# ---- 1. nose: Z30 + cove out, smooth R16.2 skin (removable joint kept), ELP camera placeholder ----
screws = S('Nose_Joint_Screws_M3x6_ISO7380_Fuselage')
for side in ('Left', 'Right'):
    replace[f'Nose_Shell_{side}_GFRP_Fuselage'] = clip(S2(f'Fuselage_Shell_{side}_GFRP_Fuselage'), -1, 179.0).cut(screws)
seam2 = S2('Fuselage_Seam_Strips_GFRP_Fuselage')
replace['Nose_Seam_Strips_GFRP_Fuselage'] = comp([s for s in seam2.intersect(box(-1, 164.0)).Solids() if s.Volume() > 1e-3])
replace['Nose_Frame_NF3_G10_Fuselage'] = [s for s in S2('Frames_Lower_and_Battery_Saddles_GFRP_Fuselage').Solids()
                                          if 134 < s.BoundingBox().xmin < 136][0]
remove += ['Nose_Cove_Liner_GFRP_Fuselage', 'Camera_Shelf_G10_Fuselage', 'Camera_Mount_Nutplates_M3_Fuselage',
           'Nose_Frame_NF1_G10_Fuselage', 'Nose_Frame_NF2_G10_Fuselage', 'REF_Z30_Camera_Gimbal_Fuselage', 'REF_Z30_Swept_Envelope_Fuselage']
cam = cq.Solid.makeBox(38, 38, 22, V(-19, -19, -22)).fuse(cq.Solid.makeCylinder(8, 16, V(0, 0, 0), V(0, 0, 1)))
add['REF_Camera_ELP_5MP_IR_USB_Fuselage'] = cam.rotate(V(0, 0, 0), V(0, 1, 0), -135).translate(V(45.0, 0, -8.5))

# ---- 2. everything carried by the wing ----
WING_FUS = ['Wing_Joiner_CFRP_OD12_Fuselage', 'Joiner_Receiver_Sleeves_GFRP_Fuselage', 'Joiner_Axial_Stop_Ring_Fuselage',
            'Wing_Root_Side_Rails_GFRP_Fuselage', 'Wing_Pin_Bushing_Pads_G10_Fuselage', 'Wing_Root_Fairings_ASA_Fuselage']
moved = [n for n in N if n.endswith(('_Wing_R', '_Wing_L', '_Boom_R', '_Boom_L')) or '_LG_Front_' in n] + WING_FUS
for n in moved: replace[n] = S(n).translate(T)
fr = S('Frames_Ring_GFRP_Fuselage')
replace['Frames_Ring_GFRP_Fuselage'] = comp([s.translate(T) if s.BoundingBox().xmin < 330 else s for s in fr.Solids()])

# ---- 3. rear battery module and its bay parts aft with the joiner ----
for n in ['Battery_Trays_GFRP_Fuselage', 'Battery_End_Stops_GFRP_Fuselage', 'Battery_Insulating_Pads_Foam_Fuselage',
          'REF_Battery_Modules_75x68x47_Fuselage', 'REF_M65A_Cells_6S2P_Fuselage']:
    s = S(n); f, a = clip(s, -1, 300.0), clip(s, 300.0, 2000)
    replace[n] = comp([f, a.translate(TB) if a else None])
fl = S('Frames_Lower_and_Battery_Saddles_GFRP_Fuselage')
replace['Frames_Lower_and_Battery_Saddles_GFRP_Fuselage'] = comp(
    [s.translate(TB) if 320 < s.BoundingBox().xmin < 410 else s for s in fl.Solids()]).cut(S('Fuselage_Seam_Strips_GFRP_Fuselage'))

for n in ['ESC_Deck_GFRP_Fuselage', 'ESC_Pads_Foam_Fuselage', 'REF_ESC_AIR40A_x4_Fuselage']:
    replace[n] = S(n).translate(TE)

# ---- 4. fuselage shells: fill the wing-root holes, re-cut them 35 mm aft ----
HOLES = [(310.0, 4.2, 6.1), (345.0, 4.0, 3.1), (385.0, 3.0, 1.6)]
ann = cq.Solid.makeCylinder(45.0, 400, V(250, 0, 0), V(1, 0, 0)).cut(cq.Solid.makeCylinder(44.67, 400, V(250, 0, 0), V(1, 0, 0)))
def holes(dx, r_add=0.0):
    out = None
    for x, z, r in HOLES:
        c = cq.Solid.makeCylinder(r + r_add, 120, V(x + dx, -60, z), V(0, 1, 0))
        out = c if out is None else out.fuse(c)
    return out
for side in ('Left', 'Right'):
    sh = S(f'Fuselage_Shell_{side}_GFRP_Fuselage')
    half = box(0, 2000, -1000, 0) if side == 'Left' else box(0, 2000, 0, 1000)
    filler = holes(0).intersect(ann).intersect(half)
    replace[f'Fuselage_Shell_{side}_GFRP_Fuselage'] = sh.fuse(filler).clean().cut(holes(DXW))

for n, s in list(replace.items()) + list(add.items()): s.exportBrep(f'out/{n}.brep')
json.dump({'replace': sorted(replace), 'add': sorted(add), 'remove': remove, 'moved_with_wing': moved}, open('ops.json', 'w'), indent=1)
print('replace', len(replace), 'add', len(add), 'remove', len(remove), 'moved', len(moved))
