"""VTK off-screen renderer for the R16.9 CAD (BREP round-trip in r169/rt)."""
import pickle, math, re
import numpy as np
import cadquery as cq
import vtk
from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray
from PIL import Image, ImageDraw, ImageFont

RT = '/home/claude/work/r169/rt'
NAMES = [x.split('/')[-1] for x in pickle.load(open(f'{RT}/names.pkl', 'rb'))]
_shape, _poly = {}, {}

def shape(k):
    if k not in _shape:
        _shape[k] = cq.Shape.importBrep(f'{RT}/{NAMES.index(k):03d}.brep')
    return _shape[k]

def to_poly(s, tol=0.12, ang=0.25):
    vs, tris = s.tessellate(tol, ang)
    V = np.array([v.toTuple() for v in vs], float); T = np.array(tris, np.int64)
    pts = vtk.vtkPoints(); pts.SetData(numpy_to_vtk(V, deep=True))
    conn = np.hstack([np.full((len(T), 1), 3, np.int64), T]).ravel()
    cells = vtk.vtkCellArray(); cells.SetCells(len(T), numpy_to_vtkIdTypeArray(conn, deep=True))
    pd = vtk.vtkPolyData(); pd.SetPoints(pts); pd.SetPolys(cells)
    n = vtk.vtkPolyDataNormals(); n.SetInputData(pd); n.SetFeatureAngle(30); n.SplittingOn(); n.ConsistencyOn(); n.Update()
    return n.GetOutput()

def poly(k):
    if k not in _poly:
        _poly[k] = to_poly(shape(k))
    return _poly[k]

# ---------------------------------------------------------------- colours
COL = {
    'gfrp': (0.93, 0.91, 0.86), 'g10': (0.86, 0.66, 0.26), 'cfrp': (0.20, 0.21, 0.23), 'al': (0.74, 0.77, 0.81),
    'steel': (0.46, 0.47, 0.50), 'brass': (0.80, 0.66, 0.30), 'pacf': (0.42, 0.34, 0.58), 'asa': (0.62, 0.62, 0.64),
    'xps': (0.62, 0.79, 0.93), 'eva': (0.25, 0.25, 0.27), 'tpu': (0.92, 0.42, 0.14), 'ptfe': (0.96, 0.96, 0.96),
    'bat': (0.18, 0.44, 0.82), 'esc': (0.36, 0.38, 0.42), 'cam': (0.84, 0.24, 0.52), 'fc': (0.95, 0.62, 0.10),
    'servo': (0.12, 0.62, 0.44), 'buoy': (0.95, 0.45, 0.18), 'motor': (0.30, 0.33, 0.37), 'prop': (0.55, 0.58, 0.62),
    'hi': (0.85, 0.35, 0.06), 'teal': (0.12, 0.39, 0.45),
}

def material(k):
    if k.startswith('REF_Camera'): return 'cam'
    if k.startswith(('REF_Battery', 'REF_M65A')): return 'bat'
    if k.startswith('REF_ESC'): return 'esc'
    if k.startswith(('REF_Flight', 'REF_Receiver')): return 'fc'
    if k.startswith(('REF_VTail_Servos', 'REF_Servo')): return 'servo'
    if k.startswith('REF_Payload'): return 'buoy'
    if k.startswith(('UM2807', 'Tarot')): return 'motor'
    if k.startswith(('APC', 'REF_Prop')): return 'prop'
    if 'Foot' in k: return 'tpu'
    if 'PA-CF' in k: return 'pacf'
    if 'ASA' in k: return 'asa'
    if 'XPS' in k: return 'xps'
    if 'Foam' in k: return 'eva'
    if 'PTFE' in k: return 'ptfe'
    if 'Brass' in k: return 'brass'
    if re.search(r'6061|Knee_Block|Compression_Tubes|Backing_Rings|Knuckle|Servo_Arm_LG|Tendon_Bracket', k): return 'al'
    if re.search(r'Screw|Pin|Nut|Bolts|Shaft|Nutplates', k): return 'steel'
    if re.search(r'Tendon_Plate', k): return 'cfrp'
    if re.search(r'Guide_Tab|Servo_Mount', k): return 'g10'
    if re.search(r'G10|Frames_|Battery_Trays|End_Stops|ESC_Deck|Avionics_Deck|Avionics_Adjust|Side_Rails', k): return 'g10'
    if re.search(r'CFRP|Boom_(Upper|Lower)|Saddle_U|Leg_Rod|Trough|Pad_Access|Junction', k):
        return 'cfrp' if 'Junction' not in k else 'gfrp'
    return 'gfrp'

