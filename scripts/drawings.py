"""Project delivered STL geometry and draw a millimetre A3 engineering study."""
from pathlib import Path
import numpy as np,trimesh as tm, json
from scipy.spatial import ConvexHull
from xml.sax.saxutils import escape
R=Path(__file__).resolve().parents[1]
P=json.loads((R/'assets/parameters.json').read_text());DV=P['device'];C=P['clearance_per_side'];SZ=P['seam_z']
lo=tm.load(R/'models/lower-shell.stl');up=tm.load(R/'models/beret-lid.stl');dev=tm.load(R/'models/device-envelope.stl')
allm=tm.util.concatenate([lo,up]);W,D,H=allm.extents
s=['<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm" viewBox="0 0 420 297">', '<defs><pattern id="hatch" width="2" height="2" patternUnits="userSpaceOnUse" patternTransform="rotate(35)"><path d="M0 0V2" stroke="#bfc7b7" stroke-width=".3"/></pattern><marker id="arrow" markerWidth="5" markerHeight="5" refX="2.5" refY="2.5" orient="auto-start-reverse"><path d="M5 0L0 2.5L5 5" fill="none" stroke="#89977d" stroke-width=".7"/></marker></defs><rect width="420" height="297" fill="#fbfaf6"/><g font-family="Noto Sans CJK SC, sans-serif" fill="#304335">']
def text(x,y,t,size=2.8,fill='#304335',anchor='start'):
 s.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}">{escape(t)}</text>')
