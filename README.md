# RP2350 Embedded Rust Knowledge Base

A **local, offline-first knowledge base** for building embedded firmware on the
RP2040 / RP2350 in **Rust** with **[Embassy](https://embassy.dev/)** (and RTIC,
`rp-hal`, or bare-metal where you need it).

The target reference board for this repository is the **Pimoroni Pico Plus 2 W**
(RP2350B, 16 MB flash, 8 MB PSRAM, USB-C, Qwiic/STEMMA QT, battery connector,
3-pin debug header, CYW43439 Wi-Fi/BLE), but everything here applies to any
RP2040/RP2350 board — Raspberry Pi Pico, Pico W, Pico 2, Pico 2 W, and most
third-party boards.

---

## Why this repository exists

Rust + Embassy on the RP2350 is a powerful but still **exotic** combination. The
documentation you need is scattered across a dozen upstream repositories, three
large Raspberry Pi PDFs, several crate docs, and a handful of books. When you
pair-program with an LLM (Claude, GPT, Gemini, or a local model), the assistant
normally has to **search the web on every turn** — which is slow, burns tokens,
returns stale or wrong-version answers, and often hallucinates APIs that don't
exist in the crate version you actually use.

This repository solves that by pulling **the canonical sources down to disk**,
chunking the big PDFs into small, metadata-tagged Markdown files, and giving the
model a single `INDEX.md` map. The result:

- **No web round-trips.** The model reads local files. Faster, cheaper, private.
- **Version-pinned truth.** The crate docs and examples on disk match the
  versions you build against — no "the latest blog post says…" drift.
- **Grep-able and chunked.** The official PDFs are split per chapter / section /
  API module so a retrieval step pulls *only* the relevant 2–10 KB file, not a
  500-page document.
- **Contrast material on demand.** The official C/C++ SDK and `tinyusb` are
  included specifically so the model can answer *"how is this done in C?"* and
  translate the pattern to Rust.

> **In one sentence:** this is a curated, offline RAG corpus that turns a
> general-purpose LLM into a competent RP2350-Rust-Embassy pair-programmer
> without it ever touching the network.

---

## Repository layout

The corpus is organised in **two layers**.

### Layer 1 — Curated knowledge base (`01-raspberrypi-pdfs-md/`)

Official Raspberry Pi PDFs converted to Markdown and **split into small files**
by chapter, section, and API module. Every file carries a **YAML frontmatter**
header with structured metadata so a retriever (or the model itself) can filter
precisely:

```yaml
---
mcu: rp2350
chapter: "Chapter 11. PIO"
section: "11.2. Programmer's model"
api_module: hardware_pio
topics: [pio, state-machine, fifo, dma]
---
```

What's inside:

| Group | Files | Contents |
|---|---|---|
| RP2040 datasheet (chapters) | ~36 | Full datasheet, one file per section (bus, clocks, GPIO, PIO, peripherals, electrical). |
| RP2350 datasheet (chapters) | ~38 | Same, for RP2350 — adds security, Cortex-M33, Hazard3 RISC-V, OTP, HSTX, TRNG, SHA-256. |
| Pico C/C++ SDK (chapters + API modules) | ~76 | Per-module API reference (`hardware_*`, `pico_*`). |
| Board datasheets | 6 | Pico, Pico W, Pico 2, Pico 2 W + RP2040/RP2350 silicon datasheets. |
| Hardware design | 2 | "Hardware design with RP2040 / RP2350". |
| Product briefs | 3 | Short overviews. |
| Getting-started / Python SDK / networking | 4 | Tutorials, Pico-W internet guide. |

### Layer 2 — Source repositories (`docs/…`, cloned from GitHub)

Full upstream repos (code + Markdown docs) so the assistant can read **real,
compiling example code** and **actual crate documentation**. These are best
indexed natively by your tool (Cursor indexes them by AST + semantic Markdown);
`INDEX.md` is just the map.

