from pathlib import Path
import FreeCAD as A,Part,json,subprocess,os,math,numpy as np
base=Path(__file__).resolve().parent;out=base/'r08_joint';out.mkdir(exist_ok=True);fem=out/'fea';fem.mkdir(exist_ok=True)
exe=Path('C:/Program Files/FreeCAD 1.1/bin');doc=A.openDocument(str(base/'r07_study/RescU_R07_Arm_Wing_Study.FCStd'))
s=doc.getObject('Aft_compact_clevis').Shape;s.exportBrep(str(fem/'clevis.brep'))
results=[]
for size in [2.0,1.2,.8]:
 name='clevis_'+str(size).replace('.','p');folder=fem/name;folder.mkdir(exist_ok=True)
 geo=folder/'mesh.geo';geo.write_text('SetFactory("OpenCASCADE");\nMerge "'+(fem/'clevis.brep').as_posix()+'";\nMesh.MeshSizeMin='+str(size)+';\nMesh.MeshSizeMax='+str(size)+';\nMesh.ElementOrder=2;\nMesh.SaveAll=1;\n')
 with (folder/'gmsh.log').open('w') as log:run=subprocess.run([str(exe/'gmsh.exe'),str(geo),'-3','-format','inp','-o',str(folder/'mesh.inp'),'-nopopup'],stdout=log,stderr=log)
 assert run.returncode==0,'gmsh failed'
 nodes={};elements={};mode=None
 for line in (folder/'mesh.inp').read_text().splitlines():
  if line.startswith('*'):
   mode='n' if line.upper().startswith('*NODE') else 'e' if line.upper().startswith('*ELEMENT') and 'C3D10' in line.upper() else None
  elif line.strip() and mode:
   vals=[v.strip() for v in line.split(',') if v.strip()]
   if mode=='n':nodes[int(vals[0])]=list(map(float,vals[1:4]))
   else:elements[int(vals[0])]=list(map(int,vals[1:]))
 assert elements and nodes
 used=set(v for el in elements.values() for v in el);nodes={n:p for n,p in nodes.items() if n in used}
 fixed=[n for n,(x,y,z) in nodes.items() if abs(z+15.8)<1e-5 and 255.1<y<274.9]
 loaded=[n for n,(x,y,z) in nodes.items() if abs(math.hypot(x-405,z+8)-1.6)<.025 and (261.49<=y<=263.86 or 266.14<=y<=268.51)]
 assert len(fixed)>3 and len(loaded)>3,(len(fixed),len(loaded))
 inp='*HEADING\nR08 clevis linear elastic screening, N mm MPa\n*NODE\n'+''.join(str(n)+','+','.join(map(str,p))+'\n' for n,p in nodes.items())
 inp+='*ELEMENT,TYPE=C3D10,ELSET=ALL\n'+''.join(str(n)+','+','.join(map(str,p))+'\n' for n,p in elements.items())
 inp+='*NSET,NSET=FIX\n'+''.join(str(n)+'\n' for n in fixed)+'*NSET,NSET=ALLN\n'+''.join(str(n)+'\n' for n in nodes)
 inp+='*MATERIAL,NAME=AL_ASSUMED\n*ELASTIC\n69000,.33\n*SOLID SECTION,ELSET=ALL,MATERIAL=AL_ASSUMED\n*BOUNDARY\nFIX,1,3\n*STEP\n*STATIC\n*CLOAD\n'
 inp+=''.join(f'{n},3,{54.37142857142857/len(loaded):.12f}\n' for n in loaded)
 inp+='*NODE PRINT,NSET=ALLN\nU\n*NODE PRINT,NSET=FIX,TOTALS=YES\nRF\n*EL PRINT,ELSET=ALL\nS\n*NODE FILE\nU\n*EL FILE\nS\n*END STEP\n'
 (folder/'solve.inp').write_text(inp)
 with (folder/'solver.log').open('w') as log:r=subprocess.run([str(exe/'ccx.exe'),'-i','solve'],cwd=folder,stdout=log,stderr=log,env=dict(os.environ,OMP_NUM_THREADS='2'))
 assert r.returncode==0,(name,r.returncode)
 data=(folder/'solve.dat').read_text();mode=None;disp=[];stress=[];reaction=[]
 for line in data.splitlines():
  low=line.lower()
  if 'displacements (' in low:mode='u';continue
  if 'stresses (' in low:mode='s';continue
  if 'forces (' in low:mode='r';continue
  if 'total force' in low:mode=None;continue
  vals=line.split()
  if not vals or not vals[0].isdigit():continue
  try:
   if mode=='u' and len(vals)==4:disp.append([int(vals[0])]+list(map(float,vals[1:])))
   if mode=='r' and len(vals)==4:reaction.append(list(map(float,vals[1:])))
   if mode=='s' and len(vals)==8:
    ss=list(map(float,vals[2:]));xx,yy,zz,xy,xz,yz=ss;vm=math.sqrt(.5*((xx-yy)**2+(yy-zz)**2+(zz-xx)**2)+3*(xy*xy+xz*xz+yz*yz));stress.append([int(vals[0]),int(vals[1]),vm]+ss)
  except ValueError:pass
 assert disp and stress,(name,data[:500])
 rf=np.sum(reaction,axis=0);assert abs(rf[2]+54.37142857)<.02,(name,rf)
 dmax=max(np.linalg.norm(row[1:]) for row in disp);vms=[r[2] for r in stress]
 results.append(dict(mesh_size_mm=size,nodes=len(nodes),elements=len(elements),fixed_nodes=len(fixed),loaded_nodes=len(loaded),max_displacement_mm=dmax,max_integration_point_von_mises_MPa=max(vms),p95_integration_point_von_mises_MPa=float(np.percentile(vms,95)),support_reaction_N=rf.tolist()))
 (folder/'parsed.json').write_text(json.dumps({'nodes':nodes,'elements':elements,'displacements':disp,'stress':stress,'fixed':fixed,'loaded':loaded}))
 print(results[-1],flush=True)
(out/'fea_results.json').write_text(json.dumps(results,indent=2))