def line(x1,y1,x2,y2,color='#c1c9b8',dash='',width=.2):
 s.append(f'<path d="M{x1} {y1}L{x2} {y2}" fill="none" stroke="{color}" stroke-width="{width}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
def path(points,fill='none',stroke='#42533e',width=.28,close=True):
 q=' '.join(f'{p[0]:.3f},{p[1]:.3f}' for p in points)
 s.append(f'<{ "polygon" if close else "polyline"} points="{q}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linejoin="round"/>')
def dim(x1,y1,x2,y2,label,tx=None,ty=None):
 s.append(f'<path d="M{x1} {y1}L{x2} {y2}" stroke="#89977d" stroke-width=".2" marker-start="url(#arrow)" marker-end="url(#arrow)"/>')
 text(tx if tx is not None else (x1+x2)/2,ty if ty is not None else (y1+y2)/2-1.8,label,2.5,'#74836b','middle')
def contour(mesh,axes,ox,oy,fill):
 # Boundary of union of projected triangles preserves hair gaps and side silhouette.
 from shapely.geometry import Polygon
 from shapely.ops import unary_union
 verts=mesh.vertices[:,axes]
 # silhouette faces: front-facing boundary union; simplification below is 0.05 mm.
 polys=[Polygon(verts[f]) for f in mesh.faces if abs(np.linalg.det(np.stack([verts[f[1]]-verts[f[0]],verts[f[2]]-verts[f[0]]])))>.002]
 g=unary_union(polys).simplify(.05,preserve_topology=True)
 for p in getattr(g,'geoms',[g]):
  pts=np.asarray(p.exterior.coords);pts[:,0]+=ox;pts[:,1]=oy-pts[:,1];path(pts,fill)
  for hole in p.interiors:
   pts=np.array(hole.coords);pts[:,0]+=ox;pts[:,1]=oy-pts[:,1];path(pts,'#fbfaf6',width=.16)

text(15,18,'BERET / 贝雷帽女孩',7)
text(15,25,'AIRPODS PRO 3 · 参考三视图重建 · 分体保护壳 · V1.0 打印试配版',3,'#7c8875')
text(405,18,'DESIGN SHEET 01 / 01',3,'#7c8875','end');text(405,24,'A3  ·  mm  ·  SCALE 1:1 @ A3',2.5,'#7c8875','end')
line(15,31,405,31)
# 1:1 orthographic silhouettes. Positions have deliberately aligned baselines.
for axes,ox,oy,title in [([0,2],68,122,'01  FRONT / 正面'),([1,2],180,122,'02  SIDE / 侧面'),([0,2],287,122,'03  REAR / 背面')]:
 contour(lo,axes,ox,oy,'#e9ecdf');contour(up,axes,ox,oy,'#d5ddca')
 # original device envelope projected as a dashed design envelope (rectangle, not a tracing claim)
 b=dev.bounds
 x0=b[0,axes[0]]+ox;x1=b[1,axes[0]]+ox;z0=oy-b[0,2];z1=oy-b[1,2]
 s.append(f'<rect x="{x0}" y="{z1}" width="{x1-x0}" height="{z0-z1}" rx="10.5" fill="none" stroke="#9baa8e" stroke-width=".22" stroke-dasharray="1.4 1"/>')
 line(ox,48,ox,129,'#d3d8cc','1 1');text(ox,139,title,3,anchor='middle')
# Relief outlines from front-plane section contours help read eyes/hair in this orthographic sheet.
for y in [-17.4,-18.6]:
 section=lo.section(plane_origin=[0,y,0],plane_normal=[0,1,0])
 if section:
  for pts in section.discrete:
   q=pts[:,[0,2]].copy();q[:,0]+=68;q[:,1]=122-q[:,1];path(q,'none','#7f8f73',.18,False)
# outer dimensions from actual mesh bounds
x0,x1=allm.bounds[:,0];z0,z1=allm.bounds[:,2]
line(68+x0,56,68+x0,43);line(68+x1,56,68+x1,43);dim(68+x0,45,68+x1,45,f'{W:.2f} overall')
line(68+x0-3,122-z0,17,122-z0);line(68+x0-3,122-z1,17,122-z1);dim(19,122-z0,19,122-z1,f'{H:.2f}',tx=13,ty=91)
y0,y1=allm.bounds[:,1];line(180+y0,56,180+y0,43);line(180+y1,56,180+y1,43);dim(180+y0,45,180+y1,45,f'{D:.2f} depth')
# split gap magnified callout
line(105,122-SZ,121,77,'#98a98c');text(123,75,f"{P['split_gap']:.2f} 分缝",2.7);text(123,80,'帽盖与下壳独立打印',2.3,'#7c8875')
line(15,149,405,149)
text(17,161,'04  SECTION A–A / 中央纵截面',3.3)
# middle X section in YZ plane, enlarged 1.1x to make wall and cavity legible.
for m in [lo,up]:
 section=m.section(plane_origin=[0,0,0],plane_normal=[1,0,0])
 if section:
  for pts in section.discrete:
   q=pts[:,[1,2]].copy();q[:,0]=q[:,0]*1.1+56;q[:,1]=239-q[:,1]*1.1;path(q,'url(#hatch)','#536647',.3,False)
text(21,248,'Hinge relief / 后侧开盖避让',2.5,'#7c8875')
text(105,161,'05  FIT PARAMETERS / 装配参数',3.3)
rows=[('充电盒包络 W × H × D',f"{DV['width']:.2f} × {DV['height']:.2f} × {DV['depth']:.2f}"),('内腔包络 W × H × D',f"{DV['width']+2*C:.2f} × {DV['height']+2*C:.2f} × {DV['depth']+2*C:.2f}"),('默认单边余量 / 首样',f'{C:.2f} / 可调 0.15–0.65'),('下壳分割高度 / 自设备底部',f"{P['seam_height_assumed']:.2f} / 待实测校准"),('内腔圆角 / 工程近似',f"R{DV['corner_radius_approx']:.2f} + {C:.2f} 余量"),('底部 USB-C 开口','14.00 × 8.00'),('正面指示灯通孔','Ø3.60 / 高 26.31'),('后侧主避让宽度','51.00 + 帽盖扫掠修形')]
for i,(k,v) in enumerate(rows):
 y=173+i*8.7;line(105,y+3,245,y+3);text(105,y,k,2.6,'#7c8875');text(245,y,v,2.6,anchor='end')
text(268,161,'06  PRINT & ASSEMBLY / 制作要点',3.3)
notes=['① 先打印 5 mm 试配环，检查松紧与装入方向。','② 优先 TPU 95A；0.4 喷嘴，0.16–0.20 层高。','③ 下壳底朝下；帽子开口朝下，需支撑内顶。','④ 浮雕外侧与悬垂发梢按切片预览添加支撑。','⑤ 帽盖用薄型可移除胶片固定于原仓上盖。','⑥ 禁止胶片跨越分缝；外壳借用原设备铰链。','⑦ 先手动慢开，检查碰撞、线缆和各开口。','⑧ 厚发型会影响无线充电；默认拆壳充电。']
for i,n in enumerate(notes):text(268,173+i*8.7,n,2.6,'#6c7d62')
line(15,257,405,257)
text(15,266,'验证范围：STL 闭合 / 单连通体 / 名义设备包络无重叠 / 帽盖 0–115° 每 2.5° 采样检查。',2.7)
text(15,273,'待实测：设备曲率、铰链轴、帽盖固定、触控配对、接口与挂绳位置。数字验证不等于实物适配。',2.7,'#8b774d')
text(15,285,'Nominal device dimensions: Apple developer dimensional drawing · 2025-09-09 revision · User reference supplies character styling.',2.4,'#7c8875')
text(405,285,'BERET / PROTOTYPE',2.7,'#7c8875','end')
s.append('</g></svg>');(R/'docs/design-sheet.svg').write_text('\n'.join(s),encoding='utf8')
print('drawing exported',W,D,H)
