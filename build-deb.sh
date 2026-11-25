#!/bin/bash
# Package root/ (laid out exactly as installed under /) into endless-summer-theme_<version>_all.deb
# Usage: ./build-deb.sh            (VERSION=26.1.6 ./build-deb.sh to bump)
# Personal use only: the photos and Chicken Joe avatar are not ours to redistribute.
set -euo pipefail
cd "$(dirname "$0")"

VERSION=${VERSION:-26.1.5}
OUT=endless-summer-theme_${VERSION}_all.deb
PKG=$(mktemp -d)
trap 'rm -rf "$PKG"' EXIT

# Colloid icons (GPLv3, github.com/vinceliuice/Colloid-icon-theme), pinned and checksummed, assembled
# the way its install.sh does (we don't run it): day = light set, night = dark set, folders in our palette.
COLLOID=2026-08-10
COLLOID_SHA256=367c3ce3ab85721e41ca9aa4fccd1761ec236d1b8cd7daf65f5e9ec88c1a8a15
TGZ=assets/colloid-$COLLOID.tar.gz  # cached, gitignored
[ -e "$TGZ" ] || curl -fsSL -o "$TGZ" "https://github.com/vinceliuice/Colloid-icon-theme/archive/refs/tags/$COLLOID.tar.gz"
echo "$COLLOID_SHA256  $TGZ" | sha256sum -c --quiet
C=$(mktemp -d)
tar xzf "$TGZ" -C "$C" --strip-components=1
trap 'rm -rf "$PKG" "$C"' EXIT
colloid() {  # <theme dir name> <display name> <folder color> <light|dark>
    local d=$PKG/usr/share/icons/$1
    mkdir -p "$d"
    sed "s/^Name=Colloid/Name=$2/; s/^Comment=.*/Comment=Colloid icons for Endless Summer Linux/" "$C/src/index.theme" > "$d/index.theme"
    cp -a "$C"/src/{actions,apps,categories,devices,emblems,mimetypes,places,status} "$d"
    cp -a "$C"/notint/*.svg "$d/places/scalable"
    sed -i "s/#60c0f0/$3/g" "$d"/places/scalable/*.svg "$d"/apps/scalable/*.svg
    if [ "$4" = dark ]; then
        cp -a "$C"/dark/*.svg "$d/places/scalable"
        sed -i "s/#363636/#dedede/g" "$d"/{actions,devices,places,status}/{16,22,24}/*.svg "$d"/{actions,devices,status}/32/*.svg \
            "$d"/{apps,categories}/22/*.svg "$d"/{actions,apps,categories,devices,emblems,mimetypes,places,status}/symbolic/*.svg
    fi
    cp -a "$C"/links/* "$d"
    for x in actions apps categories devices emblems mimetypes places status; do ln -s $x "$d/$x@2x"; done
}
colloid EndlessSummer "Endless Summer" "#F28C28" light
colloid EndlessSummerNight "Endless Summer Night" "#2BB3C9" dark

# Colloid's fixed-size start-here/distributor-logo icons (16/22/24 px, symbolic) would beat our scalable
# logo at panel sizes, so drop every copy; root/ supplies ours under all the names Plasma asks for.
find "$PKG"/usr/share/icons/EndlessSummer* \( -name 'start-here*' -o -name 'distributor-logo*' \) -delete
cp -a root/. "$PKG/"
mkdir -p "$PKG/DEBIAN"
chmod -R u=rwX,go=rX "$PKG"
chmod 755 "$PKG/usr/libexec/endless-summer-first-login"
(cd "$PKG" && find etc -type f | sed 's|^|/|') > "$PKG/DEBIAN/conffiles"

cat > "$PKG/DEBIAN/control" <<EOF
Package: endless-summer-theme
Version: $VERSION
Architecture: all
Section: x11
Priority: optional
Maintainer: kylep33 <kyleapereira33@gmail.com>
Depends: kde-plasma-desktop, sddm, plymouth, xserver-xorg
Conflicts: hannah-montana-theme
Installed-Size: $(du -sk "$PKG/usr" "$PKG/etc" | awk '{s+=$1} END {print s}')
Description: Endless Summer look for KDE Plasma 6
 60s surf-film global theme in day and night variants: colors, Colloid icons
 with orange/teal folders, navy panel style, wallpapers, SDDM login, Plasma splash and Plymouth
 boot splash.
EOF

PLY=/usr/share/plymouth/themes/endless-summer/endless-summer.plymouth

# files also shipped by desktop-base: divert theirs to *.distrib so ours take the path
DIVERT="/etc/skel/.face /etc/skel/.face.icon /etc/xdg/kcm-about-distrorc"
cat > "$PKG/DEBIAN/preinst" <<EOF
#!/bin/sh
set -e
if [ "\$1" = install ] || [ "\$1" = upgrade ]; then
    for f in $DIVERT; do
        dpkg-divert --package endless-summer-theme --rename --divert "\$f.distrib" --add "\$f"
    done
fi
EOF
cat > "$PKG/DEBIAN/postrm" <<EOF
#!/bin/sh
set -e
case "\$1" in
    remove|purge|abort-install|disappear)
        for f in $DIVERT; do
            dpkg-divert --package endless-summer-theme --rename --divert "\$f.distrib" --remove "\$f"
        done
        ;;
esac
EOF

cat > "$PKG/DEBIAN/postinst" <<EOF
#!/bin/sh
set -e
if [ "\$1" = configure ]; then
    # 26.1.2 and older put links to Papirus folders in 16x16/ etc., unowned by dpkg
    rm -rf /usr/share/icons/EndlessSummer/[0-9]*x[0-9]* /usr/share/icons/EndlessSummerNight/[0-9]*x[0-9]*
    # priority 200 beats Ubuntu's bgrt (110); removal falls back automatically
    update-alternatives --install /usr/share/plymouth/themes/default.plymouth default.plymouth $PLY 200
    if command -v update-initramfs >/dev/null; then update-initramfs -u || echo "warning: update-initramfs failed, boot splash unchanged" >&2; fi
fi
EOF
cat > "$PKG/DEBIAN/prerm" <<EOF
#!/bin/sh
set -e
if [ "\$1" = remove ]; then
    update-alternatives --remove default.plymouth $PLY
    if command -v update-initramfs >/dev/null; then update-initramfs -u || true; fi
fi
EOF
chmod 755 "$PKG/DEBIAN/preinst" "$PKG/DEBIAN/postinst" "$PKG/DEBIAN/prerm" "$PKG/DEBIAN/postrm"

dpkg-deb --root-owner-group -Zxz --build "$PKG" "$OUT"

# self-check: the pieces the look-and-feel packages point at made it in
LIST=$(dpkg-deb -c "$OUT")
for f in usr/share/plasma/look-and-feel/org.endlesssummer.desktop/metadata.json \
         usr/share/plasma/look-and-feel/org.endlesssummer.desktop/contents/splash/Splash.qml \
         usr/share/plasma/look-and-feel/org.endlesssummernight.desktop/metadata.json \
         usr/share/plasma/look-and-feel/org.endlesssummernight.desktop/contents/splash/Splash.qml \
         usr/share/wallpapers/EndlessSummer/metadata.json \
         usr/share/wallpapers/EndlessSummer/contents/images/1920x1080.jpg \
         usr/share/wallpapers/EndlessSummer/contents/images_dark/1920x1080.jpg \
         usr/share/endless-summer/wallpapers/01.jpg \
         usr/share/color-schemes/EndlessSummer.colors \
         usr/share/color-schemes/EndlessSummerNight.colors \
         usr/share/icons/EndlessSummer/index.theme \
         usr/share/icons/EndlessSummerNight/index.theme \
         usr/share/icons/EndlessSummer/places/scalable/start-here-kde.svg \
         usr/share/icons/EndlessSummer/places/scalable/folder-documents.svg \
         usr/share/icons/EndlessSummerNight/status/22/audio-volume-high-panel.svg \
         usr/share/plasma/desktoptheme/EndlessSummer/colors \
         usr/share/sddm/themes/endless-summer-sddm/Main.qml \
         usr/share/sddm/themes/endless-summer-sddm/background.jpg \
         usr/share/plymouth/themes/endless-summer/endless-summer.plymouth \
         usr/share/plymouth/themes/endless-summer/endless-summer.script \
         usr/share/fonts/truetype/bebas-neue/BebasNeue-Regular.ttf \
         etc/skel/.config/kdeglobals \
         etc/xdg/autostart/endless-summer-first-login.desktop \
         etc/xdg/plasma-workspace/env/endless-summer-layout.sh \
         usr/libexec/endless-summer-first-login; do
    grep -q " \./$f\$" <<<"$LIST" || { echo "missing $f in $OUT" >&2; exit 1; }
done
echo "built $OUT"
