import sys, time, glob, cadquery as cq, lg, ctx
t=time.time()
FIX={f[3:-5]:cq.Shape.importBrep(f) for f in glob.glob('fx_*.brep')}
FIX.update({f[4:-5]:cq.Shape.importBrep(f) for f in glob.glob('ctx_*.brep')})
mode=sys.argv[1]
if mode=='fixed':
    ks=list(FIX)
    for i in range(len(ks)):
        for j in range(i+1,len(ks)):
            v=ctx.ov(FIX[ks[i]],FIX[ks[j]])
            if v>0.01: print('FIXED clash',ks[i],ks[j],round(v,3),flush=True)
    print('fixed done',round(time.time()-t)); sys.exit()
groups={'LEG':lg.LEG,'TEN':lg.TENDON,'ARM':lg.ARMG}
for psi in [float(a) for a in sys.argv[2:]]:
    m,d,th=lg.moving_parts(psi); out=[]
    for g,mem in groups.items():
        for mk in mem:
            for fk,f in FIX.items():
                v=ctx.ov(m[mk],f)
                if v>0.01: out.append((mk,fk,round(v,3)))
    gl=list(groups)
    for a in range(3):
        for b in range(a+1,3):
            for x in groups[gl[a]]:
                for y in groups[gl[b]]:
                    v=ctx.ov(m[x],m[y])
                    if v>0.01: out.append((x,y,round(v,3)))
    print(round(psi,1),'d',round(d,2),'th',round(th,1),out,round(time.time()-t),flush=True)
