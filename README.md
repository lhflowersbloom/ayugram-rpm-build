# AyuGram Desktop RPM for Fedora

[![Build AyuGram Desktop RPM](https://github.com/lhflowersbloom/ayugram-rpm-build/actions/workflows/build-ayugram-rpm.yml/badge.svg)](https://github.com/lhflowersbloom/ayugram-rpm-build/actions/workflows/build-ayugram-rpm.yml)

Automated **Fedora RPM** builds of [AyuGram Desktop](https://github.com/AyuGram/AyuGramDesktop) — the Telegram Desktop
fork with Ghost mode, anti-recall and extended customisation.

Upstream ships macOS (`.dmg`) and Windows (`.zip`) only and publishes source for Linux. These packages are compiled
from that source on GitHub Actions, smoke tested with a real `dnf install`, and published alongside a portable tarball.

> Unofficial build. Not affiliated with AyuGram or Telegram. GPL-3.0-or-later, same as upstream.

## Install

Open [the latest release](https://github.com/lhflowersbloom/ayugram-rpm-build/releases/latest) and install the `.rpm`
straight from its URL — the file name carries the version, so it changes with every build:

```bash
sudo dnf install https://github.com/lhflowersbloom/ayugram-rpm-build/releases/latest/download/ayugram-desktop-<version>.fc45.x86_64.rpm
```

Or install a downloaded file, then launch it:

```bash
sudo dnf install ./ayugram-desktop-*.rpm
ayugram-desktop     # or "AyuGram Desktop" from the app menu
```

> **Package name clash:** RPM Fusion also ships an `ayugram-desktop` package. `dnf` treats this file as the same
> package rather than a second one, so remove the RPM Fusion build first if you want to switch.

## What is in the package

```
/usr/bin/AyuGram
/usr/share/applications/com.ayugram.desktop.desktop
/usr/share/metainfo/com.ayugram.desktop.metainfo.xml
/usr/share/dbus-1/services/com.ayugram.desktop.service
/usr/share/icons/hicolor/{16,32,48,64,128,256,512}x*/apps/com.ayugram.desktop.png
```

Runtime requirements are pinned by soname plus `glibc >= 2.28`; the binary links a static Qt, so it does not chase
Fedora's Qt updates between releases.

## How it works

```
check ──▶ upstream releases/latest ──▶ already packaged? ──yes──▶ stop (10 s)
                                           │
                                           no
                                           ▼
        clone upstream (recursive) ──▶ build libtlottie.a ──▶ cmake/ninja build
        ──▶ strip ──▶ rpmbuild ──▶ smoke test in fedora:latest ──▶ release
```

- **Compile**: the image upstream's own docs use, `ghcr.io/telegramdesktop/tdesktop/centos_env:latest`, driven by
  `Telegram/build/docker/centos_env/build.sh`. About 110 minutes on a 4-core runner.
- **tlottie**: that image ships `tlottie.h` but not `libtlottie.a`, so configure fails. The workflow builds the static
  lib from `dkaraush/tlottie` + `desktop-app/patches` first.
- **Packaging**: `rpmbuild` with automatic dependency generation disabled (it produces nothing in this setup), so
  dependencies are listed explicitly by soname.
- **Smoke test**: `dnf install` inside a clean `fedora:latest` container, so resolution and linking are exercised
  rather than assumed.
- **Safety net**: the stripped binary is uploaded as an artifact right after compiling, so a packaging failure never
  costs another two-hour build.

Everything lives in one file: `.github/workflows/build-ayugram-rpm.yml`.

## Triggers

| Trigger | Behaviour |
| --- | --- |
| Schedule (`0 20 * * *` UTC = 04:00 Asia/Shanghai) | builds only when upstream released a version without a `build-<version>-N` tag here yet |
| Manual *Run workflow* | always builds; empty `ref` = latest upstream release tag |
| Push tags | intentionally **not** configured — release tags would re-trigger the workflow |

Builds are serialised with a `concurrency` group; two concurrent runs would fight over 4 cores and RAM while linking.

## Notes

- Uses the public Telegram API credentials that AyuGram's build docs specify (`api_id 2040`).
- Each release also carries `AyuGram-<version>-linux-x86_64.tar.gz` — the same binary, no install needed.
- A failed build still leaves the compile output under that run's artifacts.

## 中文速览

- 上游只发 macOS/Windows 包，Linux 只给源码；本仓库在 GitHub Actions 上编译源码出 Fedora RPM，另附便携 tar.gz。
- 装：`sudo dnf install ./ayugram-desktop-*.rpm`；启动命令 `ayugram-desktop`。
- 每天 20:00 UTC 检查上游，有新版本才构建；每次发布前都在干净的 `fedora:latest` 容器里真装一遍。
- 包名与 RPM Fusion 的 `ayugram-desktop` 相同，两者只能留一个。
