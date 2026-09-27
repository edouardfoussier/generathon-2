/**
 * Procedural, editable storyboard maquettes — not reconstructed photo meshes.
 * Three.js 0.180.0 is vendored locally. No requests leave this module.
 *
 * createSceneViewer(element, { onChange, onError }) ->
 *   load(scene), update(partialBlocking), setCamera(preset|camera), play(),
 *   pause(), capture(): PNG data URL, exportGLB(): Promise<Blob>, dispose().
 * onChange receives { type, blocking, selectedId }. Alt-drag moves an actor
 * or custom prop on the floor; ordinary drag orbits, wheel zooms.
 */
import * as THREE from './vendor/three/build/three.module.js';
import { OrbitControls } from './vendor/three/examples/jsm/controls/OrbitControls.js';
import { GLTFExporter } from './vendor/three/examples/jsm/exporters/GLTFExporter.js';

const PI = Math.PI;
const LOCATIONS = ['attic', 'basketball', 'salsa', 'wedding', 'nursery', 'handover', 'product'];
const CREAM = '#efe6d2';
const clamp = (x, a, b) => Math.min(b, Math.max(a, Number.isFinite(+x) ? +x : a));
const clone = value => JSON.parse(JSON.stringify(value));
const vector = (value, fallback = [0, 0, 0]) => Array.isArray(value) && value.length >= 3
  ? value.slice(0, 3).map((x, i) => Number.isFinite(+x) ? +x : fallback[i]) : [...fallback];
const color = (value, fallback) => {
  if (typeof value === 'string' && (/^#[a-f\d]{3,8}$/i.test(value) || /^[a-z]+$/i.test(value))) return value;
  return fallback;
};

function material(value, roughness = .8, extra = {}) {
  return new THREE.MeshStandardMaterial({ color: value, roughness, metalness: 0, ...extra });
}
function mesh(parent, geometry, mat, position = [0, 0, 0], name = '') {
  const item = new THREE.Mesh(geometry, mat);
  item.position.fromArray(position);
  item.name = name;
  item.castShadow = true;
  item.receiveShadow = true;
  parent.add(item);
  return item;
}
function box(parent, size, pos, mat, name = '') {
  return mesh(parent, new THREE.BoxGeometry(...size), mat, pos, name);
}
function ellipsoid(parent, scale, pos, mat, name = '') {
  const item = mesh(parent, new THREE.SphereGeometry(1, 20, 14), mat, pos, name);
  item.scale.fromArray(scale);
  return item;
}
function cylinder(parent, radius, height, pos, mat, name = '', radiusTop = radius) {
  return mesh(parent, new THREE.CylinderGeometry(radiusTop, radius, height, 16), mat, pos, name);
}
function beam(parent, a, b, radius, mat, name = '') {
  const start = new THREE.Vector3(...a), end = new THREE.Vector3(...b);
  const direction = end.clone().sub(start);
  const item = cylinder(parent, radius, direction.length(), start.clone().add(end).multiplyScalar(.5).toArray(), mat, name);
  item.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), direction.normalize());
  return item;
}
function tube(parent, points, radius, mat, name = '') {
  const curve = new THREE.CatmullRomCurve3(points.map(v => new THREE.Vector3(...v)));
  return mesh(parent, new THREE.TubeGeometry(curve, 36, radius, 8, false), mat, [0, 0, 0], name);
}
function group(parent, name, pos = [0, 0, 0]) {
  const result = new THREE.Group();
  result.name = name;
  result.position.fromArray(pos);
  parent.add(result);
  return result;
}

function sneaker(parent, pos = [0, 0, 0], size = 1, canvasColor = '#202329', name = 'Canvas high-top') {
  const shoe = group(parent, name, pos);
  shoe.scale.setScalar(size);
  const canvas = material(canvasColor, .95), rubber = material(CREAM, .8), ink = material('#20222a');
  // A single rounded footprint keeps the outsole connected under the toe.
  const footprint = new THREE.Shape();
  footprint.moveTo(-.10, -.158);
  footprint.quadraticCurveTo(-.126, -.158, -.126, -.11);
  footprint.lineTo(-.126, .18);
  footprint.bezierCurveTo(-.126, .28, -.078, .33, 0, .334);
  footprint.bezierCurveTo(.078, .33, .126, .28, .126, .18);
  footprint.lineTo(.126, -.11);
  footprint.quadraticCurveTo(.126, -.158, .10, -.158);
  footprint.closePath();
  const soleGeometry = new THREE.ExtrudeGeometry(footprint, { depth: .052, bevelEnabled: true, bevelSegments: 2, steps: 1, bevelSize: .004, bevelThickness: .003, curveSegments: 12 });
  soleGeometry.rotateX(PI / 2);
  soleGeometry.translate(0, .052, 0);
  mesh(shoe, soleGeometry, rubber, [0, 0, 0], 'Continuous rounded rubber sole');
  const stripeGeometry = new THREE.ExtrudeGeometry(footprint, { depth: .006, bevelEnabled: false, curveSegments: 12 });
  stripeGeometry.rotateX(PI / 2);
  stripeGeometry.translate(0, .042, 0);
  const stripe = mesh(shoe, stripeGeometry, ink, [0, 0, 0], 'Midsole pinstripe');
  stripe.scale.set(1.009, 1, 1.009);
  // Lofted half-ellipses share a flat base on the sole: no floating toe sphere.
  const upper = (sections, mat, label) => {
    const vertices = [], indices = [], steps = 12;
    for (const [z, width, height] of sections) for (let j = 0; j <= steps; j++) {
      const angle = PI - j / steps * PI;
      vertices.push(Math.cos(angle) * width, .053 + Math.sin(angle) * height, z);
    }
    for (let i = 0; i < sections.length - 1; i++) for (let j = 0; j < steps; j++) {
      const a = i * (steps + 1) + j, b = a + steps + 1;
      indices.push(a, b, a + 1, b, b + 1, a + 1);
    }
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
    geometry.setIndex(indices);
    geometry.computeVertexNormals();
    return mesh(shoe, geometry, mat, [0, 0, 0], label);
  };
  // End the canvas just inside the cap lip, avoiding intersecting toe surfaces.
  upper([[-.14, .085, .115], [-.07, .11, .145], [.035, .117, .12], [.145, .119, .078]], canvas, 'Connected canvas upper');
  cylinder(shoe, .102, .15, [0, .185, -.065], canvas, 'High ankle', .093);
  upper([[.14, .124, .087], [.21, .116, .073], [.275, .088, .047], [.316, .038, .015], [.331, .003, .001]], rubber, 'Low attached rubber toe cap');
  const tongue = box(shoe, [.085, .018, .19], [0, .182, .01], canvas, 'Tongue');
  tongue.rotation.x = .20;
  for (let i = 0; i < 5; i++) {
    const z = -.055 + i * .035;
    beam(shoe, [-.047, .199 - i * .008, z], [.047, .199 - i * .008, z + .018], .006, rubber, 'Lace');
    beam(shoe, [.047, .200 - i * .008, z], [-.047, .200 - i * .008, z + .018], .006, rubber, 'Lace');
  }
  const patch = cylinder(shoe, .034, .005, [.102, .19, -.068], rubber, 'Ankle roundel');
  patch.rotation.z = PI / 2;
  const star = new THREE.Shape();
  for (let i = 0; i < 10; i++) {
    const a = i * PI / 5 - PI / 2, r = i % 2 ? .009 : .021;
    if (!i) star.moveTo(Math.cos(a) * r, Math.sin(a) * r);
    else star.lineTo(Math.cos(a) * r, Math.sin(a) * r);
  }
  star.closePath();
  const emblem = mesh(shoe, new THREE.ShapeGeometry(star), ink, [.106, .19, -.068]);
  emblem.rotation.y = PI / 2;
  return shoe;
}

