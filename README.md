# Cp-T Interactive Materials Database

## What's in this folder
- `app.py` — Streamlit dashboard (search, category filter, multi-material plotting,
  comparison table, user-defined T range, out-of-range warnings, data source display).
- `data/materials_database.csv` — 200 materials across 8 classes (Metals & Alloys,
  Ceramics, Semiconductors, Polymers, Glasses, Refractories, Composites, Other).
- `data/build_dataset.py` — the script that generated the CSV (re-run it any time
  after you edit source data, or use it as a template to add more materials).
- `requirements.txt` — dependencies for local run / cloud deployment.

## ⚠️ Read this before submitting
The assignment requires every data point to be properly cited. To get you a fully
working 200-material platform immediately, the dataset has two tiers, flagged in the
`data_quality` column:

- **`verified`** (~38 materials: common metals, oxide ceramics, semiconductors,
  refractories) — representative coefficients of the type found in standard
  handbooks (Kubaschewski & Alcock's *Materials Thermochemistry*, Barin's
  *Thermochemical Data of Pure Substances*, NIST-JANAF). Treat these as a strong
  starting point, but **still look up and cite the exact table/edition you use**.
- **`placeholder`** (~162 materials: most polymers, glasses, composites, and the
  bulk of metals/ceramics/semiconductors) — generated from typical class behavior
  (typical room-T specific heat + a modest slope) so the app has 200+ working
  entries and every feature is demonstrable today. **These are NOT citable data.**
  You must replace their A/B/C/D coefficients with real values before final
  submission.

### Fastest way to replace placeholders with real, cited data
1. **NIST-JANAF Thermochemical Tables** (https://janaf.nist.gov) — free, gives
   Cp(T) tables directly for many inorganic compounds/elements — fit or read off
   values into the CSV.
2. **NIST Chemistry WebBook** (https://webbook.nist.gov) — Shomate equation
   coefficients for many species; the app's `A + B·T + C·T² + D/T²` form is close
   enough — set unused terms to 0, or extend `cp_of_T` in `app.py` if you want the
   exact Shomate form (`A + Bt + Ct² + Dt³ + E/t²`, t = T/1000).
3. **Materials Project** (https://materialsproject.org) — has an API; useful for
   ceramics/semiconductors; requires a free API key.
4. **MatWeb / AZoM** — good for engineering alloys, polymers, composites (room-T
   Cp values; combine with a literature slope or treat as ~constant if no T-dependence
   is published, which is a legitimate class-typical assumption **if you cite it**).
5. **PoLyInfo (NIMS)** — polymer-specific thermal data.

Each row's `source` column is where you write the exact citation once replaced.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Get a "working link" for submission (free, ~5 minutes)
1. Create a GitHub repo and push this whole folder (including `data/`).
2. Go to https://share.streamlit.io, sign in with GitHub, click "New app",
   point it at your repo and `app.py`.
3. Deploy — you'll get a public URL like `https://yourapp.streamlit.app`.
   That link satisfies the "working link / executable app" submission requirement.

## Features implemented (mapped to assignment requirements)
- Searchable list + category dropdown ✅
- Multi-material selection & simultaneous plotting ✅
- Comparison of Cp values at a chosen T (table) ✅
- User-defined temperature range (slider) ✅
- Material name, formula, category, source shown (details table) ✅
- Interactive zoom/pan/hover cursor values (Plotly) ✅
- Axis titles, units, legend ✅
- Out-of-valid-range warning (dotted line + explicit warning banner) ✅
- Data-quality flag as an extra transparency feature beyond the brief ✅
