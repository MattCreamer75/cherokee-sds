# Cherokee SDS Finder — Setup & Maintenance

A free, phone-and-computer SDS lookup for employees. No app store, no logins,
no monthly cost. Employees open one web address (or scan a QR code), type a
product name, and tap to open the Safety Data Sheet.

Everything lives in this `SDS-App` folder:

| Item | What it is |
|------|------------|
| `index.html` | The search page employees use. Don't edit it. |
| `sds-index.json` | The searchable list. Built automatically — don't hand-edit. |
| `sds/` | All your SDS PDFs, in category folders. **This is what you maintain.** |
| `tools/build_index.py` | Rebuilds the list from the PDFs. |
| `.github/workflows/build-index.yml` | Rebuilds the list automatically when you add PDFs. |

---

## One-time setup (about 15 minutes)

You publish this folder for free using **GitHub Pages**.

1. **Make a free GitHub account** at https://github.com (work email is fine).
2. Click **+** (top right) → **New repository**.
   - Name it `cherokee-sds` (or anything).
   - Set it to **Public** (SDS aren't confidential; Pages is free for public repos).
   - Click **Create repository**.
3. On the new repo page, click **uploading an existing file**.
4. Open this `SDS-App` folder on your computer, select **everything inside it**
   (the `index.html`, `sds-index.json`, the `sds` folder, the `assets` folder
   with the Cherokee logo, the `tools` folder, the `.github` folder, and
   `.nojekyll`), and drag it all into the browser.
   Wait for the upload to finish, then click **Commit changes**.
5. Turn on the website: go to **Settings → Pages**.
   - Under "Build and deployment", Source = **Deploy from a branch**.
   - Branch = **main**, folder = **/ (root)**. Click **Save**.
6. Wait ~1–2 minutes, refresh the Pages settings page. It will show your live
   address, like: `https://YOURNAME.github.io/cherokee-sds/`
7. Open that address on your phone. That's the app. Done.

> **Tip:** On a phone, open the address and use the browser's
> "Add to Home Screen" — it then behaves like an installed app icon.

---

## Posting the QR code

Once you have the live address, make a free QR code that points to it
(e.g. qr-code-generator.com or any free generator). Print it and post it at
workstations, the paint area, welding bay, and the chemical storage area so
anyone can scan straight to the SDS list.

---

## Adding new SDS later (the only routine task)

1. In your GitHub repo, open the `sds` folder, then the category folder you want
   (`General`, `Welding`, `Paint Area`, `Fuel`, etc.).
2. Click **Add file → Upload files**, drag in the new SDS PDF(s), **Commit**.
   - To make a **new category**, just upload into a new folder name.
3. That's it. Within a minute the index rebuilds itself automatically (the
   GitHub Action) and the new sheet appears in search. No code, no buttons.

**Naming tip** — name files so they're easy to find and so the manufacturer
shows up automatically. Put the maker in parentheses:
`Acetone (WM Barr).pdf`, `Argon Compressed (Matheson).pdf`.

To remove a discontinued product: open its PDF in the repo and click the trash
icon. The index updates itself the same way.

---

## OSHA note (read once)

- This satisfies "readily accessible" electronic SDS access under
  29 CFR 1910.1200(g) **only if** employees can actually reach it on shift.
- **Keep the printed binder (or a downloaded copy) as backup** for power/internet
  outages and for inspectors who ask. The app is the fast path, not the only path.
- Scanned image SDS (a few of yours) are searchable by **name** but their text
  can't be read by the search. They still open fine. Re-download a text-based
  copy from the manufacturer when convenient.

---

## If you'd rather not use GitHub

The same folder also works from any web host or an internal SharePoint site —
the app only needs `index.html`, `sds-index.json`, and the `sds/` folder served
together over a web address. If you go the SharePoint route, you'd rebuild the
index by running `python tools/build_index.py` instead of the auto-Action.