function character(parent, definition, index, location) {
  const isRafa = /rafa|father|dad|père/i.test(`${definition.id} ${definition.label}`);
  const isLuna = /luna/i.test(`${definition.id} ${definition.label}`);
  const isElena = /elena/i.test(`${definition.id} ${definition.label}`);
  const numericAge = Number(definition.age);
  const isChild = Number.isFinite(numericAge) && numericAge > 0 && numericAge < 14;
  const isSenior = Number.isFinite(numericAge) && numericAge >= 60;
  const childScale = isChild ? .5 + clamp(numericAge / 26, .1, .48) : 1;
  const actor = group(parent, definition.label || definition.id || `Personnage ${index + 1}`, vector(definition.position, [index ? .65 : -.65, 0, 0]));
  actor.userData = { entityId: definition.id, kind: 'character', age: definition.age, label: definition.label, proceduralMaquette: true };
  actor.scale.setScalar(childScale * clamp(definition.scale ?? 1, .3, 2));
  actor.rotation.y = Number(definition.rotation ?? 0) || 0;
  const basePosition = actor.position.clone();
  const skin = material(color(definition.skinColor, isRafa ? '#b77855' : '#d2a17b'));
  if (definition.age !== undefined && numericAge === 0) {
    const torso = group(actor, 'Swaddled baby');
    ellipsoid(torso, [.15, .14, .29], [0, 0, -.03], material(color(definition.color, '#efe3bc')), 'Blanket');
    const head = group(torso, 'Baby head', [0, .035, .24]);
    ellipsoid(head, [.115, .105, .11], [0, 0, 0], skin);
    for (const side of [-1, 1]) ellipsoid(head, [.016, .004, .012], [side * .038, .075, .059], material('#735544'), 'Closed eye');
    torso.rotation.z = -.1;
    return { root: actor, torso, head, arms: [], legs: [], basePosition, baseRotation: actor.rotation.y, index, definition, isBaby: true };
  }
  const hair = material(color(definition.hairColor, isSenior ? '#77736d' : '#352c29'));
  const outfitColor = color(definition.color, isRafa ? '#aa7555' : '#708881');
  const shirt = material(isLuna ? '#444345' : outfitColor);
  const pants = material(color(definition.pantsColor, isLuna ? outfitColor : isRafa ? '#434d62' : '#51627a'));
  const basketballKit = isRafa && location === 'basketball';
  const skirt = isElena && ['salsa', 'wedding'].includes(location);
  const face = material('#26252a');
  const torso = group(actor, 'Torso');
  ellipsoid(torso, [.255, .315, .155], [0, 1.175, 0], shirt, 'Clothing');
  box(torso, [.25, .035, .18], [0, .9, 0], pants, 'Waist');
  if (skirt) cylinder(torso, .38, .57, [0, .69, 0], shirt, 'Dress skirt', .22);
  if (isLuna) for (const side of [-1, 1]) box(torso, [.11, .17, .055], [side * .155, .68, .08], pants, 'Cargo pocket');
  cylinder(torso, .068, .15, [0, 1.5, 0], skin, 'Neck');
  const head = group(torso, 'Head', [0, 1.68, 0]);
  ellipsoid(head, [.185, .218, .175], [0, 0, 0], skin, 'Face');
  const crown = mesh(head, new THREE.SphereGeometry(1, 20, 14, 0, PI * 2, 0, PI * .53), hair, [0, .037, -.008], 'Hair');
  crown.scale.set(.194, .203, .186);
  const curlCount = isRafa ? 7 : 11;
  for (let i = 0; i < curlCount; i++) {
    const angle = i / (curlCount - 1) * PI * 1.3 + PI * .35;
    ellipsoid(head, isRafa ? [.065, .065, .065] : [.07, .12, .085], [Math.cos(angle) * .165, isRafa ? .1 : -.02, Math.sin(angle) * .13 - .045], hair, 'Hair curl');
  }
  if (isLuna) {
    ellipsoid(head, [.11, .18, .12], [0, -.08, -.22], hair, 'Low curly ponytail');
    ellipsoid(head, [.12, .16, .1], [.02, -.23, -.25], hair, 'Ponytail curls');
  }
  for (const side of [-1, 1]) {
    ellipsoid(head, [.014, .019, .009], [side * .063, .012, .164], face, 'Eye');
    ellipsoid(head, [.025, .038, .023], [side * .18, -.01, 0], skin, 'Ear');
  }
  ellipsoid(head, [.022, .028, .025], [0, -.027, .174], skin, 'Nose');
  tube(head, [[-.043, -.078, .162], [0, -.087, .173], [.043, -.078, .162]], .0045, material('#875848'), 'Smile');
  const arms = [], legs = [];
  for (const side of [-1, 1]) {
    const arm = group(torso, `${side < 0 ? 'Right' : 'Left'} shoulder`, [side * .274, 1.39, 0]);
    arm.rotation.z = side * .11;
    ellipsoid(arm, [.081, .167, .087], [0, -.139, 0], basketballKit ? skin : shirt, basketballKit ? 'Bare upper arm' : 'Sleeve');
    const elbow = group(arm, 'Elbow', [0, -.285, 0]);
    ellipsoid(elbow, [.061, .153, .06], [0, -.13, 0], skin, 'Forearm');
    ellipsoid(elbow, [.064, .085, .043], [0, -.28, .006], skin, 'Hand');
    arms.push({ joint: arm, elbow, side });
    const leg = group(actor, `${side < 0 ? 'Right' : 'Left'} hip`, [side * .122, .89, 0]);
    cylinder(leg, .096, .4, [0, -.19, 0], basketballKit || skirt ? skin : pants, 'Upper leg', .102);
    if (basketballKit) cylinder(leg, .115, .22, [0, -.07, 0], pants, 'Basketball shorts', .13);
    const knee = group(leg, 'Knee', [0, -.395, 0]);
    cylinder(knee, .076, .38, [0, -.18, 0], basketballKit || skirt ? skin : pants, 'Lower leg', .09);
    if (basketballKit) {
      cylinder(knee, .078, .17, [0, -.31, 0], material(CREAM), 'Tube sock');
      for (const y of [-.25, -.27]) cylinder(knee, .079, .012, [0, y, 0], material('#7f4244'), 'Sock stripe');
    }
    const foot = sneaker(knee, [0, -.465, .045], 1, color(definition.shoeColor, '#202329'), 'Black canvas sneaker');
    legs.push({ joint: leg, knee, foot, side });
  }
  return { root: actor, torso, head, arms, legs, basePosition, baseRotation: actor.rotation.y, index, definition };
}

