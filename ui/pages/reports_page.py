import sys
import os
import subprocess
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout,
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QSplitter, QFrame, QListWidget, QDateEdit
)
from PySide6.QtCore import Qt, QThread, Signal, QDate


class ReportCompilationWorker(QThread):
    """
    Background compilation worker to assemble databases, inject templates,
    and render flat PDF or spreadsheet files without freezing the UI.
    """
    compilation_complete = Signal(str)  # Sends back generated file path

    def __init__(self, template_type, export_format):
        super().__init__()
        self.template_type = template_type
        self.export_format = export_format

    def run(self):
        # Simulate data querying, structural compilation, and filesystem writing
        import time
        time.sleep(1.5)
        
        # Returns a mock file path target destination configuration
        mock_filename = f"CMI_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{self.export_format.lower()}"
        self.compilation_complete.emit(mock_filename)


class ReportsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(16)

        # =====================================================================
        # HEADER CONTROL BAR
        # =====================================================================
        header_frame = QFrame()
        header_frame.setObjectName("HeaderFrame")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(16, 12, 16, 12)

        title_section = QVBoxLayout()
        title = QLabel("Reports & Documentation Workspace")
        title.setStyleSheet("color: #0f172a; font-size: 20px; font-weight: 700;")
        sub = QLabel("Generate compliance documentation, export pipeline summaries, and review historical assets.")
        sub.setStyleSheet("color: #64748b; font-size: 12px;")
        title_section.addWidget(title)
        title_section.addWidget(sub)
        header_layout.addLayout(title_section)
        header_layout.addStretch()

        # Quick Generation Action Triggers
        action_layout = QHBoxLayout()
        action_layout.setSpacing(8)

        self.format_selector = QComboBox()
        self.format_selector.addItems(["PDF Document (.pdf)", "Excel Spreadsheet (.xlsx)", "Comma Separated (.csv)"])
        self.format_selector.setStyleSheet("padding: 6px 12px; font-size: 13px;")

        btn_generate = QPushButton("✨ Generate Report")
        btn_generate.clicked.connect(self.trigger_report_generation)
        btn_generate.setStyleSheet("""
            QPushButton { background-color: #10b981; color: white; padding: 7px 16px; font-weight: bold; border-radius: 6px; font-size: 13px; }
            QPushButton:hover { background-color: #059669; }
        """)

        action_layout.addWidget(self.format_selector)
        action_layout.addWidget(btn_generate)
        header_layout.addLayout(action_layout)

        main_layout.addWidget(header_frame)

        # =====================================================================
        # WORKSPACE SPLITTER (TEMPLATES vs RECENT GENERATIONS)
        # =====================================================================
        workspace_splitter = QSplitter(Qt.Horizontal)
        workspace_splitter.setStyleSheet("QSplitter::handle { background-color: #e2e8f0; width: 2px; }")

        # Left Column Panel: Report Templates Configuration
        left_panel = QWidget()
        left_panel_layout = QVBoxLayout(left_panel)
        left_panel_layout.setContentsMargins(0, 0, 8, 0)
        left_panel_layout.setSpacing(10)

        template_lbl = QLabel("Report Design Blueprints")
        template_lbl.setStyleSheet("color: #1e293b; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;")
        
        self.template_list = QListWidget()
        self.template_list.addItems([
            "📋 Daily Site Production Summary",
            "🛡 Equipment Validation Audit Log",
            "📊 Volumetric Payload Ingestion Profile",
            "📉 Operational Pipeline Anomaly Sweep",
            "⏱ Fleet Workspace Velocity Analytics"
        ])
        self.template_list.setCurrentRow(0)
        self.template_list.setStyleSheet("""
            QListWidget { background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 6px; }
            QListWidget::item { padding: 12px 10px; border-radius: 6px; color: #334155; font-weight: 500; margin-bottom: 2px; }
            QListWidget::item:hover { background-color: #f8fafc; color: #0f172a; }
            QListWidget::item:selected { background-color: #eff6ff; color: #2563eb; font-weight: 600; }
        """)

        # Calendar Constraint Controls inside Left Stack
        date_frame = QFrame()
        date_frame.setStyleSheet("background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px;")
        date_layout = QGridLayout(date_frame)
        date_layout.setSpacing(8)
        
        date_layout.addWidget(QLabel("<b>Target Start Scope:</b>"), 0, 0)
        self.start_date = QDateEdit(QDate.currentDate().addDays(-7))
        self.start_date.setCalendarPopup(True)
        date_layout.addWidget(self.start_date, 0, 1)

        date_layout.addWidget(QLabel("<b>Target End Scope:</b>"), 1, 0)
        self.end_date = QDateEdit(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        date_layout.addWidget(self.end_date, 1, 1)

        left_panel_layout.addWidget(template_lbl)
        left_panel_layout.addWidget(self.template_list, stretch=2)
        left_panel_layout.addWidget(QLabel("Date Scope Aggregation Matrix Constraints:"), stretch=0)
        left_panel_layout.addWidget(date_frame, stretch=0)

        # Right Column Panel: Generated Documents File Archival Grid
        right_panel = QWidget()
        right_panel_layout = QVBoxLayout(right_panel)
        right_panel_layout.setContentsMargins(8, 0, 0, 0)
        right_panel_layout.setSpacing(10)

        archive_lbl = QLabel("Historical Compilation Record Hub")
        archive_lbl.setStyleSheet("color: #1e293b; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;")
        right_panel_layout.addWidget(archive_lbl)

        self.table = QTableWidget(4, 4)
        self.table.setHorizontalHeaderLabels(["Compiled Filename", "Document Type", "File Size", "Execution Action Steps"])
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.mock_history = [
            ("CMI_Report_Daily_Prod_20260528.xlsx", "Excel Spreadsheet", "142 KB"),
            ("CMI_Report_Audit_Log_20260529.pdf", "PDF Document", "1.2 MB"),
            ("CMI_Report_Payload_Ingest_20260530.csv", "Comma Separated", "48 KB"),
            ("CMI_Report_Anomaly_Sweep_20260531.pdf", "PDF Document", "892 KB"),
        ]
        self.refresh_history_table()

        right_panel_layout.addWidget(self.table)
        workspace_splitter.addWidget(left_panel)
        workspace_splitter.addWidget(right_panel)
        workspace_splitter.setSizes([380, 820])
        main_layout.addWidget(workspace_splitter, stretch=1)

        # Global Sheet Styling definitions
        self.setStyleSheet("""
            QFrame#HeaderFrame { background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; }
            QTableWidget { background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; }
            QHeaderView::section { background-color: #f8fafc; color: #64748b; font-weight: 700; border: none; border-bottom: 2px solid #e2e8f0; padding: 8px; font-size: 11px; }
            QComboBox { background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 6px; min-width: 180px; }
            QDateEdit { background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 4px; padding: 4px; }
        """)

    def refresh_history_table(self):
        """Redraws the history logs grid layout table cleanly."""
        self.table.setRowCount(len(self.mock_history))
        for r, row in enumerate(self.mock_history):
            # Filename
            self.table.setItem(r, 0, QTableWidgetItem(row[0]))
            # Type
            self.table.setItem(r, 1, QTableWidgetItem(row[1]))
            # Size
            self.table.setItem(r, 2, QTableWidgetItem(row[2]))
            
            # Interactive Download/View trigger widget cell injection
            action_btn = QPushButton("📁 Open File")
            action_btn.setStyleSheet("""
                QPushButton { background-color: #475569; color: white; border-radius: 4px; padding: 2px 8px; max-width: 100px; font-size: 12px; font-weight: bold; }
                QPushButton:hover { background-color: #334155; }
            """)
            # Connect row index to target execution scopes
            action_btn.clicked.connect(lambda checked=False, filename=row[0]: self.open_compiled_document(filename))
            
            cell_container = QWidget()
            cell_layout = QHBoxLayout(cell_container)
            cell_layout.setContentsMargins(0, 2, 0, 2)
            cell_layout.setAlignment(Qt.AlignCenter)
            cell_layout.addWidget(action_btn)
            self.table.setCellWidget(r, 3, cell_container)

    def trigger_report_generation(self):
        """Asynchronously compiles and bundles database elements via threads."""
        selected_template = self.template_list.currentItem().text() if self.template_list.currentItem() else "Default"
        chosen_format = self.format_selector.currentText().split(" ")[0] # Extracts flat token tags: PDF / Excel / Comma
        
        self.log_temporary_status_indicator()

        self.worker = ReportCompilationWorker(selected_template, chosen_format)
        self.worker.compilation_complete.connect(self.handle_compilation_success)
        self.worker.start()

    def log_temporary_status_indicator(self):
        # Insert a temporary compilation line at row index 0 to show visual activity progress
        self.table.insertRow(0)
        item_loading = QTableWidgetItem("⚙ Assembling target data matrices...")
        item_loading.setForeground(Qt.GlobalColor.blue)
        self.table.setItem(0, 0, item_loading)
        self.table.setItem(0, 1, QTableWidgetItem("Compiling..."))
        self.table.setItem(0, 2, QTableWidgetItem("Calculating..."))

    def handle_compilation_success(self, filename):
        """Appends generated properties to document register database grids cleanly."""
        # Calculate human readable descriptive metrics mappings
        doc_type = "PDF Document" if filename.endswith(".pdf") else ("Excel Spreadsheet" if filename.endswith(".xlsx") else "Comma Separated")
        
        # Remove processing temporary loader indicator, register row element
        self.table.removeRow(0)
        self.mock_history.insert(0, (filename, doc_type, "124 KB"))
        self.refresh_history_table()

    def open_compiled_document(self, filename):
        """Locates and displays compiled results on operating system platform environments."""
        # Since these are mock generations, we look in the runtime system base path context
        mock_file_path = os.path.normpath(os.path.join(os.getcwd(), filename))
        
        # Create a dummy blank file to prevent operating system open errors during testing
        with open(mock_file_path, 'w') as f:
            f.write("CMI Data Platform Generated Report Asset Core Payload Header.")

        if os.name == "nt": 
            os.startfile(mock_file_path)
        elif sys.platform == "darwin": 
            subprocess.run(["open", mock_file_path])
        else: 
            subprocess.run(["xdg-open", mock_file_path])