# AbodyStudio projects

Author: AbodyStudio Limited - https://abodystudio.com/ - Support@abodystudio.com - WhatsApp +212 663 033 383

## pool-garden-plan

Plan set for the pool and garden at Douar Ghanem (Gharsa Foquiya), Tanger-Assilah.

- `pool-garden-plan/src/model.py` - survey data, owner's dimensions, levels, quantities, estimate. Bump `VERSION` for every update.
- `pool-garden-plan/src/sheets.py` - A3 drawing sheets PL-01 to PL-05 (SVG, Moroccan plan conventions).
- `pool-garden-plan/build.py` - builds `dist/vX.Y.Z/` (HTML page, SVG sheets, photos) and `releases/*.zip`.

Build: `pip install pillow && python3 pool-garden-plan/build.py` (Font Awesome SVGs expected in `$FA_DIR`, default `/tmp/fa/package/svgs`).

| Version | Date | Notes |
|---|---|---|
| 1.0.0 | 02/10/2026 | First issue (indice A): 5 sheets, specification, sequence, estimate, schedule, FR/EN/AR glossary |
