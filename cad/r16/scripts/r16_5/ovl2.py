import cadquery as cq, pickle, glob, os, json
from multiprocessing import Pool
names=pickle.load(open('/home/claude/verify4/orig/names.pkl','rb')); nm=[n.split('/')[-1] for n in names]
F={n:f'/home/claude/verify4/orig/{i:03d}.brep' for i,n in enumerate(nm)}
F.pop('REF_Z30_Swept_Envelope_Fuselage')
for f in glob.glob('out/*.brep'): F[os.path.basename(f)[:-5]]=f
new=['VTail_Root_Block_PA-CF_Fuselage','VTail_Root_Receivers_GFRP_Fuselage','VTail_Retention_Inserts_M3_Brass_Fuselage','VTail_Retention_Screws_M3x20_ISO4762_Fuselage',
 'VTail_Spar_Root_Plug_6061_VTail_R','VTail_Spar_Root_Plug_6061_VTail_L','VTail_AntiRotation_Pin_D3_VTail_R','VTail_AntiRotation_Pin_D3_VTail_L','VTail_Spar_CFRP_VTail_R','VTail_Spar_CFRP_VTail_L',
 'Wing_AntiRotation_Pin_D3_Wing_R','Wing_AntiRotation_Pin_D3_Wing_L','Wing_Pin_Bushing_Pads_G10_Fuselage','VTail_Root_Fairings_ASA_Fuselage','Wing_Root_Fairings_ASA_Fuselage',
 'VTail_Root_Diaphragm_GFRP_VTail_R','VTail_Root_Diaphragm_GFRP_VTail_L','Wing_Root_Diaphragm_GFRP_Wing_R','Wing_Root_Diaphragm_GFRP_Wing_L']
BB={n:cq.Shape.importBrep(f).BoundingBox() for n,f in F.items()}
def near(a,b,g=0.5):
    A,B=BB[a],BB[b]; return max(B.xmin-A.xmax,A.xmin-B.xmax,B.ymin-A.ymax,A.ymin-B.ymax,B.zmin-A.zmax,A.zmin-B.zmax)<g
pairs=sorted({tuple(sorted((a,b))) for a in new for b in F if a!=b and near(a,b)})
def job(p):
    a,b=p
    A=cq.Shape.importBrep(F[a]); Bs=cq.Shape.importBrep(F[b])
    v=sum(sa.intersect(sb).Volume() for sa in A.Solids() for sb in Bs.Solids())
    return (round(v,3),a,b)
if __name__=='__main__':
    print('pairs', len(pairs), flush=True)
    with Pool(6) as pool:
        res=[]
        for r in pool.imap_unordered(job,pairs):
            res.append(r)
            if abs(r[0])>0.001: print(r, flush=True)
    print('done', len(res)); json.dump(res,open('ovl165b.json','w'),indent=0)
