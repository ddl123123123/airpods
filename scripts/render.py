"""Run: blender -b -t 4 --python scripts/render.py"""
import bpy, math, json
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH'
scene.display.render_aa='32'
shade=scene.display.shading;shade.light='STUDIO';shade.studio_light='paint.sl';shade.color_type='MATERIAL';shade.background_type='WORLD'
shade.show_shadows=True;shade.shadow_intensity=.25;shade.show_cavity=True;shade.cavity_type='WORLD'
shade.curvature_ridge_factor=1.1;shade.curvature_valley_factor=.9
scene.render.resolution_x=1400;scene.render.resolution_y=1400;scene.render.resolution_percentage=100
scene.world.color=(.88,.87,.82)
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.72,.74,.69,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.65
scene.view_settings.view_transform='AgX'
scene.render.image_settings.file_format='PNG'

def mat(name,color,rough=.72):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*color,1);n.inputs['Roughness'].default_value=rough;return m
ivory=mat('Warm unpainted prototype',(.68,.65,.58));sage=mat('Sage beret / colour study',(.31,.40,.29));floor=mat('Warm studio',(.88,.87,.82))

def load(file,material):
    bpy.ops.wm.stl_import(filepath=str(R/'models'/file));o=bpy.context.object;o.data.materials.append(material)
    for p in o.data.polygons:p.use_smooth=True
    normal=o.modifiers.new('Area weighted shading normals','WEIGHTED_NORMAL');normal.keep_sharp=True;normal.weight=50
    return o
body=load('lower-shell.stl',ivory);cap=load('beret-lid.stl',ivory)
# Hide original device envelope except for the exploded assembly study.
device=load('device-envelope.stl',mat('Nominal fit envelope',(.55,.62,.48)));device.hide_render=True
original=mat('Original case approximate envelope',(.91,.91,.88))
device_body=load('device-lower-envelope.stl',original);device_cap=load('device-lid-envelope.stl',original)
bpy.ops.mesh.primitive_plane_add(size=2000,location=(0,0,-.3));plane=bpy.context.object;plane.data.materials.append(floor)

def light(name,loc,power,size):
    d=bpy.data.lights.new(name,'AREA');o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;d.energy=power;d.shape='DISK';d.size=size;o.rotation_euler=(Vector((0,0,30))-o.location).to_track_quat('-Z','Y').to_euler()
light('Large softbox',(-70,-100,150),250000,110)
light('Front fill',(90,-30,75),80000,90)
light('Soft rim',(0,90,110),160000,80)
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO';cam.data.lens=50

def shot(name,loc,target,scale=108,w=1000,h=1000):
    cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
    scene.render.resolution_x=w;scene.render.resolution_y=h;scene.render.filepath=str(R/'assets'/name);bpy.ops.render.render(write_still=True)
shot('hero.png',(95,-180,100),(0,0,31),112)
shot('front.png',(0,-200,32),(0,0,32),105)
shot('side.png',(200,0,32),(0,0,32),105)
shot('back.png',(0,200,32),(0,0,32),105)
cap.data.materials[0]=sage
shot('sage.png',(95,-180,100),(0,0,31),112)
# Independent hat is raised, illustrating the mounting surfaces.
cap.location.z=37;device.hide_render=False;device.location.z=9;device_body.hide_render=True;device_cap.hide_render=True
shot('exploded.png',(90,-170,108),(0,0,46),131,w=900,h=1050)
device.hide_render=True;device_body.hide_render=False;device_cap.hide_render=False;cap.location.z=0;cap.data.materials[0]=ivory
# Place cap on an empty at the approximate original hinge axis.
pivot=Vector(json.loads((R/'assets/parameters.json').read_text())['hinge_pivot_illustrative']);cap.location=-pivot;device_cap.location=-pivot
bpy.ops.object.empty_add(location=pivot);hinge=bpy.context.object;cap.parent=hinge;device_cap.parent=hinge;hinge.rotation_euler.x=math.radians(-105)
shot('open.png',(100,-180,105),(0,0,40),120)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models'/'beret-studio.blend'))