function plant(parent, pos, size = 1) {
  const g = group(parent, 'Plant', pos);
  g.scale.setScalar(size);
  cylinder(g, .21, .35, [0, .175, 0], material('#b57858'), 'Terracotta pot', .28);
  const green = material('#68816a');
  for (let i = 0; i < 8; i++) {
    const a = i * 2.399;
    const end = [Math.cos(a) * .27, .65 + (i % 3) * .16, Math.sin(a) * .27];
    beam(g, [0, .3, 0], end, .012, material('#5b6945'));
    const leaf = ellipsoid(g, [.1, .27, .035], end, green);
    leaf.rotation.set(.25, a, -.45 + (i % 2) * .9);
  }
  return g;
}
function bench(parent, pos, width = 1.8, mat = material('#a67b51')) {
  const g = group(parent, 'Oak bench', pos);
  box(g, [width, .11, .5], [0, .47, 0], mat);
  for (const x of [-width * .41, width * .41]) for (const z of [-.16, .16]) box(g, [.09, .44, .09], [x, .22, z], mat);
  return g;
}
function chest(parent, pos) {
  const g = group(parent, 'Memory trunk', pos), wood = material('#795b45'), metal = material('#c5a46d', .5, { metalness: .6 });
  box(g, [1.45, .55, .76], [0, .3, 0], wood);
  box(g, [1.28, .025, .58], [0, .59, 0], material('#302a29'));
  for (const x of [-.53, .53]) box(g, [.05, .57, .785], [x, .3, 0], metal);
  const lid = group(g, 'Open trunk lid', [0, .59, -.38]);
  lid.rotation.x = -.88;
  box(lid, [1.46, .07, .77], [0, 0, .385], wood);
  for (const x of [-.53, .53]) box(lid, [.055, .076, .78], [x, 0, .385], metal);
  sneaker(g, [-.17, .61, .05], .85);
  sneaker(g, [.16, .61, .05], .85);
  return g;
}
function basketball(parent, pos) {
  const g = group(parent, 'Basketball', pos), orange = material('#c87f42', .93), dark = material('#493e33');
  ellipsoid(g, [.145, .145, .145], [0, 0, 0], orange);
  for (const rot of [[0, 0, 0], [PI / 2, 0, 0], [0, PI / 2, 0]]) {
    const ring = mesh(g, new THREE.TorusGeometry(.145, .003, 5, 36), dark);
    ring.rotation.fromArray(rot);
  }
  return g;
}
function chair(parent, pos, rotation = 0) {
  const g = group(parent, 'Chair', pos), mat = material('#a88463');
  g.rotation.y = rotation;
  box(g, [.46, .07, .45], [0, .46, 0], mat);
  for (const x of [-.18, .18]) for (const z of [-.16, .16]) box(g, [.047, .45, .047], [x, .23, z], mat);
  for (const x of [-.18, .18]) box(g, [.047, .55, .047], [x, .72, -.18], mat);
  box(g, [.42, .15, .045], [0, .9, -.18], mat);
  return g;
}
function stringLights(parent, z, height, warm) {
  const cable = material('#5c594d'), bulb = material('#ffe5aa', .35, { emissive: '#ffc86e', emissiveIntensity: 1.7 });
  const points = Array.from({ length: 13 }, (_, i) => { const x = -4 + i * 2 / 3; return [x, height - .55 * Math.sin(i / 12 * PI), z]; });
  tube(parent, points, .011, cable, 'Garland cable');
  for (let i = 0; i < points.length; i++) {
    const [x, y, depth] = points[i];
    beam(parent, [x, y, depth], [x, y - .09, depth], .01, cable);
    ellipsoid(parent, [.055, .075, .055], [x, y - .13, depth], bulb, 'Festoon bulb');
  }
  if (warm) {
    const light = new THREE.PointLight('#ffcd88', 5, 8, 2);
    light.position.set(0, height - .7, z);
    parent.add(light);
  }
}
function roomWindow(parent, x = -2.5, z = -3.06) {
  const frame = material('#d9c7a9'), glass = material('#c4d7d6', .45, { emissive: '#adc7c7', emissiveIntensity: .12 });
  box(parent, [1.45, 1.8, .04], [x, 1.85, z], glass, 'Window light');
  for (const dx of [-.75, 0, .75]) box(parent, [.06, 1.9, .09], [x + dx, 1.85, z + .04], frame);
  for (const dy of [-.93, 0, .93]) box(parent, [1.55, .06, .09], [x, 1.85 + dy, z + .04], frame);
}

