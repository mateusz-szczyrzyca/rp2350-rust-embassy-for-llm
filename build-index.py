#!/usr/bin/env python3
# build-index.py — two-layer INDEX: curated (from preprocessing) + repo summaries
import pathlib
import re
from collections import defaultdict

import yaml

ROOT = pathlib.Path("docs")
OUT = ROOT / "INDEX.md"
CURATED_ROOT = ROOT / "01-raspberrypi-pdfs-md"

SKIP_PARTS = {
    "_archive_full_chapters",
    ".git",
    "target",
    "node_modules",
    "01-raspberrypi-pdfs",
    "02-chip-datasheets",
}
NOISE_FILES = {
    "CHANGELOG.md",
    "LICENSE.md",
    "LICENSE-MIT.md",
    "LICENSE-APACHE.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    "AUTHORS.md",
    "RELEASE.md",
    "RELEASES.md",
    "MAINTENANCE.md",
}


def is_skipped(path: pathlib.Path) -> bool:
    return any(p in SKIP_PARTS for p in path.parts)


def parse_fm(path: pathlib.Path):
    try:
        text = path.read_text(errors="ignore")[:4000]
    except Exception:
        return {}
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}


def describe(meta, path):
    # Titles come straight from each file's YAML frontmatter (already English,
    # as extracted from the official RPi PDFs). `api_module` is a C/Rust module
    # identifier and is emitted verbatim in backticks.
    parts = []
    if api := meta.get("api_module"):
        parts.append(f"`{api}`")
    if sec := meta.get("section"):
        parts.append(sec)
    elif ch := meta.get("chapter"):
        parts.append(ch)
    elif src := meta.get("source"):
        parts.append(src)
    return " — ".join(parts) if parts else path.stem


def group_curated(rel: pathlib.Path) -> str:
    if "rp2040-chapters" in rel.parts:
        return "RP2040 datasheet (chapters)"
    if "rp2350-chapters" in rel.parts:
        return "RP2350 datasheet (chapters)"
    if "pico-c-sdk-chapters" in rel.parts:
        return "Pico C/C++ SDK (chapters and API modules)"
    name = rel.name
    if "datasheet.md" in name:
        return "Board datasheets (Pico, Pico W, Pico 2, Pico 2 W)"
    if "product-brief" in name:
        return "Product briefs"
    if "hardware-design" in name:
        return "Hardware design"
    return "Other (tutorials, Python SDK, networking)"


def collect_curated():
    groups = defaultdict(list)
    if not CURATED_ROOT.exists():
        return groups
    for md in CURATED_ROOT.rglob("*.md"):
        if is_skipped(md):
            continue
        meta = parse_fm(md)
        rel = md.relative_to(ROOT)
        groups[group_curated(rel)].append((rel, meta))
    return groups


def collect_repo_summary():
    counts = defaultdict(int)
    for md in ROOT.rglob("*.md"):
        if is_skipped(md):
            continue
        try:
            md.relative_to(CURATED_ROOT)
            continue
        except ValueError:
            pass
        if md.name in NOISE_FILES:
            continue
        parts = md.relative_to(ROOT).parts
        key = "/".join(parts[:2]) if len(parts) > 1 else parts[0]
        counts[key] += 1
    return dict(sorted(counts.items()))


