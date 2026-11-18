import cadquery as cq, pickle, glob, os, json, sys
from multiprocessing import Pool
names=pickle.load(open('/home/claude/verify/orig/names.pkl','rb')); nm=[n.split('/')[-1] for n in names]
F={n:f'/home/claude/verify/orig/{i:03d}.brep' for i,n in enumerate(nm)}
F.pop('Nose_Shell_GFRP_Fuselage'); F.pop('REF_Z30_Swept_Envelope_Fuselage')
new=[]
for f in glob.glob('p164/*.brep'):
    n=os.path.basename(f)[:-5]; F[n]=f; new.append(n)
BB={n:cq.Shape.importBrep(f).BoundingBox() for n,f in F.items()}
def near(a,b,g=0.5):
    A,B=BB[a],BB[b]
    return max(B.xmin-A.xmax,A.xmin-B.xmax,B.ymin-A.ymax,A.ymin-B.ymax,B.zmin-A.zmax,A.zmin-B.zmax)<g
pairs=set()
for a in new:
    for b in F:
        if a!=b and near(a,b): pairs.add(tuple(sorted((a,b))))
pairs=sorted(pairs)
def job(p):
    a,b=p; v=cq.Shape.importBrep(F[a]).intersect(cq.Shape.importBrep(F[b])).Volume(); return (round(v,3),a,b)
if __name__=='__main__':
    with Pool(8) as pool: res=pool.map(job,pairs)
    for r in sorted(res,reverse=True):
        if r[0]>0.001: print(r)
    print('pairs', len(res), 'all others 0.000')
    json.dump(res,open('ovl164.json','w'),indent=0)
