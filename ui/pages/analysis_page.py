import sys
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout,
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QSplitter, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, QThread, Signal


class AnalysisWorker(QThread):
    """
    Worker thread to run background mathematical aggregations, 
    preventing UI lockups during complex matrix operations.
    """
    calculation_complete = Signal(dict)

    def __init__(self, data_matrix):
        super().__init__()
        self.data_matrix = data_matrix

    def run(self):
        # Simulate heavy calculations or statistical matrix processing
        # e.g., calculating standard deviations, rolling means, or regressions
        import time
        time.sleep(0.4) 
        
        metrics = {
            "mean": "412.85",
            "median": "398.00",
            "std_dev": "45.12",
            "variance": "2,035.81",
            "skewness": "+0.34",
            "kurtosis": "2.11"
        }
        self.calculation_complete.emit(metrics)


class StatTile(QFrame):
    """A clean, math-focused statistical metric display component."""
    def __init__(self, label, value, symbol=""):
        super().__init__()
        self.setObjectName("StatTile")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(4)

        title_lay = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setStyleSheet("color: #475569; font-size: 11px; font-weight: 700; text-transform: uppercase;")
        title_lay.addWidget(lbl)
        
        if symbol:
            sym_lbl = QLabel(symbol)
            sym_lbl.setStyleSheet("color: #94a3b8; font-family: 'Cambria', serif; font-size: 13px; font-style: italic;")
            title_lay.addWidget(sym_lbl)
        
        val_lbl = QLabel(value)
        val_lbl.setObjectName("TileValue")
        val_lbl.setStyleSheet("color: #0f172a; font-size: 20px; font-weight: 700; font-family: monospace;")
        
        layout.addLayout(title_lay)
        layout.addWidget(val_lbl)
        
        self.setStyleSheet("""
            QFrame#StatTile {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
        """)


