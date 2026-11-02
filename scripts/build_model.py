"""BERET / AirPods Pro 3 • millimetres; X right, Y back, Z up.
Regenerates the very same meshes shown on the website. No scaled display proxy.
A reference-led sculpt, not a 3D scan. Nominal device envelope comes from Apple.
"""
from pathlib import Path
import json, math, argparse
import numpy as np
import trimesh as tm
from scipy.interpolate import PchipInterpolator

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('--clearance',type=float,default=.30,help='per-side radial clearance, mm')
p.add_argument('--width',type=float,default=62.22)
p.add_argument('--depth',type=float,default=21.84)
p.add_argument('--height',type=float,default=47.22)
p.add_argument('--seam-height',type=float,default=32.5,help='lid seam above device bottom; verify on physical device')
a=p.parse_args()
if not .15<=a.clearance<=.65: raise ValueError('clearance must be 0.15–0.65 mm')
C=a.clearance; BOTTOM=3.; SEAM=BOTTOM+a.seam_height; GAP=.6
PIVOT=np.array([0.,9.7,SEAM]) # kinematic illustration; not a measured hinge-pin axis
OUT=ROOT/'models';OUT.mkdir(exist_ok=True)

def rounded_box(size,r,center):
    m=tm.creation.icosphere(subdivisions=4,radius=r)
    m.vertices += np.sign(m.vertices)*(np.array(size)/2-r)
    m=m.convex_hull
    m.apply_translation(center);return m

def box(size,center): return tm.creation.box(size,tm.transformations.translation_matrix(center))
def ell(center,scale,sub=3):
    m=tm.creation.icosphere(subdivisions=sub);m.apply_scale(scale);m.apply_translation(center);return m

def union(ms): return tm.boolean.union(ms,engine='manifold',check_volume=True)
def diff(m,cut): return tm.boolean.difference([m]+(cut if isinstance(cut,list) else [cut]),engine='manifold',check_volume=True)
def inter(m,cut): return tm.boolean.intersection([m,cut],engine='manifold',check_volume=True)

def rings_mesh(rings,segments=80):
    # Rings are [cx,cy,z,rx,ry]; caps are flat discs.
    vs=[]
    for x,y,z,rx,ry in rings:
        for t in np.linspace(0,2*np.pi,segments,endpoint=False): vs.append([x+rx*np.cos(t),y+ry*np.sin(t),z])
    fs=[]
    for k in range(len(rings)-1):
        for j in range(segments):
            jn=(j+1)%segments;u=k*segments+j;v=k*segments+jn;w=(k+1)*segments+jn;q=(k+1)*segments+j
            fs.extend([[u,v,w],[u,w,q]])
    for k,reverse in [(0,True),(len(rings)-1,False)]:
        ci=len(vs);vs.append(rings[k][:3])
        for j in range(segments):
            f=[ci,k*segments+j,k*segments+(j+1)%segments];fs.append(f[::-1] if reverse else f)
    m=tm.Trimesh(vs,fs,process=True);m.fix_normals();return m

def leaf(points,width,thick,n=24):
    # Curved fused locks with a blunt 0.9 mm end instead of fragile knife points.
    pts=np.array(points);t=np.linspace(0,1,n);q=[]
    for u in t:
        pos=(1-u)**3*pts[0]+3*(1-u)**2*u*pts[1]+3*(1-u)*u*u*pts[2]+u**3*pts[3]
        radius=max(.45,width*(math.sin(math.pi*(.12+.88*u))**.65))
        if u==1:radius=.45
        q.append([*pos,radius,max(.45,thick*(radius/width)**.5)])
    # leaves aligned vertically: each ring lies in XY plane
    return rings_mesh(q,28)

def tube(points,r=.7):
    # sphere-capsule chain for relief strokes; all elements intentionally overlap
    ms=[]
    for u,v in zip(points[:-1],points[1:]):
        u=np.array(u);v=np.array(v);d=v-u
        m=tm.creation.cylinder(radius=r,height=np.linalg.norm(d),sections=12)
        m.apply_transform(tm.geometry.align_vectors([0,0,1],d));m.apply_translation((u+v)/2);ms.append(m)
    ms.extend(ell(q,[r,r,r],2) for q in points)
    return union(ms)