function environment(parent, location) {
  const decor = group(parent, `Décor — ${location}`);
  const oak = material('#b18c64'), paleWood = material('#d0b38e'), pale = material('#e8e0d1');
  const floorColor = location === 'basketball' ? '#8ea19b' : location === 'product' ? '#b8b4ac' : '#c6ae8a';
  box(decor, [9, .18, 7], [0, -.13, 0], material('#65645f'), 'Diorama plinth');
  box(decor, [8.9, .055, 6.9], [0, -.012, 0], material(floorColor), 'Stage floor');
  if (!['basketball', 'product'].includes(location)) {
    for (let i = 0; i < 22; i++) box(decor, [8.9, .012, .007], [0, .021, -3.3 + i * .31], material('#aa8e69'));
  }
  if (['attic', 'nursery', 'handover'].includes(location)) {
    box(decor, [9, 3.2, .12], [0, 1.53, -3.42], pale, 'Back wall');
    box(decor, [.12, 2.9, 3.3], [-4.42, 1.38, -1.8], material('#d5cabb'), 'Open side wall');
    roomWindow(decor, -2.65, -3.34);
  }
  const dynamic = {};
  if (location === 'attic') {
    const timber = material('#715543');
    for (const z of [-3.3, -1.8, -.3]) {
      beam(decor, [-4.2, 2.65, z], [0, 4.1, z], .11, timber, 'Roof rafter');
      beam(decor, [0, 4.1, z], [4.2, 2.65, z], .11, timber, 'Roof rafter');
      if (z < -1) beam(decor, [-4.2, 2.65, z], [4.2, 2.65, z], .075, timber, 'Tie beam');
    }
    beam(decor, [0, 4.1, -3.45], [0, 4.1, -.1], .13, timber, 'Ridge beam');
    chest(decor, [-2, 0, -.9]);
    for (const [x, z, w, h] of [[2.8, -2.5, .8, .7], [3.25, -1.7, .6, .5], [2.5, -2.45, .6, .5]]) {
      box(decor, [w, h, .7], [x, h / 2, z], material('#ae9779'), 'Storage box');
      box(decor, [w + .04, .04, .74], [x, h, z], paleWood);
    }
    bench(decor, [.1, 0, -2.1], 1.8);
    plant(decor, [3.3, 0, 1.9], .8);
  } else if (location === 'basketball') {
    const line = material('#eee8d8');
    for (const x of [-3.6, 3.6]) box(decor, [.04, .015, 5.7], [x, .025, 0], line);
    for (const z of [-2.85, 2.85]) box(decor, [7.25, .015, .04], [0, .025, z], line);
    const center = mesh(decor, new THREE.TorusGeometry(1.05, .023, 6, 64), line, [0, .026, 0]);
    center.rotation.x = PI / 2;
    const wire = material('#637773', .7);
    for (let i = 0; i < 18; i++) beam(decor, [-4.25 + i * .5, .04, -3.3], [-4.25 + i * .5, 2.7, -3.3], .012, wire);
    for (let i = 0; i < 7; i++) beam(decor, [-4.25, .08 + i * .42, -3.3], [4.25, .08 + i * .42, -3.3], .012, wire);
    const hoopMat = material('#716f68');
    beam(decor, [0, 0, -2.8], [0, 3.25, -2.8], .065, hoopMat);
    box(decor, [1.35, .88, .08], [0, 2.87, -2.62], material('#e4ded0'), 'Backboard');
    box(decor, [.55, .43, .009], [0, 2.83, -2.573], material('#b4684e'));
    box(decor, [.48, .36, .012], [0, 2.83, -2.564], pale);
    const rim = mesh(decor, new THREE.TorusGeometry(.27, .024, 8, 32), material('#b76543'), [0, 2.54, -2.21], 'Basketball hoop');
    rim.rotation.x = PI / 2;
    for (let i = 0; i < 12; i++) {
      const a = i / 12 * 2 * PI;
      beam(decor, [Math.cos(a) * .265, 2.54, -2.21 + Math.sin(a) * .265], [Math.cos(a + .25) * .15, 2.15, -2.21 + Math.sin(a + .25) * .15], .008, line, 'Net cord');
    }
    dynamic.ball = basketball(decor, [1.08, .18, .38]);
  } else if (location === 'salsa') {
    const mortar = material('#b7a18c');
    box(decor, [9, 2.55, .15], [0, 1.2, -3.4], mortar);
    for (let row = 0; row < 8; row++) for (let col = 0; col < 14; col++) {
      box(decor, [.57, .265, .035], [-4.2 + col * .62 + (row % 2) * .13, .1 + row * .305, -3.3], material(row % 3 ? '#ae7961' : '#a16f5b'));
    }
    stringLights(decor, -2.4, 3.4, true);
    stringLights(decor, .9, 3.5, false);
    for (const x of [-3.3, 3.3]) {
      cylinder(decor, .54, .055, [x, .83, -1.7], paleWood, 'Bistro table');
      cylinder(decor, .075, .8, [x, .4, -1.7], oak);
      chair(decor, [x + .65, 0, -1.7], PI / 2);
      chair(decor, [x - .65, 0, -1.7], -PI / 2);
      plant(decor, [x, 0, -2.8], 1.25);
    }
  } else if (location === 'wedding') {
    const ivory = material('#eee9dc'), gold = material('#bb9b69', .45, { metalness: .35 });
    box(decor, [1.6, .01, 5.5], [0, .025, 0], material('#dec7bd'), 'Ceremony runner');
    beam(decor, [-1.55, 0, -2], [-1.55, 2.25, -2], .05, gold);
    beam(decor, [1.55, 0, -2], [1.55, 2.25, -2], .05, gold);
    const arch = mesh(decor, new THREE.TorusGeometry(1.55, .052, 8, 48, PI), gold, [0, 2.25, -2], 'Wedding arch');
    for (let i = 0; i < 16; i++) {
      const a = i / 15 * PI;
      ellipsoid(decor, [.14, .11, .12], [Math.cos(a) * 1.55, 2.25 + Math.sin(a) * 1.55, -2], material(i % 3 ? '#9ea78b' : '#e6c3b2'), 'Arch foliage');
    }
    for (const side of [-1, 1]) {
      const drape = box(decor, [.55, 2.2, .04], [side * 1.43, 1.16, -1.97], ivory, 'Ceremony drape');
      drape.rotation.z = side * .08;
      plant(decor, [side * 1.75, 0, -1.8], .85);
      for (const z of [.4, 1.5]) chair(decor, [side * 2.3, 0, z], PI);
    }
  } else if (location === 'nursery') {
    const rug = cylinder(decor, 1.25, .025, [0, .03, .3], material('#c7ac87'));
    rug.scale.z = .7;
    const crib = group(decor, 'Crib', [2, 0, -1.4]);
    box(crib, [1.75, .12, .86], [0, .53, 0], paleWood);
    box(crib, [1.59, .1, .72], [0, .64, 0], material('#e5d6c5'), 'Mattress');
    for (const x of [-.86, .86]) for (const z of [-.42, .42]) box(crib, [.07, 1.15, .07], [x, .58, z], oak);
    for (const z of [-.42, .42]) {
      box(crib, [1.78, .06, .06], [0, 1.14, z], paleWood);
      for (let i = 0; i < 10; i++) cylinder(crib, .018, .5, [-.77 + i * .17, .87, z], paleWood);
    }
    beam(crib, [.82, 1.15, -.4], [.82, 1.8, -.4], .019, oak);
    beam(crib, [.82, 1.8, -.4], [.15, 1.8, -.4], .019, oak);
    for (let i = 0; i < 3; i++) {
      beam(crib, [.22 + i * .18, 1.8, -.4], [.22 + i * .18, 1.5 - i * .08, -.4], .003, pale);
      ellipsoid(crib, [.055, .055, .04], [.22 + i * .18, 1.45 - i * .08, -.4], material(['#cfa676', '#91aaa1', '#cd9b8b'][i]));
    }
    chair(decor, [-2.2, 0, -.6], .45);
    plant(decor, [-3.4, 0, -2.2]);
    const moon = mesh(decor, new THREE.TorusGeometry(.35, .1, 12, 40, PI * 1.5), material('#dbc294'), [1.7, 2.35, -3.28], 'Moon wall ornament');
    moon.rotation.z = .3;
  } else if (location === 'handover') {
    bench(decor, [0, 0, -1.9], 2.4);
    plant(decor, [-3.2, 0, -.7], 1.3);
    box(decor, [1.3, .06, .3], [2.5, 1.7, -3.18], oak, 'Shelf');
    for (let i = 0; i < 5; i++) box(decor, [.13, .25 + i % 2 * .1, .2], [2.02 + i * .2, 1.88, -3.18], material(['#987d69', '#6e8181', '#b49a72'][i % 3]), 'Book');
    const pendant = group(decor, 'Pendant', [2.9, 2.4, -.8]);
    cylinder(pendant, .3, .18, [0, 0, 0], material('#c2a582'), '', .16);
    beam(decor, [2.9, 2.5, -.8], [2.9, 3.5, -.8], .007, material('#71685b'));
    sneaker(decor, [-.15, .85, .48], 1.05);
    sneaker(decor, [.15, .85, .48], 1.05);
    box(decor, [.72, .76, .6], [0, .38, .48], material('#bea789'), 'Presentation pedestal');
  } else {
    cylinder(decor, 1.65, .24, [0, .12, 0], material('#ddd7c9'), 'Product podium');
    const left = sneaker(decor, [-.38, .25, -.08], 2.5);
    const right = sneaker(decor, [.35, .25, .02], 2.5);
    left.rotation.y = -.2;
    right.rotation.y = .12;
  }
  return { decor, dynamic };
}

