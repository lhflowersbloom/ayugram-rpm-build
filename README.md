# AyuGram Desktop — Fedora RPM builds

[![Build AyuGram Desktop RPM](https://github.com/lhflowersbloom/ayugram-rpm-build/actions/workflows/build-ayugram-rpm.yml/badge.svg)](https://github.com/lhflowersbloom/ayugram-rpm-build/actions/workflows/build-ayugram-rpm.yml)

Automated **Fedora RPM** builds of [AyuGram Desktop](https://github.com/AyuGram/AyuGramDesktop) — a Telegram Desktop fork with Ghost mode, anti-recall and extended customisation.

Upstream only ships macOS (`.dmg`) and Windows (`.zip`) builds. For Linux it publishes source only, so the packages here are compiled from that source on GitHub Actions, then packaged with `rpmbuild`.

> Unofficial build. Not affiliated with AyuGram or Telegram. GPL-3.0-or-later, same as upstream.

## Install

Open the [latest release](https://github.com/lhflowersbloom/ayugram-rpm-build/releases/latest) and install the `.rpm` directly from its URL — the file name carries the version, so it changes with every build:

```bash
sudo dnf install https://github.com/lhflowersbloom/ayugram-rpm-build/releases/latest/download/ayugram-desktop-7.2.9-2.fc45.x86_64.rpm
```

Or download it and install locally:

```bash
sudo dnf install ./ayugram-desktop-*.rpm
ayugram-desktop     # or "AyuGram Desktop" from the app menu
```

Installed files:

```
/usr/bin/AyuGram
/usr/share/applications/com.ayugram.desktop.desktop
/usr/share/metainfo/com.ayugram.desktop.metainfo.xml
/usr/share/dbus-1/services/com.ayugram.desktop.service
/usr/share/icons/hicolor/{16,32,48,64,128,256,512}x*/apps/com.ayugram.desktop.png
```

## Current build

| | |
| --- | --- |
| Version | 7.2.9 (upstream tag `v7.2.9`) |
| Source | compiled from upstream git, static Qt, glibc ≥ 2.28 |
| RPM | `ayugram-desktop-7.2.9-2.fc45.x86_64.rpm` (107 MB) |
| SHA256 | `f0a7fca5c333c305a0715732b6ed18fe086cf97e9581b87f160a857e9a3f38b0` |
| Verified | `dnf install` resolves all sonames; `ldd` clean; launches on Fedora 45 / Wayland |

## How it works

```
check ──▶ upstream releases/latest ──▶ already packaged? ──yes──▶ stop (10 s)
                                           │
                                           no
                                           ▼
        clone upstream (recursive) ──▶ build libtlottie.a ──▶ cmake/ninja build
        ──▶ strip ──▶ rpmbuild ──▶ smoke test in fedora:latest ──▶ release
```

- **Compile environment**: the same image the upstream docs use, `ghcr.io/telegramdesktop/tdesktop/centos_env:latest`, driven by `Telegram/build/docker/centos_env/build.sh`. Build time is ~110 minutes on a 4-core runner.
- **tlottie**: that image ships `tlottie.h` but **not** `libtlottie.a` (its build history has no tlottie stage), so configure fails with `Could not find DESKTOP_APP_TLOTTIE_LIBRARY`. The workflow builds the static lib from `dkaraush/tlottie` @ `31f1b54` + `desktop-app/patches` @ `519aaa08` in a Rust container and drops it into `/usr/local/lib` before configuring.
- **Packaging**: dependencies are pinned explicitly by soname (`libX11.so.6`, `libfontconfig.so.1`, …) plus `glibc >= 2.28`; rpmbuild's automatic dependency generation is disabled because it silently produces nothing in this setup.
- **Smoke test**: the RPM is installed with `dnf` inside a clean `fedora:latest` container — dependency resolution and linking are actually exercised, not assumed.
- **Safety net**: the stripped binary is uploaded as an artifact (`ayugram-binary-<version>`) right after compiling, so a packaging failure never costs another two-hour build.

## Triggers

| Trigger | Behaviour |
| --- | --- |
| Schedule (`0 20 * * *` UTC = 04:00 Asia/Shanghai) | builds only when upstream released a version that has no `build-<version>-N` tag here yet |
| Manual *Run workflow* | always builds; `ref` empty = latest upstream release tag |
| Push tags | intentionally **not** configured — release tags would re-trigger the workflow |

Builds are serialised with a `concurrency` group; two concurrent builds would fight over 4 cores and RAM during linking.

## Layout

```
.github/workflows/build-ayugram-rpm.yml   # the whole pipeline
```

## Notes

- Uses the public Telegram API credentials that AyuGram's own build docs specify (`api_id 2040`).
- Each release also carries `AyuGram-<version>-linux-x86_64.tar.gz` (portable binary, no install needed).
- If a build fails, the compile output is still available under that run's artifacts.