print('Sculpting lower shell...',flush=True)
# Sculpt envelope; dimensional changes beyond default require a new fit and wall audit.
base=rounded_box([68,29.4,39],12.8,[0,0,19.5])
parts=[base,ell([0,-12.5,18.5],[29,5.4,15])]
# Ears — integrated into the lower part.
for s in [-1,1]:
    parts.append(ell([s*34.4,-.3,18.4],[6.2,6,7.5]))
    # Front side locks; tucked roots at the hat line.
    parts.append(leaf([[s*26,-12,35.3],[s*30,-16,28],[s*27,-19,8],[s*22.8,-19.6,1.0]],6.1,3.6))
    parts.append(leaf([[s*29,-7,34],[s*34,-9,24],[s*34,-8,8],[s*39,-7,6]],4.2,3.8))
    # Three sweeping bangs open in the middle.
    parts.append(leaf([[s*13,-14,35.1],[s*13,-18,32],[s*16,-18.4,28],[s*18,-17.5,26]],3.7,2.8))
    parts.append(leaf([[s*22,-12,35.1],[s*21,-17,32],[s*19,-18,29],[s*16.5,-18,28]],4.0,3.0))
# Back hair, staggered locks around the rear silhouette.
for x in [-29,-21,-12,0,12,21,29]:
    y=11.0 if abs(x)<24 else 6.0
    endx=x+(3.5 if x>0 else -3.5 if x<0 else 0)
    parts.append(leaf([[x,y,34.8],[x,y+4,25],[x,y+4,8],[endx,y+4.5,3.5+2*(abs(x)/30)]],6.5,4.2))
for s in [-1,1]:
    parts.append(leaf([[s*28,9,24],[s*32,11,18],[s*31,12,7],[s*39,11,7]],4,3.8))
# Eyes, raised contours and large glints are physical relief, not image textures.
for s in [-1,1]:
    x=s*12.8
    parts.append(ell([x,-17.25,19],[4.8,1.9,6.2]))
    parts.append(ell([x-.6,-18.9,21.8],[2.7,.8,1.9]))
    parts.append(ell([x+.2,-19.0,16.2],[1.6,.7,1.0]))
    parts.append(ell([x+.3,-19.1,18.1],[.55,.4,.55],2))
    pts=[[x+u,-18.1,24.3+1.9*math.sin(math.pi*(u+6)/12)] for u in np.linspace(-6,6,18)]
    parts.append(tube(pts,1.05))
    pts=[[s*(9.5+u),-16.4,29+u*.42] for u in np.linspace(0,2.8,8)]
    parts.append(tube(pts,.52))
parts.append(ell([0,-17.4,15.7],[1.35,1.25,1.5]))
lower=union(parts)
lower=inter(lower,box([160,120,SEAM-GAP/2],[0,0,(SEAM-GAP/2)/2]))
# Real cavity, smooth rounded cuboid; extend a matching prism upward for insertion.
nominal=rounded_box([a.width,a.depth,a.height],10.5,[0,0,BOTTOM+a.height/2])
cavity=rounded_box([a.width+2*C,a.depth+2*C,a.height+2*C],10.5+C,[0,0,BOTTOM+a.height/2])
insertion=rounded_box([a.width+2*C,a.depth+2*C,90],10.5+C,[0,0,BOTTOM+45+10.5+C])
# The lower cup opens through a straight section, not a constricted spherical rim.
lower=diff(lower,[cavity,insertion])
# Interface seam & lid clearance. Broad rear scoop also exposes original hinge.
keepout=box([51,40,20],[0,27,SEAM+1.0])
lower=diff(lower,keepout)
# Functional bottom apertures: USB plug, acoustic openings, and front LED access.
cuts=[rounded_box([14,8,20],2.6,[0,0,0]),box([10,5,20],[13.5,0,0]),ell([-11.3,0,1],[2.2,2.2,9]),
      tm.creation.cylinder(radius=1.8,height=30,sections=40,transform=tm.transformations.compose_matrix(angles=[math.pi/2,0,0],translate=[0,-17,BOTTOM+26.31])),
      ell([0,-18,9.0],[3.6,2.8,2.0])]