function customProp(parent, definition, index) {
  const type = definition.type || definition.kind || 'box';
  const pos = vector(definition.position);
  let result;
  if (type === 'plant') result = plant(parent, pos);
  else if (type === 'bench') result = bench(parent, pos);
  else if (type === 'chest' || type === 'trunk') result = chest(parent, pos);
  else if (type === 'shoe' || type === 'sneaker') result = sneaker(parent, pos, 1, color(definition.color, '#202329'));
  else if (type === 'ball') result = basketball(parent, pos);
  else if (type === 'chair') result = chair(parent, pos);
  else {
    result = group(parent, definition.label || type, pos);
    box(result, vector(definition.size, [.6, .6, .6]), [0, .3, 0], material(color(definition.color, '#a78d72')));
  }
  result.userData = { entityId: definition.id || `prop-${index}`, kind: 'prop', label: definition.label || type };
  if (Array.isArray(definition.scale)) result.scale.fromArray(vector(definition.scale, [1, 1, 1]));
  else result.scale.multiplyScalar(clamp(definition.scale ?? 1, .1, 5));
  result.rotation.y = Number(definition.rotation) || 0;
  return result;
}

function normalize(source = {}) {
  const input = source.blocking || (typeof source.environment === 'object' ? source.environment : source);
  let location = input.location || (typeof source.environment === 'string' ? source.environment : 'attic');
  if (!LOCATIONS.includes(location)) {
    const aliases = { grenier: 'attic', basket: 'basketball', dance: 'salsa', mariage: 'wedding', bébé: 'nursery', transmission: 'handover' };
    location = aliases[location] || 'attic';
  }
  const fallbackCharacters = location === 'product' ? [] : [
    { id: 'luna', label: 'Luna', age: 24, position: [-.65, 0, .2], color: '#738e86' },
    { id: 'rafa', label: 'Rafa', age: 25, position: [.65, 0, .1], color: '#b38564' },
  ];
  return {
    location,
    characters: (Array.isArray(input.characters) ? input.characters : fallbackCharacters).map((c, i) => ({ ...clone(c), id: c.id || `character-${i}`, position: vector(c.position, [i ? .65 : -.65, 0, .1]) })),
    camera: { position: vector(input.camera?.position, location === 'product' ? [3.3, 2.1, 4.2] : [6.7, 4.6, 7.7]), target: vector(input.camera?.target, [0, location === 'product' ? .7 : 1.15, 0]), fov: clamp(input.camera?.fov ?? 40, 18, 85) },
    lighting: { warmth: clamp(input.lighting?.warmth ?? .65, 0, 1), intensity: clamp(input.lighting?.intensity ?? 1, .1, 3), ...clone(input.lighting || {}) },
    props: Array.isArray(input.props) ? clone(input.props) : [],
    animationSpeed: clamp(input.animationSpeed ?? 1, 0, 3),
    showGrid: !!input.showGrid,
  };
}
function disposeTree(object) {
  const geometries = new Set(), materials = new Set();
  object.traverse(item => {
    if (item.geometry) geometries.add(item.geometry);
    if (item.material) (Array.isArray(item.material) ? item.material : [item.material]).forEach(mat => materials.add(mat));
  });
  geometries.forEach(item => item.dispose());
  materials.forEach(item => item.dispose());
}

