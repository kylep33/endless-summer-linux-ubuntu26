# Endless Summer Linux for Ubuntu 26.04

Turns an Ubuntu (or any Debian-family) install into a 60s surf-film desktop: KDE Plasma 6 global theme in **Endless Summer** (day) and **Endless Summer Night** variants, sand/ocean color schemes, Papirus icons with sand or ocean folders, real HD surf photos as wallpaper (a new random one at every login), SDDM login screen, Plasma splash and Plymouth boot splash. Works the same way as Hannah Montana Linux (`../hannah-montana-linux-ubuntu26`).

**Personal use only.** The photos (including the wallpapers), the Chicken Joe avatar and the sound clips come from films and records we don't own. Don't publish the `.deb`s or this folder.

## Build

```
./build-deb.sh          # → endless-summer-theme_26.1.2_all.deb
./build-sounds-deb.sh   # → endless-summer-sounds_26.1.2_all.deb (optional)
```

Needs only `dpkg-deb`.

## Install

```
cp endless-summer-*.deb /tmp/
sudo apt install /tmp/endless-summer-theme_26.1.2_all.deb /tmp/endless-summer-sounds_26.1.2_all.deb
```

1. Apt pulls in KDE Plasma, SDDM, Plymouth, Papirus and the X server. When asked for a display manager, pick **sddm**.
2. Reboot.
3. On the login screen, pick the **Plasma** session (bottom-left), then log in.

On each user's first Plasma login the day theme is applied, once. Every login after that sets a random photo from `/usr/share/endless-summer/wallpapers/` as the desktop wallpaper, overriding any wallpaper picked in between. Switch to Night in System Settings → Global Theme. To re-apply: `rm ~/.config/endless-summer-applied` and log in again.

Cannot be installed alongside `hannah-montana-theme` (both take over the same skel and about-dialog files).

## Sounds

Every login, each desktop event gets a random clip from its pool.

| Pool | Events | Clips |
|------|--------|-------|
| `login_sounds` | login, unlock, alarm | The Sandals' *Theme from The Endless Summer*, "I'm Chicken Joe, man", "Whoo-hoo! I'm flying!" … |
| `logout_sounds` | logout, lock | theme intro, "I'll see you in the lineup", "See you guys later" … |
| `notification_sounds` | trash, device added, done, message | "Sweet, man", "Check it out", "Got it!" … |
| `error_sounds` | errors, warnings, questions | "I lost a bet", "Oh, crap", "I won?" … |

Add or swap clips by dropping `.wav` files into `transitions/<pool>/` and rebuilding.

## Layout

- `root/`: main theme, installed as-is under `/`. Edit here.
- `sounds/root/` + `transitions/`: sounds add-on.
- `assets/`: sources, not packaged.
  - `make-art.py` renders every image in `root/` (needs `cairosvg`, `pillow`).
  - `make-clips.py` cuts `transitions/` from the YouTube sources listed in it (needs `yt-dlp`, `faster-whisper`, `imageio-ffmpeg`).
  - `photos/` holds the reference photos. `photos/surf/` holds the wallpaper photos, listed in `PHOTOS` in `make-art.py`.

## Credits

Built on KDE Breeze (SDDM theme, color scheme structure, splash) and [Papirus](https://github.com/PapirusDevelopmentTeam/papirus-icon-theme) icons (GPLv3). Font: [Bebas Neue](https://github.com/dharmatype/Bebas-Neue) (OFL). Package structure from Hannah Montana Linux 26. Licensed GPLv3+ (see `LICENSE`), except the third-party media noted above.
