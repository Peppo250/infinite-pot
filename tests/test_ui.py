import sys
import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from engine.state import GameState
from ui.main_window import MainWindow
from ui.dialogs.custom_dialogs import OptionsDialog, PlaceUpgradesDialog, MoneyMgmtDialog, RelationshipMgmtDialog, ConfirmDialog, ChoicesDialog, ReceiptDialog, DevSetupDialog

# Ensure QApplication exists for PySide6 widgets
@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

@pytest.fixture
def main_window(qapp, monkeypatch):
    # Mock modal dialog execution so tests run non-interactively
    monkeypatch.setattr(ConfirmDialog, "exec", lambda self: True)
    monkeypatch.setattr(ChoicesDialog, "exec", lambda self: True)
    monkeypatch.setattr(ReceiptDialog, "exec", lambda self: True)
    monkeypatch.setattr(OptionsDialog, "exec", lambda self: True)
    monkeypatch.setattr(PlaceUpgradesDialog, "exec", lambda self: True)
    monkeypatch.setattr(MoneyMgmtDialog, "exec", lambda self: True)
    monkeypatch.setattr(RelationshipMgmtDialog, "exec", lambda self: True)
    monkeypatch.setattr(DevSetupDialog, "exec", lambda self: True)
    
    state = GameState()
    window = MainWindow(state)
    window.show_gameplay()
    return window

def test_main_window_initial_state(main_window):
    assert main_window.current_place == "Restaurant"
    assert main_window.stacked_widget.currentIndex() == 1
    assert main_window.sidebar_stacked.currentIndex() == 0
    assert main_window.world_speed == 1.0
    assert main_window.is_working is False
    assert main_window.is_paused is False
    assert main_window.sim_btn.text() == "Start Day"
    assert main_window.stop_btn.isVisible() is False

def test_place_locking_and_navigation(main_window):
    # Level 0 restaurant, no house -> unlocked places: ["Restaurant"]
    unlocked = main_window.get_unlocked_places()
    assert unlocked == ["Restaurant"]
    
    # Try navigating right -> stays at Restaurant
    main_window.on_nav_right()
    assert main_window.current_place == "Restaurant"
    
    # Unlock Bar (level 3)
    main_window.state.restaurant.level = 3
    unlocked = main_window.get_unlocked_places()
    assert unlocked == ["Restaurant", "Bar"]
    
    # Navigate right -> goes to Bar
    main_window.on_nav_right()
    assert main_window.current_place == "Bar"
    assert main_window.stacked_widget.currentIndex() == 4
    assert main_window.sidebar_stacked.currentIndex() == 1
    
    # Unlock Home (house purchased)
    main_window.state.house.purchased = True
    unlocked = main_window.get_unlocked_places()
    assert unlocked == ["Restaurant", "Bar", "Home"]
    
    # Navigate right -> goes to Home
    main_window.on_nav_right()
    assert main_window.current_place == "Home"
    assert main_window.stacked_widget.currentIndex() == 3
    assert main_window.sidebar_stacked.currentIndex() == 2
    
    # Navigate left -> goes to Bar
    main_window.on_nav_left()
    assert main_window.current_place == "Bar"

def test_workday_simulation_controls(main_window):
    # 1. Start Day
    main_window.on_sim_btn_clicked()
    assert main_window.is_working is True
    assert main_window.is_paused is False
    assert main_window.sim_btn.text() == "Pause"
    assert not main_window.stop_btn.isHidden()
    assert main_window.day_clock_timer.isActive() is True
    
    # 2. Pause
    main_window.on_sim_btn_clicked()
    assert main_window.is_working is True
    assert main_window.is_paused is True
    assert main_window.sim_btn.text() == "Continue"
    assert main_window.day_clock_timer.isActive() is False
    
    # 3. Continue
    main_window.on_sim_btn_clicked()
    assert main_window.is_paused is False
    assert main_window.sim_btn.text() == "Pause"
    assert main_window.day_clock_timer.isActive() is True
    
    # 4. Stop Work
    main_window.on_stop_work_clicked()
    assert main_window.is_working is False
    assert main_window.is_paused is False
    assert main_window.evening_phase is True
    assert main_window.sim_btn.text() == "Sleep & End Day"
    assert main_window.stop_btn.isHidden()
    assert main_window.day_clock_timer.isActive() is False
    
    # 5. Sleep & End Day
    main_window.on_sim_btn_clicked()
    assert main_window.evening_phase is False
    assert main_window.sim_btn.text() == "Start Day"

