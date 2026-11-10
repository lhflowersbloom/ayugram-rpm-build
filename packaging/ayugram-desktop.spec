# Packaging for the AyuGram binary the workflow compiles in the step before this
# one. Nothing is compiled here: the binary, the XDG files and the icons are
# staged into SOURCES, then rpmbuild is invoked with
#
#   --define "aver <upstream version>"    e.g. 7.2.9
#   --define "arel <release>"             e.g. 12
#
# aver has no default on purpose: a bare `rpmbuild -bb` should fail on "Version
# field must be present" rather than quietly produce a 0-version package.
#
# Runtime dependencies cannot be auto-generated in this setup (rpmbuild emits
# none for this stripped binary with a statically linked Qt), so the workflow
# derives them from `ldd` and injects them at the @LDD_REQUIRES@ marker below.

%global debug_package %{nil}

Name:           ayugram-desktop
Version:        %{?aver}
Release:        %{!?arel:2}%{?arel}%{?dist}
Summary:        AyuGram Desktop - Telegram Desktop fork with Ghost mode
License:        GPL-3.0-or-later
URL:            https://github.com/AyuGram/AyuGramDesktop
Source0:        AyuGram
Source1:        com.ayugram.desktop.desktop
Source2:        com.ayugram.desktop.metainfo.xml
Source3:        com.ayugram.desktop.service
Source4:        icon16.png
Source5:        icon32.png
Source6:        icon48.png
Source7:        icon64.png
Source8:        icon128.png
Source9:        icon256.png
Source10:       icon512.png
BuildArch:      x86_64
AutoReqProv:    no
# @LDD_REQUIRES@
Requires:       glibc >= 2.28

%description
AyuGram Desktop is an unofficial Telegram Desktop fork with Ghost mode,
anti-recall and extended customisation. Linux build compiled from upstream
sources.

%prep
%build

%install
umask 022
install -d %{buildroot}%{_bindir} %{buildroot}%{_datadir}/applications \
           %{buildroot}%{_datadir}/metainfo %{buildroot}%{_datadir}/dbus-1/services
for d in 16x16 32x32 48x48 64x64 128x128 256x256 512x512; do
  install -d %{buildroot}%{_datadir}/icons/hicolor/$d/apps
done
install -m 0755 %{SOURCE0} %{buildroot}%{_bindir}/AyuGram
install -m 0644 %{SOURCE1} %{buildroot}%{_datadir}/applications/
install -m 0644 %{SOURCE2} %{buildroot}%{_datadir}/metainfo/
install -m 0644 %{SOURCE3} %{buildroot}%{_datadir}/dbus-1/services/
install -m 0644 %{SOURCE4} %{buildroot}%{_datadir}/icons/hicolor/16x16/apps/com.ayugram.desktop.png
install -m 0644 %{SOURCE5} %{buildroot}%{_datadir}/icons/hicolor/32x32/apps/com.ayugram.desktop.png
install -m 0644 %{SOURCE6} %{buildroot}%{_datadir}/icons/hicolor/48x48/apps/com.ayugram.desktop.png
install -m 0644 %{SOURCE7} %{buildroot}%{_datadir}/icons/hicolor/64x64/apps/com.ayugram.desktop.png
install -m 0644 %{SOURCE8} %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/com.ayugram.desktop.png
install -m 0644 %{SOURCE9} %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/com.ayugram.desktop.png
install -m 0644 %{SOURCE10} %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/com.ayugram.desktop.png

%post
[ -x /usr/bin/gtk-update-icon-cache ] && /usr/bin/gtk-update-icon-cache -q -t -f %{_datadir}/icons/hicolor 2>/dev/null || :
[ -x /usr/bin/update-desktop-database ] && /usr/bin/update-desktop-database -q %{_datadir}/applications 2>/dev/null || :

%postun
[ -x /usr/bin/gtk-update-icon-cache ] && /usr/bin/gtk-update-icon-cache -q -t -f %{_datadir}/icons/hicolor 2>/dev/null || :

%files
%{_bindir}/AyuGram
%{_datadir}/applications/com.ayugram.desktop.desktop
%{_datadir}/metainfo/com.ayugram.desktop.metainfo.xml
%{_datadir}/dbus-1/services/com.ayugram.desktop.service
%{_datadir}/icons/hicolor/*/apps/com.ayugram.desktop.png

%changelog
* Tue Nov 10 2026 CI <ci@localhost> - %{?aver}-%{?arel}
- Build from upstream sources
