"""V-tail halves: GFRP skin over XPS core, split fixed surface / ruddervator at 69% chord, tapered CFRP spar."""
import cadquery as cq, numpy as np, sys
from geom import *
GAP = 1.0
def _ud(xx, t):
    yt = 5*0.10*(0.2969*np.sqrt(xx)-0.1260*xx-0.3516*xx**2+0.2843*xx**3-0.1036*xx**4)
    return yt
def part_wire(sg, s, part, inset=0.0, n=28):
    c = tchord(s); place = tail_place(sg, s); uh = HINGE_FRAC
    g = GAP/2/c
    if part == 'fixed':
        x0, x1 = inset*1.2/c, uh - g - inset/c
        b = np.linspace(0, np.pi, n); xx = x0 + (x1-x0)*(1-np.cos(b))/2
        yt = _ud(xx, 0)*c - inset
        up = [place(x*c, y) for x, y in zip(xx[::-1], yt[::-1])]
        lo = [place(x*c, -y) for x, y in zip(xx[1:], yt[1:])]
        e1 = cq.Edge.makeSpline(up + lo)
        e2 = cq.Edge.makeLine(lo[-1], up[0])
        return cq.Wire.assembleEdges([e1, e2])
    else:
        x0 = uh + g + inset/c
        xs = np.linspace(0, 1, 400); th = 2*_ud(xs, 0)*c - 2*inset
        x1 = xs[np.where(th >= 0.25)[0][-1]] if inset > 0 else 1.0
        xx = np.linspace(x0, x1, n)
        yt = _ud(xx, 0)*c - inset
        if inset == 0: yt[-1] = 0.0
        up = [place(x*c, y) for x, y in zip(xx, yt)]
        lo = [place(x*c, -y) for x, y in zip(xx, yt)]
        if inset == 0:
            e1 = cq.Edge.makeSpline(up); e2 = cq.Edge.makeSpline(lo[::-1][:-1] + [up[-1]][:0] or lo[::-1])
            e2 = cq.Edge.makeSpline([up[-1]] + lo[::-1][1:])
            e3 = cq.Edge.makeLine(lo[0], up[0])
            return cq.Wire.assembleEdges([e1, e2, e3])
        e1 = cq.Edge.makeSpline(up); e2 = cq.Edge.makeLine(up[-1], lo[-1]); e3 = cq.Edge.makeSpline(lo[::-1])
        e4 = cq.Edge.makeLine(lo[0], up[0])
        return cq.Wire.assembleEdges([e1, e2, e3, e4])
def loft(sg, part, inset):
    return cq.Workplane().add(cq.Solid.makeLoft([part_wire(sg, 0.0, part, inset), part_wire(sg, TSPAN, part, inset)], True))
def build_tail(sg, log=print):
    fus = fus_solid()
    a = np.radians(TDIH); e = np.array([0, sg*np.cos(a), np.sin(a)])
    P = {}
    for part, nm in (('fixed', 'Fixed'), ('rudd', 'Ruddervator')):
        o = loft(sg, part, 0.0); i = loft(sg, part, TSKIN)
        skin = o.cut(i).cut(fus); core = i.cut(fus)
        P[f'VTail_{nm}_Skin_GFRP'] = skin; P[f'VTail_{nm}_Core_XPS'] = core
    log('surfaces')
    # tapered spar at 30% chord, s 4.5 -> 236 ; OD 6 -> 4 (two-step taper)
    def spt(s): return np.array([txle(s) + 0.30*tchord(s), 0, 0]) + e*s
    spar = tube_between(tuple(spt(4.5)), tuple(spt(120)), 3.0, 2.2).union(tube_between(tuple(spt(120)), tuple(spt(236)), 2.0, 1.4))
    env = tube_between(tuple(spt(0)), tuple(spt(120)), 3.05).union(tube_between(tuple(spt(119)), tuple(spt(240)), 3.05))
    P['VTail_Fixed_Core_XPS'] = P['VTail_Fixed_Core_XPS'].cut(env).cut(fus_solid(-1.0))
    # anti-rotation pin (D3) at 60% root chord, parallel to span axis, root end in fuselage
    def ppt(s): return np.array([TLE + 0.60*TCR + TSWEEP*s/TSPAN*0.0, 0, 0]) + e*s
    pin = tube_between(tuple(ppt(6)), tuple(ppt(40)), 1.5)
    P['VTail_Fixed_Core_XPS'] = P['VTail_Fixed_Core_XPS'].cut(tube_between(tuple(ppt(0)), tuple(ppt(42)), 1.6))
    # root diaphragm at the fuselage surface (GFRP 1 mm) on fixed surface
    i = loft(sg, 'fixed', TSKIN)
    shell_band = fus_solid(-1.0).cut(fus_solid(0.0))
    diaph = i.intersect(shell_band).cut(env).cut(tube_between(tuple(ppt(0)), tuple(ppt(42)), 1.6))
    # hinge: 3 printed/nylon pin hinges per ruddervator along hinge line (REF placeholders)
    def hpt(s): return np.array([txle(s) + HINGE_FRAC*tchord(s), 0, 0]) + e*s
    hinges = None
    for s in (40, 130, 220):
        h = tube_between(tuple(hpt(s)-e*6), tuple(hpt(s)+e*6), 1.2)
        hinges = h if hinges is None else hinges.union(h)
    for k in ('VTail_Fixed_Core_XPS', 'VTail_Fixed_Skin_GFRP', 'VTail_Ruddervator_Core_XPS', 'VTail_Ruddervator_Skin_GFRP'):
        P[k] = P[k].cut(hinges)
    P.update(VTail_Spar_CFRP=spar, VTail_AntiRotation_Pin_D3=pin, VTail_Root_Diaphragm_GFRP=diaph, VTail_Hinge_Pins_REF=hinges)
    log('spar')
    return P
if __name__ == '__main__':
    import os, time; t0 = time.time(); sg = int(sys.argv[1]); side = 'R' if sg > 0 else 'L'
    out = f'/home/claude/full/out/tail_{side}'; os.makedirs(out, exist_ok=True)
    P = build_tail(sg, log=lambda m: (print('T'+side, m, round(time.time()-t0, 1)), sys.stdout.flush()))
    for k, v in P.items():
        s = v.val() if len(v.vals()) == 1 else cq.Compound.makeCompound(v.vals())
        print('T'+side, k, s.isValid(), len(s.Solids()), round(s.Volume(), 1)); s.exportBrep(f'{out}/{k}.brep')
