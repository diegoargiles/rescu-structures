import time, pickle, cadquery as cq, lg, ctx
t=time.time()
c=ctx.boom_ctx(crop=True)
for k,v in c.items(): v.exportBrep(f'ctx_{k}.brep')
shells=[c['Boom_Upper_Half_Boom_R'],c['Boom_Lower_Half_Boom_R']]
F=lg.fixed_parts()
for k,v in F.items():
    tv=ctx.trim(v,shells); tv.exportBrep(f'fx_{k}.brep'); print('trim',k,round(v.Volume(),1),'->',round(tv.Volume(),1),len(tv.Solids()),flush=True)
print('t',round(time.time()-t))
