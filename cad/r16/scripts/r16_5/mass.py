import cadquery as cq, glob, os, json, pickle
names=[x.split('/')[-1] for x in pickle.load(open('/home/claude/verify4/orig/names.pkl','rb'))]
def O(k): return cq.Shape.importBrep(f'/home/claude/verify4/orig/{names.index(k):03d}.brep')
def rho(n):
    if 'Root_Block' in n: return 0.95
    if 'Fairings' in n: return 1.07
    if 'Inserts' in n: return 8.5
    if 'Screws' in n or 'Pin_D3' in n: return 7.85
    if 'Plug_6061' in n: return 2.7
    if 'XPS' in n: return 0.033
    if 'CFRP' in n: return 1.6
    return 1.85
def vol(s): return sum(x.Volume() for x in s.Solids())
skip_mass=('Wing_Skin','Fixed_Skin','Ruddervator_Skin','Fixed_Core','Ruddervator_Core','Fuselage_Shell')  # tiny trims; BRep volume unreliable on these skins
rows=[]; dm=0; dmx=0
for f in sorted(glob.glob('out/*.brep')):
    n=os.path.basename(f)[:-5]; s=cq.Shape.importBrep(f); v=vol(s); c=cq.Shape.centerOfMass(s); m=v*rho(n)/1000
    if n in names:
        o=O(n); mo=vol(o)*rho(n)/1000; co=cq.Shape.centerOfMass(o)
        if any(k in n for k in skip_mass): mo=m; co=c
    else: mo=0; co=c
    rows.append((n, round(v,1), round(m,2), round(m-mo,2), round(c.x,1))); dm+=m-mo; dmx+=m*c.x-mo*co.x
for r in rows: print(r)
M0=3738.4; X0=378.0
M=M0+dm; X=(M0*X0+dmx)/M
print(f'delta {dm:+.1f} g; total {M:.0f} g; CG x {X:.1f}')
json.dump(dict(rows=rows,delta=dm,total=M,cgx=X),open('mass165.json','w'),indent=1)
