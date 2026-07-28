# Getting your captures out (and back in)

*A step-by-step guide. It assumes you have never run a Python script before and
explains everything as it goes.*

---

## What this is for

When you capture a moment into **Spectral Vowel Passage** (or **Spectral Vowel
Morpher**), the plugin keeps the actual recorded audio inside your REAPER project
file. That's handy — your captures come back every time you open the project —
but it also means each capture lives in exactly one place and nowhere else. You
can't reuse a good vowel in another piece, you can't back one up on its own, and
you can't tell your eight slots apart without playing all eight.

Two small programs fix that:

- **`passage_captures.py`** — tells you what's in every slot, and can save each
  one as a WAV file. It only ever *reads* your project. It cannot change it.
- **`passage_inject.py`** — puts a WAV file *into* a slot. This one does write,
  so it makes a copy of your project by default rather than editing yours.

You don't need to understand any of the machinery. You type one line, press
Enter, and read what it tells you.

---

## Before you start: do you have Python?

Python is a free program that runs scripts like these. Most computers don't have
it until you install it.

**To check:** open a terminal (the next section explains how) and type this,
then press Enter:

```
python --version
```

If you see something like `Python 3.12.1`, you're set — skip to
[Step one](#step-one-see-what-is-in-a-project).

If you instead see *"Python was not found"* or *"command not found"*, install it:

- **Windows:** go to [python.org/downloads](https://www.python.org/downloads/)
  and get the latest version. **When the installer opens, tick the box that says
  "Add python.exe to PATH" before clicking Install.** That box is easy to miss
  and everything below depends on it. If you skip it, the commands here will keep
  saying Python wasn't found even though you installed it.
- **macOS:** same site, or `brew install python3` if you use Homebrew. On macOS
  you may need to type `python3` instead of `python` everywhere below.

Nothing else needs installing. These two scripts use only what comes with Python.

---

## Opening a terminal

A terminal is a window where you type commands instead of clicking things.

**Windows:** press <kbd>Windows</kbd>+<kbd>R</kbd>, type `cmd`, press Enter.

**macOS:** press <kbd>Command</kbd>+<kbd>Space</kbd>, type `Terminal`, press
Enter.

A window opens with a line of text and a cursor. That's it — you type a command,
press Enter, and it prints its answer. Everything these scripts produce is plain
text, so a screen reader reads it like any other text on screen.

---

## About typing file paths

Every command below needs two paths: where the script is, and where your project
is. You don't have to navigate anywhere — **just give the full path to each**,
and it works from wherever the terminal happens to start.

**If a path has a space in it, put quotes around it.** `E:\reaper\my song.RPP`
will fail; `"E:\reaper\my song.RPP"` works. When in doubt, quote it — quoting a
path that didn't need it does no harm.

A shortcut worth knowing: in Windows File Explorer, holding <kbd>Shift</kbd> and
right-clicking a file gives you **"Copy as path"**, which puts the full path on
your clipboard with the quotes already added. Paste it straight into the terminal
with <kbd>Ctrl</kbd>+<kbd>V</kbd>.

In the examples below, replace `C:\git-src\rozaya-jsfx` with wherever you put
this project's folder, and the `.RPP` path with your own.

---

## Step one: see what is in a project

```
python C:\git-src\rozaya-jsfx\tools\passage_captures.py "E:\reaper\nightfall.RPP"
```

This changes nothing. It reads your project and describes it. You'll get
something like:

```
== E:\reaper\nightfall.RPP
   08  (spectral_vowel_passage, line 136) -- 8 slot(s), 48000 Hz
      slot 1   0.68 s  peak   -6.8 dB  rms  -15.9 dB  F#2   -41 cents    90.3 Hz
      slot 2   0.68 s  peak   -5.9 dB  rms  -15.9 dB  F#2   +22 cents    93.7 Hz
      slot 3   0.68 s  peak   -6.2 dB  rms  -16.3 dB  unpitched
```

Reading a line, left to right:

- **`slot 1`** — which slot, matching the Capture slot control in the plugin.
- **`0.68 s`** — how much of it is actual sound rather than silence.
- **`peak` and `rms`** — how loud it is. `peak` is the loudest instant, `rms` is
  the general loudness. Both in dB, same as the plugin's level controls.
- **`F#2 -41 cents 90.3 Hz`** — the note it's singing. A cent is a hundredth of
  a semitone, so *−41 cents* means a little under halfway flat of F#2. The Hz
  figure is the same thing said differently.

Two things you'll see instead of a note:

- **`unpitched`** — it couldn't find a clear note. Usually a breath, a
  consonant, or something too noisy to have one. This is useful rather than a
  failure: those slots are the ones the **voice** engine will struggle with and
  the **wash** engine will like.
- **`(empty -- captured silence)`** — nothing was playing when Capture fired.
  That's the classic mistake, and now you can see it in a list instead of
  discovering it when the morph goes quiet.

If your project has several copies of the plugin, you'll get a block like this
for each, labelled with its track name.

---

## Step two: save them as files

```
python C:\git-src\rozaya-jsfx\tools\passage_captures.py "E:\reaper\nightfall.RPP" --extract "E:\captures"
```

The `--extract` part means "and also write them out, into this folder". The
folder is created if it doesn't exist. You get one WAV per non-empty slot, named
after the project, track and slot, at your project's own sample rate.

Now they're just audio files. You can play them, keep them, back them up, or:

- put them in your REAPER `Data\glasswings_samples\` folder and they'll appear in
  **Sustain Looper**'s file list;
- run them through `loop_finder.py` to pull loop-ready pieces out;
- capture them into a different project.

**This is worth doing even if you have no plan for them.** A capture that exists
only inside one project file is one bad save away from gone.

---

## Step three (optional): put a WAV into a slot

```
python C:\git-src\rozaya-jsfx\tools\passage_inject.py "E:\reaper\nightfall.RPP" --set 3=vowel.wav
```

`--set 3=vowel.wav` means "put this file into slot 3". You can repeat it —
`--set 3=a.wav --set 5=b.wav` — to fill several at once.

**Close the project in REAPER first.** REAPER holds its own copy of an open
project in memory and writes it back over any changes when you next save, so an
edit made underneath an open project silently vanishes.

By default this writes a **new** project next to yours, named with `-injected` on
the end, and leaves your original untouched. Open the new one to hear the result.

Two things it will tell you about:

- **Wrong sample rate.** It stops rather than continuing. This isn't fussiness:
  nothing inside a project records what rate a capture was made at, so a 44.1 kHz
  file in a 48 kHz project would simply play sharp and short — no error anywhere,
  and a result that sounds plausible enough to fool you. Either supply a file at
  the project's rate, or add `--resample` to have it converted.
- **Short files.** Anything under about 0.68 seconds gets centred with silence
  around it, and the slot's **Capture point** is set for you so the plugin
  analyses the sound instead of the silence. Without that the slot would come out
  silent and look like the whole thing had failed.

After writing, it re-reads its own work and checks that your slots landed *and*
that nothing else moved. If either check fails it says so plainly instead of
claiming success.

---

## When something goes wrong

| What you see | What it means |
|---|---|
| `Python was not found` | Python isn't installed, or the "Add to PATH" box wasn't ticked during install. Reinstall and tick it. |
| `can't open file ...` | The path to the script is wrong. Check the folder name and spelling. |
| `No such file or directory` | The path to your project is wrong, or it has a space in it and needs quotes. |
| `no Passage / Morpher instances found` | That project doesn't use either plugin — or you pointed at the wrong project. |
| `unrecognised blob layout` | The captures were saved by a version of the plugin these tools don't know. They stop rather than guess, because a wrong guess would produce believable nonsense. |
| `This project has 20 instances` | The project has several copies of the plugin. It lists them; pick one by adding `--instance 2` (or whichever number). |
| Nothing at all happens | You may have missed the Enter key, or the terminal is waiting on an unclosed quote. Press <kbd>Ctrl</kbd>+<kbd>C</kbd> and try again. |

---

## Is this safe?

**`passage_captures.py` cannot damage anything.** It opens your project
read-only and never writes to it. The worst it can do is misread something and
tell you something wrong.

**`passage_inject.py` writes**, so it defaults to making a copy and leaving your
project alone. If you ask it to edit in place with `--in-place`, it first saves a
backup next to the original ending in `.pre-inject-bak`, and refuses to start if
such a backup already exists — so it can never quietly overwrite your safety net.

Every command takes `--help` if you want the full list of what it accepts:

```
python C:\git-src\rozaya-jsfx\tools\passage_captures.py --help
```
