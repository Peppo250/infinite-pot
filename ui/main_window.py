# ui/main_window.py
import sys
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget, QProgressBar, QFrame, QGraphicsOpacityEffect, QPushButton
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
        
        # Places cycle list for bottom-right navigation
        self.places_cycle = ["Home", "Restaurant", "Bar"]
        self.current_place_idx = 1 # Start on Restaurant (Diner)
        
        # 1. Top HUD Bar
        self.init_hud_bar()
        self.hud_bar.setVisible(False)  # Hidden on Main Menu
        self.main_layout.addWidget(self.hud_bar)
        
        # Content horizontal layout (Stacked screen on left, Sidebar on right)
        self.content_widget = QWidget(self)
        self.content_layout = QHBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        # 2. Stacked Screen Layout
        self.stacked_widget = QStackedWidget(self)
        self.content_layout.addWidget(self.stacked_widget, stretch=4)
        
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
        
        # 2. Calendar / Phase
        self.day_lbl = QLabel(self)
        self.day_lbl.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {ThemeManager.DARK_BROWN};")
        hud_layout.addWidget(self.day_lbl)
        
        # 3. Cash
        self.cash_lbl = QLabel(self)
        self.cash_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #3A5F43;")
        hud_layout.addWidget(self.cash_lbl)
        
        # 4. Energy
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
        
        # 5. Reputation
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
        
        # 6. Partner
        self.partner_lbl = QLabel(self)
        self.partner_lbl.setStyleSheet(f"font-size: 16px; color: {ThemeManager.DARK_BROWN}; font-weight: bold;")
        hud_layout.addWidget(self.partner_lbl)
        
        # Stretch columns equally
        hud_layout.setStretch(0, 2)
        hud_layout.setStretch(1, 3)
        hud_layout.setStretch(2, 2)
        hud_layout.setStretch(3, 2)
        hud_layout.setStretch(4, 2)
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
        self.animate_switch(0)

    def show_gameplay(self):
        self.hud_bar.setVisible(True)
        self.sidebar_widget.setVisible(True)
        self.update_place_screen()
        self.update_hud()

    def show_business(self):
        self.open_place_upgrades()

    def show_personal_life(self):
        self.current_place_idx = 0  # Home
        self.show_gameplay()

    def show_tavern(self):
        self.current_place_idx = 2  # Bar
        self.show_gameplay()

    def show_game_over(self):
        UIAudio.play_music("home")
        self.hud_bar.setVisible(False)
        self.sidebar_widget.setVisible(False)
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
        
        layout = QVBoxLayout(self.sidebar_widget)
        layout.setContentsMargins(5, 10, 5, 10)
        layout.setSpacing(12)
        
        # 1. Start Day / Pause / Continue Controls
        self.sim_btn = QPushButton("Start Day", self)
        self.sim_btn.setObjectName("sim-btn")
        self.sim_btn.setStyleSheet("font-weight: bold; background-color: #8ADAB2;")
        self.sim_btn.clicked.connect(self.on_sim_btn_clicked)
        layout.addWidget(self.sim_btn)
        
        # 2. Upgrades Button
        self.upgrades_btn = QPushButton("Place Upgrades", self)
        self.upgrades_btn.clicked.connect(self.open_place_upgrades)
        layout.addWidget(self.upgrades_btn)
        
        # 3. Money Mgmt Button
        self.money_btn = QPushButton("Money Mgmt", self)
        self.money_btn.clicked.connect(self.open_money_mgmt)
        layout.addWidget(self.money_btn)
        
        # 4. Relationship Mgmt Button
        self.rel_btn = QPushButton("Relationship Mgmt", self)
        self.rel_btn.clicked.connect(self.open_relationship_mgmt)
        layout.addWidget(self.rel_btn)
        
        # 5. Options Button
        self.options_btn = QPushButton("Options", self)
        self.options_btn.clicked.connect(self.open_options)
        layout.addWidget(self.options_btn)
        
        layout.addStretch()
        
        # 6. Bottom Navigation Controls: < place name >
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(4)
        
        self.left_nav_btn = QPushButton("<", self)
        self.left_nav_btn.setMaximumWidth(40)
        self.left_nav_btn.clicked.connect(self.on_nav_left)
        nav_layout.addWidget(self.left_nav_btn)
        
        self.place_label = QLabel("Restaurant", self)
        self.place_label.setAlignment(Qt.AlignCenter)
        self.place_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {ThemeManager.DARK_BROWN};")
        nav_layout.addWidget(self.place_label)
        
        self.right_nav_btn = QPushButton(">", self)
        self.right_nav_btn.setMaximumWidth(40)
        self.right_nav_btn.clicked.connect(self.on_nav_right)
        nav_layout.addWidget(self.right_nav_btn)
        
        layout.addLayout(nav_layout)
        
        self.sidebar_widget.setVisible(False)
        return self.sidebar_widget

    def on_sim_btn_clicked(self):
        UIAudio.play_click()
        if self.evening_phase:
            self.on_sleep_and_end_day()
            return
            
        if not self.is_working:
            dlg = ChoicesDialog(
                "Open Restaurant",
                "Choose the length of your work shift today:",
                [
                    "Short Shift (4 Hours) - Conserves Energy",
                    "Standard Shift (8 Hours) - Normal Operation",
                    "Overtime Shift (12 Hours) - Spouse help triggers possible"
                ],
                self
            )
            if dlg.exec() and dlg.chosen_index != -1:
                self.target_work_hours = [4, 8, 12][dlg.chosen_index]
                self.active_hours_passed = 0
                self.is_working = True
                self.is_paused = False
                
                self.state.finance.start_new_day()
                
                self.sim_btn.setText("Pause")
                self.sim_btn.setStyleSheet("font-weight: bold; background-color: #F8C4B4;")
                
                self.day_clock_timer.start(10000)
                self.notification_manager.add_notification(
                    f"Diner open! Real-time shift started: {self.target_work_hours} hours.", "info"
                )
                self.update_hud()
        else:
            if self.is_paused:
                self.is_paused = False
                self.sim_btn.setText("Pause")
                self.sim_btn.setStyleSheet("font-weight: bold; background-color: #F8C4B4;")
                self.day_clock_timer.start(10000)
                self.notification_manager.add_notification("Game continued.", "info")
            else:
                self.is_paused = True
                self.sim_btn.setText("Continue")
                self.sim_btn.setStyleSheet("font-weight: bold; background-color: #8ADAB2;")
                self.day_clock_timer.stop()
                self.notification_manager.add_notification("Game paused.", "info")

    def on_game_clock_tick(self):
        if not self.is_working or self.is_paused:
            return
            
        if self.state.player.energy <= 0.0:
            self.day_clock_timer.stop()
            self.is_working = False
            UIAudio.play_sad()
            ConfirmDialog("Exhausted!", "You ran out of energy and passed out!\nYour staff closed down the shop.", self).exec()
            self.on_sleep_and_end_day()
            return
            
        if self.active_hours_passed >= self.target_work_hours:
            self.day_clock_timer.stop()
            self.is_working = False
            self.evening_phase = True
            UIAudio.play_success()
            
            dlg = ReceiptDialog(self.state.finance.get_daily_report(), self)
            dlg.exec()
            
            self.sim_btn.setText("Sleep & End Day")
            self.sim_btn.setStyleSheet("font-weight: bold; background-color: #82A0D8;")
            self.notification_manager.add_notification("Workday finished! You are now in the Evening Phase.", "info")
            self.update_hud()
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
            
        self.update_hud()
        
    def open_place_upgrades(self):
        PlaceUpgradesDialog(self.state, self).exec()
        
    def open_money_mgmt(self):
        MoneyMgmtDialog(self.state, self).exec()
        
    def open_relationship_mgmt(self):
        RelationshipMgmtDialog(self.state, self).exec()
        
    def open_options(self):
        OptionsDialog(self).exec()

    def update_place_screen(self):
        place = self.places_cycle[self.current_place_idx]
        self.place_label.setText(place)
        
        if place == "Home":
            UIAudio.play_music("romance")
            self.stacked_widget.setCurrentIndex(3)
            self.personal_life_screen.update_ui()
        elif place == "Restaurant":
            UIAudio.play_music("hotel")
            self.stacked_widget.setCurrentIndex(1)
            self.gameplay_screen.update_ui(self.evening_phase)
        elif place == "Bar":
            UIAudio.play_music("bar")
            self.stacked_widget.setCurrentIndex(4)
            self.tavern_screen.update_ui()
            
    def on_nav_left(self):
        UIAudio.play_click()
        self.current_place_idx = (self.current_place_idx - 1) % len(self.places_cycle)
        self.update_place_screen()
        
    def on_nav_right(self):
        UIAudio.play_click()
        self.current_place_idx = (self.current_place_idx + 1) % len(self.places_cycle)
        self.update_place_screen()

    def on_sleep_and_end_day(self):
        UIAudio.play_click()
        
        # Stop simulation timer if sleeping early
        if self.day_clock_timer.isActive():
            self.day_clock_timer.stop()
            
        self.is_working = False
        self.is_paused = False
        self.active_hours_passed = 0
        
        # Reset button text
        self.sim_btn.setText("Start Day")
        self.sim_btn.setStyleSheet("font-weight: bold; background-color: #8ADAB2;")
        
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
        
        self.shop_name_lbl.setText(f"🏰 {r.name} (Lvl {r.level})")
        phase_str = "Evening" if self.evening_phase else ("Working (Hour %d/%d)" % (self.active_hours_passed, self.target_work_hours) if self.is_working else "Morning Prep")
        self.day_lbl.setText(f"📅 Day {self.state.day} ({self.state.day_name}) • {phase_str}")
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
            
        # Re-verify and refresh current active screen content
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
