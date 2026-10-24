# AI-Enabled-ATE

Desktop assistant for electronics learning: component identification, an AI chat assistant and a manuals library.
**This folder currently contains only the GUI (MMI = Man-Machine Interface). The backend comes later.**

## Run it
```
pip install -r requirements.txt
python main.py                       # full window (all pages + navigation)
python main.py MMI/ui/dashboard.ui      # preview a single .ui file with the theme applied
```

## Folder layout
```
AI-Enabled-ATE/
├── main.py                 Preview launcher: loads the .ui files, wires GUI-only behaviour
├── requirements.txt
└── MMI/
    └── ui/
        ├── main_window.ui      Shell: left sidebar + header + QStackedWidget (pageStack)
        ├── dashboard.ui        Page 1 - identify components, quick actions, recent scans
        ├── AI-assistant.ui     Page 2 - chat history sidebar, chat area, input bar
        ├── library.ui          Page 3 - "User Manuals": manuals hub, PDF viewer, host for usermanual.ui
        ├── usermanual.ui       "App User Guide": search box, table of contents, 9 documentation sections
        ├── styles/dark.qss     All colours/fonts/borders for the dark theme
        ├── styles/light.qss    Same selectors, light colours
        └── icons/              SVG icons (Lucide). File name = <icon>__<hex colour>[__<size>].svg
```
Open any `.ui` file with **Qt Designer** (`designer` or `pyqt5-tools designer`).

## Conventions (please keep them)
* **objectName is unique and describes what the widget IS**: `btnUploadImage`, `chatInput`, `statTotalCard`.
  Backend code will find widgets by these names, so do not rename casually.
* **Look comes from two dynamic properties**, not from the name:
  * `kind` on buttons: `primary`, `secondary`, `danger`, `chip`, `chipActive`, `sidebarNav`, `sidebarNavActive`, `tocItem`, `tocItemActive`, `qaCardPrimary`/`Teal`/`Mint`/`Lime` (quick-action cards)
  * `role` on everything else: `card`, `dropZone`, `imgPanel`, `h1`, `h2`, `subtitle`, `caption`, `muted`, `badge`, `badgeOk`, `statCard`, `manualCard`, `chatItem`, `questionCard`, `callout*`, `codeSnippet`, `tocCard` ...
  * To add one in Designer: Property Editor -> green **+** -> *String* -> name `kind` or `role`.
  * Each rule is in `MMI/ui/styles/dark.qss` as `QPushButton[kind="primary"] { ... }` / `QFrame[role="card"] { ... }`.
* **Do not put colours in the .ui files** (a few one-off inline styles exist, copied from the original app).
  Change look & feel in the `.qss` files.
* **Pages are separate files** and are assembled in `main.py`:
  `pageStack` <- dashboard, AI-assistant, library; `library.userGuideHostLayout` <- usermanual.
* Sample content (two manual cards, one chat item) is placeholder. Delete/replace when the backend fills these lists.
* Hidden-by-default widgets (shown by the backend later): `voiceBar`, `typingCard`, `btnViewManual`, `btnResetScope`, `matchStatusLabel`, `matchDetailLabel`, `matchedBox`, `manualDropProgressBox`, `manualsEmptyState`, `btnDeleteSelected`, `recentBox`.

## Notes
* Written for **PyQt5**. (The earlier prototype used PyQt6; the `.ui` files are plain XML and the loader only needs its imports changed.)
* In button text, a literal "&" must be written "&&" (single "&" makes a keyboard shortcut).
* `kind`/`role` changes at run time need a re-polish: see `repolish()` in `main.py`.