class AnalysisPage(QWidget):
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
        title = QLabel("Advanced Analytics Module")
        title.setStyleSheet("color: #0f172a; font-size: 20px; font-weight: 700;")
        sub = QLabel("Apply statistical transformations, filter variables, and evaluate dataset behaviors.")
        sub.setStyleSheet("color: #64748b; font-size: 12px;")
        title_section.addWidget(title)
        title_section.addWidget(sub)
        header_layout.addLayout(title_section)
        header_layout.addStretch()

        # Toolbar Actions
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(8)

        self.column_selector = QComboBox()
        self.column_selector.addItems(["Target Metric Column", "Velocity Vector", "Volumetric Mass", "Timestamp Offset"])
        self.column_selector.setStyleSheet("padding: 6px 12px; font-size: 13px;")

        self.transform_selector = QComboBox()
        self.transform_selector.addItems(["No Transform (Raw)", "Z-Score Normalization", "Logarithmic Base-10", "Moving Average Filter"])
        self.transform_selector.setStyleSheet("padding: 6px 12px; font-size: 13px;")

        btn_compute = QPushButton("⚡ Compute Statistics")
        btn_compute.clicked.connect(self.run_analysis_pipeline)
        btn_compute.setStyleSheet("""
            QPushButton { background-color: #2563eb; color: white; padding: 7px 16px; font-weight: bold; border-radius: 6px; font-size: 13px; }
            QPushButton:hover { background-color: #1d4ed8; }
        """)

        toolbar_layout.addWidget(self.column_selector)
        toolbar_layout.addWidget(self.transform_selector)
        toolbar_layout.addWidget(btn_compute)
        header_layout.addLayout(toolbar_layout)

        main_layout.addWidget(header_frame)

        # =====================================================================
        # MAIN LAYOUT WORKSPACE SPLITTER
        # =====================================================================
        workspace_splitter = QSplitter(Qt.Horizontal)
        workspace_splitter.setStyleSheet("QSplitter::handle { background-color: #e2e8f0; width: 2px; }")

        # Left Column Panel: Summary & Statistical Cards
        left_panel = QWidget()
        left_panel_layout = QVBoxLayout(left_panel)
        left_panel_layout.setContentsMargins(0, 0, 8, 0)
        left_panel_layout.setSpacing(12)

        panel_title = QLabel("Calculated Statistical Vectors")
        panel_title.setStyleSheet("color: #1e293b; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;")
        left_panel_layout.addWidget(panel_title)

        # Scrollable area to handle dense lists of metric groups smoothly
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll_content = QWidget()
        self.grid_metrics = QGridLayout(scroll_content)
        self.grid_metrics.setContentsMargins(0, 0, 0, 0)
        self.grid_metrics.setSpacing(10)

        # Instantiate descriptive tiles using standard math notation formulations
        self.tile_mean = StatTile("Arithmetic Mean", "412.85", "μ")
        self.tile_median = StatTile("Median Value", "398.00", "x̃")
        self.tile_std = StatTile("Std. Deviation", "45.12", "σ")
        self.tile_var = StatTile("Sample Variance", "2,035.81", "σ²")
        self.tile_skew = StatTile("Skewness Coefficient", "+0.34", "γ₁")
        self.tile_kurt = StatTile("Kurtosis Factor", "2.11", "β₂")

        self.grid_metrics.addWidget(self.tile_mean, 0, 0)
        self.grid_metrics.addWidget(self.tile_median, 0, 1)
        self.grid_metrics.addWidget(self.tile_std, 1, 0)
        self.grid_metrics.addWidget(self.tile_var, 1, 1)
        self.grid_metrics.addWidget(self.tile_skew, 2, 0)
        self.grid_metrics.addWidget(self.tile_kurt, 2, 1)

        scroll.setWidget(scroll_content)
        left_panel_layout.addWidget(scroll)

        # Right Column Panel: Numerical Data Grids & Visualization Spots
        right_panel = QWidget()
        right_panel_layout = QVBoxLayout(right_panel)
        right_panel_layout.setContentsMargins(8, 0, 0, 0)
        right_panel_layout.setSpacing(12)

        # Upper plot canvas mock placeholder block frame
        plot_placeholder = QFrame()
        plot_placeholder.setObjectName("PlotCanvasFrame")
        plot_layout = QVBoxLayout(plot_placeholder)
        plot_layout.setContentsMargins(16, 16, 16, 16)
        
        chart_lbl = QLabel("📈 Distribution Analysis Overlay Workspace")
        chart_lbl.setStyleSheet("color: #1e293b; font-size: 13px; font-weight: 700;")
        hint_lbl = QLabel("[Drop Matplotlib Histogram / Probability Density Plot Engine Layers Here]")
        hint_lbl.setAlignment(Qt.AlignCenter)
        hint_lbl.setStyleSheet("color: #94a3b8; font-size: 12px; font-style: italic;")
        
        plot_layout.addWidget(chart_lbl)
        plot_layout.addWidget(hint_lbl, stretch=1)
        right_panel_layout.addWidget(plot_placeholder, stretch=3)

        # Lower data frame preview grid
        grid_title = QLabel("Analyzed Matrix Summary Elements")
        grid_title.setStyleSheet("color: #1e293b; font-size: 12px; font-weight: 700; text-transform: uppercase;")
        right_panel_layout.addWidget(grid_title)

        self.table = QTableWidget(4, 4)
        self.table.setHorizontalHeaderLabels(["Row Index", "Observed Input Value", "Normalized Offset", "Outlier Flag"])
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        mock_rows = [
            ("0001", "380.20", "-0.72", "False"),
            ("0002", "450.10", "+0.82", "False"),
            ("0003", "590.40", "+3.93", "⚠️ True (Anomalous)"),
            ("0004", "395.00", "-0.39", "False")
        ]
        for r, row in enumerate(mock_rows):
            for c, item_text in enumerate(row):
                item = QTableWidgetItem(item_text)
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                if c == 3 and "True" in item_text:
                    item.setForeground(Qt.GlobalColor.red)
                self.table.setItem(r, c, item)
                
        right_panel_layout.addWidget(self.table, stretch=2)

        # Assemble elements inside the workspace splitter layout
        workspace_splitter.addWidget(left_panel)
        workspace_splitter.addWidget(right_panel)
        workspace_splitter.setSizes([450, 750]) # Initial widths balance allocation split
        main_layout.addWidget(workspace_splitter, stretch=1)

        # Apply component-isolated style overrides
        self.setStyleSheet("""
            QFrame#HeaderFrame {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
            }
            QFrame#PlotCanvasFrame {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                color: #64748b;
                font-weight: 700;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                padding: 6px;
                font-size: 11px;
            }
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                min-width: 160px;
            }
        """)

    def run_analysis_pipeline(self):
        """Asynchronously triggers the mathematical background pipeline."""
        self.title_mean = self.tile_mean.findChild(QLabel, "TileValue")
        if self.title_mean:
            self.title_mean.setText("⏳ ...")
            
        # Passing an empty array template for mock demonstration testing runs
        self.worker = AnalysisWorker(data_matrix=[])
        self.worker.calculation_complete.connect(self.update_displayed_metrics)
        self.worker.start()

    def update_displayed_metrics(self, data):
        """Safely apply values emitted back from the calculation threads."""
        self.tile_mean.findChild(QLabel, "TileValue").setText(data["mean"])
        self.tile_median.findChild(QLabel, "TileValue").setText(data["median"])
        self.tile_std.findChild(QLabel, "TileValue").setText(data["std_dev"])
        self.tile_var.findChild(QLabel, "TileValue").setText(data["variance"])
        self.tile_skew.findChild(QLabel, "TileValue").setText(data["skewness"])
        self.tile_kurt.findChild(QLabel, "TileValue").setText(data["kurtosis"])