# A generous opening exposes the device's lanyard recess instead of an unmeasured blind bore.
cuts.append(box([20,10,14],[36,1,26]))
# Shallow cheek marks.
for s in [-1,1]:
    for k in range(2):
        x=s*(22+k*1.3)
        cuts.append(tube([[x,-17.5,12.4],[x+s*.35,-17.7,10.8]],.30))
lower=diff(lower,cuts)

print('Sculpting independent beret lid...',flush=True)
# Smooth asymmetric loft; brim and button belong only to the upper print.
zs=np.array([SEAM+.3,38,42,47,52,57,61,64,65])
profiles=np.array([[0,0,38.8,17.7],[-.7,0,40,18.8],[-2,0,40.8,20.2],[-3.3,.4,39.5,20.6],[-4.4,.5,36,19.8],[-5,.6,29.5,17.1],[-5,.5,21.4,13],[-4,.5,10.5,7],[-3.5,.4,.6,.5]])
interp=PchipInterpolator(zs,profiles,axis=0)
rings=[[float(v[0]),float(v[1]),float(z),float(v[2]),float(v[3])] for z in np.linspace(zs[0],zs[-1],62) for v in [interp(z)]]
dome=rings_mesh(rings,112)
brim=rings_mesh([[0,-.2,z,rx,ry] for z,rx,ry in [(SEAM+.3,38.7,17.8),(SEAM+.8,39.4,18.5),(SEAM+2.2,39.5,18.8),(SEAM+3.2,38.5,18.1)]],112)
# Front fold climbs to the button in the same silhouette as the reference.
foldpts=[[float(x),float(-18.25+1.5*(abs(x)/32)**2),float(SEAM+2.1+5*math.exp(-((x-21)/8)**2))] for x in np.linspace(-34,34,80)]
fold=tube(foldpts,.95)
button=ell([26,-18.1,SEAM+7.2],[3.5,1.7,3.5])
upper=union([dome,brim,fold,button])
# Upper cavity keeps the curved ceiling, but has a fully open underside.
upper_open=rounded_box([a.width+2*C,a.depth+2*C,100],10.5+C,[0,0,SEAM-50+10.5+C])
# restrict the deep insertion cut to z <= seam; sphere corner of top must stay intact.
upper_open=inter(upper_open,box([130,80,100],[0,0,SEAM-50+1]))
upper=diff(upper,[cavity,upper_open,box([51,40,8],[0,27,SEAM+.5])])
# A restrained stitched meridian along the left crown, cut shallowly into the surface.
seampts=[]
for z in np.linspace(40,64,36):
    cx,cy,rx,ry=interp(z);t=-1.95+.15*(z-40)/24
    seampts.append([cx+rx*np.cos(t),cy+ry*np.sin(t),z])
upper=diff(upper,tube(seampts,.35))

# Remove the swept lid envelope from the rear lower hair for collision-free visual motion.
# Discrete 2.5 degree samples, and an expanded (0.35 mm) lid for manufacturing margin.
print('Relieving hinge sweep...',flush=True)
sweeps=[]
# Use a conservative solid convex envelope, expanded 0.35 mm in all axes.
# This contains the full cap (including its hollow interior) and gives clearance.
hull=upper.convex_hull
corners=np.array([[x,y,z] for x in [-.35,.35] for y in [-.35,.35] for z in [-.35,.35]])
sweep_envelope=tm.convex.convex_hull((hull.vertices[:,None,:]+corners[None,:,:]).reshape(-1,3))
for deg in np.arange(2.5,115.1,2.5):
    m=sweep_envelope.copy()
    m.apply_transform(tm.transformations.rotation_matrix(-math.radians(deg),[1,0,0],PIVOT))
    sweeps.append(m)
lower=diff(lower,union(sweeps))