# Human-facing one-line descriptions per repo. Keys are repo paths (do NOT
# translate the keys); values are English prose. Backtick'd tokens are crate /
# module / path identifiers and are kept verbatim.
REPO_DESCRIPTIONS = {
    "04-rust-rp/rp-hal": "RP2040 + RP2350 bare-metal HAL; `rp2040-hal`, `rp235x-hal` + `rp{2040,235x}-hal-examples/` (blinky, pio, dma, usb, i2c, spi, uart, multicore, pwm). **First stop** for bare-metal Rust patterns.",
    "04-rust-rp/rp-hal-boards": "BSPs (rp-pico, adafruit_kb2040, sparkfun, pimoroni, ...) — ready-made board configurations.",
    "04-rust-rp/rp2040-project-template": "rp2040-hal starter project: defmt + defmt-rtt + panic-probe + flip-link + probe-rs runner.",
    "04-rust-rp/rp235x-project-template": "rp235x-hal starter project — the RP2350 equivalent.",
    "04-rust-rp/pio-rs": "PIO assembler in Rust + the `pio!` macro. For bare-metal compile-time generation of PIO programs.",
    "05-embassy/embassy": "Main Embassy repo (sparse checkout): `embassy-rp`, `embassy-executor`, `embassy-net`, `embassy-usb`, `cyw43`, `cyw43-firmware/`, `examples/rp/`, `examples/rp23/`. **First stop** for async/await patterns.",
    "05-embassy/trouble": "BLE host stack compatible with `cyw43` (Pico W, Pico 2 W).",
    "05-embassy/bt-hci": "HCI traits used by TrouBLE.",
    "05-embassy/cyw43-driver": "Original georgerobotics CYW43 C driver — semantics reference for the Rust `cyw43`.",
    "06-rtic/rtic": "RTIC v2 framework + book in `book/en/`. Real-time with SRP priorities.",
    "06-rtic/rtic-examples": "RTIC examples for various MCUs.",
    "07-tooling/probe-rs": "Flash/debug toolkit for ARM+RISC-V (SWD/JTAG). Runner for `cargo run`. Docs in `docs/`.",
    "07-tooling/defmt": "Deferred-formatting logger for MCUs + `defmt-rtt` + book.",
    "07-tooling/flip-link": "Linker wrapper, zero-cost stack overflow protection.",
    "07-tooling/elf2uf2-rs": "ELF → UF2 conversion for the BOOTSEL drive.",
    "07-tooling/cargo-binutils": "`cargo size/nm/objdump/readobj` via LLVM.",
    "08-traits-infra/embedded-hal": "Traits (`SpiBus`, `I2c`, `DelayNs`, ...) + `embedded-hal-async`.",
    "08-traits-infra/cortex-m": "`cortex-m`, `cortex-m-rt` (#[entry], link.x), `cortex-m-semihosting`.",
    "08-traits-infra/riscv": "RISC-V support (Hazard3 in RP2350).",
    "08-traits-infra/critical-section": "Plug-and-play critical sections.",
    "08-traits-infra/portable-atomic": "Portable atomics (RP2040 M0+ has no native CAS — requires critical-section).",
    "08-traits-infra/fugit": "Compile-time time types (`Duration`, `Instant`, `Rate`).",
    "08-traits-infra/heapless": "`Vec`, `String`, `Deque`, MPMC queues without alloc.",
    "09-usb/usb-device": "No-std device-side USB framework.",
    "09-usb/usbd-serial": "CDC-ACM (USB virtual serial).",
    "09-usb/usbd-hid": "USB HID + descriptor macros.",
    "09-usb/tinyusb": "C USB stack — contrast/reference for embassy-usb.",
    "10-net/smoltcp": "Event-driven TCP/IP stack without heap. Used by `embassy-net`.",
    "10-net/reqwless": "Async HTTP client.",
    "11-graphics/embedded-graphics": "No-std graphics (primitives, fonts, BMP).",
    "12-raspberrypi-c-sdk/pico-sdk": "Official C/C++ SDK.",
    "12-raspberrypi-c-sdk/pico-examples": 'Official RPi examples: blink, PIO, DMA, USB CDC, networking, pico_w. **Contrast to Embassy/rp-hal** — when you want to see "how it\'s done in C".',
    "12-raspberrypi-c-sdk/pico-extras": "Experimental libraries (audio I2S/PWM/SPDIF, sleep, scanvideo, SDIO).",
    "12-raspberrypi-c-sdk/picotool": "CLI: UF2/ELF inspection, BOOTSEL, OTP/sign on RP2350.",
    "12-raspberrypi-c-sdk/pico-bootrom-rp2040": "RP2040 bootrom sources.",
    "12-raspberrypi-c-sdk/pico-bootrom-rp2350": "RP2350 bootrom sources (secure boot, M33 + M23 NS + RISC-V).",
    "12-raspberrypi-c-sdk/debugprobe": "Debug Probe firmware (CMSIS-DAP) — used as a probe on a Pico/Pico 2.",
    "13-books/book": "**The Embedded Rust Book** — bare-metal Rust fundamentals.",
    "13-books/embedonomicon": "**The Embedonomicon** — how to bootstrap `no_std` (vector table, linker, semihosting).",
    "13-books/discovery-mb2": "Discovery book (micro:bit v2) — an introduction to MCUs through Rust.",
    "13-books/awesome-embedded-rust": "Curated list of crates, BSPs, tools, and tutorials.",
}


