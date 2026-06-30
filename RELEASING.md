# Releasing rozaya-jsfx

How a release is cut for this suite. It's deliberately lightweight — there's no
build step and nothing to compile. The plugins **are** the source.

## What a release is

- A **`vX.Y` git tag** on `master`. Versions are sequential — after `v2.13` comes
  `v2.14`.
- A **GitHub release** on that tag, carrying human-readable notes.
- **No assets.** Nothing is uploaded or zipped. Users install by copying the
  `.jsfx` files from `src/` into their REAPER `Effects` folder (see the README).
  The deliverable is simply the repo's source at that tag.

## When to cut one

Release when a **plugin changes in a way players should know about** — a new
plugin, a new feature or slider, a behaviour fix. Every release in the history is
a plugin change.

Docs-only commits (manuals, design notes) just ride on `master` — they do **not**
need their own version bump. Don't cut a release for a docs change alone.

## Writing the notes

Match the style of **v2.8** and **v2.11** (good examples). Write **for players and
modders**, in plain language — what it *does*, not how it's implemented. Point to
the manual for parameter detail.

Structure (omit sections that don't apply):

```
## vX.Y — <headline change>

<one-line summary of the release's theme>

### New
- **Feature / plugin name** — what it does for the user, plainly.

### Fixed
- **What was wrong** — and what works now.

### Housekeeping
- Archive moves, repo tidying, etc.

Public domain (CC0), as always.
```

Tip: `git log --oneline <prev-tag>..HEAD` lists everything since the last release —
a good basis for the notes.

## Cutting it

From `master`, with everything committed and pushed:

```
gh release create v2.14 --title "v2.14 — <headline>" --notes-file notes.md
# (or --notes "..." inline)
```

That's the whole job: tag + notes, no assets. To fix notes after the fact:

```
gh release edit vX.Y --notes-file notes.md
```
