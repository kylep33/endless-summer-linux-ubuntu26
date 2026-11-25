loadTemplate("org.kde.plasma.desktop.defaultPanel")

var desktopsArray = desktopsForActivity(currentActivity());
for( var j = 0; j < desktopsArray.length; j++) {
    desktopsArray[j].wallpaperPlugin = 'org.kde.image';
}

// floating panel; the EndlessSummer Plasma style makes it solid navy
panels().forEach(function (p) {
    p.floating = true;
});
