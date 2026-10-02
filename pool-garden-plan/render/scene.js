/* 3D views of the pool & garden plan, built from the same model as the drawings.
 * Author: AbodyStudio Limited - https://abodystudio.com/
 * World axes: x = u (along the facade, towards the driveway), y = level (+-0.00 = villa floor),
 * z = v (from the road towards the pool and the orchard).
 */
(function () {
  const S = window.SCENE;
  const P = S.proposal;
  const night = S.view.night;
  THREE.ColorManagement.legacyMode = false;

  const W = S.width, H = S.height;
  const canvas = document.getElementById('c');
  canvas.width = W; canvas.height = H;
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
  renderer.setSize(W, H, false);
  renderer.outputEncoding = THREE.sRGBEncoding;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = night ? 1.05 : 0.92;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  const scene = new THREE.Scene();
  // real-world frame: u = SE, v = NE, up. three.js is right-handed with z = -north, so v is mirrored here.
  const root = new THREE.Group(); root.scale.z = -1; scene.add(root);
  const mats = {};
  function mat(key, color, o) {
    if (mats[key]) return mats[key];
    const m = new THREE.MeshStandardMaterial(Object.assign({ color: new THREE.Color(color), roughness: 0.85, metalness: 0 }, o || {}));
    mats[key] = m;
    return m;
  }
  function add(mesh, cast, receive) {
    mesh.castShadow = cast !== false; mesh.receiveShadow = receive !== false; root.add(mesh); return mesh;
  }
  function box(u0, u1, y0, y1, v0, v1, m, cast, receive) {
    const g = new THREE.BoxGeometry(Math.abs(u1 - u0), Math.abs(y1 - y0), Math.abs(v1 - v0));
    const mesh = new THREE.Mesh(g, m);
    mesh.position.set((u0 + u1) / 2, (y0 + y1) / 2, (v0 + v1) / 2);
    return add(mesh, cast, receive);
  }
  function shapeOf(pts) {
    const sh = new THREE.Shape();
    pts.forEach((p, i) => (i ? sh.lineTo(p[0], -p[1]) : sh.moveTo(p[0], -p[1])));
    sh.closePath();
    return sh;
  }
  function flat(pts, y, m, holes) {
    const sh = shapeOf(pts);
    (holes || []).forEach(h => { const p = new THREE.Path(); h.forEach((q, i) => (i ? p.lineTo(q[0], -q[1]) : p.moveTo(q[0], -q[1]))); p.closePath(); sh.holes.push(p); });
    const mesh = new THREE.Mesh(new THREE.ShapeGeometry(sh), m);
    mesh.rotation.x = -Math.PI / 2; mesh.position.y = y;
    return add(mesh, false, true);
  }
  function quad(a, b, c, d, m) {
    const g = new THREE.BufferGeometry();
    const v = new Float32Array([...a, ...b, ...c, ...a, ...c, ...d]);
    g.setAttribute('position', new THREE.BufferAttribute(v, 3));
    g.computeVertexNormals();
    return add(new THREE.Mesh(g, m), false, true);
  }
  function rod(a, b, r, m) {
    const va = new THREE.Vector3(...a), vb = new THREE.Vector3(...b);
    const len = va.distanceTo(vb);
    const mesh = new THREE.Mesh(new THREE.CylinderGeometry(r, r, len, 8), m);
    mesh.position.copy(va).add(vb).multiplyScalar(0.5);
    mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), vb.clone().sub(va).normalize());
    return add(mesh);
  }
  function sphere(u, y, v, r, m, sy) {
    const mesh = new THREE.Mesh(new THREE.SphereGeometry(r, 18, 12), m);
    mesh.position.set(u, y, v); mesh.scale.y = sy || 1;
    return add(mesh);
  }
  const TN = S.lv.tn;
  const rnd = (() => { let x = 7; return () => (x = (x * 16807) % 2147483647) / 2147483647; })();

  // ---------- sky + light
  const skyTop = new THREE.Color(night ? '#0e1d3a' : '#5d9bd5'), skyHor = new THREE.Color(night ? '#f2a65a' : '#e8f0f5');
  const skyMat = new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false,
    uniforms: { top: { value: skyTop }, hor: { value: skyHor } },
    vertexShader: 'varying vec3 p; void main(){ p = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }',
    fragmentShader: 'uniform vec3 top; uniform vec3 hor; varying vec3 p; void main(){ float t = clamp(p.y*2.2, 0.0, 1.0); gl_FragColor = vec4(mix(hor, top, pow(t,0.7)),1.0); }'
  });
  const sky = new THREE.Mesh(new THREE.SphereGeometry(900, 32, 16), skyMat);
  sky.position.set(11, 0, 20); root.add(sky);

  const sunDir = new THREE.Vector3(S.sun[0], night ? 0.10 : 0.95, S.sun[1]).normalize();
  const sun = new THREE.DirectionalLight(night ? 0xffa060 : 0xfff2dc, night ? 0.6 : 1.75);
  sun.position.copy(sunDir).multiplyScalar(60).add(new THREE.Vector3(11, 0, 20));
  sun.target.position.set(11, 0, 20); root.add(sun.target);
  sun.castShadow = true;
  sun.shadow.mapSize.set(4096, 4096);
  Object.assign(sun.shadow.camera, { left: -40, right: 40, top: 40, bottom: -40, near: 1, far: 160 });
  sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.03;
  root.add(sun);
  scene.add(new THREE.HemisphereLight(night ? 0x5a6a9a : 0xcfe4ff, night ? 0x2a2014 : 0x6b5a3a, night ? 0.6 : 0.5));

  // ---------- land
  flat([[-400, -400], [400, -400], [400, 400], [-400, 400]], TN - 0.06, mat('field', '#9c9a62'));
  const plots = ['#a8955f', '#8f9a58', '#b49b6a', '#7f8e4c', '#a3a46c', '#c0a874'];
  for (let i = 0; i < 46; i++) {
    const a = rnd() * Math.PI * 2, d = 28 + rnd() * 150, w = 12 + rnd() * 30, l = 15 + rnd() * 40;
    const cu = 11 + Math.cos(a) * d, cv = 20 + Math.sin(a) * d;
    if (cu > -12 && cu < 34 && cv > -8 && cv < 58) continue;
    const pm = new THREE.Mesh(new THREE.PlaneGeometry(w, l), mat('plot' + (i % plots.length), plots[i % plots.length]));
    pm.rotation.x = -Math.PI / 2; pm.rotation.z = rnd() * Math.PI; pm.position.set(cu, TN - 0.05 + i * 0.0005, cv); add(pm, false, true);
  }
  [[60, 160, 90, 0.18], [-60, 210, 110, 0.15], [140, 120, 80, 0.16], [10, 300, 160, 0.12], [-150, 140, 90, 0.14]].forEach(h =>
    sphere(h[0], TN - h[2] * 0.9, h[1], h[2], mat('hill' + h[3], h[3] > 0.15 ? '#8e8a52' : '#7b8550'), 1));
  for (let i = 0; i < 70; i++) {
    const a = rnd() * Math.PI * 1.2 - 0.1, d = 55 + rnd() * 120;
    const u = 11 + Math.cos(a) * d, v = 20 + Math.sin(a) * d;
    sphere(u, TN + 1.5, v, 2 + rnd() * 2.5, mat('farTree', '#4e6a35'), 0.8);
  }
  const water = S.pool;
  const holeRect = [[water.u0, water.v0], [water.u1, water.v0], [water.u1, water.v1], [water.u0, water.v1]];
  flat(S.bornes, TN, mat('parcel', '#93a65e'), [holeRect]);
  const lawn = mat('lawn', P.lawn);
  S.lawns.forEach(z => flat(z, TN + 0.015, lawn));
  flat(S.drive, TN + 0.02, mat('gravel', '#cdc4b2'));
  flat(S.chicken, TN + 0.015, mat('soil', '#a8865c'));
  flat(S.backyard, TN + 0.012, mat('soil2', '#b9a27c'));

  // ---------- pool
  const L = water.u1 - water.u0, Wd = water.v1 - water.v0;
  const mosaic = mat('mosaic', P.mosaic, { roughness: 0.35, side: THREE.DoubleSide });
  const frieze = mat('frieze', P.frieze, { roughness: 0.3, side: THREE.DoubleSide });
  const prof = S.profile;
  const top = S.lv.coping - 0.03;
  [water.v0, water.v1].forEach(vw => {
    const pts = [[water.u0, top], [water.u1, top]];
    for (let i = prof.length - 1; i >= 0; i--) pts.push([water.u0 + prof[i][0], prof[i][1]]);
    const sh = new THREE.Shape(); pts.forEach((p, i) => (i ? sh.lineTo(p[0], p[1]) : sh.moveTo(p[0], p[1])));
    const m = new THREE.Mesh(new THREE.ShapeGeometry(sh), mosaic); m.position.z = vw; add(m, false, true);
    box(water.u0, water.u1, top - 0.16, top, vw - 0.005, vw + 0.005, frieze, false, true);
  });
  [[water.u0, prof[0][1]], [water.u1, prof[prof.length - 1][1]]].forEach(([uw, zf]) => {
    quad([uw, top, water.v0], [uw, top, water.v1], [uw, zf, water.v1], [uw, zf, water.v0], mosaic);
    box(uw - 0.005, uw + 0.005, top - 0.16, top, water.v0, water.v1, frieze, false, true);
  });
  for (let i = 0; i < prof.length - 1; i++) {
    const [x1, z1] = prof[i], [x2, z2] = prof[i + 1];
    quad([water.u0 + x1, z1, water.v0], [water.u0 + x2, z2, water.v0], [water.u0 + x2, z2, water.v1], [water.u0 + x1, z1, water.v1], mosaic);
  }
  // slope-break line
  const bx = water.u0 + S.break_x;
  box(bx - 0.06, bx + 0.06, S.floor_break - 0.01, S.floor_break + 0.012, water.v0, water.v1, mat('breakline', P.frieze), false, true);
  // steps (shallow end, villa side)
  const st = S.step;
  for (let i = 0; i < st.n_tread; i++) {
    const u0 = water.u1 - st.tread * (st.n_tread - i);
    box(u0, water.u1, S.floor_shallow, S.lv.coping - st.rise * (i + 1), water.v0, water.v0 + st.width, mosaic, false, true);
  }
  const wMat = new THREE.MeshPhysicalMaterial({
    color: new THREE.Color(P.water), roughness: 0.04, metalness: 0, transparent: true, opacity: night ? 0.7 : 0.66,
    clearcoat: 1, clearcoatRoughness: 0.05, emissive: new THREE.Color(night ? P.water : '#000000'), emissiveIntensity: night ? 0.55 : 0
  });
  const wm = new THREE.Mesh(new THREE.PlaneGeometry(L, Wd), wMat);
  wm.rotation.x = -Math.PI / 2; wm.position.set((water.u0 + water.u1) / 2, S.lv.water, (water.v0 + water.v1) / 2);
  root.add(wm);
  S.lights.forEach(([x]) => {
    const lu = water.u0 + x, ly = S.lv.water - S.light_depth;
    const disc = new THREE.Mesh(new THREE.CircleGeometry(0.13, 20), new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: new THREE.Color(night ? '#e8fbff' : '#888888'), emissiveIntensity: night ? 2.5 : 0.2 }));
    disc.position.set(lu, ly, water.v0 + 0.01); root.add(disc);
    if (night) { const pl = new THREE.PointLight(0x9fe9ff, 2.2, 9, 1.6); pl.position.set(lu, ly, water.v0 + 0.6); root.add(pl); }
  });

  // ---------- coping, deck, front strip, access stair
  const coping = mat('coping', P.coping, { roughness: 0.6 });
  const wk = S.walk, cy0 = S.lv.coping - 0.05, cy1 = S.lv.coping;
  box(water.u0 - wk, water.u1 + wk, cy0, cy1, water.v0 - wk, water.v0, coping);
  box(water.u0 - wk, water.u1 + wk, cy0, cy1, water.v1, water.v1 + wk, coping);
  box(water.u0 - wk, water.u0, cy0, cy1, water.v0, water.v1, coping);
  box(water.u1, water.u1 + wk, cy0, cy1, water.v0, water.v1, coping);
  const deck = mat('deck', P.deck, { roughness: 0.7 });
  const Ho = S.house, Fg = S.front, Dk = S.deck, ps = S.pstair;
  box(Ho.u0, Ho.u1, TN, S.lv.deck_edge - 0.02, Dk[0], Dk[1], deck);
  box(Ho.u0, ps.u0, TN, S.lv.channel + 0.01, Fg[1] - 0.08, Fg[1] + 0.08, mat('channel', '#3a3d40'), false);
  quad([Ho.u0, -0.30, Fg[0]], [ps.u0, -0.30, Fg[0]], [ps.u0, S.lv.channel, Fg[1] - 0.08], [Ho.u0, S.lv.channel, Fg[1] - 0.08], mat('bed', '#6f5a40'));
  quad([Ho.u0, -0.30, Fg[0]], [Ho.u0, S.lv.channel, Fg[1] - 0.08], [Ho.u0, TN, Fg[1] - 0.08], [Ho.u0, TN, Fg[0]], mat('stone', P.plinth));
  for (let k = 0; k * 0.9 + Ho.u0 + 0.5 < ps.u0 - 0.4; k++) {
    const u = Ho.u0 + 0.5 + k * 0.9;
    sphere(u, -0.32, Fg[0] + 0.55, 0.32, mat('shrub' + (k % 3), ['#7f74b5', '#52803a', '#9a8fd0'][k % 3]), 0.8);
    sphere(u + 0.45, -0.55, Fg[0] + 1.25, 0.26, mat('shrubB' + (k % 2), ['#5d8f3d', '#c7b25a'][k % 2]), 0.8);
  }
  const land = Fg[0] + ps.landing;
  box(ps.u0, S.stair.u1, TN, 0, Fg[0], land, deck);
  for (let i = 0; i < ps.n - 1; i++) box(ps.u0, ps.u1, TN, -ps.rise * (i + 1), land + i * ps.tread, land + (i + 1) * ps.tread, deck);
  const rail = mat('rail', P.rail, { metalness: 0.6, roughness: 0.35 });
  const ru = ps.u0 + 0.06;
  rod([ru, 0.9, Fg[0] + 0.1], [ru, 0.9, land], 0.025, rail);
  rod([ru, 0.9, land], [ru, 0.9 - ps.rise * (ps.n - 1), Fg[1]], 0.025, rail);
  [[Fg[0] + 0.1, 0], [land, 0], [Fg[1] - 0.05, -ps.rise * (ps.n - 1)]].forEach(([v, y]) => rod([ru, y, v], [ru, y + 0.9, v], 0.02, rail));

  // ---------- villa
  const wall = mat('wall', P.wall, { roughness: 0.9 });
  const plinth = mat('plinth', P.plinth, { roughness: 0.95 });
  box(Ho.u0, Ho.u1, TN, 0.0, Ho.v0, Ho.v1, plinth);
  box(Ho.u0, Ho.u1, 0.0, S.lv.roof, Ho.v0, Ho.v1, wall);
  const pt = 0.15, pr = S.lv.parapet;
  box(Ho.u0, Ho.u1, S.lv.roof, pr, Ho.v0, Ho.v0 + pt, wall);
  box(Ho.u0, Ho.u1, S.lv.roof, pr, Ho.v1 - pt, Ho.v1, wall);
  box(Ho.u0, Ho.u0 + pt, S.lv.roof, pr, Ho.v0, Ho.v1, wall);
  box(Ho.u1 - pt, Ho.u1, S.lv.roof, pr, Ho.v0, Ho.v1, wall);
  box(Ho.u0, Ho.u1, pr, pr + 0.04, Ho.v1 - pt - 0.02, Ho.v1 + 0.02, mat('cap', P.coping));
  const glass = new THREE.MeshStandardMaterial({ color: new THREE.Color('#1f2a33'), roughness: 0.15, metalness: 0.2,
    emissive: new THREE.Color(night ? '#ffc979' : '#000000'), emissiveIntensity: night ? 1.3 : 0 });
  const frame = mat('frame', P.frame, { roughness: 0.4, metalness: 0.3 });
  function opening(u, w, y0, h, face) {
    const z = face === 'ne' ? Ho.v1 : Ho.v0;
    const s = face === 'ne' ? 1 : -1;
    box(u - w / 2 - 0.07, u + w / 2 + 0.07, y0 - 0.07, y0 + h + 0.07, z, z + s * 0.03, frame, false);
    const g = new THREE.Mesh(new THREE.PlaneGeometry(w, h), glass);
    g.position.set(u, y0 + h / 2, z + s * 0.035); if (s < 0) g.rotation.y = Math.PI; root.add(g);
    for (let k = 1; k < 4; k++) box(u - w / 2 + k * w / 4 - 0.012, u - w / 2 + k * w / 4 + 0.012, y0, y0 + h, z, z + s * 0.05, frame, false);
  }
  S.windows.forEach(w => opening(w.u, w.w, w.y, w.h, 'ne'));
  // curved awning on two columns
  const aw = S.awning;
  const ash = new THREE.Shape();
  ash.moveTo(aw.uc - aw.r, -Ho.v1);
  for (let i = 0; i <= 24; i++) { const t = Math.PI * i / 24; ash.lineTo(aw.uc - aw.r * Math.cos(t), -(Ho.v1 + aw.depth * Math.sin(t))); }
  const ag = new THREE.ExtrudeGeometry(ash, { depth: 0.22, bevelEnabled: false });
  const am = new THREE.Mesh(ag, wall); am.rotation.x = -Math.PI / 2; am.position.y = S.lv.roof - 0.22; add(am);
  [-1, 1].forEach(sg => { const cu = aw.uc + sg * aw.r * 0.66; const cv = Ho.v1 + aw.depth * Math.sqrt(1 - 0.66 * 0.66) - 0.15;
    box(cu - 0.13, cu + 0.13, 0.0, S.lv.roof - 0.22, cv - 0.13, cv + 0.13, wall); box(cu - 0.15, cu + 0.15, TN, 0.0, cv - 0.15, cv + 0.15, plinth); });
  // existing roof stair on the driveway side
  const sr = S.stair, nst = 18, rise = S.lv.roof / nst, run = (sr.v1 - sr.v0) / nst;
  for (let i = 0; i < nst; i++) box(sr.u0, sr.u1, TN, rise * (i + 1), sr.v1 - run * (i + 1), sr.v1 - run * i, wall);
  box(sr.u1 - 0.1, sr.u1, S.lv.roof, S.lv.roof + 0.9, sr.v0, sr.v0 + 0.6, wall);

  // ---------- equipment room, loungers, shower
  const T = S.tech;
  box(T.u0, T.u1, TN, 0.45, T.v0, T.v1, wall);
  box(T.u0 - 0.08, T.u1 + 0.08, 0.45, 0.55, T.v0 - 0.08, T.v1 + 0.08, mat('cap', P.coping));
  box(T.u0 + 0.65, T.u0 + 1.45, TN, 0.3, T.v1, T.v1 + 0.03, frame, false);
  const cushion = mat('cushion', P.cushion, { roughness: 0.95 }), wood = mat('wood', P.wood, { roughness: 0.7 });
  for (let i = 0; i < 4; i++) {
    const u = water.u0 + 0.9 + i * 2.35;
    const yb = S.lv.deck_edge;
    box(u, u + 0.72, yb, yb + 0.28, Dk[0] + 0.55, Dk[1] - 0.15, wood);
    box(u + 0.03, u + 0.69, yb + 0.28, yb + 0.36, Dk[0] + 0.55, Dk[1] - 0.15, cushion);
    const back = new THREE.Mesh(new THREE.BoxGeometry(0.66, 0.08, 0.75), cushion);
    back.position.set(u + 0.36, yb + 0.6, Dk[0] + 0.78); back.rotation.x = 0.75; add(back);
    if (i < 3) box(u + 1.1, u + 1.5, yb, yb + 0.42, Dk[0] + 0.9, Dk[0] + 1.3, wood);
  }
  rod([S.shower.u, TN, S.shower.v], [S.shower.u, 1.6, S.shower.v], 0.04, rail);
  rod([S.shower.u, 1.6, S.shower.v], [S.shower.u, 1.6, S.shower.v - 0.35], 0.03, rail);
  box(S.shower.u - 0.6, S.shower.u + 0.6, TN, TN + 0.06, S.shower.v - 0.6, S.shower.v + 0.6, deck);

  // ---------- vegetation, hedge, bollards, fences, chickens
  const leaf = mat('leaf', '#3f6e2c'), trunk = mat('trunk', '#6b4f36'), fruit = mat('fruit', '#f29a2e', { roughness: 0.6 });
  function citrus(u, v, s) {
    rod([u, TN, v], [u, TN + 0.9 * s, v], 0.07 * s, trunk);
    sphere(u, TN + 1.55 * s, v, 0.95 * s, leaf, 0.9);
    for (let k = 0; k < 6; k++) { const a = k * 1.05 + rnd(); sphere(u + Math.cos(a) * 0.8 * s, TN + (1.3 + rnd() * 0.6) * s, v + Math.sin(a) * 0.8 * s, 0.07 * s, fruit); }
  }
  S.trees.forEach(t => citrus(t[0], t[1], t[2] || 1));
  const cyp = mat('cypress', '#2f5a2a');
  S.hedge.forEach(([u, v]) => { const c = new THREE.Mesh(new THREE.ConeGeometry(0.38, 2.6, 10), cyp); c.position.set(u, TN + 1.3, v); add(c); });
  S.olives.forEach(([u, v, r]) => { rod([u, TN, v], [u, TN + 2.2, v], 0.25, trunk); sphere(u, TN + 3.6, v, r, mat('olive', '#5c7445'), 0.75); });
  const bol = new THREE.MeshStandardMaterial({ color: new THREE.Color('#2b2b2b'), emissive: new THREE.Color(night ? '#ffd28a' : '#000000'), emissiveIntensity: night ? 2 : 0 });
  S.bollards.forEach(([u, v], i) => { box(u - 0.07, u + 0.07, TN, TN + 0.6, v - 0.07, v + 0.07, bol); if (night && i < 4) { const pl = new THREE.PointLight(0xffc77a, 0.9, 6, 2); pl.position.set(u, TN + 0.7, v); root.add(pl); } });
  function fence(a, b, h, m, postM) {
    const du = b[0] - a[0], dv = b[1] - a[1], len = Math.hypot(du, dv);
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(len, h, 0.03), m);
    mesh.position.set((a[0] + b[0]) / 2, TN + h / 2, (a[1] + b[1]) / 2); mesh.rotation.y = -Math.atan2(dv, du); add(mesh, true, false);
    for (let k = 0; k <= Math.floor(len / 3); k++) { const t = k * 3 / len; rod([a[0] + du * t, TN, a[1] + dv * t], [a[0] + du * t, TN + h + 0.1, a[1] + dv * t], 0.04, postM); }
  }
  const post = mat('post', '#7a6a55');
  fence(S.se_fence[0], S.se_fence[1], 1.8, mat('net', '#1d2124', { transparent: true, opacity: 0.88 }), post);
  fence(S.nw_fence[0], S.nw_fence[1], 1.6, mat('reed', '#9c8660'), post);
  const mesh = mat('mesh', '#c9cdd0', { transparent: true, opacity: 0.16 });
  for (let i = 0; i < S.chicken.length; i++) { const a = S.chicken[i], b = S.chicken[(i + 1) % S.chicken.length]; if (i !== 3) fence(a, b, 1.5, mesh, post); }
  const cp = S.coop;
  box(cp.u0, cp.u1, TN, TN + 1.4, cp.v0, cp.v1, wood);
  const roof = new THREE.Mesh(new THREE.BoxGeometry(cp.u1 - cp.u0 + 0.3, 0.06, cp.v1 - cp.v0 + 0.4), mat('roofT', '#8c3b2a'));
  roof.position.set((cp.u0 + cp.u1) / 2, TN + 1.6, (cp.v0 + cp.v1) / 2); roof.rotation.z = 0.18; add(roof);
  S.neighbours.forEach(([u0, u1, v0, v1, h]) => box(u0, u1, TN, TN + h, v0, v1, mat('nb', '#efeee9')));

  // ---------- camera
  const V = S.view;
  const cam = new THREE.PerspectiveCamera(V.fov, W / H, 0.1, 2000);
  cam.position.set(V.pos[0], V.pos[1], -V.pos[2]); cam.lookAt(new THREE.Vector3(V.target[0], V.target[1], -V.target[2]));
  renderer.render(scene, cam);
  document.getElementById('out').textContent = canvas.toDataURL('image/png');
})();
