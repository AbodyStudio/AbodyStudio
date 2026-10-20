# AbodyStudio projects

Author: AbodyStudio Limited - https://abodystudio.com/ - Support@abodystudio.com - WhatsApp +212 663 033 383

## pool-garden-plan

Plan set for the pool and garden at Douar Ghanem (Gharsa Foquiya), Tanger-Assilah.

- `pool-garden-plan/src/model.py` - survey data, owner's dimensions, levels, quantities, estimate. Bump `VERSION` for every update.
- `pool-garden-plan/src/sheets.py` - A3 drawing sheets PL-01 to PL-06 (SVG, Moroccan plan conventions).
- `pool-garden-plan/build.py` - builds `dist/vX.Y.Z/` (HTML page, SVG sheets, photos) and `releases/*.zip`.
- `pool-garden-plan/src/variant_b.py` - variant B (no technical room): equipment envelopes, pipe routes, head-loss calculation per selector position, vault/sump quantities, estimate, cost and operating-cost comparison with indice E.
- `pool-garden-plan/src/sheets_b.py` - variant B sheets VB-01 to VB-10 (+ PL-01, PL-02, PL-05 reissued).
- `pool-garden-plan/build_b.py` - builds `dist/v2.0.0/` and `releases/AbodyStudio_Gharsa-Foquiya_Piscine-Sans-Local-Technique_v2.0.0.zip`.

Build: `pip install pillow && python3 pool-garden-plan/build.py` (Font Awesome SVGs expected in `$FA_DIR`, default `/tmp/fa/package/svgs`).

| Version | Date | Notes |
|---|---|---|
| 2.0.0 | 20/10/2026 | Indice F, variant B "sans local technique": same pool (dimensions, levels, depth profile, structure), new hydraulic system - dry pump vault 1.10 × 1.30 × 1.00 m beside the deep end under a lockable A15 tile-insert hatch, sump with 800 × 600 anti-entrapment grille, both skimmers kept, one 12 m³/h pump at 9 mCE, 13.9 m² cartridge filter, selector A (concealed inlets) / B (cascade) / A+B / C (controlled garden discharge via a control post with vacuum breaker) / E (maintenance); head losses calculated per position (6.07 mCE average vs 7.16 for indice E); sheets VB-01 to VB-10 (concept, general plan, hydraulic schematic, sections, vault detail, cascade, garden discharge, structure and waterproofing, electrical safety concept, equipment schedule); calculated cost comparison (+14 485 DH HT in total, +3 422 DH HT like-for-like, −430 DH per year to run). Electrical concept not checked for compliance. |
| 1.0.0 | 02/10/2026 | First issue (indice A): 5 sheets, specification, sequence, estimate, schedule, FR/EN/AR glossary |
| 1.1.0 | 02/10/2026 | Indice B: full French version; access stair to the pool on the left (driveway) side of the villa, at the foot of the roof stair (PL-02, detail D2 on PL-05, estimate 6.03); PL-02/03/06 drawn as seen from the pool towards the villa; new PL-06 (pipe routing, equipment room 1/25, hydraulic synoptic, single-line diagram); accent and typography fixes |
| 1.3.1 | 02/10/2026 | Indice E: exact calculated values instead of approximations; water volume 50.373 m³ with a slice-by-slice calculation table (page section 05 and sheet PL-04), filtration turnover 4 h 12 min, steel 2 187 kg; volumes rounded half-up to the litre |
| 1.3.0 | 02/10/2026 | Indice D: full-width cover (img/cover.png) above the title and a gallery under the site photos (img/image1.png, image2.png, ...), both loaded automatically from the img folder (png, jpg, jpeg or webp), with placeholders and a full-screen viewer; images placed in pool-garden-plan/assets/gallery/ are copied into the build |
| 1.2.0 | 02/10/2026 | Indice C: water depth 0.55 m (children's zone) → 1.20 m slope break → 1.80 m deep end, pool volume ≈ 50 m³, pump 12 m³/h and Ø600 filter, lights and drains repositioned, 4-step ladder; light theme on white backgrounds; work-phases list layout fixed; estimate with company header, grand totals HT / TVA 20 % / TTC, amount in words and signature blocks; ABOUDI BTP Group (SARL, RC 168595 Tanger, ICE 003823697000094) as contractor in the page and on every title block |
