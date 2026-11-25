# Sourced by startplasma before plasmashell starts. On the first themed login, set the old panel layout
# aside so plasmashell builds ours from the look-and-feel package itself. (Resetting it from autostart,
# once plasmashell was up, raced plasmashell's own first-run layout and left two panels.)
es_c="${XDG_CONFIG_HOME:-$HOME/.config}"
if [ ! -e "$es_c/endless-summer-applied" ]; then
    for es_f in plasma-org.kde.plasma.desktop-appletsrc plasmashellrc; do
        [ -e "$es_c/$es_f" ] && mv -f "$es_c/$es_f" "$es_c/$es_f.before-endless-summer"
    done
    kwriteconfig6 --file kdeglobals --group KDE --key LookAndFeelPackage org.endlesssummer.desktop
fi
unset es_c es_f