export function createSceneViewer(container, { onChange = () => {}, onError = () => {} } = {}) {
  if (!container || typeof container.appendChild !== 'function') throw new TypeError('A viewer container is required.');
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, preserveDrawingBuffer: true, powerPreference: 'high-performance' });
  } catch (error) {
    onError(new Error(`Le navigateur ne peut pas ouvrir la maquette WebGL : ${error.message}`));
    throw error;
  }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.12;
  const canvas = renderer.domElement;
  canvas.style.cssText = 'display:block;width:100%;height:100%;touch-action:none;outline:none';
  canvas.tabIndex = 0;
  canvas.setAttribute('aria-label', 'Maquette 3D éditable. Glisser pour orbiter, molette pour zoomer, Alt-glisser pour déplacer un personnage.');
  container.appendChild(canvas);
  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#d5d5cf');
  const camera = new THREE.PerspectiveCamera(40, 16 / 9, .05, 80);
  camera.name = 'Storyboard camera';
  const controls = new OrbitControls(camera, canvas);
  controls.enableDamping = true;
  controls.dampingFactor = .085;
  controls.minDistance = .7;
  controls.maxDistance = 25;
  controls.maxPolarAngle = PI * .49;
  controls.target.set(0, 1.15, 0);
  const hemisphere = new THREE.HemisphereLight('#fff2df', '#858d83', 2.1);
  scene.add(hemisphere);
  const key = new THREE.DirectionalLight('#ffe5c0', 3.5);
  key.position.set(-3.8, 7, 4);
  key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  Object.assign(key.shadow.camera, { left: -6, right: 6, top: 6, bottom: -6, near: .5, far: 22 });
  key.shadow.normalBias = .025;
  key.shadow.bias = -.00012;
  scene.add(key);
  const fill = new THREE.DirectionalLight('#c9dce2', 1.0);
  fill.position.set(5, 3, -3);
  scene.add(fill);
  const grid = new THREE.GridHelper(9, 18, '#829795', '#a9b3ab');
  grid.position.y = .029;
  grid.material.transparent = true;
  grid.material.opacity = .25;
  scene.add(grid);
  let content = new THREE.Group();
  content.name = 'Procedural storyboard maquette';
  scene.add(content);
  let state = normalize(), actors = [], propObjects = [], dynamic = {}, selectedId = null;
  let disposed = false, playing = false, elapsed = 0, previousTime = performance.now(), frameId = 0, suppressChange = false;
  const raycaster = new THREE.Raycaster(), pointer = new THREE.Vector2();
  const dragPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
  let dragging = null, dragOffset = new THREE.Vector3(), pointerOrigin = null;

  function notify(type) {
    if (!disposed) onChange({ type, blocking: clone(state), selectedId });
  }
  function saveCamera() {
    state.camera = { position: camera.position.toArray(), target: controls.target.toArray(), fov: camera.fov };
  }
  function resize() {
    if (disposed) return;
    const rect = container.getBoundingClientRect();
    const width = Math.max(1, Math.round(rect.width || 800));
    const height = Math.max(1, Math.round(rect.height || 450));
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.render(scene, camera);
  }
  const observer = typeof ResizeObserver !== 'undefined' ? new ResizeObserver(resize) : null;
  observer?.observe(container);
  if (!observer) window.addEventListener('resize', resize);

  function applyLighting() {
    const warmth = clamp(state.lighting.warmth, 0, 1), intensity = clamp(state.lighting.intensity, .1, 3);
    key.color.copy(new THREE.Color('#e3efff').lerp(new THREE.Color('#ffd49c'), warmth));
    key.intensity = 3.5 * intensity;
    hemisphere.intensity = 1.8 * intensity;
    fill.intensity = .85 * intensity;
    renderer.toneMappingExposure = clamp(state.lighting.exposure ?? 1.12, .25, 2.5);
    const bg = new THREE.Color(state.location === 'product' ? '#c7c9c4' : '#d5d5cf');
    bg.lerp(new THREE.Color('#dbc8ab'), warmth * .18);
    scene.background = bg;
  }
  function setCamera(preset, emit = true) {
    const presets = {
      wide: { position: [6.7, 4.6, 7.7], target: [0, 1.15, 0], fov: 40 },
      front: { position: [0, 2.1, 7], target: [0, 1.05, 0], fov: 37 },
      side: { position: [7, 2.5, .8], target: [0, 1.05, 0], fov: 40 },
      top: { position: [0, 10, .001], target: [0, .1, 0], fov: 43 },
      close: { position: [2.6, 2, 3.7], target: [0, 1.12, .1], fov: 38 },
      shoes: { position: [2, .64, 2.7], target: [0, .19, .12], fov: 34 },
      product: { position: [3.3, 2.1, 4.2], target: [0, .7, 0], fov: 38 },
    };
    const data = typeof preset === 'string' ? presets[preset] || presets.wide : preset || state.camera;
    suppressChange = true;
    camera.position.fromArray(vector(data.position, state.camera.position));
    controls.target.fromArray(vector(data.target, state.camera.target));
    camera.fov = clamp(data.fov ?? state.camera.fov, 18, 85);
    camera.updateProjectionMatrix();
    controls.update();
    saveCamera();
    suppressChange = false;
    renderer.render(scene, camera);
    if (emit) notify('camera');
    return clone(state.camera);
  }
  function rebuild() {
    scene.remove(content);
    disposeTree(content);
    content = new THREE.Group();
    content.name = `Previz — ${state.location}`;
    content.userData = { type: 'procedural-previz', location: state.location, description: 'Editable stylized 3D blocking; not photoreal scene reconstruction.' };
    scene.add(content);
    const env = environment(content, state.location);
    dynamic = env.dynamic;
    actors = state.characters.map((data, index) => character(content, data, index, state.location));
    propObjects = state.props.map((data, index) => customProp(content, data, index));
    grid.visible = state.showGrid;
    applyLighting();
    pose(elapsed);
  }
  function pose(time) {
    const location = state.location;
    for (const actor of actors) {
      const phase = time * 2.7 * state.animationSpeed + actor.index * .35;
      if (actor.isBaby) { actor.torso.scale.y = 1 + Math.sin(phase * .7) * .012; continue; }
      const dance = location === 'salsa' || location === 'wedding';
      const walk = location === 'basketball';
      actor.root.position.copy(actor.basePosition);
      actor.root.rotation.y = actor.baseRotation;
      actor.torso.rotation.set(0, 0, 0);
      actor.head.rotation.set(0, 0, 0);
      if (dance) {
        actor.root.position.x += Math.sin(phase) * .10;
        actor.root.position.y += Math.abs(Math.sin(phase)) * .012;
        actor.root.rotation.y += Math.sin(phase * .5) * .12;
        actor.torso.rotation.z = Math.sin(phase) * .045;
      } else if (walk) actor.root.position.z += Math.sin(phase * .5) * .055;
      else if (location === 'attic') { actor.torso.rotation.x = .07; actor.head.rotation.x = .12; }
      else if (location === 'nursery') actor.head.rotation.set(.14, actor.index ? -.25 : .25, 0);
      else if (location === 'handover') actor.head.rotation.y = actor.index ? -.2 : .2;
      actor.arms.forEach(({ joint, elbow, side }) => {
        joint.rotation.x = dance ? -.38 + Math.sin(phase + side) * .17 : walk ? Math.sin(phase + (side > 0 ? PI : 0)) * .25 : -.07;
        joint.rotation.z = side * (dance ? .28 : .11);
        elbow.rotation.x = dance ? -.32 : location === 'handover' ? -.62 : location === 'attic' ? -.26 : -.08;
        if (location === 'handover') joint.rotation.x = -.47;
        if (location === 'nursery' && /rafa/i.test(`${actor.definition.id} ${actor.definition.label}`)) {
          joint.rotation.x = -.46;
          joint.rotation.z = side * .08;
          elbow.rotation.x = -1.0;
        }
      });
      actor.legs.forEach(({ joint, knee, foot, side }) => {
        const stride = Math.sin(phase + (side > 0 ? PI : 0));
        joint.rotation.x = (dance ? .07 : walk ? .17 : .008) * stride;
        knee.rotation.x = walk ? Math.max(0, -stride) * .13 : dance ? Math.max(0, -stride) * .055 : 0;
        foot.rotation.x = -(joint.rotation.x + knee.rotation.x) * .5;
      });
    }
    if (dynamic.ball) dynamic.ball.position.y = .15 + Math.abs(Math.sin(time * 3.5 * state.animationSpeed)) * .68;
  }
  function load(source, emit = true) {
    state = normalize(source);
    elapsed = 0;
    selectedId = null;
    rebuild();
    setCamera(state.camera, false);
    if (emit) notify('load');
    return clone(state);
  }
  function update(settings = {}) {
    const changes = settings.blocking || settings;
    const merged = { ...state, ...clone(changes), camera: { ...state.camera, ...changes.camera }, lighting: { ...state.lighting, ...changes.lighting } };
    if (typeof changes.environment === 'string') merged.location = changes.environment;
    if (changes.character) {
      merged.characters = state.characters.map(item => item.id === changes.character.id ? { ...item, ...clone(changes.character) } : item);
    }
    state = normalize(merged);
    const structural = ['location', 'environment', 'characters', 'character', 'props'].some(key => key in changes);
    if (structural) rebuild();
    else { grid.visible = state.showGrid; applyLighting(); pose(elapsed); }
    if (changes.camera) setCamera(state.camera, false);
    renderer.render(scene, camera);
    notify('update');
    return clone(state);
  }
  function pointerRay(event) {
    const rect = canvas.getBoundingClientRect();
    pointer.set((event.clientX - rect.left) / rect.width * 2 - 1, -(event.clientY - rect.top) / rect.height * 2 + 1);
    raycaster.setFromCamera(pointer, camera);
  }
  function findEntity(event) {
    pointerRay(event);
    const hits = raycaster.intersectObjects([...actors.map(a => a.root), ...propObjects], true);
    for (const hit of hits) {
      let item = hit.object;
      while (item && !item.userData.entityId) item = item.parent;
      if (item) return item;
    }
    return null;
  }
  function pointerDown(event) {
    pointerOrigin = [event.clientX, event.clientY];
    if (!event.altKey) return;
    const entity = findEntity(event);
    if (!entity) return;
    event.preventDefault();
    controls.enabled = false;
    dragging = entity;
    dragPlane.constant = -entity.position.y;
    const point = raycaster.ray.intersectPlane(dragPlane, new THREE.Vector3());
    if (point) dragOffset.copy(entity.position).sub(point);
    canvas.setPointerCapture(event.pointerId);
    selectedId = entity.userData.entityId;
  }
  function pointerMove(event) {
    if (!dragging) return;
    pointerRay(event);
    const point = raycaster.ray.intersectPlane(dragPlane, new THREE.Vector3());
    if (!point) return;
    point.add(dragOffset);
    dragging.position.x = clamp(point.x, -4.2, 4.2);
    dragging.position.z = clamp(point.z, -3, 3);
    const actor = actors.find(a => a.root === dragging);
    if (actor) actor.basePosition.copy(dragging.position);
    const list = dragging.userData.kind === 'character' ? state.characters : state.props;
    const entry = list.find((item, index) => (item.id || `prop-${index}`) === dragging.userData.entityId);
    if (entry) entry.position = dragging.position.toArray();
  }
  function pointerUp(event) {
    if (dragging) {
      dragging = null;
      controls.enabled = true;
      if (canvas.hasPointerCapture(event.pointerId)) canvas.releasePointerCapture(event.pointerId);
      notify('move');
    } else if (pointerOrigin && Math.hypot(event.clientX - pointerOrigin[0], event.clientY - pointerOrigin[1]) < 5) {
      const item = findEntity(event);
      selectedId = item?.userData.entityId || null;
      notify('select');
    }
    pointerOrigin = null;
  }
  function orbitEnd() { if (!suppressChange) { saveCamera(); notify('camera'); } }
  function contextLost(event) {
    event.preventDefault();
    playing = false;
    onError(new Error('Le contexte 3D a été interrompu. Le navigateur essaiera de le restaurer ; le projet reste enregistré.'));
  }
  function contextRestored() {
    if (disposed) return;
    resize();
    notify('context-restored');
  }
  canvas.addEventListener('pointerdown', pointerDown, true);
  canvas.addEventListener('pointermove', pointerMove);
  canvas.addEventListener('pointerup', pointerUp);
  canvas.addEventListener('pointercancel', pointerUp);
  canvas.addEventListener('webglcontextlost', contextLost);
  canvas.addEventListener('webglcontextrestored', contextRestored);
  controls.addEventListener('end', orbitEnd);
  function animate(now) {
    if (disposed) return;
    const delta = Math.min((now - previousTime) / 1000, .05);
    previousTime = now;
    if (playing && !dragging) { elapsed += delta; pose(elapsed); }
    controls.update(delta);
    renderer.render(scene, camera);
    frameId = requestAnimationFrame(animate);
  }
  function capture() {
    if (disposed) throw new Error('Viewer disposed.');
    const gridVisible = grid.visible;
    grid.visible = false;
    renderer.render(scene, camera);
    const result = canvas.toDataURL('image/png');
    grid.visible = gridVisible;
    return result;
  }
  async function exportGLB() {
    if (disposed) throw new Error('Viewer disposed.');
    try {
      const exportScene = new THREE.Scene();
      exportScene.name = `Converse previz — ${state.location}`;
      exportScene.userData = { blocking: clone(state), note: 'Procedural editable maquette. Static pose export; preview motion is not baked.' };
      exportScene.add(content.clone(true));
      const exportCamera = camera.clone();
      exportScene.add(exportCamera);
      for (const sourceLight of [key, fill]) {
        // glTF stores a punctual light's direction along its local -Z axis.
        // Keep live lights untouched; orient each export clone once, then give
        // it the canonical local target expected by GLTFExporter.
        const light = sourceLight.clone(false);
        const targetWorld = sourceLight.target.getWorldPosition(new THREE.Vector3());
        sourceLight.getWorldPosition(light.position);
        exportScene.add(light);
        light.lookAt(targetWorld);
        light.target = new THREE.Object3D();
        light.target.name = 'Export light direction';
        light.target.position.set(0, 0, -1);
        light.add(light.target);
      }
      const output = await new GLTFExporter().parseAsync(exportScene, { binary: true, onlyVisible: true, trs: true });
      return new Blob([output], { type: 'model/gltf-binary' });
    } catch (error) { onError(error); throw error; }
  }
  function dispose() {
    if (disposed) return;
    disposed = true;
    cancelAnimationFrame(frameId);
    observer?.disconnect();
    if (!observer) window.removeEventListener('resize', resize);
    controls.removeEventListener('end', orbitEnd);
    controls.dispose();
    canvas.removeEventListener('pointerdown', pointerDown, true);
    canvas.removeEventListener('pointermove', pointerMove);
    canvas.removeEventListener('pointerup', pointerUp);
    canvas.removeEventListener('pointercancel', pointerUp);
    canvas.removeEventListener('webglcontextlost', contextLost);
    canvas.removeEventListener('webglcontextrestored', contextRestored);
    disposeTree(scene);
    renderer.dispose();
    canvas.remove();
  }
  load({ blocking: state }, false);
  resize();
  frameId = requestAnimationFrame(animate);
  return {
    load, update, setCamera, capture, exportGLB, dispose, resize,
    play() { playing = true; previousTime = performance.now(); notify('play'); },
    pause() { playing = false; notify('pause'); },
    getState() { saveCamera(); return clone(state); },
    get isPlaying() { return playing; },
    get canvas() { return canvas; },
  };
}
