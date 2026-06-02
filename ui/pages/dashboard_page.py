import sys
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt


class KPICard(QWidget):
    """Reusable Production-Grade metric widget layout with icon and trend lines."""
    def __init__(self, title, value, unit, status_color="#2563eb", subtitle=""):
        super().__init__()
        self.setObjectName("KPICard")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(6)
        
        # Upper descriptive label
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 600; text-transform: uppercase;")
        
        # Primary Metric Line
        val_layout = QHBoxLayout()
        val_layout.setSpacing(4)
        
        val_lbl = QLabel(value)
        val_lbl.setStyleSheet(f"color: #1e293b; font-size: 26px; font-weight: 700;")
        
        unit_lbl = QLabel(unit)
        unit_lbl.setStyleSheet("color: #94a3b8; font-size: 14px; font-weight: 500; margin-top: 8px;")
        
        val_layout.addWidget(val_lbl)
        val_layout.addWidget(unit_lbl)
        val_layout.addStretch()
        
        # Sub-context metric trend indicator
        sub_lbl = QLabel(subtitle)
        sub_lbl.setStyleSheet("color: #475569; font-size: 12px; font-weight: 500;")
        
        layout.addWidget(title_lbl)
        layout.addLayout(val_layout)
        layout.addWidget(sub_lbl)
        
        # Component styling sheet
        self.setStyleSheet(f"""
            QWidget#KPICard {{
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                border-left: 4px solid {status_color};
            }}
        """)


class ChartPlaceholder(QWidget):
    """Structural card block holding visualization frames."""
    def __init__(self, title):
        super().__init__()
        self.setObjectName("ChartFrame")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: #1e293b; font-size: 14px; font-weight: 700; margin-bottom: 10px;")
        layout.addWidget(title_lbl)
        
        # Canvas space representation area
        self.canvas = QWidget()
        self.canvas.setObjectName("ChartCanvas")
        canvas_layout = QVBoxLayout(self.canvas)
        
        inner_hint = QLabel("📊 Chart Stream Platform Layer\n[Integrate Matplotlib / PySide6 Charts Here]")
        inner_hint.setAlignment(Qt.AlignCenter)
        inner_hint.setStyleSheet("color: #94a3b8; font-family: 'Segoe UI'; font-size: 13px; font-style: italic;")
        canvas_layout.addWidget(inner_hint)
        
        layout.addWidget(self.canvas, stretch=1)
        
        self.setStyleSheet("""
            QWidget#ChartFrame {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
            QWidget#ChartCanvas {
                background-color: #f8fafc;
                border: 1px dashed #cbd5e1;
                border-radius: 8px;
            }
        """)


class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(24)

        # =====================================================================
        # SECTION 1: HEADER BANNER ROW
        # =====================================================================
        header_layout = QHBoxLayout()
        
        title_container = QVBoxLayout()
        main_title = QLabel("System Dashboard")
        main_title.setStyleSheet("color: #0f172a; font-size: 24px; font-weight: 700; letter-spacing: -0.5px;")
        sub_title = QLabel("Operational control overview and workspace execution telemetry metrics.")
        sub_title.setStyleSheet("color: #64748b; font-size: 13px; font-weight: 500;")
        title_container.addWidget(main_title)
        title_container.addWidget(sub_title)
        
        sync_lbl = QLabel(f"System Sync: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        sync_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        sync_lbl.setStyleSheet("color: #64748b; font-family: 'Segoe UI'; font-size: 12px; font-weight: 600; background-color: #e2e8f0; padding: 6px 12px; border-radius: 6px;")
        
        header_layout.addLayout(title_container)
        header_layout.addStretch()
        header_layout.addWidget(sync_lbl)
        main_layout.addLayout(header_layout)

        # =====================================================================
        # SECTION 2: TELEMETRY KPI TILES (Grid)
        # =====================================================================
        kpi_grid = QGridLayout()
        kpi_grid.setSpacing(16)
        
        # Setup specific structural KPI statuses
        card1 = KPICard("Processed Datasets", "142", "files", status_color="#10b981", subtitle="🟢 12 processed today")
        card2 = KPICard("Pipeline Output Velocity", "3,842", "rows/sec", status_color="#2563eb", subtitle="📈 Up 4.2% this session")
        card3 = KPICard("Validation Flags", "3", "issues", status_color="#f59e0b", subtitle="⚠️ Warning thresholds reached")
        card4 = KPICard("Storage Footprint", "1.42", "GB", status_color="#6366f1", subtitle="💾 Active global workspace")
        
        kpi_grid.addWidget(card1, 0, 0)
        kpi_grid.addWidget(card2, 0, 1)
        kpi_grid.addWidget(card3, 0, 2)
        kpi_grid.addWidget(card4, 0, 3)
        main_layout.addLayout(kpi_grid)

        # =====================================================================
        # SECTION 3: VISUALIZATION MODULES (Double Columns Layout)
        # =====================================================================
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(16)
        
        chart_left = ChartPlaceholder("Data Ingestion Volumetric Trends")
        chart_right = ChartPlaceholder("Equipment Parsing Distribution Allocations")
        
        charts_layout.addWidget(chart_left, stretch=1)
        charts_layout.addWidget(chart_right, stretch=1)
        main_layout.addLayout(charts_layout, stretch=2)

        # =====================================================================
        # SECTION 4: RECENT AUDIT TRACKING GRID
        # =====================================================================
        audit_container = QWidget()
        audit_container.setObjectName("AuditFrame")
        audit_layout = QVBoxLayout(audit_container)
        audit_layout.setContentsMargins(20, 20, 20, 20)
        
        audit_title = QLabel("Recent Pipeline Activities")
        audit_title.setStyleSheet("color: #1e293b; font-size: 14px; font-weight: 700; margin-bottom: 8px;")
        audit_layout.addWidget(audit_title)
        
        # Setup Enterprise Level Sheet Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Timestamp", "Target Pipeline Task", "Assigned Asset Group", "Status Context"])
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        self.table.setFocusPolicy(Qt.NoFocus)
        
        # Configure sizing parameters for headers
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # Feed mock visual testing configurations row vectors
        logs = [
            ("23:14:02", "Excel Data Splitting Pipeline Run", "Excavator-Main_S1.xlsx", "✅ Success Complete"),
            ("22:45:19", "Clean Target Operational Cells", "Dozer-Aggregated_V2.xlsx", "✅ Success Complete"),
            ("19:02:11", "Template Field Aggregator Calculation", "Truck_Logs_May.xlsx", "⚠️ 3 Warnings Issued"),
        ]
        
        self.table.setRowCount(len(logs))
        for row_idx, data in enumerate(logs):
            for col_idx, value in enumerate(data):
                item = QTableWidgetItem(value)
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                # Apply custom colors to status cells
                if col_idx == 3:
                    if "Success" in value: item.setForeground(Qt.GlobalColor.darkGreen)
                    else: item.setForeground(Qt.GlobalColor.red)
                self.table.setItem(row_idx, col_idx, item)
                
        audit_layout.addWidget(self.table)
        main_layout.addWidget(audit_container, stretch=3)

        # Global Sheet Styling definitions for underlying lists
        self.setStyleSheet("""
            QWidget#AuditFrame {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
            QTableWidget {
                border: none;
                background-color: transparent;
                gridline-color: transparent;
                font-size: 13px;
                color: #334155;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #f1f5f9;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                color: #64748b;
                font-weight: 700;
                text-transform: uppercase;
                font-size: 11px;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                padding: 8px 12px;
            }
        """)