def colour(k):
    return COL[material(k)]

# ---------------------------------------------------------------- scene
class Scene:
    def __init__(self, W=2000, H=1240, bg=(1, 1, 1), transparent=False):
        self.W, self.H = W, H
        self.rw = vtk.vtkRenderWindow(); self.rw.SetOffScreenRendering(1); self.rw.SetSize(W, H)
        self.rw.SetAlphaBitPlanes(1); self.rw.SetMultiSamples(0)
        self.ren = vtk.vtkRenderer(); self.rw.AddRenderer(self.ren)
        self.ren.SetBackground(*bg); self.ren.SetBackgroundAlpha(0.0 if transparent else 1.0)
        self.ren.SetUseDepthPeeling(1); self.ren.SetMaximumNumberOfPeels(60); self.ren.SetOcclusionRatio(0.0)
        self.ren.SetUseFXAA(True)
        self.transparent = transparent
        lk = vtk.vtkLightKit(); lk.SetKeyLightIntensity(0.85); lk.AddLightsToRenderer(self.ren)
        self.anchors = {}

    def add(self, k_or_shape, col=None, op=1.0, off=(0, 0, 0), edges=True, rot=None, spec=0.25):
        if isinstance(k_or_shape, str):
            pd = poly(k_or_shape); col = col or colour(k_or_shape)
        else:
            pd = to_poly(k_or_shape)
        m = vtk.vtkPolyDataMapper(); m.SetInputData(pd)
        a = vtk.vtkActor(); a.SetMapper(m)
        p = a.GetProperty(); p.SetColor(*col); p.SetOpacity(op); p.SetSpecular(spec); p.SetSpecularPower(25)
        p.SetDiffuse(0.85); p.SetAmbient(0.18)
        t = vtk.vtkTransform(); t.PostMultiply()
        if rot: t.RotateWXYZ(rot[0], *rot[1]);
        t.Translate(*off); a.SetUserTransform(t)
        self.ren.AddActor(a)
        if edges and op > 0.5:
            fe = vtk.vtkFeatureEdges(); fe.SetInputData(pd); fe.BoundaryEdgesOn(); fe.FeatureEdgesOn(); fe.SetFeatureAngle(50)
            fe.ManifoldEdgesOff(); fe.NonManifoldEdgesOff(); fe.ColoringOff()
            em = vtk.vtkPolyDataMapper(); em.SetInputConnection(fe.GetOutputPort())
            ea = vtk.vtkActor(); ea.SetMapper(em); ea.GetProperty().SetColor(0.12, 0.12, 0.14); ea.GetProperty().SetOpacity(0.55)
            ea.GetProperty().SetLineWidth(1.4); ea.GetProperty().LightingOff(); ea.SetUserTransform(t)
            self.ren.AddActor(ea)
        return a

    def camera(self, pos, focal, up=(0, 0, 1), parallel=None, view_angle=26):
        c = self.ren.GetActiveCamera(); c.SetPosition(*pos); c.SetFocalPoint(*focal); c.SetViewUp(*up)
        if parallel:
            c.ParallelProjectionOn(); c.SetParallelScale(parallel)
        else:
            c.SetViewAngle(view_angle)
        self.ren.ResetCameraClippingRange()

    def fit(self, pad=1.05):
        self.ren.ResetCamera(); c = self.ren.GetActiveCamera()
        if c.GetParallelProjection(): c.SetParallelScale(c.GetParallelScale() / pad)
        else: c.Zoom(pad)
        self.ren.ResetCameraClippingRange()

    def grab(self):
        self.rw.Render()
        w = vtk.vtkWindowToImageFilter(); w.SetInput(self.rw); w.SetInputBufferTypeToRGBA(); w.ReadFrontBufferOff(); w.Update()
        from vtk.util.numpy_support import vtk_to_numpy
        im = w.GetOutput(); W, H, _ = im.GetDimensions()
        a = vtk_to_numpy(im.GetPointData().GetScalars()).reshape(H, W, -1)[::-1]
        return a

    def fit2(self, pad=0.92, iters=3):
        c = self.ren.GetActiveCamera()
        for _ in range(iters):
            self.ren.ResetCameraClippingRange()
            a = self.grab()
            mask = a[:, :, 3] > 8 if self.transparent else a[:, :, :3].min(axis=2) < 250
            ys, xs = np.where(mask)
            if not len(xs): return
            x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
            bw, bh = max(x1 - x0, 1), max(y1 - y0, 1)
            f = min(self.W * pad / bw, self.H * pad / bh)
            dxp = (x0 + x1) / 2 - self.W / 2; dyp = (y0 + y1) / 2 - self.H / 2
            P = np.array(c.GetPosition()); F = np.array(c.GetFocalPoint()); up = np.array(c.GetViewUp())
            dop = F - P; dist = np.linalg.norm(dop); dop /= dist
            right = np.cross(dop, up); right /= np.linalg.norm(right); up2 = np.cross(right, dop)
            wpp = 2 * c.GetParallelScale() / self.H if c.GetParallelProjection() else 2 * dist * math.tan(math.radians(c.GetViewAngle() / 2)) / self.H
            sh = right * dxp * wpp - up2 * dyp * wpp
            c.SetPosition(*(P + sh)); c.SetFocalPoint(*(F + sh))
            if c.GetParallelProjection(): c.SetParallelScale(c.GetParallelScale() / f)
            else: c.SetViewAngle(math.degrees(2 * math.atan(math.tan(math.radians(c.GetViewAngle() / 2)) / f)))
        self.ren.ResetCameraClippingRange()

    def w2d(self, p):
        co = vtk.vtkCoordinate(); co.SetCoordinateSystemToWorld(); co.SetValue(*p)
        x, y = co.GetComputedDoubleDisplayValue(self.ren)
        return x, self.H - y

    def render(self, fn, callouts=(), crop=True, r=26):
        self.rw.Render()
        w = vtk.vtkWindowToImageFilter(); w.SetInput(self.rw); w.SetInputBufferTypeToRGBA(); w.ReadFrontBufferOff(); w.Update()
        tmp = fn + '.tmp.png'; pw = vtk.vtkPNGWriter(); pw.SetFileName(tmp); pw.SetInputConnection(w.GetOutputPort()); pw.Write()
        im = Image.open(tmp).convert('RGBA')
        if not self.transparent:
            bg = Image.new('RGBA', im.size, (255, 255, 255, 255)); bg.alpha_composite(im); im = bg
        draw_callouts(im, [(num, self.w2d(p), d) for num, p, d in callouts], r=r)
        if crop:
            arr = np.array(im)
            mask = (arr[:, :, 3] > 8) if self.transparent else (arr[:, :, :3].min(axis=2) < 250)
            ys, xs = np.where(mask)
            if len(xs):
                m = 24; im = im.crop((max(xs.min() - m, 0), max(ys.min() - m, 0), min(xs.max() + m, im.width), min(ys.max() + m, im.height)))
        im.save(fn)
        import os; os.remove(tmp)
        return fn

FONT = '/usr/share/fonts/truetype/google-fonts/ofl/firasans/FiraSans-Bold.ttf'
def draw_callouts(im, items, r=26):
    d = ImageDraw.Draw(im); f = ImageFont.truetype(FONT, int(r * 1.25))
    for num, (x, y), (dx, dy) in items:
        cx, cy = x + dx, y + dy
        d.line([(x, y), (cx, cy)], fill=(31, 100, 116, 255), width=4)
        d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=(31, 100, 116, 255))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(217, 88, 15, 255), outline=(255, 255, 255, 255), width=4)
        t = str(num); bb = d.textbbox((0, 0), t, font=f)
        d.text((cx - (bb[2] - bb[0]) / 2 - bb[0], cy - (bb[3] - bb[1]) / 2 - bb[1]), t, fill=(255, 255, 255, 255), font=f)

def crop_shape(k, box):
    """intersect a part with an axis-aligned box (xmin,xmax,ymin,ymax,zmin,zmax)."""
    x0, x1, y0, y1, z0, z1 = box
    b = cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))
    return shape(k).intersect(b)
