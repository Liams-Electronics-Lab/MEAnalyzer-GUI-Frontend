import sys
import os
import shutil
import json
import subprocess
import webbrowser
import configparser
import glob
import shlex
from datetime import datetime

# PyQt5 Imports
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel,
                             QPushButton, QFileDialog, QFormLayout, QLineEdit,
                             QMessageBox, QDialog, QTextEdit, QFrame,
                             QHBoxLayout, QToolButton)
from PyQt5.QtCore import Qt

# Configuration Constants
MEANALYZER_EXE = "meanalyzer.exe"
SETTINGS_FILE = "settings.ini"
FLASH_TOOL_BASE_DIR = "FlashTool"

# Base64 SVG Icons (Data URIs)
GITHUB_SVG = "data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiPz48IS0tIFVwbG9hZGVkIHRvOiBTVkcgUmVwbywgd3d3LnN2Z3JlcG8uY29tLCBHZW5lcmF0b3I6IFNWRyBSZXBvIE1peGVyIFRvb2xzIC0tPgo8c3ZnIGZpbGw9IiMwMDAwMDAiIHdpZHRoPSI4MDBweCIgaGVpZ2h0PSI4MDBweCIgdmlld0JveD0iMCAtMC41IDI1IDI1IiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxwYXRoIGQ9Im0xMi4zMDEgMGguMDkzYzIuMjQyIDAgNC4zNC42MTMgNi4xMzcgMS42OGwtLjA1NS0uMDMxYzEuODcxIDEuMDk0IDMuMzg2IDIuNjA5IDQuNDQ5IDQuNDIybC4wMzEuMDU4YzEuMDQgMS43NjkgMS42NTQgMy44OTYgMS42NTQgNi4xNjYgMCA1LjQwNi0zLjQ4MyAxMC04LjMyNyAxMS42NThsLS4wODcuMDI2Yy0uMDYzLjAyLS4xMzUuMDMxLS4yMDkuMDMxLS4xNjIgMC0uMzEyLS4wNTQtLjQzMy0uMTQ0bC4wMDIuMDAxYy0uMTI4LS4xMTUtLjIwOC0uMjgxLS4yMDgtLjQ2NiAwLS4wMDUgMC0uMDEgMC0uMDE0di4wMDFxMC0uMDQ4LjAwOC0xLjIyNnQuMDA4LTIuMTU0Yy4wMDctLjA3NS4wMTEtLjE2MS4wMTEtLjI0OSAwLS43OTItLjMyMy0xLjUwOC0uODQ0LTIuMDI1LjYxOC0uMDYxIDEuMTc2LS4xNjMgMS43MTgtLjMwNWwtLjA3Ni4wMTdjLjU3My0uMTYgMS4wNzMtLjM3MyAxLjUzNy0uNjQybC0uMDMxLjAxN2MuNTA4LS4yOC45MzgtLjYzNiAxLjI5Mi0xLjA1OGwuMDA2LS4wMDdjLjM3Mi0uNDc2LjY2My0xLjAzNi44NC0xLjY0NWwuMDA5LS4wMzVjLjIwOS0uNjgzLjMyOS0xLjQ2OC4zMjktMi4yODEgMC0uMDQ1IDAtLjA5MS0uMDAxLS4xMzZ2LjAwN2MwLS4wMjIuMDAxLS4wNDcuMDAxLS4wNzIgMC0xLjI0OC0uNDgyLTIuMzgzLTEuMjY5LTMuMjNsLjAwMy4wMDNjLjE2OC0uNDQuMjY1LS45NDguMjY1LTEuNDc5IDAtLjY0OS0uMTQ1LTEuMjYzLS40MDQtMS44MTRsLjAxMS4wMjZjLS4xMTUtLjAyMi0uMjQ2LS4wMzUtLjM4MS0uMDM1LS4zMzQgMC0uNjQ5LjA3OC0uOTI5LjIxNmwuMDEyLS4wMDVjLS41NjguMjEtMS4wNTQuNDQ4LTEuNTEyLjcyNmwuMDM4LS4wMjItLjYwOS4zODRjLS45MjItLjI2NC0xLjk4MS0uNDE2LTMuMDc1LS40MTZzLTIuMTUzLjE1Mi0zLjE1Ny40MzZsLjA4MS0uMDJxLS4yNTYtLjE3Ni0uNjgxLS40MzNjLS4zNzMtLjIxNC0uODE0LS40MjEtMS4yNzItLjU5NWwtLjA2Ni0uMDIyYy0uMjkzLS4xNTQtLjY0LS4yNDQtMS4wMDktLjI0NC0uMTI0IDAtLjI0Ni4wMS0uMzY0LjAzbC4wMTMtLjAwMmMtLjI0OC41MjQtLjM5MyAxLjEzOS0uMzkzIDEuNzg4IDAgLjUzMS4wOTcgMS4wNC4yNzUgMS41MDlsLS4wMS0uMDI5Yy0uNzg1Ljg0NC0xLjI2NiAxLjk3OS0xLjI2NiAzLjIyNyAwIC4wMjUgMCAuMDUxLjAwMS4wNzZ2LS4wMDRjLS4wMDEuMDM5LS4wMDEuMDg0LS4wMDEuMTMgMCAuODA5LjEyIDEuNTkxLjM0NCAyLjMyN2wtLjAxNS0uMDU3Yy4xODkuNjQzLjQ3NiAxLjIwMi44NSAxLjY5M2wtLjAwOS0uMDEzYy4zNTQuNDM1Ljc4Mi43OTMgMS4yNjcgMS4wNjJsLjAyMi4wMTFjLjQzMi4yNTIuOTMzLjQ2NSAxLjQ2LjYxNGwuMDQ2LjAxMWMuNDY2LjEyNSAxLjAyNC4yMjcgMS41OTUuMjg0bC4wNDYuMDA0Yy0uNDMxLjQyOC0uNzE4IDEtLjc4NCAxLjYzOGwtLjAwMS4wMTJjLS4yMDcuMTAxLS40NDguMTgzLS42OTkuMjM2bC0uMDIxLjAwNGMtLjI1Ni4wNTEtLjU0OS4wOC0uODUuMDgtLjAyMiAwLS4wNDQgMC0uMDY2IDBoLjAwMmMtLjM5NC0uMDA4LS43NTYtLjEzNi0xLjA1NS0uMzQ4bC4wMDYuMDA0Yy0uMzcxLS4yNTktLjY3MS0uNTk1LS44ODEtLjk4NmwtLjAwNy0uMDE1Yy0uMTk4LS4zMzYtLjQ1OS0uNjE0LS43NjgtLjgyN2wtLjAwOS0uMDA2Yy0uMjI1LS4xNjktLjQ5LS4zMDEtLjc3Ni0uMzhsLS4wMTYtLjAwNC0uMzItLjA0OGMtLjAyMy0uMDAyLS4wNS0uMDAzLS4wNzctLjAwMy0uMTQgMC0uMjczLjAyOC0uMzk0LjA3N2wuMDA3LS4wMDNxLS4xMjguMDcyLS4wOC4xODRjLjAzOS4wODYuMDg3LjE2LjE0NS4yMjVsLS4wMDEtLjAwMWMuMDYxLjA3Mi4xMy4xMzUuMjA1LjE5bC4wMDMuMDAyLjExMi4wOGMuMjgzLjE0OC41MTYuMzU0LjY5My42MDNsLjAwNC4wMDZjLjE5MS4yMzcuMzU5LjUwNS40OTQuNzkybC4wMS4wMjQuMTYuMzY4Yy4xMzUuNDAyLjM4LjczOC43Ljk4MWwuMDA1LjAwNGMuMy4yMzQuNjYyLjQwMiAxLjA1Ny40NzhsLjAxNi4wMDJjLjMzLjA2NC43MTQuMTA0IDEuMTA2LjExMmguMDA3Yy4wNDUuMDAyLjA5Ny4wMDIuMTUuMDAyLjI2MSAwIC41MTctLjAyMS43NjctLjA2MmwtLjAyNy4wMDQuMzY4LS4wNjRxMCAuNjA5LjAwOCAxLjQxOHQuMDA4Ljg3M3YuMDE0YzAgLjE4NS0uMDguMzUxLS4yMDguNDY2aC0uMDAxYy0uMTE5LjA4OS0uMjY4LjE0My0uNDMxLjE0My0uMDc1IDAtLjE0Ny0uMDExLS4yMTQtLjAzMmwuMDA1LjAwMWMtNC45MjktMS42ODktOC40MDktNi4yODMtOC40MDktMTEuNjkgMC0yLjI2OC42MTItNC4zOTMgMS42ODEtNi4yMTlsLS4wMzIuMDU4YzEuMDk0LTEuODcxIDIuNjA5LTMuMzg2IDQuNDIyLTQuNDQ5bC4wNTgtLjAzMWMxLjczOS0xLjAzNCAzLjgzNS0xLjY0NSA2LjA3My0xLjY0NWguMDk4LS4wMDV6bS03LjY0IDE3LjY2NnEuMDQ4LS4xMTItLjExMi0uMTkyLS4xNi0uMDQ4LS4yMDguMDMyLS4wNDguMTEyLjExMi4xOTIuMTQ0LjA5Ni4yMDgtLjAzMnptLjQ5Ny41NDVxLjExMi0uMDgtLjAzMi0uMjU2LS4xNi0uMTQ0LS4yNTYtLjA0OC0uMTEyLjA4LjAzMi4yNTYuMTU5LjE1Ny4yNTYuMDQ3em0uNDguNzJxLjE0NC0uMTEyIDAtLjMwNC0uMTI4LS4yMDgtLjI3Mi0uMDk2LS4xNDQuMDggMCAuMjg4dC4yNzIuMTEyem0uNjcyLjY3M3EuMTI4LS4xMjgtLjA2NC0uMzA0LS4xOTItLjE5Mi0uMzItLjA0OC0uMTQ0LjEyOC4wNjQuMzA0LjE5Mi4xOTIuMzIuMDQ0em0uOTEzLjRxLjA0OC0uMTc2LS4yMDgtLjI1Ni0uMjQtLjA2NC0uMzA0LjExMnQuMjA4LjI0cS4yNC4wOTcuMzA0LS4wOTZ6bTEuMDA5LjA4cTAtLjIwOC0uMjcyLS4xNzYtLjI1NiAwLS4yNTYuMTc2IDAgLjIwOC4yNzIuMTc2LjI1Ni4wMDEuMjU2LS4xNzV6bS45MjktLjE2cS0uMDMyLS4xNzYtLjI4OC0uMTQ0LS4yNTYuMDQ4LS4yMjQuMjR0LjI4OC4xMjguMjI1LS4yMjR6Ii8+PC9zdmc+"
YOUTUBE_SVG = "data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+DQo8IS0tIFVwbG9hZGVkIHRvOiBTVkcgUmVwbywgd3d3LnN2Z3JlcG8uY29tLCBHZW5lcmF0b3I6IFNWRyBSZXBvIE1peGVyIFRvb2xzIC0tPg0KPHN2ZyB3aWR0aD0iODAwcHgiIGhlaWdodD0iODAwcHgiIHZpZXdCb3g9IjAgLTcgNDggNDgiIHZlcnNpb249IjEuMSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4bWxuczp4bGluaz0iaHR0cDovL3d3dy53My5vcmcvMTk5OS94bGluayI+DQogICAgDQogICAgPHRpdGxlPllvdXR1YmUtY29sb3I8L3RpdGxlPg0KICAgIDxkZXNjPkNyZWF0ZWQgd2l0aCBTa2V0Y2guPC9kZXNjPg0KICAgIDxkZWZzPg0KDQo8L2RlZnM+DQogICAgPGcgaWQ9Ikljb25zIiBzdHJva2U9Im5vbmUiIHN0cm9rZS13aWR0aD0iMSIgZmlsbD0ibm9uZSIgZmlsbC1ydWxlPSJldmVub2RkIj4NCiAgICAgICAgPGcgaWQ9IkNvbG9yLSIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoLTIwMC4wMDAwMDAsIC0zNjguMDAwMDAwKSIgZmlsbD0iI0NFMTMxMiI+DQogICAgICAgICAgICA8cGF0aCBkPSJNMjE5LjA0NCwzOTEuMjY5OTE2IEwyMTkuMDQyNSwzNzcuNjg3NzQyIEwyMzIuMDExNSwzODQuNTAyMjQ0IEwyMTkuMDQ0LDM5MS4yNjk5MTYgWiBNMjQ3LjUyLDM3NS4zMzQxNjMgQzI0Ny41MiwzNzUuMzM0MTYzIDI0Ny4wNTA1LDM3Mi4wMDMxOTkgMjQ1LjYxMiwzNzAuNTM2MzY2IEMyNDMuNzg2NSwzNjguNjEwMjk5IDI0MS43NDA1LDM2OC42MDEyMzUgMjQwLjgwMywzNjguNDg5NDQ4IEMyMzQuMDg2LDM2OCAyMjQuMDEwNSwzNjggMjI0LjAxMDUsMzY4IEwyMjMuOTg5NSwzNjggQzIyMy45ODk1LDM2OCAyMTMuOTE0LDM2OCAyMDcuMTk3LDM2OC40ODk0NDggQzIwNi4yNTgsMzY4LjYwMTIzNSAyMDQuMjEzNSwzNjguNjEwMjk5IDIwMi4zODY1LDM3MC41MzYzNjYgQzIwMC45NDgsMzcyLjAwMzE5OSAyMDAuNDgsMzc1LjMzNDE2MyAyMDAuNDgsMzc1LjMzNDE2MyBDMjAwLjQ4LDM3NS4zMzQxNjMgMjAwLDM3OS4yNDY3MjMgMjAwLDM4My4xNTc3NzMgTDIwMCwzODYuODI1NjEgQzIwMCwzOTAuNzM4MTcgMjAwLjQ4LDM5NC42NDkyMiAyMDAuNDgsMzk0LjY0OTIyIEMyMDAuNDgsMzk0LjY0OTIyIDIwMC45NDgsMzk3Ljk4MDE4NCAyMDIuMzg2NSwzOTkuNDQ3MDE2IEMyMDQuMjEzNSw0MDEuMzczMDg0IDIwNi42MTIsNDAxLjMxMjY1OCAyMDcuNjgsNDAxLjUxMzU3NCBDMjExLjUyLDQwMS44ODUxOTEgMjI0LDQwMiAyMjQsNDAyIEMyMjQsNDAyIDIzNC4wODYsNDAxLjk4NDg5NCAyNDAuODAzLDQwMS40OTU0NDYgQzI0MS43NDA1LDQwMS4zODIxNDggMjQzLjc4NjUsNDAxLjM3MzA4NCAyNDUuNjEyLDM5OS40NDcwMTYgQzI0Ny4wNTA1LDM5Ny45ODAxODQgMjQ3LjUyLDM5NC42NDkyMiAyNDcuNTIsMzk0LjY0OTIyIEMyNDcuNTIsMzk0LjY0OTIyIDI0OCwzOTAuNzM4MTcgMjQ4LDM4Ni44MjU2MSBMMjQ4LDM4My4xNTc3NzMgQzI0OCwzNzkuMjQ2NzIzIDI0Ny41MiwzNzUuMzM0MTYzIDI0Ny41MiwzNzUuMzM0MTYzIEwyNDcuNTIsMzc1LjMzNDE2MyBaIiBpZD0iWW91dHViZSI+DQoNCjwvcGF0aD4NCiAgICAgICAgPC9nPg0KICAgIDwvZz4NCjwvc3ZnPg=="

