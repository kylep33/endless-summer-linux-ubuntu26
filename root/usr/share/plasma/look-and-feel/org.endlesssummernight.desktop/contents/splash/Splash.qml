/*
    Endless Summer login splash. Based on Breeze's Splash.qml by Marco Martin.
    SPDX-License-Identifier: GPL-2.0-or-later
*/
import QtQuick
import org.kde.kirigami 2 as Kirigami

Rectangle {
    id: root
    color: "#0B1D2E"

    property int stage
    readonly property var captions: ["Waxing the board…", "Waxing the board…", "Paddling out…", "Checking the swell…", "Catching a wave…", "Hanging ten…", "Surf's up!"]

    Image {
        anchors.fill: parent
        source: "images/background.jpg"
        fillMode: Image.PreserveAspectCrop
        asynchronous: true
    }

    // keeps the text readable on the bright day art
    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#200B1D2E" }
            GradientStop { position: 1.0; color: "#B00B1D2E" }
        }
    }

    Column {
        id: content
        anchors.centerIn: parent
        spacing: Kirigami.Units.gridUnit
        opacity: root.stage >= 2 ? 1 : 0
        Behavior on opacity { OpacityAnimator { duration: Kirigami.Units.veryLongDuration * 2; easing.type: Easing.InOutQuad } }

        Image {
            anchors.horizontalCenter: parent.horizontalCenter
            source: "images/logo.png"
            width: Kirigami.Units.gridUnit * 9
            height: width
            sourceSize.width: width
            sourceSize.height: height
            asynchronous: true
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: "ENDLESS SUMMER"
            color: "#FBF4E4"
            font.family: "Bebas Neue"
            font.pixelSize: Kirigami.Units.gridUnit * 3.5
            font.letterSpacing: Kirigami.Units.gridUnit * 0.35
            style: Text.Raised
            styleColor: "#800B1D2E"
            Accessible.role: Accessible.StaticText
        }

        Rectangle {
            anchors.horizontalCenter: parent.horizontalCenter
            width: Kirigami.Units.gridUnit * 14
            height: 6
            radius: 3
            color: "#40FBF4E4"

            Rectangle {
                height: parent.height
                radius: parent.radius
                color: "#F28C28"
                width: parent.width * Math.min(root.stage, 6) / 6
                Behavior on width { NumberAnimation { duration: Kirigami.Units.longDuration * 3; easing.type: Easing.OutCubic } }
            }
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: root.captions[Math.min(root.stage, 6)]
            color: "#FBF4E4"
            font.pointSize: Kirigami.Theme.defaultFont.pointSize + 1
            Accessible.role: Accessible.StaticText
        }
    }
}
