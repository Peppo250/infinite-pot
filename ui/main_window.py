# ui/main_window.py
import sys
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget, QProgressBar, QFrame, QGraphicsOpacityEffect, QPushButton, QScrollArea, QTextEdit
from PySide6.QtGui import QTextCursor
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from ui.theme import ThemeManager
from ui.audio import UIAudio
from ui.widgets.notifications import NotificationManager
from ui.dialogs.custom_dialogs import ConfirmDialog, TextInputDialog, ReceiptDialog, ChoicesDialog, PlaceUpgradesDialog, MoneyMgmtDialog, RelationshipMgmtDialog, OptionsDialog

from ui.screens.main_menu import MainMenuScreen
from ui.screens.gameplay import GameplayScreen
from ui.screens.business_menu import BusinessMenuScreen
from ui.screens.personal_life_menu import PersonalLifeScreen
from ui.screens.tavern_menu import TavernMenuScreen
from ui.screens.game_over import GameOverScreen

class MainWindow(QMainWindow):
    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.state = state
        
        self.setWindowTitle("Infinite Pot — V1 Desktop Prototype")
        self.resize(1000, 700)
        self.setStyleSheet(ThemeManager.get_style_sheet())
        
        self.days_survived_competitor = 0
        self.victory = False
        self.game_over = False
        self.evening_phase = False
        
        # Central widget and layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Real-time Simulation Clock variables
        self.is_working = False
        self.is_paused = False
        self.active_hours_passed = 0
        self.target_work_hours = 8
        self.day_clock_timer = QTimer(self)
        self.day_clock_timer.timeout.connect(self.on_game_clock_tick)
        self.world_speed = 1.0
        
        # Places cycle state for bottom-right navigation
        self.current_place = "Restaurant"
        
        # 1. Top HUD Bar
        self.init_hud_bar()
        self.hud_bar.setVisible(False)  # Hidden on Main Menu
        self.main_layout.addWidget(self.hud_bar)
        
        # Content horizontal layout (Stacked screen on left, Sidebar on right)
        self.content_widget = QWidget(self)
        self.content_layout = QHBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        # Left Area Container (Viewport + Bottom Activity Log)
        self.left_area_widget = QWidget(self)
        left_layout = QVBoxLayout(self.left_area_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        
        # 2. Stacked Screen Layout
        self.stacked_widget = QStackedWidget(self)
        left_layout.addWidget(self.stacked_widget, stretch=1)
        
        # Bottom Place Activity & Dialogue Log Box
        self.place_log_frame = QFrame(self)
        self.place_log_frame.setObjectName("place-log-frame")
        self.place_log_frame.setFixedHeight(120)
        self.place_log_frame.setStyleSheet(f"""
            QFrame#place-log-frame {{
                background-color: rgba(245, 235, 224, 0.94);
                border-top: 3px solid {ThemeManager.DARK_BROWN};
                padding: 4px 8px;
            }}
        """)
        place_log_layout = QVBoxLayout(self.place_log_frame)
        place_log_layout.setContentsMargins(6, 4, 6, 4)
        place_log_layout.setSpacing(2)
        
        self.log_hdr_lbl = QLabel("<b>📜 Place Activity & Dialogue Log</b>", self)
        self.log_hdr_lbl.setStyleSheet(f"font-size: 13px; color: {ThemeManager.DARK_BROWN};")
        place_log_layout.addWidget(self.log_hdr_lbl)
        
        self.log_text_edit = QTextEdit(self)
        self.log_text_edit.setReadOnly(True)
        self.log_text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.log_text_edit.setStyleSheet(f"background: transparent; border: none; font-size: 13px; font-family: VT323, monospace; color: {ThemeManager.DARK_BROWN};")
        place_log_layout.addWidget(self.log_text_edit)
        
        left_layout.addWidget(self.place_log_frame)
        self.place_log_frame.setVisible(False)
        
        self.content_layout.addWidget(self.left_area_widget, stretch=3)
        
        # 3. Sidebar Widget
        self.sidebar_widget = self.init_sidebar_widget()
        self.content_layout.addWidget(self.sidebar_widget, stretch=1)
        
        self.main_layout.addWidget(self.content_widget)
        
        # Instantiate Screens
        self.main_menu_screen = MainMenuScreen(self)
        self.gameplay_screen = GameplayScreen(self.state, self)
        self.business_screen = BusinessMenuScreen(self.state, self)
        self.personal_life_screen = PersonalLifeScreen(self.state, self)
        self.tavern_screen = TavernMenuScreen(self.state, self)
        self.game_over_screen = GameOverScreen(self)
        
        # Add to stack
        self.stacked_widget.addWidget(self.main_menu_screen)        # Index 0
        self.stacked_widget.addWidget(self.gameplay_screen)        # Index 1
        self.stacked_widget.addWidget(self.business_screen)        # Index 2
        self.stacked_widget.addWidget(self.personal_life_screen)    # Index 3
        self.stacked_widget.addWidget(self.tavern_screen)         # Index 4
        self.stacked_widget.addWidget(self.game_over_screen)       # Index 5
        
        # 3. Notification overlay
        self.notification_manager = NotificationManager(self.central_widget)
        
        # Connect Signals
        self.main_menu_screen.start_game.connect(self.on_start_game)
        self.main_menu_screen.quit_game.connect(self.close)
        
        self.business_screen.go_back.connect(self.show_gameplay)
        self.business_screen.state_changed.connect(self.update_hud)
        
        self.personal_life_screen.go_back.connect(self.show_gameplay)
        self.personal_life_screen.state_changed.connect(self.update_hud)
        self.personal_life_screen.sleep_clicked.connect(self.on_sleep_and_end_day)
        
        self.tavern_screen.go_back.connect(self.show_gameplay)
        self.tavern_screen.state_changed.connect(self.update_hud)
        
        self.game_over_screen.restart_game.connect(self.on_restart_game)
        self.game_over_screen.quit_game.connect(self.close)
        
        # Start Theme Music
        UIAudio.play_music("home")
        
        # Show Main Menu
        self.stacked_widget.setCurrentIndex(0)

    def init_hud_bar(self):
        self.hud_bar = QFrame(self)
        self.hud_bar.setObjectName("hud-bar")
        
        hud_layout = QHBoxLayout(self.hud_bar)
        hud_layout.setContentsMargins(10, 4, 10, 4)
        hud_layout.setSpacing(10)
        
        # 1. Shop Name
        self.shop_name_lbl = QLabel(self)
        self.shop_name_lbl.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {ThemeManager.DARK_BROWN};")
        hud_layout.addWidget(self.shop_name_lbl)
        
        # 2. Cash
        self.cash_lbl = QLabel(self)
        self.cash_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #3A5F43;")
        hud_layout.addWidget(self.cash_lbl)
        
        # 3. Energy
        energy_widget = QWidget(self)
        energy_layout = QHBoxLayout(energy_widget)
        energy_layout.setContentsMargins(0, 0, 0, 0)
        energy_layout.setSpacing(5)
        e_lbl = QLabel("Energy:", self)
        e_lbl.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {ThemeManager.DARK_BROWN};")
        self.energy_bar = QProgressBar(self)
        self.energy_bar.setRange(0, 100)
        self.energy_bar.setMaximumWidth(80)
        self.energy_bar.setStyleSheet("QProgressBar::chunk { background-color: #E25E3E; }")
        energy_layout.addWidget(e_lbl)
        energy_layout.addWidget(self.energy_bar)
        hud_layout.addWidget(energy_widget)
        
        # 4. Reputation
        rep_widget = QWidget(self)
        rep_layout = QHBoxLayout(rep_widget)
        rep_layout.setContentsMargins(0, 0, 0, 0)
        rep_layout.setSpacing(5)
        r_lbl = QLabel("Rep:", self)
        r_lbl.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {ThemeManager.DARK_BROWN};")
        self.rep_bar = QProgressBar(self)
        self.rep_bar.setRange(0, 100)
        self.rep_bar.setMaximumWidth(80)
        self.rep_bar.setStyleSheet("QProgressBar::chunk { background-color: #82A0D8; }")
        rep_layout.addWidget(r_lbl)
        rep_layout.addWidget(self.rep_bar)
        hud_layout.addWidget(rep_widget)

        # 5. Calendar / Phase (Now moved between Reputation and Partner!)
        self.day_lbl = QLabel(self)
        self.day_lbl.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {ThemeManager.DARK_BROWN};")
        hud_layout.addWidget(self.day_lbl)
        
        # 6. Partner
        self.partner_lbl = QLabel(self)
        self.partner_lbl.setStyleSheet(f"font-size: 16px; color: {ThemeManager.DARK_BROWN}; font-weight: bold;")
        hud_layout.addWidget(self.partner_lbl)
        
        # Stretch columns
        hud_layout.setStretch(0, 2)
        hud_layout.setStretch(1, 2)
        hud_layout.setStretch(2, 2)
        hud_layout.setStretch(3, 2)
        hud_layout.setStretch(4, 3)
        hud_layout.setStretch(5, 2)

    def animate_switch(self, target_index: int):
        self.stacked_opacity = QGraphicsOpacityEffect(self.stacked_widget)
        self.stacked_widget.setGraphicsEffect(self.stacked_opacity)
            
        self.fade_out = QPropertyAnimation(self.stacked_opacity, b"opacity")
        self.fade_out.setDuration(120)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.setEasingCurve(QEasingCurve.OutQuad)
        
        # When fade out completes, change screen and fade back in
        def on_fade_out_done():
            self.stacked_widget.setCurrentIndex(target_index)
            self.fade_in = QPropertyAnimation(self.stacked_opacity, b"opacity")
            self.fade_in.setDuration(120)
            self.fade_in.setStartValue(0.0)
            self.fade_in.setEndValue(1.0)
            self.fade_in.setEasingCurve(QEasingCurve.InQuad)
            
            # Remove graphics effect on fade in complete to ensure click interactions work perfectly!
            def on_fade_in_done():
                self.stacked_widget.setGraphicsEffect(None)
                
            self.fade_in.finished.connect(on_fade_in_done)
            self.fade_in.start()
            
        # Disconnect any previously bound signals to avoid duplicate executions
        try:
            self.fade_out.finished.disconnect()
        except RuntimeError:
            pass
            
        self.fade_out.finished.connect(on_fade_out_done)
        self.fade_out.start()

    def show_main_menu(self):
        UIAudio.play_music("home")
        self.hud_bar.setVisible(False)
        self.sidebar_widget.setVisible(False)
        self.place_log_frame.setVisible(False)
        self.animate_switch(0)

    def show_gameplay(self):
        self.hud_bar.setVisible(True)
        self.sidebar_widget.setVisible(True)
        self.place_log_frame.setVisible(True)
        self.update_place_screen()
        self.update_hud()

    def show_business(self):
        self.open_place_upgrades()

    def show_personal_life(self):
        self.current_place = "Home"
        self.show_gameplay()

    def show_tavern(self):
        self.current_place = "Bar"
        self.show_gameplay()

    def show_game_over(self):
        UIAudio.play_music("home")
        self.hud_bar.setVisible(False)
        self.sidebar_widget.setVisible(False)
        self.place_log_frame.setVisible(False)
        p = self.state.player
        r = self.state.restaurant
        rom = self.state.romance
        self.game_over_screen.set_results(self.victory, rom.partner_name, r.reputation, p.cash)
        self.animate_switch(5)

    def on_start_game(self):
        # Prompt for shop name
        dlg = TextInputDialog("Welcome to Infinite Pot!", "What will be the name of your restaurant?", "Mystic Diner", self)
        if dlg.exec():
            name = dlg.get_text()
            self.state.restaurant.custom_name = name
            self.show_gameplay()
            self.notification_manager.add_notification("Journey started! Welcome to Level 0.", "success")

    def on_restart_game(self):
        # Reinstate state from config
        from engine.state import GameState
        self.state = GameState()
        self.days_survived_competitor = 0
        self.victory = False
        self.game_over = False
        self.evening_phase = False
        
        # Recreate screens
        self.gameplay_screen = GameplayScreen(self.state, self)
        self.business_screen = BusinessMenuScreen(self.state, self)
        self.personal_life_screen = PersonalLifeScreen(self.state, self)
        self.tavern_screen = TavernMenuScreen(self.state, self)
        
        self.business_screen.go_back.connect(self.show_gameplay)
        self.business_screen.state_changed.connect(self.update_hud)
        self.personal_life_screen.go_back.connect(self.show_gameplay)
        self.personal_life_screen.state_changed.connect(self.update_hud)
        self.personal_life_screen.sleep_clicked.connect(self.on_sleep_and_end_day)
        self.tavern_screen.go_back.connect(self.show_personal_life)
        self.tavern_screen.state_changed.connect(self.update_hud)
        
        # Re-add to stacked layout
        self.stacked_widget.removeWidget(self.stacked_widget.widget(1))
        self.stacked_widget.removeWidget(self.stacked_widget.widget(1))
        self.stacked_widget.removeWidget(self.stacked_widget.widget(1))
        self.stacked_widget.removeWidget(self.stacked_widget.widget(1))
        
        self.stacked_widget.insertWidget(1, self.gameplay_screen)
        self.stacked_widget.insertWidget(2, self.business_screen)
        self.stacked_widget.insertWidget(3, self.personal_life_screen)
        self.stacked_widget.insertWidget(4, self.tavern_screen)
        
        self.show_main_menu()

    def init_sidebar_widget(self):
        self.sidebar_widget = QFrame(self)
        self.sidebar_widget.setObjectName("sidebar-frame")
        self.sidebar_widget.setStyleSheet(f"""
            QFrame#sidebar-frame {{
                background-color: {ThemeManager.CREAM};
                border-left: 4px solid {ThemeManager.DARK_BROWN};
                padding: 10px;
            }}
            QPushButton {{
                font-family: VT323, monospace;
                font-size: 16px;
                background-color: {ThemeManager.CREAM};
                border: 2px solid {ThemeManager.DARK_BROWN};
                padding: 8px;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: #E25E3E;
                color: white;
            }}
        """)
        
    def init_sidebar_widget(self):
        self.sidebar_widget = QFrame(self)
        self.sidebar_widget.setObjectName("sidebar-frame")
        self.sidebar_widget.setMinimumWidth(320)
        self.sidebar_widget.setMaximumWidth(400)
        self.sidebar_widget.setStyleSheet(f"""
            QFrame#sidebar-frame {{
                background-color: {ThemeManager.CREAM};
                border-left: 2px solid {ThemeManager.DARK_BROWN};
                padding: 6px;
            }}
            QPushButton {{
                font-family: VT323, monospace;
                font-size: 16px;
                background-color: {ThemeManager.CREAM};
                border: 1.5px solid {ThemeManager.DARK_BROWN};
                padding: 6px 10px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: #E25E3E;
                color: white;
            }}
        """)
        
        layout = QVBoxLayout(self.sidebar_widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)
        
        # Stacked widget for contextual sidebar pages
        self.sidebar_stacked = QStackedWidget(self)
        
        # ==========================================
        # PAGE 0: Restaurant Sidebar
        # ==========================================
        rest_page = QWidget(self)
        rest_lay = QVBoxLayout(rest_page)
        rest_lay.setContentsMargins(0, 0, 0, 0)
        rest_lay.setSpacing(6)
        
        self.sim_btn = QPushButton("Start Day", self)
        self.sim_btn.setObjectName("sim-btn")
        self.sim_btn.setStyleSheet("font-weight: bold; background-color: #8ADAB2;")
        self.sim_btn.clicked.connect(self.on_sim_btn_clicked)
        rest_lay.addWidget(self.sim_btn)
        
        self.sidebar_status_lbl = QLabel(self)
        self.sidebar_status_lbl.setWordWrap(True)
        self.sidebar_status_lbl.setStyleSheet(f"font-size: 13px; line-height: 1.3; border: 1.5px solid {ThemeManager.DARK_BROWN}; padding: 6px; background-color: rgba(245, 235, 224, 0.6); color: {ThemeManager.DARK_BROWN};")
        rest_lay.addWidget(self.sidebar_status_lbl)
        
        self.stop_btn = QPushButton("Stop Work", self)
        self.stop_btn.setObjectName("stop-btn")
        self.stop_btn.setStyleSheet("font-weight: bold; background-color: #F8C4B4;")
        self.stop_btn.clicked.connect(self.on_stop_work_clicked)
        self.stop_btn.setVisible(False)
        rest_lay.addWidget(self.stop_btn)
        
        self.upgrades_btn = QPushButton("Place Mgmt", self)
        self.upgrades_btn.clicked.connect(self.open_place_upgrades)
        rest_lay.addWidget(self.upgrades_btn)
        
        self.money_btn = QPushButton("Money Mgmt", self)
        self.money_btn.clicked.connect(self.open_money_mgmt)
        rest_lay.addWidget(self.money_btn)
        
        self.rel_btn = QPushButton("Relationship Mgmt", self)
        self.rel_btn.clicked.connect(self.open_relationship_mgmt)
        rest_lay.addWidget(self.rel_btn)
        
        rest_lay.addStretch()
        self.sidebar_stacked.addWidget(rest_page) # Index 0
        
        # ==========================================
        # PAGE 1: Bar (Tavern) Sidebar
        # ==========================================
        bar_page = QWidget(self)
        bar_lay = QVBoxLayout(bar_page)
        bar_lay.setContentsMargins(0, 0, 0, 0)
        bar_lay.setSpacing(4)
        
        soc_hdr = QLabel("<b>🌹 Socialize</b>", self)
        soc_hdr.setStyleSheet(f"font-size: 15px; color: {ThemeManager.DARK_BROWN};")
        bar_lay.addWidget(soc_hdr)
        
        self.bar_girls_scroll = QScrollArea(self)
        self.bar_girls_scroll.setWidgetResizable(True)
        self.bar_girls_scroll.setMaximumHeight(180)
        self.bar_girls_content = QWidget()
        self.bar_girls_layout = QVBoxLayout(self.bar_girls_content)
        self.bar_girls_layout.setContentsMargins(0, 0, 0, 0)
        self.bar_girls_layout.setSpacing(3)
        self.bar_girls_scroll.setWidget(self.bar_girls_content)
        bar_lay.addWidget(self.bar_girls_scroll)
        
        app_hdr = QLabel("<b>👥 Job Applicants</b>", self)
        app_hdr.setStyleSheet(f"font-size: 15px; color: {ThemeManager.DARK_BROWN};")
        bar_lay.addWidget(app_hdr)
        
        self.bar_cand_scroll = QScrollArea(self)
        self.bar_cand_scroll.setWidgetResizable(True)
        self.bar_cand_scroll.setMaximumHeight(180)
        self.bar_cand_content = QWidget()
        self.bar_cand_layout = QVBoxLayout(self.bar_cand_content)
        self.bar_cand_layout.setContentsMargins(0, 0, 0, 0)
        self.bar_cand_layout.setSpacing(3)
        self.bar_cand_scroll.setWidget(self.bar_cand_content)
        bar_lay.addWidget(self.bar_cand_scroll)
        
        bar_lay.addStretch()
        self.sidebar_stacked.addWidget(bar_page) # Index 1
        
        # ==========================================
        # PAGE 2: Home (Cottage) Sidebar
        # ==========================================
        home_page = QWidget(self)
        home_lay = QVBoxLayout(home_page)
        home_lay.setContentsMargins(0, 0, 0, 0)
        home_lay.setSpacing(4)
        
        rom_hdr = QLabel("<b>🌹 Dating & Romance</b>", self)
        rom_hdr.setStyleSheet(f"font-size: 15px; color: {ThemeManager.DARK_BROWN};")
        home_lay.addWidget(rom_hdr)
        
        self.home_rom_lbl = QLabel(self)
        self.home_rom_lbl.setWordWrap(True)
        self.home_rom_lbl.setStyleSheet("font-size: 13px; font-weight: bold;")
        home_lay.addWidget(self.home_rom_lbl)
        
        self.home_rom_progress = QProgressBar(self)
        self.home_rom_progress.setRange(0, 100)
        self.home_rom_progress.setStyleSheet("QProgressBar::chunk { background-color: #E25E3E; }")
        home_lay.addWidget(self.home_rom_progress)
        
        self.home_date_btn = QPushButton("💖 Go on a Date (-$100 | 25 E)", self)
        self.home_date_btn.clicked.connect(self.on_go_date)
        home_lay.addWidget(self.home_date_btn)
        
        self.home_ring_btn = QPushButton("💍 Buy Ring (-$2500)", self)
        self.home_ring_btn.clicked.connect(self.on_buy_ring)
        home_lay.addWidget(self.home_ring_btn)
        
        self.home_propose_btn = QPushButton("Propose Marriage", self)
        self.home_propose_btn.clicked.connect(self.on_propose)
        home_lay.addWidget(self.home_propose_btn)
        
        self.home_break_btn = QPushButton("Break Up", self)
        self.home_break_btn.setObjectName("quit-btn")
        self.home_break_btn.clicked.connect(self.on_break_up)
        home_lay.addWidget(self.home_break_btn)
        
        furn_hdr = QLabel("<b>🏡 Home Furnishings</b>", self)
        furn_hdr.setStyleSheet(f"font-size: 15px; color: {ThemeManager.DARK_BROWN};")
        home_lay.addWidget(furn_hdr)
        
        self.home_upgrades_scroll = QScrollArea(self)
        self.home_upgrades_scroll.setWidgetResizable(True)
        self.home_upgrades_scroll.setMaximumHeight(140)
        self.home_upgrades_content = QWidget()
        self.home_upgrades_layout = QVBoxLayout(self.home_upgrades_content)
        self.home_upgrades_layout.setContentsMargins(0, 0, 0, 0)
        self.home_upgrades_layout.setSpacing(3)
        self.home_upgrades_scroll.setWidget(self.home_upgrades_content)
        home_lay.addWidget(self.home_upgrades_scroll)
        
        self.home_sleep_btn = QPushButton("🛌 Sleep & End Day", self)
        self.home_sleep_btn.setStyleSheet("font-weight: bold; background-color: #82A0D8;")
        self.home_sleep_btn.clicked.connect(self.on_sleep_and_end_day)
        home_lay.addWidget(self.home_sleep_btn)
        
        home_lay.addStretch()
        self.sidebar_stacked.addWidget(home_page) # Index 2
        
        layout.addWidget(self.sidebar_stacked)
        
        # Options Button (Common)
        self.options_btn = QPushButton("Options", self)
        self.options_btn.clicked.connect(self.open_options)
        layout.addWidget(self.options_btn)
        
        # Bottom Navigation Controls: < place name >
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(4)
        
        self.left_nav_btn = QPushButton("<", self)
        self.left_nav_btn.setMaximumWidth(35)
        self.left_nav_btn.clicked.connect(self.on_nav_left)
        nav_layout.addWidget(self.left_nav_btn)
        
        self.place_label = QLabel("Restaurant", self)
        self.place_label.setAlignment(Qt.AlignCenter)
        self.place_label.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {ThemeManager.DARK_BROWN};")
        nav_layout.addWidget(self.place_label)
        
        self.right_nav_btn = QPushButton(">", self)
        self.right_nav_btn.setMaximumWidth(35)
        self.right_nav_btn.clicked.connect(self.on_nav_right)
        nav_layout.addWidget(self.right_nav_btn)
        
        layout.addLayout(nav_layout)
        
        self.sidebar_widget.setVisible(False)
        return self.sidebar_widget

    def add_log(self, text: str, speaker: str = None):
        """Append entry to place activity log box and scroll to bottom."""
        if speaker:
            entry = f"<b><font color='#E25E3E'>{speaker}:</font></b> \"{text}\""
        else:
            entry = f"<font color='#5B3923'>• {text}</font>"
        self.log_text_edit.append(entry)
        self.log_text_edit.moveCursor(QTextCursor.End)

    def on_sim_btn_clicked(self):
        UIAudio.play_click()
        if self.evening_phase:
            self.on_sleep_and_end_day()
            return
            
        if not self.is_working:
            # Start Day
            self.active_hours_passed = 0
            self.target_work_hours = 12 # maximum overtime cutoff
            self.is_working = True
            self.is_paused = False
            
            self.state.finance.start_new_day()
            
            # Button becomes "Pause"
            self.sim_btn.setText("Pause")
            self.sim_btn.setStyleSheet("font-weight: bold; background-color: #E25E3E; color: white;")
            self.stop_btn.setVisible(True)
            
            # Start ticking clock based on world speed
            interval_ms = int(10000 / self.world_speed)
            self.day_clock_timer.start(interval_ms)
            self.notification_manager.add_notification("Workday started! Timer is progressing.", "info")
            self.update_hud()
        else:
            # Toggle Pause/Continue
            if self.is_paused:
                self.is_paused = False
                self.sim_btn.setText("Pause")
                self.sim_btn.setStyleSheet("font-weight: bold; background-color: #E25E3E; color: white;")
                interval_ms = int(10000 / self.world_speed)
                self.day_clock_timer.start(interval_ms)
                self.notification_manager.add_notification("Workday resumed.", "info")
            else:
                self.is_paused = True
                self.sim_btn.setText("Continue")
                self.sim_btn.setStyleSheet("font-weight: bold; background-color: #8ADAB2;")
                self.day_clock_timer.stop()
                self.notification_manager.add_notification("Workday paused.", "info")
            self.update_hud()

    def on_stop_work_clicked(self):
        UIAudio.play_click()
        self.day_clock_timer.stop()
        self.is_working = False
        self.is_paused = False
        self.evening_phase = True
        self.stop_btn.setVisible(False)
        UIAudio.play_success()
        
        # Present Daily Report Ledger popup
        dlg = ReceiptDialog(self.state.finance.get_daily_report(), self)
        dlg.exec()
        
        # Main button becomes Sleep & End Day
        self.sim_btn.setText("Sleep & End Day")
        self.sim_btn.setStyleSheet("font-weight: bold; background-color: #82A0D8;")
        self.notification_manager.add_notification(f"Workday stopped after {self.active_hours_passed} hours. Evening phase started.", "info")
        self.update_hud()

    def on_game_clock_tick(self):
        if not self.is_working or self.is_paused:
            return
            
        if self.state.player.energy <= 0.0:
            self.day_clock_timer.stop()
            self.is_working = False
            self.stop_btn.setVisible(False)
            UIAudio.play_notify()
            self.notification_manager.add_notification("Exhausted! You passed out and your staff closed the shop.", "warning")
            self.on_sleep_and_end_day()
            return
            
        self.active_hours_passed += 1
        
        level_mults = {0: 1.5, 1: 1.3, 2: 1.1, 3: 0.9, 4: 0.7}
        level_mult = level_mults.get(self.state.restaurant.level, 1.0)
        
        active_employees = self.state.employees.get_active_employees()
        staff_count = len(active_employees)
        staff_mults = {0: 1.0, 1: 0.8, 2: 0.65, 3: 0.5}
        staff_mult = staff_mults.get(staff_count, 0.5 if staff_count > 3 else 1.0)
        
        hourly_drain = self.state.player.work_energy_cost_per_hour * level_mult * staff_mult
        self.state.player.adjust_energy(-hourly_drain)
        
        res = self.state.simulate_one_hour(self.active_hours_passed)
        if res["served"] > 0:
            UIAudio.play_coin()
            self.notification_manager.add_notification(
                f"Hour {self.active_hours_passed}: Served {res['served']} meals! Earned ${res['total_income']:.2f}", "success"
            )
            
        # Max overtime cutoff reached
        if self.active_hours_passed >= self.target_work_hours:
            self.day_clock_timer.stop()
            self.is_working = False
            self.evening_phase = True
            self.stop_btn.setVisible(False)
            UIAudio.play_success()
            
            ConfirmDialog("Shift Ended", "Maximum shift hours reached! Closing shop.", self).exec()
            dlg = ReceiptDialog(self.state.finance.get_daily_report(), self)
            dlg.exec()
            
            self.sim_btn.setText("Sleep & End Day")
            self.sim_btn.setStyleSheet("font-weight: bold; background-color: #82A0D8;")
            self.update_hud()
            return
            
        self.update_hud()
        
    def open_place_upgrades(self):
        PlaceUpgradesDialog(self.state, self).exec()
        
    def open_money_mgmt(self):
        MoneyMgmtDialog(self.state, self).exec()
        
    def open_relationship_mgmt(self):
        RelationshipMgmtDialog(self.state, self).exec()
        
    def open_options(self):
        OptionsDialog(self).exec()

    def get_unlocked_places(self):
        places = ["Restaurant"]
        if self.state.restaurant.level >= 3:
            places.append("Bar")
        if self.state.house.purchased:
            places.append("Home")
        return places

    def update_place_screen(self):
        unlocked = self.get_unlocked_places()
        if self.current_place not in unlocked:
            self.current_place = "Restaurant"
            
        self.place_label.setText(self.current_place)
        
        if self.current_place == "Home":
            UIAudio.play_music("romance")
            self.stacked_widget.setCurrentIndex(3)
            self.sidebar_stacked.setCurrentIndex(2)
            self.update_home_sidebar()
        elif self.current_place == "Restaurant":
            UIAudio.play_music("hotel")
            self.stacked_widget.setCurrentIndex(1)
            self.sidebar_stacked.setCurrentIndex(0)
            self.gameplay_screen.update_ui(self.evening_phase)
        elif self.current_place == "Bar":
            UIAudio.play_music("bar")
            self.stacked_widget.setCurrentIndex(4)
            self.sidebar_stacked.setCurrentIndex(1)
            self.update_bar_sidebar()

    def update_bar_sidebar(self):
        # 1. Update Girls list
        while self.bar_girls_layout.count():
            item = self.bar_girls_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        rom = self.state.romance
        for girl in rom.characters:
            f = QFrame(self.bar_girls_content)
            f.setStyleSheet("border: 1px solid #5B3923; padding: 2px; border-radius: 4px; background-color: rgba(255, 255, 255, 0.4);")
            fl = QVBoxLayout(f)
            fl.setContentsMargins(3, 3, 3, 3)
            fl.setSpacing(2)
            
            lbl = QLabel(f"<b>{girl.name}</b> ({girl.archetype})<br/><font size='1'>Romance: {girl.romance_level:.0f}/100</font>", self)
            lbl.setStyleSheet("font-size: 11px; border: none; background: transparent;")
            fl.addWidget(lbl)
            
            btn = QPushButton(f"Socialize with {girl.name}", self)
            btn.setStyleSheet("font-size: 11px; padding: 2px 4px;")
            btn.clicked.connect(lambda chk=False, g=girl: self.interact_girl(g))
            fl.addWidget(btn)
            
            self.bar_girls_layout.addWidget(f)
            
        # 2. Update Applicants list
        while self.bar_cand_layout.count():
            item = self.bar_cand_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        emp = self.state.employees
        p = self.state.player
        cand_list = getattr(emp, 'available_candidates', emp.candidates)
        for cand in cand_list:
            f = QFrame(self.bar_cand_content)
            f.setStyleSheet("border: 1px solid #5B3923; padding: 2px; border-radius: 4px; background-color: rgba(255, 255, 255, 0.4);")
            fl = QVBoxLayout(f)
            fl.setContentsMargins(3, 3, 3, 3)
            fl.setSpacing(2)
            
            lbl = QLabel(f"<b>{cand.name}</b><br/><font size='1'>Skill: {cand.skill:.1f} | ${cand.daily_salary:.0f}/day</font>", self)
            lbl.setStyleSheet("font-size: 11px; border: none; background: transparent;")
            fl.addWidget(lbl)
            
            btn = QPushButton(f"Hire (-${cand.daily_salary:.0f})", self)
            btn.setStyleSheet("font-size: 11px; padding: 2px 4px;")
            btn.clicked.connect(lambda chk=False, c=cand: self.hire_candidate(c))
            btn.setEnabled(p.cash >= cand.daily_salary)
            fl.addWidget(btn)
            
            self.bar_cand_layout.addWidget(f)

    def update_home_sidebar(self):
        p = self.state.player
        rom = self.state.romance
        h = self.state.house
        
        partner = rom.partner
        if not partner:
            self.home_rom_lbl.setText("Status: <b>Single</b>")
            self.home_rom_progress.setValue(0)
            self.home_date_btn.setEnabled(False)
            self.home_ring_btn.setEnabled(False)
            self.home_propose_btn.setEnabled(False)
            self.home_break_btn.setEnabled(False)
        else:
            self.home_rom_lbl.setText(f"Partner: <b>{partner.name}</b> ({partner.archetype})")
            self.home_rom_progress.setValue(int(rom.romance_level))
            self.home_date_btn.setEnabled(p.cash >= 100.0 and p.energy >= 25)
            self.home_ring_btn.setEnabled(not rom.has_ring and p.cash >= 2500.0)
            self.home_propose_btn.setEnabled(rom.has_ring and not rom.is_co_owner and rom.romance_level >= 75)
            self.home_break_btn.setEnabled(True)
            
        # Update house upgrades list
        while self.home_upgrades_layout.count():
            item = self.home_upgrades_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        for up in h.available_upgrades:
            f = QFrame(self.home_upgrades_content)
            f.setStyleSheet("border: 1px solid #5B3923; padding: 2px; border-radius: 4px; background-color: rgba(255, 255, 255, 0.4);")
            fl = QVBoxLayout(f)
            fl.setContentsMargins(3, 3, 3, 3)
            fl.setSpacing(2)
            
            lbl = QLabel(f"<b>{up.name}</b> (-${up.cost:.0f})<br/><font size='1'>{up.description}</font>", self)
            lbl.setStyleSheet("font-size: 11px; border: none; background: transparent;")
            fl.addWidget(lbl)
            
            if up.id in h.upgrades:
                owned_lbl = QLabel("<font color='#3A5F43'><b>Purchased</b></font>", self)
                owned_lbl.setStyleSheet("font-size: 11px; border: none; background: transparent;")
                fl.addWidget(owned_lbl)
            else:
                btn = QPushButton(f"Buy (-${up.cost:.0f})", self)
                btn.setStyleSheet("font-size: 11px; padding: 2px 4px;")
                btn.clicked.connect(lambda chk=False, u=up: self.buy_house_upgrade(u))
                btn.setEnabled(p.cash >= up.cost)
                fl.addWidget(btn)
                
            self.home_upgrades_layout.addWidget(f)

    def interact_girl(self, girl):
        UIAudio.play_click()
        rom = self.state.romance
        p = self.state.player
        
        opts = [
            f"Talk to her (10 Energy) [Energy: {p.energy:.0f}]",
            f"Buy her a drink ($25.00, 10 Energy) [Cash: ${p.cash:.2f}]"
        ]
        if girl.romance_level >= 25 and rom.partner != girl:
            opts.append("Ask out on a Date")
        if rom.has_ring and rom.partner == girl and not rom.is_co_owner:
            opts.append("Propose Marriage & Co-Ownership")
            
        dlg = ChoicesDialog(f"Socialize with {girl.name}", f"{girl.name} ({girl.archetype}) is relaxing at the bar.\n{girl.description}\n\nWhat would you like to do?", opts, self)
        if dlg.exec() and dlg.chosen_index != -1:
            idx = dlg.chosen_index
            if idx == 0:
                if p.energy < 10:
                    ConfirmDialog("Cannot Talk", "You need at least 10 energy to talk!", self).exec()
                    return
                p.adjust_energy(-10)
                msg, gain = girl.interact_talk()
                girl.romance_level = min(100.0, girl.romance_level + gain)
                rom.apply_jealousy(girl.name, self.state.day_name)
                UIAudio.play_dialogue()
                self.add_log(msg, speaker=girl.name)
                ConfirmDialog(f"Talk with {girl.name}", f"{msg}\nRomance level is now {girl.romance_level:.1f}/100.", self).exec()
            elif idx == 1:
                if p.cash < 25.0 or p.energy < 10:
                    ConfirmDialog("Cannot Buy Drink", "You need $25.00 and 10 energy to buy a drink!", self).exec()
                    return
                p.adjust_cash(-25.0)
                p.adjust_energy(-10)
                self.state.finance.record_transaction("Misc", 25.0, f"Bought drink for {girl.name}")
                msg, gain = girl.interact_drink(25.0)
                girl.romance_level = min(100.0, girl.romance_level + gain)
                rom.apply_jealousy(girl.name, self.state.day_name)
                UIAudio.play_coin()
                self.add_log(msg, speaker=girl.name)
                ConfirmDialog("Bought Drink", f"{msg}\nRomance level is now {girl.romance_level:.1f}/100.", self).exec()
            elif idx == 2 and "Ask out" in opts[idx]:
                success, msg = rom.propose_relationship(girl.name)
                if success:
                    UIAudio.play_success()
                    ConfirmDialog("Relationship Started", msg, self).exec()
                else:
                    ConfirmDialog("Cannot Date", msg, self).exec()
            elif "Propose" in opts[idx]:
                self.on_propose()
                
            self.update_hud()

    def hire_candidate(self, cand):
        UIAudio.play_click()
        emp = self.state.employees
        p = self.state.player
        max_emp = self.state.restaurant.max_employees
        if p.cash < cand.daily_salary:
            ConfirmDialog("Cannot Hire", f"You need at least ${cand.daily_salary:.2f} to hire {cand.name}!", self).exec()
            return
            
        confirm = ConfirmDialog("Hire Employee", f"Hire {cand.name} (Skill: {cand.skill:.1f}) for ${cand.daily_salary:.2f}/day?", self)
        if confirm.exec():
            success, msg = emp.hire_employee(cand.name, max_emp)
            if success:
                UIAudio.play_success()
                self.notification_manager.add_notification(msg, "success")
            else:
                ConfirmDialog("Hire Failed", msg, self).exec()
            self.update_hud()

    def on_go_date(self):
        p = self.state.player
        rom = self.state.romance
        h = self.state.house
        mult = 1.0 + h.get_romance_progress_bonus()
        success, msg, cash_spent, energy_spent = rom.go_on_date(p.cash, p.energy, progress_multiplier=mult)
        if success:
            p.adjust_cash(-cash_spent)
            p.adjust_energy(-energy_spent)
            self.state.finance.record_transaction("Date", cash_spent, f"Went on date with {rom.partner_name}")
            UIAudio.play_success()
            ConfirmDialog("Date Night", msg, self).exec()
            self.update_hud()
        else:
            ConfirmDialog("Cannot Date", msg, self).exec()

    def on_buy_ring(self):
        p = self.state.player
        rom = self.state.romance
        if rom.has_ring:
            ConfirmDialog("Already Purchased", "You already own a Diamond Engagement Ring!", self).exec()
            return
        if p.cash < 2500.0:
            ConfirmDialog("Insufficient Funds", "The Diamond Engagement Ring costs $2500.00!", self).exec()
            return
        p.adjust_cash(-2500.0)
        rom.has_ring = True
        self.state.finance.record_transaction("Ring", 2500.0, "Purchased Diamond Engagement Ring")
        UIAudio.play_coin()
        ConfirmDialog("Diamond Ring", "Purchased a stunning Diamond Engagement Ring for $2500.00!", self).exec()
        self.update_hud()

    def on_propose(self):
        p = self.state.player
        rom = self.state.romance
        h = self.state.house
        success, msg = rom.ask_to_co_own(h.purchased)
        if success:
            UIAudio.play_success()
            ConfirmDialog("Proposal Accepted!", msg, self).exec()
            self.update_hud()
        else:
            ConfirmDialog("Proposal Declined", msg, self).exec()

    def on_break_up(self):
        rom = self.state.romance
        confirm = ConfirmDialog("Break Up", f"Are you sure you want to break up with {rom.partner_name}?", self)
        if confirm.exec():
            success, msg = rom.break_up()
            UIAudio.play_notify()
            ConfirmDialog("Relationship Ended", msg, self).exec()
            self.update_hud()

    def buy_house_upgrade(self, upgrade):
        p = self.state.player
        h = self.state.house
        success, msg, cost = h.buy_upgrade(upgrade.id, p.cash)
        if success:
            p.adjust_cash(-cost)
            self.state.finance.record_transaction("Home", cost, f"Purchased home upgrade {upgrade.name}")
            UIAudio.play_coin()
            ConfirmDialog("Furnishing Purchased", msg, self).exec()
            self.update_hud()
        else:
            ConfirmDialog("Cannot Buy", msg, self).exec()

    def on_nav_left(self):
        UIAudio.play_click()
        unlocked = self.get_unlocked_places()
        if self.current_place not in unlocked:
            self.current_place = "Restaurant"
        idx = unlocked.index(self.current_place)
        next_idx = (idx - 1) % len(unlocked)
        self.current_place = unlocked[next_idx]
        self.update_place_screen()
        
    def on_nav_right(self):
        UIAudio.play_click()
        unlocked = self.get_unlocked_places()
        if self.current_place not in unlocked:
            self.current_place = "Restaurant"
        idx = unlocked.index(self.current_place)
        next_idx = (idx + 1) % len(unlocked)
        self.current_place = unlocked[next_idx]
        self.update_place_screen()

    def on_sleep_and_end_day(self):
        UIAudio.play_click()
        
        # Stop simulation timer if sleeping early
        if self.day_clock_timer.isActive():
            self.day_clock_timer.stop()
            
        self.is_working = False
        self.is_paused = False
        self.active_hours_passed = 0
        
        # Reset button and controls
        self.sim_btn.setText("Start Day")
        self.sim_btn.setStyleSheet("font-weight: bold; background-color: #8ADAB2;")
        self.stop_btn.setVisible(False)
        
        # 1. Check and trigger random events BEFORE sleep
        triggered_event = self.state.events.check_and_trigger_event(self.state)
        if triggered_event:
            UIAudio.play_notify()
            self.handle_triggered_event(triggered_event)
            
        # 2. Advance day (sleep, maintenance, payroll deductions)
        notifications = self.state.advance_day()
        if notifications:
            UIAudio.play_notify()
            for note in notifications:
                self.notification_manager.add_notification(note, "info")
                
        # 3. Competitor survival progression check
        c = self.state.competitor
        if c.is_active:
            is_married = self.state.romance.is_co_owner
            
            if (self.state.restaurant.reputation >= 60.0 and 
                self.state.romance.romance_level >= 80.0 and 
                is_married):
                self.days_survived_competitor += 1
                self.notification_manager.add_notification(
                    f"Survived rival smear campaign: {self.days_survived_competitor}/10 days", "success"
                )
                if self.days_survived_competitor >= 10:
                    self.victory = True
                    self.game_over = True
            else:
                if self.days_survived_competitor > 0:
                    self.days_survived_competitor = 0
                    self.notification_manager.add_notification("Lost survival focus! Smear count reset.", "warning")
                    
        # 4. Game Over conditions check
        p = self.state.player
        if p.cash <= -500.0 or p.energy <= 0 or self.game_over:
            self.show_game_over()
        else:
            # Transition back to morning prep phase
            self.evening_phase = False
            self.show_gameplay()

    def handle_triggered_event(self, event):
        valid_options = [o for o in event.options if o.condition(self.state)]
        option_texts = [opt.text for opt in valid_options]
        
        dlg = ChoicesDialog(f"EVENT: {event.title}", event.description, option_texts, self)
        if dlg.exec() and dlg.chosen_index != -1:
            chosen_idx = dlg.chosen_index
            chosen_text, outcome_text = self.state.events.resolve_event(chosen_idx, self.state)
            
            # Show resolution in modal confirmation
            ConfirmDialog("Event Outcome", f"You chose: {chosen_text}\n\n{outcome_text}", self).exec()
            self.update_hud()

    def update_hud(self):
        p = self.state.player
        r = self.state.restaurant
        rom = self.state.romance
        
        # Calculate time of day string
        if self.evening_phase:
            time_str = "Evening"
        elif self.is_working:
            hour = 9 + self.active_hours_passed
            am_pm = "AM" if hour < 12 else "PM"
            display_hour = hour if hour <= 12 else hour - 12
            if display_hour == 0:
                display_hour = 12
            time_str = f"{display_hour:d}:00 {am_pm}"
        else:
            time_str = "Morning Prep"
            
        self.shop_name_lbl.setText(f"🏰 {r.name} (Lvl {r.level})")
        self.day_lbl.setText(f"📅 Day {self.state.day} - {self.state.day_name} - {time_str}")
        self.cash_lbl.setText(f"💰 ${p.cash:.2f}")
        
        self.energy_bar.setValue(max(0, min(100, int(p.energy))))
        self.energy_bar.setFormat(f"%v/%m")
        
        self.rep_bar.setValue(max(0, min(100, int(r.reputation))))
        self.rep_bar.setFormat(f"%v/100")
        
        partner = rom.partner
        if not partner:
            self.partner_lbl.setText("👤 Single")
        else:
            self.partner_lbl.setText(f"🌹 {partner.name}")
            
        # Update sidebar status label
        active_employees = self.state.employees.get_active_employees()
        emp_str = ", ".join([e.name for e in active_employees]) if active_employees else "None"
        status_text = (
            f"<b>🏰 Diner Operations:</b><br/>"
            f"Name: <b>{r.name}</b><br/>"
            f"Level: <b>{r.level}</b> - {r.current_config.name}<br/>"
            f"Meal Price: <b>${r.menu_price:.2f}</b><br/>"
            f"Max Capacity: <b>{r.customer_capacity} guests</b><br/>"
            f"Economic Mult: <b>{self.state.town.economic_multiplier:.1f}x</b><br/>"
            f"Staff: <b>{emp_str}</b>"
        )
        self.sidebar_status_lbl.setText(status_text)
            
        if self.current_place == "Bar":
            self.update_bar_sidebar()
        elif self.current_place == "Home":
            self.update_home_sidebar()
            
        if self.stacked_widget.currentIndex() == 1:
            self.gameplay_screen.update_ui(self.evening_phase)
        elif self.stacked_widget.currentIndex() == 3:
            self.personal_life_screen.update_ui()
        elif self.stacked_widget.currentIndex() == 4:
            self.tavern_screen.update_ui()
            
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Re-fit notification manager dimensions
        self.notification_manager.fit_parent()