# Small ring: print and fit this before the detailed shell. It is open through Z.
ring_out=rounded_box([a.width+2*C+4.8,a.depth+2*C+4.8,26],10.5+C+2.4,[0,0,13])
ring_in=rounded_box([a.width+2*C,a.depth+2*C,80],10.5+C,[0,0,20])
fit=inter(diff(ring_out,ring_in),box([100,60,5],[0,0,13]))
fit.apply_translation([0,0,-10.5])

# Discard sub-millimetre islands left by shallow decorative grooves.
for label in ['lower','upper']:
    m=locals()[label]; islands=sorted(m.split(only_watertight=False),key=lambda q:abs(q.volume),reverse=True)
    if len(islands)>1 and all(abs(q.volume)<1 for q in islands[1:]):
        print(label,'removed tiny decorative islands mm3:',sum(abs(q.volume) for q in islands[1:]),flush=True)
        if label=='lower': lower=islands[0]
        else: upper=islands[0]
metrics={}
for name,m in [('lower-shell',lower),('beret-lid',upper),('fit-ring',fit),('device-envelope',nominal)]:
    m.remove_unreferenced_vertices();m.fix_normals()
    comps=m.split(only_watertight=False)
    if not m.is_watertight or not m.is_volume or len(comps)!=1:
        raise ValueError(f'{name}: watertight={m.is_watertight}, components={[(len(c.faces),c.volume) for c in comps]}')
    m.export(OUT/(name+'.stl'))
    metrics[name]={'triangles':len(m.faces),'watertight':bool(m.is_watertight),'components':len(comps),'volume_mm3':round(m.volume,2),'bounds_mm':m.bounds.round(3).tolist(),'size_mm':m.extents.round(3).tolist()}
    print(name,metrics[name],flush=True)
# Print-ready cap: flip so crown grows from brim (open underside on plate); retain assembly export.
capprint=upper.copy();capprint.apply_translation([0,0,-upper.bounds[0,2]]);capprint.export(OUT/'beret-lid-print.stl')
# The lower mesh rests within 0.02 mm of Z=0. Select mm and place on bed in slicer.
checks=[]
for deg in np.arange(0,115.1,2.5):
    u=upper.copy();u.apply_transform(tm.transformations.rotation_matrix(-math.radians(deg),[1,0,0],PIVOT))
    overlap=inter(lower,u)
    checks.append({'angle_deg':float(deg),'intersection_mm3':round(abs(overlap.volume),7) if len(overlap.faces) else 0})
print('sweep intersections:',[c for c in checks if c['intersection_mm3']>.01],flush=True)
if any(c['intersection_mm3']>.01 for c in checks): raise ValueError('lid interference')
# Split proxy of the original device for assembly visuals; not a printable accessory.
inter(nominal,box([150,80,SEAM-3-.1],[0,0,(SEAM+3-.1)/2])).export(OUT/'device-lower-envelope.stl')
inter(nominal,box([150,80,60],[0,0,SEAM+30+.1])).export(OUT/'device-lid-envelope.stl')
# Device fit only validates the nominal approximation, not unmeasured radii.
for n,m in [('lower',lower),('upper',upper)]:
    overlap=inter(m,nominal)
    if len(overlap.faces) and abs(overlap.volume)>.01: raise ValueError(f'{n}: device overlap')
params={'units':'mm','device':{'width':a.width,'depth':a.depth,'height':a.height,'corner_radius_approx':10.5},'clearance_per_side':C,'device_bottom_z':BOTTOM,'seam_z':SEAM,'seam_height_assumed':a.seam_height,'split_gap':GAP,'hinge_pivot_illustrative':PIVOT.tolist(),'angle_max':115,'cavity_envelope':[a.width+2*C,a.depth+2*C,a.height+2*C],'prototype':True}
(ROOT/'assets'/'parameters.json').write_text(json.dumps(params,indent=2),encoding='utf8')
(ROOT/'docs'/'mesh-validation.json').write_text(json.dumps({'parameters':params,'meshes':metrics,'lid_sweep_samples':checks,'note':'Digital mesh checks only. Device corner profile and hinge axis approximate; physical fit, lid retention, touch pairing, cable and acoustics require a prototype.'},indent=2),encoding='utf8')
print('DONE',flush=True)
