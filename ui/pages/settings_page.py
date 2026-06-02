import sys
import json
import os
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QComboBox, QPushButton, QLineEdit, QSpinBox, QCheckBox, 
    QFrame, QScrollArea, QMessageBox
)
from PySide6.QtCore import Qt


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(16)

        # =====================================================================
        # HEADER PANEL
        # =====================================================================
        header_frame = QFrame()
        header_frame.setObjectName("HeaderFrame")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(16, 12, 16, 12)

        title_section = QVBoxLayout()
        title = QLabel("Global System Preferences")
        title.setStyleSheet("color: #0f172a; font-size: 20px; font-weight: 700;")
        sub = QLabel("Configure pipeline optimization controls, connection endpoints, and visual interfaces.")
        sub.setStyleSheet("color: #64748b; font-size: 12px;")
        title_section.addWidget(title)
        title_section.addWidget(sub)
        header_layout.addLayout(title_section)
        header_layout.addStretch()

        main_layout.addWidget(header_frame)

        # =====================================================================
        # MAIN CENTRAL CONFIGURATION FORM SCROLL AREA
        # =====================================================================
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        scroll_content = QWidget()
        form_layout = QVBoxLayout(scroll_content)
        form_layout.setContentsMargins(4, 4, 4, 4)
        form_layout.setSpacing(16)

        # SECTION 1: DATABASE CORE ENDPOINTS
        db_group = QFrame()
        db_group.setObjectName("SettingGroup")
        db_layout = QFormLayout(db_group)
        db_layout.setContentsMargins(14, 14, 14, 14)
        
        db_title = QLabel("Database Connection & Network Core Endpoints")
        db_title.setStyleSheet("color: #2563eb; font-size: 13px; font-weight: 700; text-transform: uppercase; margin-bottom: 6px;")
        db_layout.addRow(db_title)
        
        self.db_host = QLineEdit("localhost:5432")
        self.db_name = QLineEdit("cmi_production_vault")
        self.db_timeout = QSpinBox()
        self.db_timeout.setRange(5, 120)
        self.db_timeout.setValue(30)
        self.db_timeout.setSuffix(" seconds")
        
        db_layout.addRow("Data Server Host Endpoint Address:", self.db_host)
        db_layout.addRow("Active Target Cluster Database Name:", self.db_name)
        db_layout.addRow("Network Query Connection Timeout:", self.db_timeout)
        form_layout.addWidget(db_group)

        # SECTION 2: PIPELINE OPTIMIZATION & WORKERS
        pipe_group = QFrame()
        pipe_group.setObjectName("SettingGroup")
        pipe_layout = QFormLayout(pipe_group)
        pipe_layout.setContentsMargins(14, 14, 14, 14)
        
        pipe_title = QLabel("Pipeline Optimization & Concurrency Limits")
        pipe_title.setStyleSheet("color: #2563eb; font-size: 13px; font-weight: 700; text-transform: uppercase; margin-bottom: 6px;")
        pipe_layout.addRow(pipe_title)
        
        self.max_threads = QSpinBox()
        self.max_threads.setRange(1, 32)
        self.max_threads.setValue(4)
        self.max_threads.setSuffix(" concurrent threads")
        
        self.ram_cache = QSpinBox()
        self.ram_cache.setRange(256, 16384)
        self.ram_cache.setValue(2048)
        self.ram_cache.setSuffix(" MB")
        
        pipe_layout.addRow("Allocated CPU Processing Background Threads:", self.max_threads)
        pipe_layout.addRow("Maximum Volumetric In-Memory Buffer RAM Cache:", self.ram_cache)
        form_layout.addWidget(pipe_group)

        # SECTION 3: FILE SYSTEM POLICIES
        fs_group = QFrame()
        fs_group.setObjectName("SettingGroup")
        fs_layout = QFormLayout(fs_group)
        fs_layout.setContentsMargins(14, 14, 14, 14)
        
        fs_title = QLabel("Automated Filesystem Retention Policies")
        fs_title.setStyleSheet("color: #2563eb; font-size: 13px; font-weight: 700; text-transform: uppercase; margin-bottom: 6px;")
        fs_layout.addRow(fs_title)
        
        self.auto_purge = QCheckBox("Automatically purge processing logs history files")
        self.auto_purge.setChecked(True)
        self.purge_days = QSpinBox()
        self.purge_days.setRange(1, 365)
        self.purge_days.setValue(30)
        self.purge_days.setSuffix(" days")
        
        self.zip_output = QCheckBox("Compress output generation directory bundles natively (.zip)")
        self.zip_output.setChecked(False)
        
        fs_layout.addRow(self.auto_purge)
        fs_layout.addRow("Retention Execution Lifecycle Window Threshold:", self.purge_days)
        fs_layout.addRow(self.zip_output)
        form_layout.addWidget(fs_group)

        # SECTION 4: DISPLAY ENVIRONMENT PREFERENCES
        ui_group = QFrame()
        ui_group.setObjectName("SettingGroup")
        ui_layout = QFormLayout(ui_group)
        ui_layout.setContentsMargins(14, 14, 14, 14)
        
        ui_title = QLabel("Display Environment & Canvas Skins Preferences")
        ui_title.setStyleSheet("color: #2563eb; font-size: 13px; font-weight: 700; text-transform: uppercase; margin-bottom: 6px;")
        ui_layout.addRow(ui_title)
        
        self.theme_selector = QComboBox()
        self.theme_selector.addItems(["Enterprise Slate Light Mode", "Obsidian Dark Mode Minimalist", "System Default Contrast Matcher"])
        
        ui_layout.addRow("Active Workspace Interface Theme:", self.theme_selector)
        form_layout.addWidget(ui_group)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll, stretch=1)

        # =====================================================================
        # LOWER COMMIT ACTION CONTROLS FOOTER
        # =====================================================================
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(4, 0, 4, 4)
        
        btn_reset = QPushButton("Reset Defaults")
        btn_reset.clicked.connect(self.restore_factory_defaults)
        btn_reset.setStyleSheet("""
            QPushButton { background-color: #e2e8f0; color: #475569; padding: 8px 16px; font-weight: bold; border-radius: 6px; font-size: 13px; }
            QPushButton:hover { background-color: #cbd5e1; color: #0f172a; }
        """)
        
        btn_save = QPushButton("💾 Save Parameter Configuration")
        btn_save.clicked.connect(self.commit_settings_to_disk)
        btn_save.setStyleSheet("""
            QPushButton { background-color: #2563eb; color: white; padding: 8px 20px; font-weight: bold; border-radius: 6px; font-size: 13px; }
            QPushButton:hover { background-color: #1d4ed8; }
        """)

        footer_layout.addWidget(btn_reset)
        footer_layout.addStretch()
        footer_layout.addWidget(btn_save)
        main_layout.addLayout(footer_layout)

        # Styled Frame Engine sheets mappings
        self.setStyleSheet("""
            QFrame#HeaderFrame {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
            }
            QFrame#SettingGroup {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
            }
            QLineEdit, QComboBox, QSpinBox {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 6px;
                min-width: 250px;
                color: #1e293b;
            }
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
                border: 1px solid #2563eb;
                background-color: #f8fafc;
            }
            QCheckBox {
                font-weight: 600;
                color: #334155;
            }
            QLabel {
                font-size: 12px;
                color: #334155;
                font-weight: 500;
            }
        """)

    def commit_settings_to_disk(self):
        """Assembles variables into a localized runtime JSON dictionary payload."""
        payload = {
            "database_host": self.db_host.text(),
            "database_name": self.db_name.text(),
            "query_timeout_sec": self.db_timeout.value(),
            "concurrency_threads": self.max_threads.value(),
            "ram_cache_limit_mb": self.ram_cache.value(),
            "auto_purge_logs": self.auto_purge.isChecked(),
            "purge_threshold_days": self.purge_days.value(),
            "compress_output_zip": self.zip_output.isChecked(),
            "selected_theme_skin": self.theme_selector.currentText()
        }
        
        try:
            with open("app_config_registry.json", "w") as target_file:
                json.dump(payload, target_file, indent=4)
            QMessageBox.information(self, "Commit Confirmed", "Platform configuration profiles synced to disk workspace storage registers.")
        except Exception as e:
            QMessageBox.critical(self, "Registry Error", f"Failed to persist platform metadata adjustments: {str(e)}")

    def restore_factory_defaults(self):
        """Reverts entry states back to standard baseline initialization indexes."""
        self.db_host.setText("localhost:5432")
        self.db_name.setText("cmi_production_vault")
        self.db_timeout.setValue(30)
        self.max_threads.setValue(4)
        self.ram_cache.setValue(2048)
        self.auto_purge.setChecked(True)
        self.purge_days.setValue(30)
        self.zip_output.setChecked(False)
        self.theme_selector.setCurrentIndex(0)