#!/bin/bash
# Package root/ (laid out exactly as installed under /) into endless-summer-theme_<version>_all.deb
# Usage: ./build-deb.sh            (VERSION=26.1.3 ./build-deb.sh to bump)
# Personal use only: the photos and Chicken Joe avatar are not ours to redistribute.
set -euo pipefail
cd "$(dirname "$0")"

VERSION=${VERSION:-26.1.2}
OUT=endless-summer-theme_${VERSION}_all.deb
PKG=$(mktemp -d)
trap 'rm -rf "$PKG"' EXIT

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
Depends: kde-plasma-desktop, sddm, plymouth, xserver-xorg, papirus-icon-theme
Conflicts: hannah-montana-theme
Installed-Size: $(du -sk "$PKG/usr" "$PKG/etc" | awk '{s+=$1} END {print s}')
Description: Endless Summer look for KDE Plasma 6
 60s surf-film global theme in day and night variants: colors, Papirus icons
 with sand/ocean folders, wallpapers, SDDM login, Plasma splash and Plymouth
 boot splash.
EOF

PLY=/usr/share/plymouth/themes/endless-summer/endless-summer.plymouth
# icon theme -> Papirus folder color it borrows
FOLDERS="EndlessSummer:paleorange EndlessSummerNight:cyan"

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
        # folder links made by postinst, not owned by dpkg
        rm -rf /usr/share/icons/EndlessSummer/*x*/ /usr/share/icons/EndlessSummerNight/*x*/
        ;;
esac
EOF

cat > "$PKG/DEBIAN/postinst" <<EOF
#!/bin/sh
set -e
if [ "\$1" = configure ]; then
    # Recolor folders the way papirus-folders does, but in our own themes so Papirus stays stock.
    # Linked against whatever Papirus is installed, e.g. folder-cyan-documents.svg -> folder-documents.svg
    for tc in $FOLDERS; do
        theme=\${tc%%:*} color=\${tc#*:}
        for d in /usr/share/icons/Papirus/*x*/places; do
            size=\$(basename "\$(dirname "\$d")")
            case \$size in *@*) continue ;; esac
            mkdir -p "/usr/share/icons/\$theme/\$size/places"
            for f in "\$d"/*-\$color.svg "\$d"/*-\$color-*.svg; do
                [ -e "\$f" ] || continue
                ln -sf "\$f" "/usr/share/icons/\$theme/\$size/places/\$(basename "\$f" | sed "s/-\$color//")"
            done
        done
    done
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
         usr/share/sddm/themes/endless-summer-sddm/Main.qml \
         usr/share/sddm/themes/endless-summer-sddm/background.jpg \
         usr/share/plymouth/themes/endless-summer/endless-summer.plymouth \
         usr/share/plymouth/themes/endless-summer/endless-summer.script \
         usr/share/fonts/truetype/bebas-neue/BebasNeue-Regular.ttf \
         etc/skel/.config/kdeglobals \
         etc/xdg/autostart/endless-summer-first-login.desktop \
         usr/libexec/endless-summer-first-login; do
    grep -q " \./$f\$" <<<"$LIST" || { echo "missing $f in $OUT" >&2; exit 1; }
done
echo "built $OUT"
