#!/bin/bash
# Optional add-on: package sounds/root/ plus the clips in transitions/ into endless-summer-sounds_<version>_all.deb
# Local builds only: the clips are not ours to redistribute, so keep this .deb to yourself.
set -euo pipefail
cd "$(dirname "$0")"

VERSION=${VERSION:-26.1.2}
OUT=endless-summer-sounds_${VERSION}_all.deb
PKG=$(mktemp -d)
trap 'rm -rf "$PKG"' EXIT

cp -a sounds/root/. "$PKG/"
for pool in login_sounds notification_sounds logout_sounds error_sounds; do
    ls transitions/$pool/*.wav >/dev/null || { echo "pool $pool has no clips" >&2; exit 1; }
    cp -r transitions/$pool "$PKG/usr/share/endless-summer-sounds/"
done
mkdir -p "$PKG/DEBIAN"
chmod -R u=rwX,go=rX "$PKG"
chmod 755 "$PKG/usr/libexec/endless-summer-sounds"
(cd "$PKG" && find etc -type f | sed 's|^|/|') > "$PKG/DEBIAN/conffiles"

cat > "$PKG/DEBIAN/control" <<EOF
Package: endless-summer-sounds
Version: $VERSION
Architecture: all
Section: sound
Priority: optional
Maintainer: kylep33 <kyleapereira33@gmail.com>
Depends: kde-plasma-desktop
Recommends: endless-summer-theme
Installed-Size: $(du -sk "$PKG/usr" "$PKG/etc" | awk '{s+=$1} END {print s}')
Description: Chicken Joe and Endless Summer sounds for Endless Summer Linux
 Plays random Chicken Joe lines and Endless Summer theme clips for desktop
 events.
EOF

# Older versions ran from autostart, too late for the login sound; dpkg keeps the obsolete conffile.
cat > "$PKG/DEBIAN/postinst" <<'EOF2'
#!/bin/sh
set -e
[ "$1" = configure ] && rm -f /etc/xdg/autostart/endless-summer-sounds.desktop
exit 0
EOF2

# Per-user links would dangle once the clips are gone.
cat > "$PKG/DEBIAN/prerm" <<'EOF'
#!/bin/sh
set -e
if [ "$1" = remove ]; then
    rm -rf /home/*/.local/share/sounds/endless-summer
fi
EOF
chmod 755 "$PKG/DEBIAN/prerm" "$PKG/DEBIAN/postinst"

dpkg-deb --root-owner-group -Zxz --build "$PKG" "$OUT"

LIST=$(dpkg-deb -c "$OUT")
for f in usr/libexec/endless-summer-sounds \
         usr/share/endless-summer-sounds/index.theme \
         etc/xdg/plasma-workspace/env/endless-summer-sounds.sh; do
    grep -q " \./$f\$" <<<"$LIST" || { echo "missing $f in $OUT" >&2; exit 1; }
done
echo "built $OUT"
