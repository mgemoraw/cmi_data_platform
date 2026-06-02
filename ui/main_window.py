from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QListWidget,
    QStackedWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont

from ui.pages.dashboard_page import DashboardPage
from ui.pages.explorer_page import ExplorerPage
from ui.pages.processing_page import ProcessingPage
from ui.pages.analysis_page import AnalysisPage
from ui.pages.reports_page import ReportsPage
from ui.pages.settings_page import SettingsPage


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("CMI Data Platform")
        self.resize(1500, 900)
        
        # Apply Global Stylesheet for a modern, flat look
        self.apply_styles()
        self.build_ui()

    def build_ui(self):
        central = QWidget()
        central.setObjectName("CentralWidget")
        self.setCentralWidget(central)

        # Eliminate default margins between sidebar and pages
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # =====================================================================
        # LEFT SIDEBAR CONTAINER
        # =====================================================================
        sidebar_container = QWidget()
        sidebar_container.setObjectName("SidebarContainer")
        sidebar_layout = QVBoxLayout(sidebar_container)
        sidebar_layout.setContentsMargins(12, 24, 12, 24)
        sidebar_layout.setSpacing(20)

        # App Title Header
        app_title = QLabel("CMI PLATFORM")
        app_title.setObjectName("AppTitle")
        app_title.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(app_title)

        # Navigation List
        self.sidebar = QListWidget()
        self.sidebar.setObjectName("SidebarMenu")
        self.sidebar.setSpacing(6)  # Space between items
        
        self.sidebar.addItems([
            "🏠   Dashboard",
            "📁   Project Explorer",
            "⚙️   Data Processing",
            "📊   Analysis Tools",
            "📈   Reports",
            "🔧   Settings"
        ])
        sidebar_layout.addWidget(self.sidebar)
        
        # =====================================================================
        # PAGE STACK CONTAINER
        # =====================================================================
        self.pages = QStackedWidget()
        self.pages.setObjectName("PageStack")

        self.pages.addWidget(DashboardPage())
        self.pages.addWidget(ExplorerPage())
        self.pages.addWidget(ProcessingPage())
        self.pages.addWidget(AnalysisPage())
        self.pages.addWidget(ReportsPage())
        self.pages.addWidget(SettingsPage())

        # Connections
        self.sidebar.currentRowChanged.connect(self.pages.setCurrentIndex)

        # Assemble Main Layout
        # Sidebar takes ~18% width, pages take ~82% width
        main_layout.addWidget(sidebar_container, 18)
        main_layout.addWidget(self.pages, 82)

        # Set default active page
        self.sidebar.setCurrentRow(0)

    def apply_styles(self):
        self.setStyleSheet("""
            /* Base Application Theme */
            QWidget#CentralWidget {
                background-color: #f8fafc; /* Crisp, light grey-blue page canvas */
            }

            /* Sidebar Panel Outer Box */
            QWidget#SidebarContainer {
                background-color: #1e293b; /* Premium slate dark blue sidebar background */
                border-right: 1px solid #cbd5e1;
            }

            /* App Logo/Text Styling */
            QLabel#AppTitle {
                color: #38bdf8; /* Bright electric sky blue highlight */
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 16px;
                font-weight: 800;
                letter-spacing: 2px;
                padding-bottom: 10px;
                border-bottom: 1px solid #334155;
            }

            /* Sidebar Core List Object */
            QListWidget#SidebarMenu {
                border: none;
                background-color: transparent;
                outline: 0;
            }

            /* Individual Sidebar Rows */
            QListWidget#SidebarMenu::item {
                color: #94a3b8; /* Muted modern text color default */
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                font-weight: 600;
                padding: 12px 16px;
                border-radius: 8px;
                transition: background-color 0.2s ease;
            }

            /* Item State Changes */
            QListWidget#SidebarMenu::item:hover {
                background-color: #334155; /* Soft background block illuminate */
                color: #f8fafc;
            }

            QListWidget#SidebarMenu::item:selected {
                background-color: #2563eb; /* Vibrant blue identity focus bar */
                color: #ffffff;
                font-weight: 700;
            }

            /* Visual Content Container Padding Frame */
            QStackedWidget#PageStack {
                background-color: #f8fafc;
                padding: 30px; /* Generous padding around workspace frames */
            }
        """)