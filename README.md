# AbodyStudio projects

Author: AbodyStudio Limited - https://abodystudio.com/ - Support@abodystudio.com - WhatsApp +212 663 033 383

## pool-garden-plan

Plan set for the pool and garden at Douar Ghanem (Gharsa Foquiya), Tanger-Assilah.

- `pool-garden-plan/src/model.py` - survey data, owner's dimensions, levels, quantities, estimate. Bump `VERSION` for every update.
- `pool-garden-plan/src/sheets.py` - A3 drawing sheets PL-01 to PL-06 (SVG, Moroccan plan conventions).
- `pool-garden-plan/build.py` - builds `dist/vX.Y.Z/` (HTML page, SVG sheets, photos) and `releases/*.zip`.

Build: `pip install pillow && python3 pool-garden-plan/build.py` (Font Awesome SVGs expected in `$FA_DIR`, default `/tmp/fa/package/svgs`).

| Version | Date | Notes |
|---|---|---|
| 1.0.0 | 02/10/2026 | First issue (indice A): 5 sheets, specification, sequence, estimate, schedule, FR/EN/AR glossary |
| 1.1.0 | 02/10/2026 | Indice B: full French version; access stair to the pool on the left (driveway) side of the villa, at the foot of the roof stair (PL-02, detail D2 on PL-05, estimate 6.03); PL-02/03/06 drawn as seen from the pool towards the villa; new PL-06 (pipe routing, equipment room 1/25, hydraulic synoptic, single-line diagram); accent and typography fixes |
| 1.3.1 | 02/10/2026 | Indice E: exact calculated values instead of approximations; water volume 50.373 m³ with a slice-by-slice calculation table (page section 05 and sheet PL-04), filtration turnover 4 h 12 min, steel 2 187 kg; volumes rounded half-up to the litre |
| 1.3.0 | 02/10/2026 | Indice D: full-width cover (img/cover.png) above the title and a gallery under the site photos (img/image1.png, image2.png, ...), both loaded automatically from the img folder (png, jpg, jpeg or webp), with placeholders and a full-screen viewer; images placed in pool-garden-plan/assets/gallery/ are copied into the build |
| 1.2.0 | 02/10/2026 | Indice C: water depth 0.55 m (children's zone) → 1.20 m slope break → 1.80 m deep end, pool volume ≈ 50 m³, pump 12 m³/h and Ø600 filter, lights and drains repositioned, 4-step ladder; light theme on white backgrounds; work-phases list layout fixed; estimate with company header, grand totals HT / TVA 20 % / TTC, amount in words and signature blocks; ABOUDI BTP Group (SARL, RC 168595 Tanger, ICE 003823697000094) as contractor in the page and on every title block |