| Area | Path(s) | What it's for |
|---|---|---|
| **Rust for RP** | `04-rust-rp/rp-hal`, `rp-hal-boards`, `pio-rs`, `rp235x-project-template`, … | Bare-metal HAL (`rp235x-hal`), board support packages, the `pio!` assembler macro, starter templates. **First stop** for bare-metal Rust patterns. |
| **Embassy** | `05-embassy/embassy`, `trouble`, `bt-hci`, `cyw43-driver` | The async framework: `embassy-rp`, `embassy-executor`, `embassy-net`, `embassy-usb`, `cyw43` + firmware, and `examples/rp23/`. **First stop** for async/await patterns. BLE via TrouBLE. |
| **RTIC v2** | `06-rtic/rtic`, `rtic-examples` | Real-time interrupt-driven concurrency (SRP priorities) + the RTIC book. The alternative to Embassy when you want hard real-time over async. |
| **Tooling** | `07-tooling/probe-rs`, `defmt`, `flip-link`, `elf2uf2-rs`, `cargo-binutils`, `svd2rust` | Flash/debug (SWD/JTAG), deferred-formatting logging, stack-overflow protection, ELF→UF2, binary inspection. |
| **Traits & infra** | `08-traits-infra/embedded-hal`, `cortex-m`, `riscv`, `critical-section`, `portable-atomic`, `fugit`, `heapless` | The trait ecosystem and `no_std` building blocks (collections without `alloc`, compile-time time types, portable atomics). |
| **USB** | `09-usb/usb-device`, `usbd-serial`, `usbd-hid`, `tinyusb` | Device-side USB framework, CDC-ACM, HID. `tinyusb` (C) as a semantic reference for `embassy-usb`. |
| **Networking** | `10-net/smoltcp`, `reqwless` | `no_std` TCP/IP stack (used by `embassy-net`) and an async HTTP client. |
| **Graphics** | `11-graphics/embedded-graphics` | `no_std` 2D graphics (primitives, fonts, BMP) for displays. |
| **C/C++ SDK (reference)** | `12-raspberrypi-c-sdk/pico-sdk`, `pico-examples`, `picotool`, `pico-bootrom-rp2350`, … | The **contrast layer** — when you need to know how the official C SDK solves something, or use `picotool` for UF2/OTP/signing on RP2350. |
| **Books** | `13-books/book`, `embedonomicon`, `discovery-mb2`, `awesome-embedded-rust` | The Embedded Rust Book, the Embedonomicon (`no_std` bootstrapping), the Discovery book, and the curated awesome-list. |
| **Pimoroni Pico Plus 2 W** | `14-pimoroni-pico-plus-2w/pimoroni-pico`, `pimoroni-pico-sdk` | Pimoroni board libraries and a patched `pico-sdk` fork (PSRAM init, board configs). Board definition for the Pico Plus 2 W: PSRAM, 16 MB flash, Qwiic, USB-C, battery, debug header. |
| Chip datasheets (raw) | `02-chip-datasheets` | Datasheets for peripheral chips you wire up (sensors, displays, …). |

> **Top-level convenience copies:** `embassy-examples-rust/` and
> `pico-examples-sdk/` mirror the example folders for quick browsing;
> `ppico_plus_2_w_pinout_diagram.pdf` is the board pinout.

### The map: `INDEX.md`