# Documentation Content
CLEAN_ME_INSTRUCTIONS = """HOW TO CLEAN THE INTEL MANAGEMENT ENGINE

1. Drop your intel bios image into the program (loading a BIOS will delete everything in \\TEMP)

2. Find the matching ME firmware (magnifying glass button), copy it to the \\TEMP Folder and rename to "ME Region.bin". Making Sure the SKU Matches (Consumer or Corporate & Chipset)

3. Start Flash Image Tool (FIT, Lightningbolt button) and open the bios file in \\TEMP (this will decompile the file to \\BIOSNAME\\decomp)

4. Change "Generate Intermediate Files" (usually under Build>Build Settings) to no and save as untitled.xml. Close FIT

5. Copy or move the ME Region.bin to the newly created decomp folder, overwriting the original

6. Start FIT again, open the untitled.xml file, click on Build>Build Image.

7. outimage.bin is the bios with clean ME firmware, rename it if you want and make sure you move it out of the \\TEMP folder.

8. Open the bios with MEAnalyzer, it should say Configured (only ME FW 11 and above will say configured)"""

DEFAULT_INI_CONTENT = """[Settings]
TempPath: Temp

[CLI_Arguments]
# MEAnalyzer.exe CLI arguments:
# These Arguments are correct as of MEA v1.311.0 r377
# Adjust accordingly for future releases

Skip welcome screen: -skip
Skip exit prompt: -exit
Use json output: -json
Use above temp path: -out
"""

