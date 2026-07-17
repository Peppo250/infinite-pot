# ui/main_window.py
import sys
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget, QProgressBar, QFrame, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from ui.theme import ThemeManager
from ui.audio import UIAudio
from ui.widgets.notifications import NotificationManager
from ui.dialogs.custom_dialogs import ConfirmDialog, TextInputDialog, ReceiptDialog, ChoicesDialog

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
        
        # 1. Top HUD Bar
        self.init_hud_bar()
        self.hud_bar.setVisible(False)  # Hidden on Main Menu
        self.main_layout.addWidget(self.hud_bar)
        
        # 2. Stacked Screen Layout
        self.stacked_widget = QStackedWidget(self)
        self.main_layout.addWidget(self.stacked_widget)
        
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
        
        self.gameplay_screen.manage_business.connect(self.show_business)
        self.gameplay_screen.personal_life.connect(self.show_personal_life)
        self.gameplay_screen.restaurant_opened.connect(self.on_open_restaurant)
        self.gameplay_screen.go_to_tavern.connect(self.on_visit_tavern)
        self.gameplay_screen.sleep_clicked.connect(self.on_sleep_and_end_day)
        
        self.business_screen.go_back.connect(self.show_gameplay)
        self.business_screen.state_changed.connect(self.update_hud)
        
        self.personal_life_screen.go_back.connect(self.show_gameplay)
        self.personal_life_screen.state_changed.connect(self.update_hud)
        self.personal_life_screen.open_wedding_planner.connect(self.show_tavern)
        
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
        self.shop_name_lbl.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {ThemeManager.DARK_BROWN};")
        hud_layout.addWidget(self.shop_name_lbl)
        
        # 2. Calendar / Phase
        self.day_lbl = QLabel(self)
        self.day_lbl.setStyleSheet("font-size: 18px; font-weight: bold;")
        hud_layout.addWidget(self.day_lbl)
        
        # 3. Cash
        self.cash_lbl = QLabel(self)
        self.cash_lbl.setStyleSheet(f"font-size: 19px; font-weight: bold; color: #4F6F52;")
        hud_layout.addWidget(self.cash_lbl)
        
        # 4. Energy
        energy_widget = QWidget(self)
        energy_layout = QHBoxLayout(energy_widget)
        energy_layout.setContentsMargins(0, 0, 0, 0)
        energy_layout.setSpacing(5)
        e_lbl = QLabel("Energy:", self)
        e_lbl.setStyleSheet("font-size: 16px; font-weight: bold;")
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
        r_lbl.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.rep_bar = QProgressBar(self)
        self.rep_bar.setRange(0, 100)
        self.rep_bar.setMaximumWidth(80)
        self.rep_bar.setStyleSheet("QProgressBar::chunk { background-color: #82A0D8; }")
        rep_layout.addWidget(r_lbl)
        rep_layout.addWidget(self.rep_bar)
        hud_layout.addWidget(rep_widget)
        
        # 6. Partner
        self.partner_lbl = QLabel(self)
        self.partner_lbl.setStyleSheet(f"font-size: 18px; color: {ThemeManager.DARK_BROWN}; font-weight: bold;")
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
        self.animate_switch(0)

    def show_gameplay(self):
        UIAudio.play_music("hotel")
        self.hud_bar.setVisible(True)
        self.gameplay_screen.update_ui(self.evening_phase)
        self.update_hud()
        self.animate_switch(1)

    def show_business(self):
        UIAudio.play_music("hotel")
        self.business_screen.update_ui()
        self.animate_switch(2)

    def show_personal_life(self):
        UIAudio.play_music("romance")
        self.personal_life_screen.update_ui()
        self.animate_switch(3)

    def show_tavern(self):
        UIAudio.play_music("bar")
        self.tavern_screen.update_ui()
        self.animate_switch(4)

    def show_game_over(self):
        UIAudio.play_music("home")
        self.hud_bar.setVisible(False)
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
        
        self.gameplay_screen.manage_business.connect(self.show_business)
        self.gameplay_screen.personal_life.connect(self.show_personal_life)
        self.gameplay_screen.restaurant_opened.connect(self.on_open_restaurant)
        
        self.business_screen.go_back.connect(self.show_gameplay)
        self.business_screen.state_changed.connect(self.update_hud)
        self.personal_life_screen.go_back.connect(self.show_gameplay)
        self.personal_life_screen.state_changed.connect(self.update_hud)
        self.personal_life_screen.open_wedding_planner.connect(self.show_tavern)
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

    def on_open_restaurant(self, hours: int):
        # 1. Run simulation
        sim = self.state.simulate_business_day(hours)
        if sim['actual_served'] > 0:
            UIAudio.play_coin()
            
        # 2. Transition music to home (review ledger phase)
        UIAudio.play_music("home")
        
        # 3. Present Ledger Check Receipt popup dialog
        dlg = ReceiptDialog(self.state.finance.get_daily_report(), self)
        dlg.exec()
        
        # 4. Enable evening phase and refresh gameplay hub controls
        self.evening_phase = True
        self.show_gameplay()

    def on_visit_tavern(self):
        p = self.state.player
        if p.energy < 15:
            ConfirmDialog("Too Exhausted", "You are too exhausted to visit the Tavern tonight! (15 Energy required)", self).exec()
            return
            
        p.adjust_energy(-15)
        self.state.finance.record_transaction("Misc", 0, "Visited Tavern")
        self.show_tavern()

    def on_sleep_and_end_day(self):
        UIAudio.play_click()
        
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
            has_wedding = self.state.romance.wedding_tier != "None"
            
            if (self.state.restaurant.reputation >= 60.0 and 
                self.state.romance.romance_level >= 80.0 and 
                is_married and 
                has_wedding):
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
        phase_str = "Evening" if self.evening_phase else "Prep"
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
        elif self.stacked_widget.currentIndex() == 2:
            self.business_screen.update_ui()
        elif self.stacked_widget.currentIndex() == 3:
            self.personal_life_screen.update_ui()
        elif self.stacked_widget.currentIndex() == 4:
            self.tavern_screen.update_ui()
            
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Re-fit notification manager dimensions
        self.notification_manager.fit_parent()
