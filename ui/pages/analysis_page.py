import os
import sys
import pandas as pd
import numpy as np
from scipy import stats

from PySide6.QtWidgets import (
    QLineEdit, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout,
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QSplitter, QFrame, QScrollArea, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIntValidator

# Modern Matplotlib rendering bindings for PySide6 Canvas embedding
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class AnalysisWorker(QThread):
    """
    Worker thread to run background mathematical aggregations, 
    preventing UI lockups during complex matrix operations.
    """
    calculation_complete = Signal(dict, pd.DataFrame)
    calculation_failed = Signal(str)

    def __init__(self, df, column_name, transform_type):
        super().__init__()
        self.df = df.copy()
        self.column_name = column_name
        self.transform_type = transform_type

    def run(self):
        try:
            # Safely isolate the chosen data array and drop non-numeric/null values
            series = pd.to_numeric(self.df[self.column_name], errors='coerce').dropna()
            
            if series.empty:
                self.calculation_failed.emit("Selected column contains no valid numerical data.")
                return

            # Apply advanced operational statistical transformations
            if self.transform_type == "Z-Score Normalization":
                mean_val = series.mean()
                std_val = series.std()
                transformed_series = (series - mean_val) / (std_val if std_val != 0 else 1)
            elif self.transform_type == "Logarithmic Base-10":
                transformed_series = np.log10(series.clip(lower=1e-5))
            elif self.transform_type == "Moving Average Filter":
                transformed_series = series.rolling(window=3, min_periods=1).mean()
            elif self.transform_type == "IQR Outlier Clean":
                q1 = series.quantile(0.25)
                q3 = series.quantile(0.75)
                iqr = q3 - q1
                # Clip values extending outside 1.5 * IQR bounds to remove extreme noise
                transformed_series = series.clip(lower=q1 - 1.5 * iqr, upper=q3 + 1.5 * iqr)
            elif self.transform_type == "Cumulative Sum Run":
                transformed_series = series.cumsum()
            elif self.transform_type == "% Change Delta":
                transformed_series = series.pct_change().fill_value(0.0) * 100
            else:
                transformed_series = series

            # Calculate primary core statistics
            mean = series.mean()
            median = series.median()
            
            # Extract Mode Profile
            mode_series = series.mode()
            mode = mode_series.iloc[0] if not mode_series.empty else series.mean()
            
            std_dev = series.std()
            variance = series.var()
            skewness = series.skew()
            kurtosis = series.kurtosis()

            metrics = {
                "mean": f"{mean:,.2f}",
                "median": f"{median:,.2f}",
                "mode": f"{mode:,.2f}",
                "std_dev": f"{std_dev:,.2f}",
                "variance": f"{variance:,.2f}",
                "skewness": f"{skewness:+.2f}" if not pd.isna(skewness) else "0.00",
                "kurtosis": f"{kurtosis:,.2f}" if not pd.isna(kurtosis) else "0.00"
            }

            # Outlier Flag Detection via Z-Score distribution thresholds
            z_scores = np.abs(stats.zscore(series)) if len(series) > 1 else np.zeros(len(series))
            
            # Construct summary matrix table frame strings
            preview_df = pd.DataFrame({
                "Row Index": series.index.astype(str),
                "Observed Input Value": series.map(lambda x: f"{x:,.2f}"),
                "Normalized Offset": transformed_series.map(lambda x: f"{x:+.2f}"),
                "Outlier Flag": ["⚠️ True (Anomalous)" if z > 2.0 else "False" for z in z_scores]
            })

            self.calculation_complete.emit(metrics, preview_df)
        except Exception as e:
            self.calculation_failed.emit(str(e))


class StatTile(QFrame):
    """A clean, math-focused statistical metric display component."""
    def __init__(self, label, value, symbol=""):
        super().__init__()
        self.setObjectName("StatTile")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(6)

        title_lay = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setStyleSheet("color: #475569; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;")
        title_lay.addWidget(lbl)
        
        if symbol:
            sym_lbl = QLabel(symbol)
            sym_lbl.setStyleSheet("color: #3b82f6; font-family: 'Cambria', serif; font-size: 14px; font-weight: bold; font-style: italic;")
            title_lay.addWidget(sym_lbl)
        
        self.val_lbl = QLabel(value)
        self.val_lbl.setObjectName("TileValue")
        self.val_lbl.setStyleSheet("color: #0f172a; font-size: 22px; font-weight: 700; font-family: monospace;")
        
        layout.addLayout(title_lay)
        layout.addWidget(self.val_lbl)
        
        self.setStyleSheet("""
            QFrame#StatTile {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            QFrame#StatTile:hover {
                border: 1px solid #cbd5e1;
                background-color: #f8fafc;
            }
        """)

    def set_value(self, value):
        self.val_lbl.setText(value)


class AnalysisPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_dataframe = None
        self.excel_file_path = None
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)

        # =====================================================================
        # TOP PATH & WORKING DIRECTORY CONTROL BAR
        # =====================================================================
        path_frame = QFrame()
        path_frame.setObjectName("PathFrame")
        path_layout = QHBoxLayout(path_frame)
        path_layout.setContentsMargins(12, 10, 12, 10)
        path_layout.setSpacing(10)

        path_lbl = QLabel("📁 Active Data Pipeline Path:")
        path_lbl.setStyleSheet("color: #334155; font-weight: 600; font-size: 13px;")
        
        self.input_path = QLineEdit()
        self.input_path.setReadOnly(True)
        self.input_path.setPlaceholderText("Select analytical working layout directory target (.xlsx, .xls)...")
        self.input_path.setStyleSheet("padding: 6px 10px; font-size: 12px; background-color: #f1f5f9; border-radius: 4px; border: 1px solid #cbd5e1;")

        btn_browse = QPushButton("Browse...")
        btn_browse.clicked.connect(self.select_working_file)
        btn_browse.setStyleSheet("""
            QPushButton { background-color: #e2e8f0; color: #1e293b; padding: 6px 14px; font-weight: 600; border-radius: 4px; font-size: 12px; border: 1px solid #cbd5e1; }
            QPushButton:hover { background-color: #cbd5e1; }
        """)

        path_layout.addWidget(path_lbl)
        path_layout.addWidget(self.input_path, stretch=1)
        path_layout.addWidget(btn_browse)
        main_layout.addWidget(path_frame)

        # =====================================================================
        # EXCEL OVERRIDE OPTIONS (SHEET SELECTOR & HEADER CONTROL)
        # =====================================================================
        config_frame = QFrame()
        config_frame.setObjectName("ConfigFrame")
        config_layout = QHBoxLayout(config_frame)
        config_layout.setContentsMargins(12, 8, 12, 8)
        config_layout.setSpacing(12)

        sheet_lbl = QLabel("🎯 Target Sheet:")
        sheet_lbl.setStyleSheet("color: #475569; font-weight: 600; font-size: 12px;")
        self.sheet_selector = QComboBox()
        self.sheet_selector.addItems(["No File Loaded"])
        self.sheet_selector.currentTextChanged.connect(self.load_excel_sheet_data)

        header_row_lbl = QLabel("📑 Header Index Row:")
        header_row_lbl.setStyleSheet("color: #475569; font-weight: 600; font-size: 12px;")
        self.header_row_input = QLineEdit("0")
        self.header_row_input.setValidator(QIntValidator(0, 1000))
        self.header_row_input.setFixedWidth(50)
        self.header_row_input.setToolTip("If the first row of your sheet isn't the header layout, input the correct row index here.")
        self.header_row_input.editingFinished.connect(self.reload_sheet_from_explicit_header)

        config_layout.addWidget(sheet_lbl)
        config_layout.addWidget(self.sheet_selector)
        config_layout.addSpacing(10)
        config_layout.addWidget(header_row_lbl)
        config_layout.addWidget(self.header_row_input)
        config_layout.addStretch()
        
        main_layout.addWidget(config_frame)

        # =====================================================================
        # HEADER CONTROL BAR
        # =====================================================================
        header_frame = QFrame()
        header_frame.setObjectName("HeaderFrame")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(16, 14, 16, 14)

        title_section = QVBoxLayout()
        title = QLabel("Advanced Analytics Module")
        title.setStyleSheet("color: #0f172a; font-size: 20px; font-weight: 700;")
        sub = QLabel("Apply statistical transformations, filter variables, and evaluate dataset behaviors.")
        sub.setStyleSheet("color: #64748b; font-size: 12px;")
        title_section.addWidget(title)
        title_section.addWidget(sub)
        header_layout.addLayout(title_section)
        header_layout.addStretch()

        # Toolbar Control Suite Actions
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(10)

        self.column_selector = QComboBox()
        self.column_selector.addItems(["No Data Loaded"])
        self.column_selector.setStyleSheet("padding: 6px 12px; font-size: 13px;")

        self.transform_selector = QComboBox()
        self.transform_selector.addItems([
            "No Transform (Raw)", "Z-Score Normalization", "Logarithmic Base-10", 
            "Moving Average Filter", "IQR Outlier Clean", "Cumulative Sum Run", "% Change Delta"
        ])
        self.transform_selector.setStyleSheet("padding: 6px 12px; font-size: 13px;")

        btn_compute = QPushButton("⚡ Compute Statistics")
        btn_compute.clicked.connect(self.run_analysis_pipeline)
        btn_compute.setStyleSheet("""
            QPushButton { background-color: #2563eb; color: white; padding: 7px 18px; font-weight: bold; border-radius: 6px; font-size: 13px; }
            QPushButton:hover { background-color: #1d4ed8; }
        """)

        toolbar_layout.addWidget(QLabel("Target Variable:"))
        toolbar_layout.addWidget(self.column_selector)
        toolbar_layout.addWidget(QLabel("Operator:"))
        toolbar_layout.addWidget(self.transform_selector)
        toolbar_layout.addWidget(btn_compute)
        header_layout.addLayout(toolbar_layout)

        main_layout.addWidget(header_frame)

        # =====================================================================
        # MAIN LAYOUT WORKSPACE SPLITTER
        # =====================================================================
        workspace_splitter = QSplitter(Qt.Horizontal)
        workspace_splitter.setStyleSheet("QSplitter::handle { background-color: #cbd5e1; width: 1px; }")

        # Left Column Panel: Summary & Statistical Cards
        left_panel = QWidget()
        left_panel_layout = QVBoxLayout(left_panel)
        left_panel_layout.setContentsMargins(0, 0, 8, 0)
        left_panel_layout.setSpacing(12)

        panel_title = QLabel("Calculated Statistical Vectors")
        panel_title.setStyleSheet("color: #1e293b; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;")
        left_panel_layout.addWidget(panel_title)

        # Scrollable metric framework container
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll_content = QWidget()
        self.grid_metrics = QGridLayout(scroll_content)
        self.grid_metrics.setContentsMargins(0, 0, 4, 0)
        self.grid_metrics.setSpacing(10)

        # Map functional metric displays
        self.tile_mean = StatTile("Arithmetic Mean", "--", "μ")
        self.tile_median = StatTile("Median Value", "--", "x̃")
        self.tile_mode = StatTile("Mode Profile", "--", "Mo")
        self.tile_std = StatTile("Std. Deviation", "--", "σ")
        self.tile_var = StatTile("Sample Variance", "--", "σ²")
        self.tile_skew = StatTile("Skewness Coefficient", "--", "γ₁")
        self.tile_kurt = StatTile("Kurtosis Factor", "--", "β₂")

        self.grid_metrics.addWidget(self.tile_mean, 0, 0)
        self.grid_metrics.addWidget(self.tile_median, 0, 1)
        self.grid_metrics.addWidget(self.tile_mode, 1, 0)
        self.grid_metrics.addWidget(self.tile_std, 1, 1)
        self.grid_metrics.addWidget(self.tile_var, 2, 0)
        self.grid_metrics.addWidget(self.tile_skew, 2, 1)
        self.grid_metrics.addWidget(self.tile_kurt, 3, 0, 1, 2)

        scroll.setWidget(scroll_content)
        left_panel_layout.addWidget(scroll)

        # Right Column Panel: Visualizations & Table Previews (Stacked vertically via nested splitter)
        right_panel = QWidget()
        right_panel_layout = QVBoxLayout(right_panel)
        right_panel_layout.setContentsMargins(8, 0, 0, 0)
        right_panel_layout.setSpacing(12)

        right_splitter = QSplitter(Qt.Vertical)
        right_splitter.setStyleSheet("QSplitter::handle { background-color: #cbd5e1; height: 1px; }")

        # Upper plot canvas integrated Matplotlib widget layout frame
        self.plot_placeholder = QFrame()
        self.plot_placeholder.setObjectName("PlotCanvasFrame")
        self.plot_layout = QVBoxLayout(self.plot_placeholder)
        self.plot_layout.setContentsMargins(12, 12, 12, 12)
        
        self.figure = Figure(figsize=(5, 3), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.plot_layout.addWidget(self.canvas)
        self.clear_chart_canvas("Load data pipeline vectors to display distribution metrics plots.")

        # Inner container holding the tabular grids
        table_container = QWidget()
        table_container_layout = QVBoxLayout(table_container)
        table_container_layout.setContentsMargins(0, 4, 0, 0)
        table_container_layout.setSpacing(12)

        # Dual Table Setup: Dynamic File Grid Raw Preview & Analyzed Metrics Preview
        tables_horizontal_splitter = QSplitter(Qt.Horizontal)
        tables_horizontal_splitter.setStyleSheet("QSplitter::handle { background-color: #cbd5e1; width: 1px; }")

        # Segment A: Spreadsheet Matrix Raw File Preview Area
        raw_preview_widget = QWidget()
        raw_lay = QVBoxLayout(raw_preview_widget)
        raw_lay.setContentsMargins(0, 0, 4, 0)
        raw_title = QLabel("📑 Spreadsheet Matrix Data Preview")
        raw_title.setStyleSheet("color: #1e293b; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;")
        self.raw_table = QTableWidget(0, 0)
        self.raw_table.setShowGrid(False)
        self.raw_table.setAlternatingRowColors(True)
        raw_lay.addWidget(raw_title)
        raw_lay.addWidget(self.raw_table)

        # Segment B: Vector Output Columns Analysis Calculations Results
        analysis_preview_widget = QWidget()
        analysis_lay = QVBoxLayout(analysis_preview_widget)
        analysis_lay.setContentsMargins(4, 0, 0, 0)
        grid_title = QLabel("📊 Analyzed Metric Output Vector")
        grid_title.setStyleSheet("color: #1e293b; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;")
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Row Index", "Observed Input Value", "Normalized Offset", "Outlier Flag"])
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        analysis_lay.addWidget(grid_title)
        analysis_lay.addWidget(self.table)

        tables_horizontal_splitter.addWidget(raw_preview_widget)
        tables_horizontal_splitter.addWidget(analysis_preview_widget)
        tables_horizontal_splitter.setSizes([500, 500])
        table_container_layout.addWidget(tables_horizontal_splitter)

        right_splitter.addWidget(self.plot_placeholder)
        right_splitter.addWidget(table_container)
        right_splitter.setSizes([350, 450])

        right_panel_layout.addWidget(right_splitter)

        # Assemble elements inside workspace layout balances
        workspace_splitter.addWidget(left_panel)
        workspace_splitter.addWidget(right_panel)
        workspace_splitter.setSizes([380, 820])
        main_layout.addWidget(workspace_splitter, stretch=1)

        # Component isolation theme styling specs
        self.setStyleSheet("""
            QFrame#PathFrame, QFrame#HeaderFrame, QFrame#PlotCanvasFrame, QFrame#ConfigFrame {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                gridline-color: #f1f5f9;
            }
            QTableWidget::item {
                padding: 6px;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                color: #475569;
                font-weight: 700;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                padding: 8px;
                font-size: 11px;
                text-transform: uppercase;
            }
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                min-width: 180px;
                padding: 4px 8px;
            }
            QComboBox:focus, QLineEdit:focus {
                border: 1px solid #3b82f6;
            }
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 4px;
                padding: 4px;
            }
        """)

    def select_working_file(self):
        """Launches file selection dialog to parse system file paths."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Data Engine Document", "", "Excel Documents (*.xlsx *.xls)"
        )
        if file_path:
            self.excel_file_path = file_path
            self.input_path.setText(file_path)
            try:
                xl = pd.ExcelFile(file_path)
                self.sheet_selector.clear()
                self.sheet_selector.addItems(xl.sheet_names)
            except Exception as e:
                QMessageBox.critical(self, "Pipeline Error", f"Failed reading sheets metadata structure:\n{str(e)}")

    def load_excel_sheet_data(self):
        """Extracts the selected sheet dataframe based on user header row choices."""
        if not self.excel_file_path:
            return
            
        sheet_name = self.sheet_selector.currentText()
        if not sheet_name or sheet_name == "No File Loaded":
            return

        try:
            row_idx = int(self.header_row_input.text()) if self.header_row_input.text() else 0
        except ValueError:
            row_idx = 0

        try:
            # Read workbook structure dynamically factoring in custom header overrides
            self.current_dataframe = pd.read_excel(self.excel_file_path, sheet_name=sheet_name, header=row_idx)
            
            # Re-populate column selection menu strings
            self.column_selector.clear()
            if not self.current_dataframe.columns.empty:
                self.column_selector.addItems(self.current_dataframe.columns.astype(str).tolist())
            else:
                self.column_selector.addItems(["No columns located"])
                
            self.populate_raw_preview_grid()
        except Exception as e:
            QMessageBox.critical(self, "Parsing Error", f"Failed processing target matrix configuration setup:\n{str(e)}")

    def reload_sheet_from_explicit_header(self):
        """Triggered automatically when editing of the header input row is completed."""
        self.load_excel_sheet_data()

    def populate_raw_preview_grid(self):
        """Generates an initial small-footprint matrix grid preview of the raw uploaded document."""
        if self.current_dataframe is None:
            return

        # Restrict real-time preview table generation sizes to safe limits
        preview_limit_df = self.current_dataframe.head(30)
        
        self.raw_table.setRowCount(0)
        self.raw_table.setColumnCount(0)
        
        self.raw_table.setColumnCount(len(preview_limit_df.columns))
        self.raw_table.setHorizontalHeaderLabels(preview_limit_df.columns.astype(str).tolist())
        self.raw_table.setRowCount(len(preview_limit_df))
        
        for r in range(len(preview_limit_df)):
            for c in range(len(preview_limit_df.columns)):
                cell_val = str(preview_limit_df.iloc[r, c]) if not pd.isna(preview_limit_df.iloc[r, c]) else ""
                item = QTableWidgetItem(cell_val)
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.raw_table.setItem(r, c, item)
        
        self.raw_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

    def clear_chart_canvas(self, custom_msg=""):
        """Safely resets the internal layout canvas space state views."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.text(0.5, 0.5, custom_msg, color="#94a3b8", style='italic', ha='center', va='center', fontsize=10)
        ax.set_axis_off()
        self.canvas.draw()

    def run_analysis_pipeline(self):
        """Asynchronously triggers the mathematical background processing pipeline."""
        if self.current_dataframe is None or self.column_selector.currentText() == "No Data Loaded":
            QMessageBox.warning(self, "Execution Deferred", "Please select a valid working data framework file before computing.")
            return

        # Interface process indicator triggers
        self.tile_mean.set_value("⏳ ...")
        self.tile_median.set_value("⏳ ...")
        self.tile_mode.set_value("⏳ ...")
        self.tile_std.set_value("⏳ ...")
        self.tile_var.set_value("⏳ ...")
        self.tile_skew.set_value("⏳ ...")
        self.tile_kurt.set_value("⏳ ...")

        selected_col = self.column_selector.currentText()
        selected_transform = self.transform_selector.currentText()

        # Allocate worker thread instantiation
        self.worker = AnalysisWorker(self.current_dataframe, selected_col, selected_transform)
        self.worker.calculation_complete.connect(self.update_displayed_metrics)
        self.worker.calculation_failed.connect(self.handle_pipeline_failure)
        self.worker.start()

    def update_displayed_metrics(self, metrics, preview_df):
        """Safely apply metrics emitted back from the analysis execution worker thread."""
        self.tile_mean.set_value(metrics["mean"])
        self.tile_median.set_value(metrics["median"])
        self.tile_mode.set_value(metrics["mode"])
        self.tile_std.set_value(metrics["std_dev"])
        self.tile_var.set_value(metrics["variance"])
        self.tile_skew.set_value(metrics["skewness"])
        self.tile_kurt.set_value(metrics["kurtosis"])

        # Repopulate internal UI previews grid
        self.table.setRowCount(0)
        self.table.setRowCount(len(preview_df))
        
        for r in range(len(preview_df)):
            for c in range(4):
                item_text = str(preview_df.iloc[r, c])
                item = QTableWidgetItem(item_text)
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                
                if c == 3 and "True" in item_text:
                    item.setForeground(Qt.GlobalColor.red)
                    item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(r, c, item)

        # Modern Matplotlib live rendering logic 
        try:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            
            selected_col = self.column_selector.currentText()
            series_data = pd.to_numeric(self.current_dataframe[selected_col], errors='coerce').dropna()
            
            # Plot distribution profile architectures
            series_data.plot(kind='hist', bins=15, density=True, ax=ax, alpha=0.4, color='#3b82f6', edgecolor='#2563eb')
            series_data.plot(kind='kde', ax=ax, color='#1d4ed8', linewidth=2)
            
            # Accentuate primary mean and median lines
            ax.axvline(series_data.mean(), color='#ef4444', linestyle='--', linewidth=1.5, label=f"Mean: {metrics['mean']}")
            ax.axvline(series_data.median(), color='#10b981', linestyle='-.', linewidth=1.5, label=f"Median: {metrics['median']}")
            
            ax.set_title(f"Distribution Vector Profile: {selected_col}", fontsize=11, fontweight='bold', color='#1e293b')
            ax.set_ylabel("Density Scale Ratio", fontsize=9, color='#64748b')
            ax.tick_params(labelsize=8)
            ax.legend(fontsize=8, loc='upper right')
            ax.grid(True, linestyle=':', alpha=0.6, color='#cbd5e1')
            
            self.figure.tight_layout()
            self.canvas.draw()
        except Exception as chart_err:
            self.clear_chart_canvas(f"Chart matrix fallback generation: {str(chart_err)}")

    def handle_pipeline_failure(self, error_message):
        """Handles background execution parsing failures gracefully."""
        QMessageBox.warning(self, "Calculation Error", f"The background pipeline encountered an error:\n{error_message}")
        self.tile_mean.set_value("Error")
        self.tile_median.set_value("Error")
        self.tile_mode.set_value("Error")
        self.tile_std.set_value("Error")
        self.tile_var.set_value("Error")
        self.tile_skew.set_value("Error")
        self.tile_kurt.set_value("Error")
        self.clear_chart_canvas("Awaiting alternative numerical array variables profile...")