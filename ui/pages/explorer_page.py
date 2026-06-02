import os
import pandas as pd
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QPushButton, QFileDialog, QLineEdit, QListWidget, QTableWidget, 
    QTableWidgetItem, QHeaderView, QSplitter
)
from PySide6.QtCore import Qt, QThread, Signal


class ExcelPreviewWorker(QThread):
    """Asynchronously reads the first few rows of an Excel file to keep the UI buttery smooth."""
    preview_ready = Signal(list, list)  # Carries (columns, row_data)
    error_occurred = Signal(str)

    def __init__(self, file_path, num_rows=15):
        super().__init__()
        self.file_path = file_path
        self.num_rows = num_rows

    def run(self):
        try:
            # Read only the header and top rows to optimize speed and memory footprint
            df = pd.read_excel(self.file_path, nrows=self.num_rows)
            
            # Clean up NaN values for clean visual display presentation
            df = df.fillna("")
            
            columns = [str(col) for col in df.columns]
            row_data = df.values.tolist()
            
            self.preview_ready.emit(columns, row_data)
        except Exception as e:
            self.error_occurred.emit(str(e))


class ExplorerPage(QWidget):
    workspace_directory_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.current_dir = ""
        self.preview_worker = None
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(16)

        # =====================================================================
        # HEADER HEADER SECTION
        # =====================================================================
        title = QLabel("Project Workspace Configuration")
        title.setStyleSheet("color: #0f172a; font-size: 22px; font-weight: 700;")
        desc = QLabel("Set up your primary system directory workspace path to track contents and preview raw data files instantly.")
        desc.setStyleSheet("color: #64748b; font-size: 13px; margin-bottom: 4px;")
        
        main_layout.addWidget(title)
        main_layout.addWidget(desc)

        # Directory Selector Subgroup Form
        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 10)
        
        self.path_display = QLineEdit()
        self.path_display.setPlaceholderText("Select your project file root directory...")
        self.path_display.setReadOnly(True)
        self.path_display.setStyleSheet("padding: 8px; font-size: 13px; background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 6px;")

        btn_browse = QPushButton("📁 Browse Workspace")
        btn_browse.clicked.connect(self.browse_folder)
        btn_browse.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; color: white; padding: 8px 16px; 
                font-weight: bold; border-radius: 6px; font-size: 13px;
            }
            QPushButton:hover { background-color: #1d4ed8; }
        """)

        form.addRow("Active Workspace Directory:", self.path_display)
        form.addRow("", btn_browse)
        main_layout.addLayout(form)

        # =====================================================================
        # CONTENT SPLITTER: LEFT (FILES LIST) vs RIGHT (DATA PREVIEW)
        # =====================================================================
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background-color: #e2e8f0; width: 2px; }")

        # Left Container: File Browser List
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 10, 0)
        
        file_list_label = QLabel("Available Workspace Sheets:")
        file_list_label.setStyleSheet("color: #1e293b; font-size: 13px; font-weight: 700; text-transform: uppercase;")
        
        self.file_list = QListWidget()
        self.file_list.itemSelectionChanged.connect(self.handle_file_selection)
        self.file_list.setStyleSheet("""
            QListWidget {
                background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 4px;
            }
            QListWidget::item {
                padding: 10px; border-radius: 6px; color: #334155; font-weight: 500; margin-bottom: 2px;
            }
            QListWidget::item:hover { background-color: #f1f5f9; color: #0f172a; }
            QListWidget::item:selected { background-color: #eff6ff; color: #2563eb; font-weight: 600; }
        """)
        
        left_layout.addWidget(file_list_label)
        left_layout.addWidget(self.file_list)

        # Right Container: Data Spreadsheet Table Preview Canvas
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 0, 0, 0)
        
        preview_label = QLabel("Live Spreadsheet Inspection Row Preview:")
        preview_label.setStyleSheet("color: #1e293b; font-size: 13px; font-weight: 700; text-transform: uppercase;")
        
        self.status_hint = QLabel("Select an asset sheet item from the left file tracker pane to run an instant preview.")
        self.status_hint.setAlignment(Qt.AlignCenter)
        self.status_hint.setStyleSheet("color: #94a3b8; font-size: 13px; font-style: italic; background-color: #ffffff; border: 1px dashed #cbd5e1; border-radius: 8px;")
        
        self.preview_table = QTableWidget()
        self.preview_table.setShowGrid(True)
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.preview_table.setVisible(False)  # Hidden initially until loaded
        self.preview_table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; gridline-color: #f1f5f9;
            }
            QHeaderView::section {
                background-color: #f8fafc; color: #475569; font-weight: 700;
                border: none; border-bottom: 2px solid #e2e8f0; padding: 8px; font-size: 12px;
            }
        """)
        
        right_layout.addWidget(preview_label)
        right_layout.addWidget(self.status_hint)
        right_layout.addWidget(self.preview_table)

        # Assemble layout via adaptive sizing splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([350, 750])  # Proportional width splitting allocation
        
        main_layout.addWidget(splitter, stretch=1)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Identify Active Core Working Folder")
        if folder:
            self.path_display.setText(folder)
            self.current_dir = folder
            self.refresh_file_list()
            self.workspace_directory_changed.emit(folder)

    def refresh_file_list(self):
        self.file_list.clear()
        self.clear_preview("Select an asset sheet item from the left file tracker pane to run an instant preview.")
        
        if not self.current_dir or not os.path.exists(self.current_dir):
            return

        try:
            files = [f for f in os.listdir(self.current_dir) if f.lower().endswith(('.xlsx', '.xls', '.csv'))]
            if files:
                for filename in files:
                    icon = "📊" if "xls" in filename.lower() else "📄"
                    self.file_list.addItem(f"{icon}  {filename}")
            else:
                self.file_list.addItem("⚠ No compatible dataset sheets found (.xlsx, .csv)")
        except Exception as e:
            self.file_list.addItem(f"Reading Exception Error: {str(e)}")

    def handle_file_selection(self):
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return

        filename_raw = selected_items[0].text()
        # Filter item string out away from design leading emoji tags
        filename = filename_raw[3:].strip() if filename_raw.startswith(("📊", "📄", "⚠")) else filename_raw
        
        if "No compatible dataset sheets found" in filename or "Reading Exception" in filename:
            self.clear_preview("No active file layout targeted.")
            return

        file_path = os.path.join(self.current_dir, filename)
        
        # UI Feedback during parsing
        self.preview_table.setVisible(False)
        self.status_hint.setVisible(True)
        self.status_hint.setText(f"⏳ Reading row matrix schemas from {filename}...")

        # Fire off background worker thread to parse the data safely
        self.preview_worker = ExcelPreviewWorker(file_path)
        self.preview_worker.preview_ready.connect(self.populate_preview_table)
        self.preview_worker.error_occurred.connect(lambda err: self.clear_preview(f"❌ Failed to parse data: {err}"))
        self.preview_worker.start()

    def populate_preview_table(self, columns, row_data):
        self.status_hint.setVisible(False)
        self.preview_table.setVisible(True)
        
        self.preview_table.clear()
        self.preview_table.setColumnCount(len(columns))
        self.preview_table.setRowCount(len(row_data))
        self.preview_table.setHorizontalHeaderLabels(columns)

        # Adjust tracking columns elegantly 
        header = self.preview_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setDefaultSectionSize(140)

        for row_idx, row_values in enumerate(row_data):
            for col_idx, value in enumerate(row_values):
                item = QTableWidgetItem(str(value))
                self.preview_table.setItem(row_idx, col_idx, item)

    def clear_preview(self, text_message):
        self.preview_table.setVisible(False)
        self.status_hint.setVisible(True)
        self.status_hint.setText(text_message)