def render():
    out = ["# RP2040 / RP2350 Knowledge Base Index", ""]
    out.append(
        "Auto-generated by `build-index.py`. Re-run it after adding or changing files in `docs/`."
    )
    out.append("")

    # === Layer 1: Curated ===
    out.append("## Part 1: Curated knowledge base (from official RPi PDFs)")
    out.append("")
    out.append(
        "These files are conversions of the official Raspberry Pi PDFs, split into chapters / sections / API modules. Each carries YAML frontmatter with metadata (`mcu`, `chapter`, `section`, `api_module`, `topics`)."
    )
    out.append("")

    groups = collect_curated()
    order = [
        "RP2040 datasheet (chapters)",
        "RP2350 datasheet (chapters)",
        "Pico C/C++ SDK (chapters and API modules)",
        "Board datasheets (Pico, Pico W, Pico 2, Pico 2 W)",
        "Hardware design",
        "Product briefs",
        "Other (tutorials, Python SDK, networking)",
    ]
    total_curated = 0
    for g in order:
        if g not in groups:
            continue
        items = sorted(groups[g], key=lambda x: str(x[0]))
        total_curated += len(items)
        out.append(f"### {g}  _({len(items)} files)_")
        out.append("")
        for path, meta in items:
            out.append(f"- `{path}` — {describe(meta, path)}")
        out.append("")

    # === Layer 2: Repos ===
    out.append("## Part 2: Code and documentation repositories (cloned from GitHub)")
    out.append("")
    out.append(
        "Cursor indexes these repos natively — code by AST, Markdown semantically. This is just the map."
    )
    out.append("")

    repo_counts = collect_repo_summary()
    total_repo = sum(repo_counts.values())

    by_top = defaultdict(list)
    for key, n in repo_counts.items():
        top = key.split("/")[0]
        by_top[top].append((key, n))

    top_titles = {
        "04-rust-rp": "Rust core for RP (rp-rs)",
        "05-embassy": "Embassy + CYW43 (WiFi/BT)",
        "06-rtic": "RTIC v2",
        "07-tooling": "Tooling: probe-rs, defmt, flip-link, elf2uf2",
        "08-traits-infra": "Traits and infrastructure (embedded-hal, cortex-m, riscv, ...)",
        "09-usb": "USB (usb-device, usbd-serial, usbd-hid, tinyusb)",
        "10-net": "Networking (smoltcp, reqwless)",
        "11-graphics": "Graphics (embedded-graphics)",
        "12-raspberrypi-c-sdk": "Raspberry Pi C/C++ SDK (as contrast/reference)",
        "13-books": "Embedded Rust books",
        "14-pimoroni-pico-plus-2w/pimoroni-pico": "Pimoroni libraries for the whole Pico family (C/C++/MicroPython). Includes board definitions for the Pico Plus 2 W (PSRAM, 16 MB flash, qwiic, USB-C, battery, debug header).",
        "14-pimoroni-pico-plus-2w/pimoroni-pico-sdk": "pico-sdk fork with Pimoroni patches (PSRAM init, board configs).",
    }
    for top, items in sorted(by_top.items()):
        title = top_titles.get(top, top)
        out.append(f"### {title}")
        out.append("")
        for key, n in sorted(items):
            desc = REPO_DESCRIPTIONS.get(key, "")
            line = f"- `docs/{key}/` — _{n} .md files_"
            if desc:
                line += f" — {desc}"
            out.append(line)
        out.append("")

    out.append("---")
    out.append("")
    out.append(
        f"**Total:** {total_curated} files in the curated layer, ~{total_repo} .md files in the repo (plus Rust/C/Python source code indexed separately)."
    )

    OUT.write_text("\n".join(out))
    print(f"✓ Generated {OUT} ({OUT.stat().st_size // 1024} KB)")
    print(f"  - {total_curated} curated files")
    print(f"  - {total_repo} .md files in the repo (counted, not listed)")


if __name__ == "__main__":
    render()
