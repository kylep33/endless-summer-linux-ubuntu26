            // Endless Summer: theme sounds switch, opposite the "Raise maximum volume" one
            PC3.Switch {
                id: esSounds
                anchors.right: parent.right
                anchors.rightMargin: Kirigami.Units.smallSpacing
                anchors.verticalCenter: parent.verticalCenter
                text: "Theme sounds"
                checked: true
                onToggled: esRun.connectSource("/usr/libexec/endless-summer-sounds " + (checked ? "--on" : "--off"))
                ESP5.DataSource {
                    id: esRun
                    engine: "executable"
                    onNewData: (source, data) => {
                        if (source.endsWith("--state")) {
                            esSounds.checked = data.stdout.trim() === "on";
                        }
                        disconnectSource(source);
                    }
                    Component.onCompleted: connectSource("/usr/libexec/endless-summer-sounds --state")
                }
            }