class TextViewerDialog(QDialog):
    """Generic dialog to display text or JSON information."""
    def __init__(self, title, content, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(550, 650)
        layout = QVBoxLayout(self)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setText(content)
        self.text_edit.setStyleSheet("font-family: 'Consolas', 'Courier New', monospace; font-size: 10pt;")
        layout.addWidget(self.text_edit)

class MEAnalyzerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.raw_json_data = {}
        
        # Load Settings & Setup Directories
        self.temp_dir, self.cli_args = self.load_settings()
        self.init_ui()
        self.ensure_temp_dir()

    def load_settings(self):
        """Initializes settings from INI or generates default."""
        # Using a custom configparser to allow ':' as a delimiter for natural looking lines
        config = configparser.ConfigParser(delimiters=('=', ':'))
        config.optionxform = str # Preserve key capitalization
        
        default_temp = "Temp"
        
        # Generate the file with descriptive comments if it doesn't exist
        if not os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                f.write(DEFAULT_INI_CONTENT)
                
        config.read(SETTINGS_FILE, encoding='utf-8')
        
        # Safely pull values
        temp_path = config.get('Settings', 'TempPath', fallback=default_temp)
        
        # Read the multiline CLI_Arguments section
        cli_args_list = []
        if config.has_section('CLI_Arguments'):
            for key in config.options('CLI_Arguments'):
                val = config.get('CLI_Arguments', key)
                if val:
                    cli_args_list.append(val)
        else:
            # Fallback if an older version of the ini exists without the block
            with open(SETTINGS_FILE, 'a', encoding='utf-8') as f:
                f.write("\n" + "\n".join(DEFAULT_INI_CONTENT.split("\n")[3:]))
            config.read(SETTINGS_FILE, encoding='utf-8')
            for key in config.options('CLI_Arguments'):
                val = config.get('CLI_Arguments', key)
                if val:
                    cli_args_list.append(val)

        return temp_path, " ".join(cli_args_list)

    def init_ui(self):
        self.setWindowTitle("MEAnalyzer GUI Frontend")
        self.resize(550, 420)
        self.setAcceptDrops(True)

        main_layout = QVBoxLayout(self)

        # Drop Zone & File Selection
        self.drop_label = QLabel("Drag & Drop .bin or .rom file here")
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #666; 
                border-radius: 5px; 
                padding: 30px; 
                font-size: 15px; 
                background-color: #f9f9f9;
            }
        """)
        main_layout.addWidget(self.drop_label)

        self.browse_btn = QPushButton("Browse for File")
        self.browse_btn.setFixedHeight(35)
        self.browse_btn.clicked.connect(self.browse_file)
        main_layout.addWidget(self.browse_btn)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        # Data Display Fields
        self.form_layout = QFormLayout()
        self.fields = {
            "Date": QLineEdit(),
            "Family": QLineEdit(),
            "Version": QLineEdit(),
            "Release": QLineEdit(),
            "Type": QLineEdit(),
            "SKU": QLineEdit(),
            "Chipset": QLineEdit(),
            "File System State": QLineEdit(),
            "Flash Image Tool": QLineEdit()
        }

        for label_text, line_edit in self.fields.items():
            line_edit.setReadOnly(True)
            
            if label_text == "Version":
                container = QHBoxLayout()
                container.addWidget(line_edit)
                self.version_search_btn = QToolButton()
                self.version_search_btn.setText("🔍")
                self.version_search_btn.setToolTip("Search Station-Drivers for matching firmware")
                self.version_search_btn.setEnabled(False)
                self.version_search_btn.clicked.connect(self.open_version_search)
                container.addWidget(self.version_search_btn)
                self.form_layout.addRow(label_text + ":", container)
            
            elif label_text == "Flash Image Tool":
                container = QHBoxLayout()
                container.addWidget(line_edit)
                self.fit_launch_btn = QToolButton()
                self.fit_launch_btn.setText("⚡")
                self.fit_launch_btn.setToolTip("Find and Copy Flash Image Tool to \\Temp")
                self.fit_launch_btn.setEnabled(False)
                self.fit_launch_btn.clicked.connect(self.handle_flash_tool_logic)
                container.addWidget(self.fit_launch_btn)
                self.form_layout.addRow(label_text + ":", container)
            
            else:
                self.form_layout.addRow(label_text + ":", line_edit)

        main_layout.addLayout(self.form_layout)

        # Global Action Buttons
        bottom_buttons_layout = QHBoxLayout()
        
        self.view_json_btn = QPushButton("View Full JSON")
        self.view_json_btn.setFixedHeight(40)
        self.view_json_btn.clicked.connect(self.show_full_json)
        self.view_json_btn.setEnabled(False)
        
        self.how_to_clean_btn = QPushButton("How to clean IME")
        self.how_to_clean_btn.setFixedHeight(40)
        self.how_to_clean_btn.clicked.connect(self.show_clean_me_instructions)
        
        bottom_buttons_layout.addWidget(self.view_json_btn)
        bottom_buttons_layout.addWidget(self.how_to_clean_btn)
        
        main_layout.addLayout(bottom_buttons_layout)

        # --- Footer Area (Social Icons and Credit) ---
        footer_layout = QHBoxLayout()
        # Changed margins from (0, 10, 0, 0) to (0, 5, 0, 0) to tighten it up
        footer_layout.setContentsMargins(0, 0, 0, 0) 
        
        # YouTube Link
        self.yt_link = QLabel()
        self.yt_link.setText(f'<a href="https://www.youtube.com/@Slot1Gamer/videos"><img src="{YOUTUBE_SVG}" height="25" width="25"></a>')
        self.yt_link.setOpenExternalLinks(True)
        self.yt_link.setToolTip("Slot1Gamer YouTube")
        
        # GitHub Link
        self.gh_link = QLabel()
        self.gh_link.setText(f'<a href="https://github.com/Liams-Electronics-Lab"><img src="{GITHUB_SVG}" height="25" width="25"></a>')
        self.gh_link.setOpenExternalLinks(True)
        self.gh_link.setToolTip("GitHub Profile")
        
        # Credit Label
        self.credit_label = QLabel("made by Liam's Electronics Lab")
        self.credit_label.setStyleSheet("color: #777; font-size: 15px;")
        self.credit_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Add items to footer
        footer_layout.addWidget(self.yt_link)
        footer_layout.addWidget(self.gh_link)
        footer_layout.addStretch() # Pushes the credit label to the far right side
        footer_layout.addWidget(self.credit_label)
        
        main_layout.addLayout(footer_layout)

    def ensure_temp_dir(self):
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

    def empty_temp_dir(self):
        if not os.path.exists(self.temp_dir): return
        for filename in os.listdir(self.temp_dir):
            file_path = os.path.join(self.temp_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Cleanup failed for {file_path}: {e}")

    # --- Interaction Events ---
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select BIOS File", "", "BIOS Files (*.bin *.rom)")
        if file_path: self.process_file(file_path)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls(): event.accept()
        else: event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files and files[0].lower().endswith(('.bin', '.rom')):
            self.process_file(files[0])

    # --- Core Processing ---
    def process_file(self, source_path):
        self.empty_temp_dir()
        self.clear_ui_fields()

        ext = os.path.splitext(source_path)[1]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        new_filename = f"bios{timestamp}{ext}"
        dest_path = os.path.abspath(os.path.join(self.temp_dir, new_filename))

        try:
            shutil.copy2(source_path, dest_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not copy file to Temp folder:\n{e}")
            return

        if not os.path.exists(MEANALYZER_EXE):
            QMessageBox.critical(self, "Error", f"{MEANALYZER_EXE} missing from application directory.")
            return

        self.drop_label.setText("Analyzing Firmware...")
        QApplication.processEvents()

        # Construct the command using parsed CLI args from settings
        cmd = [MEANALYZER_EXE]
        if self.cli_args:
            cmd.extend(shlex.split(self.cli_args))
        cmd.extend([self.temp_dir, dest_path])
        
        try:
            flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            subprocess.run(cmd, check=True, creationflags=flags)
        except Exception as e:
            QMessageBox.critical(self, "CLI Error", f"MEAnalyzer execution failed: {e}")
            self.reset_drop_label()
            return

        json_file_path = dest_path + ".json"
        if os.path.exists(json_file_path):
            self.parse_and_display_json(json_file_path)
        
        self.reset_drop_label()

    def parse_and_display_json(self, json_file_path):
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                self.raw_json_data = json.load(f)
            
            root_key = list(self.raw_json_data.keys())[0]
            me_data = self.raw_json_data[root_key].get("Management Engine", [{}])[0]

            for key, line_edit in self.fields.items():
                val = me_data.get(key, "N/A")
                line_edit.setText(str(val))

            if self.fields["Version"].text() != "N/A": self.version_search_btn.setEnabled(True)
            if self.fields["Flash Image Tool"].text() != "N/A": self.fit_launch_btn.setEnabled(True)
            self.view_json_btn.setEnabled(True)
        except:
            QMessageBox.critical(self, "JSON Error", "Could not parse MEAnalyzer output.")

    # --- Tool Buttons Logic ---
    def open_version_search(self):
        v = self.fields["Version"].text().strip()
        url = f"https://www.station-drivers.com/index.php/en/component/remository/search/lang,en-gb/?submit_search=submit&option=com_remository&func=search&search_text={v}&search_filetitle=1&search_filedesc=1&catsearch%5B5%5D=1&catsearch%5B155%5D=1"
        webbrowser.open(url)

    def handle_flash_tool_logic(self):
        fit_version = self.fields["Flash Image Tool"].text().strip()
        if fit_version == "N/A" or not fit_version: return

        found_folder = None
        if os.path.exists(FLASH_TOOL_BASE_DIR):
            for folder_name in os.listdir(FLASH_TOOL_BASE_DIR):
                full_path = os.path.join(FLASH_TOOL_BASE_DIR, folder_name)
                if os.path.isdir(full_path) and fit_version in folder_name:
                    found_folder = full_path
                    break

        if found_folder:
            try:
                for item in os.listdir(found_folder):
                    s = os.path.join(found_folder, item)
                    d = os.path.join(self.temp_dir, item)
                    if os.path.isdir(s): shutil.copytree(s, d, dirs_exist_ok=True)
                    else: shutil.copy2(s, d)
                
                exes = [e for e in glob.glob(os.path.join(self.temp_dir, "*.exe")) if "meanalyzer.exe" not in e.lower()]

                if len(exes) == 1:
                    target_exe = os.path.abspath(exes[0])
                    target_cwd = os.path.abspath(self.temp_dir)
                    subprocess.Popen([target_exe], cwd=target_cwd, shell=True)
                else:
                    os.startfile(os.path.abspath(self.temp_dir))
            except Exception as e:
                QMessageBox.warning(self, "Tool Error", f"Failed to prepare Flash Tool folder:\n{e}")
        else:
            self.show_missing_tool_dialog(fit_version)

    def show_missing_tool_dialog(self, version):
        msg = QMessageBox(self)
        msg.setWindowTitle("Flash Tool Not Found")
        msg.setText(f"Couldn't find matching Flash Image Tool folder for: {version}")
        msg.setInformativeText("Would you like to search online or check the local folder?")
        
        btn_online = msg.addButton("Search Online", QMessageBox.ActionRole)
        btn_folder = msg.addButton("Open FlashTool Folder", QMessageBox.ActionRole)
        msg.addButton(QMessageBox.Cancel)
        msg.exec_()

        if msg.clickedButton() == btn_online:
            webbrowser.open(f"https://www.google.com/search?q=Flash+Image+Tool+{version}")
        elif msg.clickedButton() == btn_folder:
            if not os.path.exists(FLASH_TOOL_BASE_DIR): os.makedirs(FLASH_TOOL_BASE_DIR)
            os.startfile(os.path.abspath(FLASH_TOOL_BASE_DIR))

    # --- UI Helpers ---
    def clear_ui_fields(self):
        for line_edit in self.fields.values(): line_edit.clear()
        self.view_json_btn.setEnabled(False)
        self.version_search_btn.setEnabled(False)
        self.fit_launch_btn.setEnabled(False)

    def reset_drop_label(self):
        self.drop_label.setText("Drag & Drop .bin or .rom file here")

    def show_full_json(self):
        if self.raw_json_data:
            content = json.dumps(self.raw_json_data, indent=4)
            TextViewerDialog("Raw JSON Data", content, self).exec_()

    def show_clean_me_instructions(self):
        TextViewerDialog("How to clean ME Region", CLEAN_ME_INSTRUCTIONS, self).exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MEAnalyzerGUI()
    window.show()
    sys.exit(app.exec_())