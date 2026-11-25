    // Endless Summer: Chicken Joe when the menu opens. Reloaded each time, so it stays quiet
    // while the link is gone (theme sounds switched off in the volume popup).
    onExpandedChanged: if (kickoff.expanded) {
        esJoe.source = "";
        esJoe.source = "file://@THEME@/stereo/es-menu-open.wav";
    }
    ESSound.SoundEffect {
        id: esJoe
        onStatusChanged: if (status === ESSound.SoundEffect.Ready) play()
    }