`INDEX.md` is the **single entry point** the model should read first. It lists
every curated file with a one-line description, and summarises every cloned repo
with a file count and a "what it's for" note. Regenerate it whenever you add or
remove files (see [Maintenance](#maintenance)).

---

## Quick start

1. **Clone / unpack** this repository to a directory your AI tool can read.
2. **Point your assistant at `INDEX.md` first** (see per-tool sections below).
3. **Ask your question.** Instruct the assistant to consult the local files
   under `docs/` and `01-raspberrypi-pdfs-md/` instead of searching the web.
4. **Pin versions.** Tell the assistant which crate versions you're on so it
   prefers the on-disk docs that match. (The example repos and crate docs here
   reflect a specific snapshot — treat them as the source of truth over its
   training memory.)

A good opening prompt, regardless of tool:

> You have a local, offline knowledge base for RP2350 + Rust + Embassy in this
> workspace. **Always read `INDEX.md` first** to locate relevant files, then read
> the specific files under `01-raspberrypi-pdfs-md/` (datasheets, split by
> section) and `docs/` (crate docs and example code). **Do not search the web** —
> the local files are version-correct and authoritative. My board is the
> **Pimoroni Pico Plus 2 W (RP2350B, 16 MB flash, 8 MB PSRAM, CYW43439
> Wi-Fi/BLE)**. When unsure how an API works, read the relevant file in
> `docs/05-embassy/embassy/` or `docs/04-rust-rp/rp-hal/` before answering, and
> cite the file path you used.

---

## Using it with the popular LLMs

### Claude Code (CLI / IDE / desktop)

Claude Code reads files in your working directory and follows a `CLAUDE.md`
project file automatically. This is the recommended setup.

Create a `CLAUDE.md` at the repo root:

```markdown
# Project: RP2350 + Rust + Embassy firmware

## Knowledge base usage (IMPORTANT)
This workspace contains a local, offline knowledge base. **Do not use web search**
for RP2040/RP2350, Embassy, rp-hal, probe-rs, or related crates — the local files
are version-correct.

**Workflow for any hardware/firmware question:**
1. Read `INDEX.md` to locate relevant files.
2. For silicon/peripheral behaviour, read the matching section under
   `01-raspberrypi-pdfs-md/rp2350-chapters/` (e.g. `rp2350-ch11-pio.md`).
3. For Rust APIs and patterns, read `docs/05-embassy/embassy/` (async) or
   `docs/04-rust-rp/rp-hal/` (bare-metal) FIRST — prefer their example code.
4. Cite the file path(s) you used in your answer.

## Target board
Pimoroni Pico Plus 2 W — RP2350B, 16 MB flash, 8 MB PSRAM, USB-C, Qwiic/STEMMA QT,
battery connector, 3-pin SWD debug header, CYW43439 (Wi-Fi + BLE).

## Toolchain
- `thumbv8m.main-none-eabihf` (RP2350 Arm) — also `riscv32imac` for Hazard3.
- Flash/run via `probe-rs run` (see `docs/07-tooling/probe-rs/`).
- Logging via `defmt` + `defmt-rtt` (see `docs/07-tooling/defmt/`).
- `flip-link` for stack-overflow protection.
```

Then just work normally:

```bash
claude
> Set up a minimal embassy-rp blinky for the Pico Plus 2 W, using the on-disk
> rp235x template and embassy examples as reference.
```

Claude Code will read `CLAUDE.md`, consult `INDEX.md`, open the relevant files,
and stay offline.

> **Tip:** For a large corpus like this, keep the model focused. Reference exact
> paths in your prompt (e.g. *"see `docs/05-embassy/embassy/examples/rp23/`"*)
> when you already know where to look — it avoids unnecessary file reads.

### Cursor

Cursor natively indexes the whole workspace (code by AST, Markdown
semantically), so retrieval over Layer 2 is automatic. Add a project rule so it
prefers local docs.

Create `.cursor/rules/knowledge-base.mdc`:

```markdown
---
description: RP2350 Rust+Embassy offline knowledge base
alwaysApply: true
---
- This workspace is an OFFLINE knowledge base for RP2350 + Rust + Embassy.
- Do NOT search the web for RP2040/RP2350, Embassy, rp-hal, probe-rs, or crate APIs.
- Read `INDEX.md` to locate sources. Datasheet sections live in
  `01-raspberrypi-pdfs-md/`; crate docs and examples live in `docs/`.
- Prefer example code in `docs/05-embassy/embassy/` and `docs/04-rust-rp/rp-hal/`.
- Target board: Pimoroni Pico Plus 2 W (RP2350B, 16MB flash, 8MB PSRAM, CYW43439).
- Cite the file path you used.
```

Then use **`@`-mentions** to scope context precisely, e.g.
`@docs/05-embassy/embassy` or `@01-raspberrypi-pdfs-md/rp2350-chapters`. For
broad questions you can `@`-mention `INDEX.md` and let Cursor's retrieval do the
rest.

### ChatGPT / GPT (Codex CLI, or the web app with Projects)

**Codex CLI / agentic mode:** add an `AGENTS.md` at the repo root with the same
instructions as the `CLAUDE.md` above (the workflow, board, and toolchain
sections). Codex reads it and operates on local files.

**ChatGPT web app:** create a **Project**, then either upload `INDEX.md` plus the
specific files you need into the project's files, or paste `INDEX.md` into the
project instructions and upload files on demand. Because the web app can't read a
local folder, the practical pattern is:

1. Paste `INDEX.md` into the conversation (or the project's custom instructions).
2. Ask the model which files it needs to answer your question.
3. Upload only those files (they're small — usually a few KB each, by design).

A reusable system/instruction block for GPT:

> You are an RP2350 + Rust + Embassy firmware expert. I will provide files from a
> curated offline knowledge base. Treat these files as authoritative and
> **version-correct — prefer them over your training data**, which may describe
> outdated crate APIs. When you need a file you don't have, tell me its path from
> `INDEX.md` and I'll provide it. Target board: Pimoroni Pico Plus 2 W (RP2350B,
> 16 MB flash, 8 MB PSRAM, CYW43439 Wi-Fi/BLE).

### Google Gemini (Gemini CLI, or the web app)

**Gemini CLI:** add a `GEMINI.md` at the repo root (same content as `CLAUDE.md`).
The Gemini CLI reads it as project context and can operate on the local tree.

**Gemini web app / AI Studio:** Gemini's very large context window is a good fit
for a corpus like this — you can paste `INDEX.md` and a generous selection of the
relevant chunked files in one go. Still instruct it to prefer the provided files
over its own memory and to ask for paths it's missing, exactly as in the GPT
block above.

### Local models (Ollama, LM Studio, llama.cpp, mlx)

Running a local code model (e.g. a Qwen-Coder or GLM-class model) keeps
everything fully offline — model *and* corpus. Because local models have smaller
context windows than the frontier hosted ones, **retrieval matters more**:

- **Don't** dump the whole repo into context. Use `INDEX.md` to pick the few
  files you need and paste only those.
- Pair the model with an editor that does retrieval for you:
  - **Continue.dev** (VS Code / JetBrains) — add this folder as a docs/context
    source so it indexes and retrieves chunks automatically against your local
    Ollama/LM Studio endpoint.
  - **Cursor** pointed at a local endpoint, using the rule above.
- The chunked Layer 1 files are deliberately small so they fit comfortably even
  in an 8–16 K context window — that's the whole point of splitting the PDFs.
- Put the short "prefer local files, don't hallucinate APIs, ask for paths"
  instruction into the model's system prompt.

> **Rule of thumb:** the smaller your model's context window, the more you should
> lean on `INDEX.md` + targeted file selection rather than bulk-loading.

---

## Recommended retrieval workflow (any tool)

To get correct answers and minimise tokens, steer the assistant through this
order:

1. **`INDEX.md`** → locate candidate files.
2. **Datasheet section** (`01-raspberrypi-pdfs-md/rp2350-chapters/…`) → *what the
   silicon does* (register behaviour, timing, electrical limits).
3. **Embassy / rp-hal example code** (`docs/05-embassy/…`, `docs/04-rust-rp/…`) →
   *how to express it in Rust* — prefer real example code over prose.
4. **Crate trait docs** (`docs/08-traits-infra/…`) → *the exact trait/signature*.
5. **C SDK / tinyusb** (`docs/12-raspberrypi-c-sdk/…`, `docs/09-usb/tinyusb/`) →
   only as a **contrast/fallback** when the Rust path is unclear.
6. **Tooling docs** (`docs/07-tooling/…`) → flashing, logging, debugging.

Tell the assistant to **cite the file path** it used. That makes its answers
auditable and lets you catch when it's drifting back to training-data guesses.

---

## Pimoroni Pico Plus 2 W cheat-sheet

Practical facts the assistant should keep in mind for this board (verify against
the on-disk datasheets and the pinout PDF):

- **MCU:** RP2350B (Cortex-M33 dual-core *or* Hazard3 RISC-V dual-core; switchable
  architecture). See `01-raspberrypi-pdfs-md/rp2350-chapters/`.
- **Flash:** 16 MB QSPI. **PSRAM:** 8 MB (needs init — see the Pimoroni SDK
  patches in `docs/14-pimoroni-pico-plus-2w/pimoroni-pico-sdk/`).
- **Wireless:** Infineon **CYW43439** (Wi-Fi 4 + Bluetooth/BLE) — driven by the
  `cyw43` crate (`docs/05-embassy/embassy/`), BLE via TrouBLE
  (`docs/05-embassy/trouble/`). Firmware blobs live in `cyw43-firmware/`.
- **Connectors:** USB-C, Qwiic/STEMMA QT (I²C), battery (with charging), 3-pin
  SWD debug header.
- **Rust target:** `thumbv8m.main-none-eabihf` (Arm) or `riscv32imac-unknown-none-elf`
  (Hazard3).
- **Flash/debug:** `probe-rs` over the debug header, or drag-and-drop UF2 via
  BOOTSEL (`elf2uf2-rs` / `picotool`).

> ⚠️ The packaged `14-pimoroni-pico-plus-2w/` directory referenced in `INDEX.md`
> did not need to be inspected to write this README; confirm the exact board
> definition files there match your hardware revision before relying on pin
> assignments.

---

## Maintenance

The index is generated by **`build-index.py`**. After adding, removing, or
re-chunking files under `docs/`, regenerate it:

```bash
python build-index.py
# ✓ Wygenerowano docs/INDEX.md (NN KB)
```

How the script works (worth knowing if you extend the corpus):

- It produces the **two-layer** index automatically:
  - **Layer 1** is read from `docs/01-raspberrypi-pdfs-md/`. The script parses
    each file's **YAML frontmatter** and groups files (RP2040 datasheet, RP2350
    datasheet, Pico C SDK, board datasheets, hardware design, product briefs,
    other). Descriptions are built from `api_module` / `section` / `chapter` /
    `source` metadata — so **good frontmatter yields a good index**. The English
    chapter/section titles coming from that frontmatter are translated to Polish
    on the fly via the `TITLE_PL` map in the script (exact-string match);
    `api_module` values such as `hardware_pio` / `pico_stdlib` are **code
    identifiers and are deliberately left untranslated**.
  - **Layer 2** walks the rest of `docs/`, counts `.md` files per repo, and
    attaches a human-written description from the `REPO_DESCRIPTIONS` /
    `top_titles` tables inside the script. **Add a new repo → add an entry to
    those tables** so it gets a meaningful description.
- It **skips** noise: `.git`, `target`, `node_modules`, the pre-conversion PDF
  folders, and standard repo boilerplate (`LICENSE*`, `CHANGELOG.md`,
  `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, etc.).

To add new silicon documentation, convert the PDF to Markdown, split it per
section, **add YAML frontmatter** (`mcu`, `chapter`, `section`, `api_module`,
`topics`), drop the files under `01-raspberrypi-pdfs-md/`, **add the Polish title
for any new `chapter`/`section` to the `TITLE_PL` map** in `build-index.py`
(otherwise it appears in its original English wording), and re-run the script.

> **Language:** `INDEX.md` is **fully Polish** — section headings, repo
> descriptions, and the chapter/section titles (translated via `TITLE_PL`). The
> only English left is intentional: `api_module` code identifiers (`hardware_*`,
> `pico_*`) and literal folder-name fallbacks. If you ever want an English index
> instead, clear/replace `TITLE_PL` and translate the Polish strings in `order`,
> `top_titles`, `REPO_DESCRIPTIONS`, and the headers in `render()`, then
> regenerate.

---

## Scope, sources, and licensing

This repository is a **convenience aggregation** of third-party material for
offline AI-assisted development. **It does not relicense anything.** Each bundled
source — the Raspberry Pi documentation/PDFs, the C/C++ SDK, Embassy, `rp-hal`,
RTIC, `probe-rs`, the embedded Rust books, the Pimoroni libraries, and every
crate — **remains under its own upstream license** (variously Apache-2.0, MIT,
BSD-3-Clause, CC-BY-SA, and others). Before redistributing, consult each
project's `LICENSE` file and the Raspberry Pi documentation terms, and keep the
upstream attribution intact.

- **Raspberry Pi documentation & SDK:** © Raspberry Pi Ltd.
- **Embassy, rp-hal, RTIC, probe-rs, embedded-hal, smoltcp, embedded-graphics,
  etc.:** © their respective authors/contributors.
- **Pimoroni libraries:** © Pimoroni Ltd.

If you are the maintainer of an included project and want it removed or its
attribution corrected, please open an issue.

---

## Acknowledgements

Built to make offline, token-efficient, version-correct LLM pair-programming on
the RP2350 in Rust practical. The chunking-with-frontmatter approach exists so
that *any* assistant — frontier or local — can retrieve exactly the right few
kilobytes instead of guessing from memory or scraping the web.
