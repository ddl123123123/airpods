import * as THREE from 'three';
import { OrbitControls } from './vendor/OrbitControls.js';
import { STLLoader } from './vendor/STLLoader.js';

const stage = document.getElementById('viewer');
const status = document.getElementById('model-status');
const poster = document.getElementById('poster');
const modeButtons = [...document.querySelectorAll('[data-mode]')];
const viewButtons = [...document.querySelectorAll('[data-view]')];
const colorButtons = [...document.querySelectorAll('[data-color]')];
const slider = document.getElementById('lid-angle');
const output = document.getElementById('angle-value');
const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
let renderer, controls, camera, scene, lid, body, envelope, pivot, params, deviceBody, deviceLid;
let targetAngle = 0, angle = 0, lift = 0, targetLift = 0, flip = 0, targetFlip = 0;
let currentMode = 'closed', ready = false, raf;
let targetCamera = null, targetLook = null;
const colors = { ivory: [0xe7e3d8, 0xe7e3d8, '原型白'], sage: [0x809379, 0xe8e0ce, '苔绿帽'], rose: [0xb68d7d, 0xe8ded0, '陶粉帽'] };

function setPressed(buttons, selected, className) {
  for (const b of buttons) { const on = b === selected; b.classList.toggle(className, on); b.setAttribute('aria-pressed', String(on)); }
}
function smoothNormals(geometry) {
  // Area-weight shared normals so broad flat cheeks do not inherit star-shaped shading from tiny relief triangles.
  // Delivered vertex positions and all printable geometry are unchanged.
  const pos = geometry.attributes.position, normal = geometry.attributes.normal;
  const sums = new Map();
  const faceNormals=[];
  const va=new THREE.Vector3(),vb=new THREE.Vector3(),vc=new THREE.Vector3();
  for(let i=0;i<pos.count;i+=3){
    va.fromBufferAttribute(pos,i);vb.fromBufferAttribute(pos,i+1);vc.fromBufferAttribute(pos,i+2);
    faceNormals.push(vb.sub(va).cross(vc.sub(va)).clone());
  }
  for (let i=0;i<pos.count;i++) {
    const key = `${pos.getX(i).toFixed(4)},${pos.getY(i).toFixed(4)},${pos.getZ(i).toFixed(4)}`;
    let n = sums.get(key); if (!n) { n = new THREE.Vector3(); sums.set(key,n); }
    n.add(faceNormals[Math.floor(i/3)]);
  }
  for (const n of sums.values()) n.normalize();
  for (let i=0;i<pos.count;i++) {
    const n=sums.get(`${pos.getX(i).toFixed(4)},${pos.getY(i).toFixed(4)},${pos.getZ(i).toFixed(4)}`);
    normal.setXYZ(i,n.x,n.y,n.z);
  }
  normal.needsUpdate=true;
  return geometry;
}
function setMode(mode, updateSlider=true) {
  currentMode=mode; stage.dataset.mode=mode;
  setPressed(modeButtons,modeButtons.find(b=>b.dataset.mode===mode),'active');
  targetAngle=mode==='open'?105:0;
  targetLift=mode==='explode'?37:mode==='cavity'?63:0;
  targetFlip=mode==='cavity'?4.0:0;
  if(updateSlider){slider.value=String(targetAngle);output.value=`${targetAngle}°`;}
  if(envelope) envelope.visible=mode==='explode';
  if(deviceBody){deviceBody.visible=mode==='closed'||mode==='open';deviceLid.visible=deviceBody.visible;}
  document.querySelectorAll('.annotation').forEach(n=>n.style.visibility=mode==='closed'?'visible':'hidden');
  if(mode==='explode'||mode==='cavity') setView('iso',true);
  else if(controls) { targetLook=new THREE.Vector3(0,0,32); }
}
function setView(view, wide=false) {
  const positions={front:[0,-160,39],side:[160,0,40],back:[0,160,40],iso:[85,-155,90]};
  const p=positions[view]||positions.iso;
  targetCamera=new THREE.Vector3(...p);
  targetLook=new THREE.Vector3(0,0,wide?58:32);
  if(wide) targetCamera.multiplyScalar(1.5);
  setPressed(viewButtons,viewButtons.find(b=>b.dataset.view===view),'selected');
}
function fail(error) {
  console.error(error);status.textContent='静态模型预览';poster.hidden=false;
  document.getElementById('fallback').hidden=false;
  document.querySelectorAll('.controls button,.angle-control button,.angle-control input,.orientation button').forEach(b=>b.disabled=true);
  document.querySelectorAll('.annotation').forEach(n=>n.hidden=true);
  cancelAnimationFrame(raf);if(renderer)renderer.dispose();
}
async function init(){
  try {
    params=await fetch('./assets/parameters.json').then(r=>{if(!r.ok)throw Error('Parameter file unavailable');return r.json()});
    document.getElementById('device-size').textContent=[params.device.width,params.device.height,params.device.depth].map(n=>n.toFixed(2)).join(' × ');
    document.getElementById('clearance-number').textContent=params.clearance_per_side.toFixed(2);document.getElementById('gap-number').textContent=params.split_gap.toFixed(2);
    scene=new THREE.Scene();
    camera=new THREE.PerspectiveCamera(30,1,.1,1200);camera.up.set(0,0,1);camera.position.set(85,-155,90);
    renderer=new THREE.WebGLRenderer({alpha:true,antialias:true,powerPreference:'low-power'});
    renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setClearColor(0,0);
    renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
    renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.35;
    stage.appendChild(renderer.domElement);
    renderer.domElement.setAttribute('aria-label','三维模型，可使用下方按钮切换视角和开盖状态');
    renderer.domElement.addEventListener('webglcontextlost',e=>{e.preventDefault();fail(new Error('WebGL context lost'));});
    controls=new OrbitControls(camera,renderer.domElement);controls.target.set(0,0,32);controls.enableDamping=true;controls.dampingFactor=.08;controls.enablePan=true;
    controls.minDistance=105;controls.maxDistance=340;controls.maxPolarAngle=Math.PI*.95;
    controls.addEventListener('start',()=>{targetCamera=null;targetLook=null;viewButtons.forEach(b=>{b.classList.remove('selected');b.setAttribute('aria-pressed','false')})});
    scene.add(new THREE.HemisphereLight(0xfffcf0,0x747b69,2.1));
    const key=new THREE.DirectionalLight(0xfff4df,3.6);key.position.set(-55,-85,140);key.castShadow=true;key.shadow.mapSize.set(1024,1024);
    key.shadow.camera.left=-110;key.shadow.camera.right=110;key.shadow.camera.top=140;key.shadow.camera.bottom=-100;key.shadow.camera.far=450;key.shadow.normalBias=.06;key.shadow.bias=-.00015;key.shadow.radius=4;scene.add(key);
    const fill=new THREE.DirectionalLight(0xe1e8ed,1.1);fill.position.set(100,0,70);scene.add(fill);
    const rim=new THREE.DirectionalLight(0xfffdf3,1.6);rim.position.set(-20,85,100);scene.add(rim);
    const floor=new THREE.Mesh(new THREE.PlaneGeometry(400,400),new THREE.ShadowMaterial({opacity:.075}));floor.position.z=-.35;floor.receiveShadow=true;scene.add(floor);
    const loader=new STLLoader();
    const [lowerGeometry,lidGeometry,deviceGeometry,deviceLowerGeometry,deviceLidGeometry]=await Promise.all(['lower-shell','beret-lid','device-envelope','device-lower-envelope','device-lid-envelope'].map(n=>loader.loadAsync(`./models/${n}.stl`)));
    const material=()=>new THREE.MeshStandardMaterial({color:colors.ivory[0],roughness:.73,metalness:0});
    body=new THREE.Mesh(smoothNormals(lowerGeometry),material());body.castShadow=true;body.receiveShadow=true;scene.add(body);
    pivot=new THREE.Vector3(...params.hinge_pivot_illustrative);
    lid=new THREE.Group();lid.position.copy(pivot);scene.add(lid);
    const lidMesh=new THREE.Mesh(smoothNormals(lidGeometry),material());lidMesh.position.copy(pivot).multiplyScalar(-1);lidMesh.castShadow=true;lidMesh.receiveShadow=true;lid.add(lidMesh);
    const deviceMaterial=new THREE.MeshStandardMaterial({color:0xf5f4f0,roughness:.4});
    deviceBody=new THREE.Mesh(smoothNormals(deviceLowerGeometry),deviceMaterial);scene.add(deviceBody);
    deviceLid=new THREE.Mesh(smoothNormals(deviceLidGeometry),deviceMaterial);deviceLid.position.copy(pivot).multiplyScalar(-1);lid.add(deviceLid);
    envelope=new THREE.Mesh(deviceGeometry,new THREE.MeshPhysicalMaterial({color:0xb3c4aa,transparent:true,opacity:.25,roughness:.45,depthWrite:false}));envelope.position.z=9;envelope.visible=false;scene.add(envelope);
    const edges=new THREE.LineSegments(new THREE.EdgesGeometry(deviceGeometry,20),new THREE.LineBasicMaterial({color:0x718a67,transparent:true,opacity:.35}));envelope.add(edges);
    ready=true;poster.hidden=true;status.textContent='已加载 · mm / V1.0';stage.dataset.loaded='true';
    const resize=()=>{const {width,height}=stage.getBoundingClientRect();renderer.setSize(width,height);camera.aspect=width/height;camera.updateProjectionMatrix();};new ResizeObserver(resize).observe(stage);resize();
    let frames=0,last=performance.now();
    function animate(now){
      raf=requestAnimationFrame(animate);frames++;
      const dt=Math.min((now-last)/1000,.25);last=now;const ease=reduceMotion?1:1-Math.exp(-dt*8);
      angle+=(targetAngle-angle)*ease;lift+=(targetLift-lift)*ease;flip+=(targetFlip-flip)*ease;
      lid.rotation.x=-THREE.MathUtils.degToRad(angle)+flip;lid.position.copy(pivot);lid.position.z+=lift;
      if(targetCamera){camera.position.lerp(targetCamera,ease);if(camera.position.distanceTo(targetCamera)<.05)targetCamera=null;}
      if(targetLook){controls.target.lerp(targetLook,ease);if(controls.target.distanceTo(targetLook)<.05)targetLook=null;}
      controls.update();renderer.render(scene,camera);
    }raf=requestAnimationFrame(animate);
    // Exposed read-only QA snapshot for checking that interaction changes the real mesh.
    window.beretState=()=>({ready,frames,mode:currentMode,angle,targetAngle,lift,flip,triangles:(lowerGeometry.attributes.position.count+lidGeometry.attributes.position.count)/3});
    colorButtons.forEach(b=>b.addEventListener('click',()=>{const c=colors[b.dataset.color];lidMesh.material.color.setHex(c[0]);body.material.color.setHex(c[1]);document.getElementById('color-name').textContent=c[2];setPressed(colorButtons,b,'selected');}));
  }catch(e){fail(e)}
}
modeButtons.forEach(b=>b.addEventListener('click',()=>{if(ready)setMode(b.dataset.mode)}));
viewButtons.forEach(b=>b.addEventListener('click',()=>{if(ready)setView(b.dataset.view,currentMode==='explode'||currentMode==='cavity')}));
slider.addEventListener('input',()=>{if(!ready)return;targetLift=0;targetFlip=0;targetAngle=Number(slider.value);output.value=`${slider.value}°`;currentMode=targetAngle===0?'closed':'open';setPressed(modeButtons,modeButtons.find(b=>b.dataset.mode===currentMode),'active');envelope.visible=false;deviceBody.visible=true;deviceLid.visible=true;document.querySelectorAll('.annotation').forEach(n=>n.style.visibility=targetAngle===0?'visible':'hidden');targetLook=new THREE.Vector3(0,0,32);});
document.getElementById('reset-view').addEventListener('click',()=>{if(ready){setMode('closed');setView('iso')}});
init();
