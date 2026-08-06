# Vendored themes

This directory contains the theme collection copied from the `mordant-py`
package's `mordant/themes/` directory. The files retain their original
upstream names and formats (`.tmTheme` and VS Code `.json`). They are loaded
with `syntect.load_themes_from_folder()` when an application wants to opt in
to the collection.

See `D:/User/Documents/Python/mordant/ThirdPartyNotices.md` in the source
repository for the upstream provenance and license notices. The collection is
not yet auto-loaded at `import syntect`; package-level bundled-theme loading is
tracked as P4.5 in `docs/syntect_upgrade_plan.md`.