def test_world_speed_slider(main_window, monkeypatch):
    dialog = OptionsDialog(main_window)
    dialog.speed_slider.setValue(10)
    assert "10x" in dialog.speed_lbl.text()
    
    # Apply settings
    dialog.on_apply()
    assert main_window.world_speed == 10.0
    
    # Verify clock interval changes when starting day
    main_window.on_sim_btn_clicked() # Start Day
    assert main_window.day_clock_timer.interval() == 1000 # 10000 / 10 = 1000ms
    main_window.on_stop_work_clicked()

def test_bar_sidebar_interactions(main_window):
    main_window.state.restaurant.level = 3
    main_window.current_place = "Bar"
    main_window.update_place_screen()
    
    # Socialize with first girl
    girl = main_window.state.romance.characters[0]
    initial_energy = main_window.state.player.energy
    main_window.interact_girl(girl)
    
    # Hire applicant
    cand = main_window.state.employees.candidates[0]
    main_window.state.player.cash = 500.0
    main_window.hire_candidate(cand)
    assert cand in main_window.state.employees.hired

def test_home_sidebar_interactions(main_window):
    main_window.state.house.purchased = True
    main_window.current_place = "Home"
    main_window.update_place_screen()
    
    # Buy ring
    main_window.state.player.cash = 3000.0
    main_window.on_buy_ring()
    assert main_window.state.romance.has_ring is True
    
    # Buy house upgrade / furnishing
    up = main_window.state.house.available_upgrades[0]
    main_window.buy_house_upgrade(up)
    assert up.id in main_window.state.house.upgrades

def test_dialog_launchers(main_window):
    # Verify opening dialog buttons work without throwing exceptions
    main_window.open_place_upgrades()
    main_window.open_money_mgmt()
    main_window.open_relationship_mgmt()
    main_window.open_options()

def test_full_romance_flow(main_window, monkeypatch):
    rom = main_window.state.romance
    p = main_window.state.player
    h = main_window.state.house
    girl = rom.characters[0]
    
    def mock_choice(idx):
        def fake_exec(self):
            self.chosen_index = idx
            return True
        return fake_exec
    
    # 1. Talk to girl
    p.energy = 100.0
    monkeypatch.setattr(ChoicesDialog, "exec", mock_choice(0)) # Talk
    main_window.interact_girl(girl)
    assert p.energy == 90.0
    
    # 2. Buy drink for girl
    p.cash = 100.0
    p.energy = 90.0
    monkeypatch.setattr(ChoicesDialog, "exec", mock_choice(1)) # Buy drink
    main_window.interact_girl(girl)
    assert p.cash == 75.0
    assert p.energy == 80.0
    
    # 3. Propose relationship
    girl.romance_level = 65.0
    monkeypatch.setattr(ChoicesDialog, "exec", mock_choice(2)) # Propose relationship
    main_window.interact_girl(girl)
    assert rom.partner_name == girl.name
    
    # 4. Buy engagement ring
    p.cash = 3000.0
    main_window.on_buy_ring()
    assert rom.has_ring is True
    
    # 5. Propose marriage & co-ownership
    girl.romance_level = 95.0
    h.purchased = True
    main_window.on_propose()
    assert rom.is_co_owner is True
    
    # 6. Break up
    main_window.on_break_up()
    assert rom.partner is None

def test_game_over_triggers(main_window):
    main_window.show_gameplay()
    # Test cash bankrupt trigger
    main_window.state.player.cash = -600.0
    main_window.on_sleep_and_end_day()
    assert main_window.hud_bar.isVisible() is False

def test_random_event_handling(main_window, monkeypatch):
    main_window.show_gameplay()
    event = main_window.state.events.events[0]
    
    def fake_exec(self):
        self.chosen_index = 0
        return True
        
    monkeypatch.setattr(ChoicesDialog, "exec", fake_exec)
    main_window.handle_triggered_event(event)
    assert main_window.game_over is False

def test_multiple_partners_selection_and_breakup(main_window):
    rom = main_window.state.romance
    g1 = rom.characters[0]
    g2 = rom.characters[1]
    
    g1.is_partner = True
    g2.is_partner = True
    
    dlg = RelationshipMgmtDialog(main_window.state, main_window)
    # Since multiple partners exist, initially shows partner selection list
    assert dlg.selected_partner_name is None
    
    # Select first partner
    dlg.select_partner(g1.name)
    assert dlg.selected_partner_name == g1.name
    
    # Break up with first partner via dialog
    dlg.on_break_up_dlg()
    assert g1.is_partner is False
    assert g2.is_partner is True

def test_dev_setup_dialog(main_window):
    dlg = DevSetupDialog(current_level=2, current_cash=5000.0, parent=main_window)
    dlg.level_combo.setCurrentIndex(2) # Level 3
    dlg.cash_spin.setValue(15000.0)
    assert dlg.get_level() == 3
    assert dlg.get_cash() == 15000.0
