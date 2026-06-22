# Cherokee Safety SDS Database — How it works & how to maintain it

A free, phone-and-computer SDS lookup for employees. Live at:
**https://mattcreamer75.github.io/cherokee-sds/**  (GitHub repo: `MattCreamer75/cherokee-sds`)

The app mirrors the **Safety Program Dashboard** — same products, the same 13
product classes (Gas, Aerosol, Paint, Solvent, Cleaner, Fuel, Welding wire,
Stick electrode, Cutting fluid, Maintenance/lube, Metal prep, Adhesive, Other),
and the same details (manufacturer, revision, status, GHS hazards).

## The Dashboard is the source of truth

You add and edit SDS in the Dashboard. The app is generated from it — you never
edit the app's product list by hand.

Files in this `SDS-App` folder:

| Item | Purpose |
|------|---------|
| `index.html` | The search page employees use. |
| `sds-index.json` | The product list the app reads. **Generated — don't hand-edit.** |
| `sds/` | The SDS PDFs. |
| `tools/sync_from_dashboard.py` | Rebuilds `sds-index.json` from the Dashboard. |
| `tools/pdf_aliases.json` | One-time clean-up: links the original 53 products to their PDFs. |
| `assets/` | Cherokee logo + app icon. |

## Adding or changing an SDS (the routine task)

1. Add or edit the SDS **in the Dashboard** as you normally do (its "Add SDS"
   form saves the PDF and the product details).
2. **Sync the app** — either:
   - just tell Claude *"sync the SDS app"* and it regenerates and publishes, **or**
   - run it yourself: `python tools/sync_from_dashboard.py`, then upload the
     changed `sds-index.json` (and any new files it lists from `sds/_added/`)
     to the GitHub repo.

That's it — the new product shows up in the app with the right category and
hazard info. Products without a PDF on file appear in search but show
"SDS not on file" instead of an Open button, so gaps are visible.

## On a phone

Open the address and use **Add to Home Screen** to get the Cherokee app icon.

## OSHA note

Keep the printed binder (or downloaded copies) as the outage/inspection backup —
the app needs internet to load.
