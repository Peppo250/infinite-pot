from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QScrollArea, QListWidget, QListWidgetItem, QProgressBar
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from ui.theme import ThemeManager
from ui.audio import UIAudio
from ui.dialogs.custom_dialogs import ConfirmDialog, ChoicesDialog

class TavernMenuScreen(QWidget):
    go_back = Signal()
    state_changed = Signal()  # Emitted when candidates hired or relationships change
    
    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.state = state
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(10)
        
        # Header
        header_layout = QHBoxLayout()
        self.back_btn = QPushButton("← Return to Evening Choices", self)
        self.back_btn.clicked.connect(self.go_back.emit)
        header_layout.addWidget(self.back_btn)
        
        self.title = QLabel("Oakhaven Tavern", self)
        self.title.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {ThemeManager.DARK_BROWN};")
        header_layout.addWidget(self.title, alignment=Qt.AlignRight)
        main_layout.addLayout(header_layout)
        
        # Tavern Pixel Art Banner (Scaled down for vertical space)
        self.banner_img = QLabel(self)
        self.banner_img.setStyleSheet(f"border: 4px solid {ThemeManager.DARK_BROWN}; border-radius: 0px;")
        pixmap = QPixmap("assets/images/tavern_bg.jpg")
        self.banner_img.setPixmap(pixmap.scaled(960, 95, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        main_layout.addWidget(self.banner_img, alignment=Qt.AlignCenter)
        
        # Split layout
        split_layout = QHBoxLayout()
        split_layout.setSpacing(20)
        
        # LEFT COLUMN: Socializing & Girls
        self.girls_card = QFrame(self)
        self.girls_card.setObjectName("card-frame")
        self.girls_layout = QVBoxLayout(self.girls_card)
        self.girls_layout.setSpacing(12)
        
        girls_title = QLabel("🌹 Socializing & Dating", self)
        girls_title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {ThemeManager.DARK_BROWN};")
        self.girls_layout.addWidget(girls_title)
        
        self.girls_scroll = QScrollArea(self)
        self.girls_scroll.setWidgetResizable(True)
        self.girls_content = QWidget()
        self.girls_scroll_layout = QVBoxLayout(self.girls_content)
        self.girls_scroll_layout.setSpacing(10)
        self.girls_scroll_layout.setAlignment(Qt.AlignTop)
        self.girls_scroll.setWidget(self.girls_content)
        self.girls_layout.addWidget(self.girls_scroll)
        
        split_layout.addWidget(self.girls_card, stretch=1)
        
        # RIGHT COLUMN: Job Candidates
        self.candidates_card = QFrame(self)
        self.candidates_card.setObjectName("card-frame")
        self.cand_layout = QVBoxLayout(self.candidates_card)
        self.cand_layout.setSpacing(12)
        
        cand_title = QLabel("👥 Job Applicants", self)
        cand_title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {ThemeManager.DARK_BROWN};")
        self.cand_layout.addWidget(cand_title)
        
        self.cand_scroll = QScrollArea(self)
        self.cand_scroll.setWidgetResizable(True)
        self.cand_content = QWidget()
        self.cand_scroll_layout = QVBoxLayout(self.cand_content)
        self.cand_scroll_layout.setSpacing(10)
        self.cand_scroll_layout.setAlignment(Qt.AlignTop)
        self.cand_scroll.setWidget(self.cand_content)
        self.cand_layout.addWidget(self.cand_scroll)
        
        split_layout.addWidget(self.candidates_card, stretch=1)
        
        main_layout.addLayout(split_layout)
        self.update_ui()

    def interact_girl(self, girl):
        UIAudio.play_click()
        rom = self.state.romance
        p = self.state.player
        h = self.state.house
        
        # We need to temporarily switch to romance music for the interaction
        UIAudio.play_music("romance")
        
        while True:
            # Build list of options dynamically
            opts = [
                f"Talk to her (Costs 10 Energy) [Current: {p.energy:.1f}]",
                f"Buy her a drink (Costs $25.00, 10 Energy) [Current: ${p.cash:.2f}]"
            ]
            
            if not girl.is_partner and not girl.is_co_owner:
                opts.append("Propose Relationship / Ask to be Partner (Requires >=40 Romance)")
            elif girl.is_partner and not girl.is_co_owner:
                opts.append("Propose Marriage & Co-ownership (Requires >=75 Romance and House)")
                opts.append("Break Up")
            elif girl.is_co_owner:
                opts.append("Speak about your shared life")
                
            dlg = ChoicesDialog(f"Interacting with {girl.name}", f"'{girl.description}'\n\nWhat would you like to do?", opts, self)
            
            if not dlg.exec() or dlg.chosen_index == -1:
                # Return to tavern music when exit dialog
                UIAudio.play_music("bar")
                break
                
            choice = dlg.chosen_index
            if choice == 0:  # Talk
                if p.energy < 10:
                    ConfirmDialog("Too Exhausted", "You don't have enough energy (10 required) to hold a conversation.", self).exec()
                else:
                    p.adjust_energy(-10)
                    dialogue, gain = girl.interact_talk()
                    UIAudio.play_dialogue()
                    ConfirmDialog(f"Talking to {girl.name}", f"{girl.name} says:\n\n\"{dialogue}\"\n\n(Romance increased by {gain:.1f})", self).exec()
                    self.update_ui()
                    self.state_changed.emit()
            elif choice == 1:  # Buy Drink
                if p.cash < 25.0:
                    ConfirmDialog("No Cash", "You need $25.00 to buy a drink.", self).exec()
                elif p.energy < 10:
                    ConfirmDialog("Too Exhausted", "You don't have enough energy (10 required) to socialize.", self).exec()
                else:
                    p.adjust_cash(-25.0)
                    p.adjust_energy(-10)
                    self.state.finance.record_transaction("Date", 25.0, f"Bought drink for {girl.name}")
                    dialogue, gain = girl.interact_drink(25.0)
                    UIAudio.play_coin()
                    UIAudio.play_dialogue()
                    ConfirmDialog(f"Bought {girl.name} a Drink", f"You buy a warm cider for {girl.name}.\n\nShe smiles:\n\"{dialogue}\"\n\n(Romance increased by {gain:.1f})", self).exec()
                    self.update_ui()
                    self.state_changed.emit()
            elif choice == 2:  # Relationship or Marriage Propose or shared life
                if not girl.is_partner and not girl.is_co_owner:
                    if p.energy < 10:
                        ConfirmDialog("Too Exhausted", "You need 10 energy to ask her out.", self).exec()
                    else:
                        p.adjust_energy(-10)
                        success, msg = rom.propose_relationship(girl.name)
                        if success:
                            UIAudio.play_success()
                            ConfirmDialog("Success!", msg, self).exec()
                        else:
                            ConfirmDialog("Relationship Proposal", msg, self).exec()
                        self.update_ui()
                        self.state_changed.emit()
                elif girl.is_partner and not girl.is_co_owner:
                    if p.energy < 10:
                        ConfirmDialog("Too Exhausted", "You need 10 energy to propose.", self).exec()
                    else:
                        p.adjust_energy(-10)
                        success, msg = rom.ask_to_co_own(h.purchased)
                        if success:
                            UIAudio.play_success()
                            ConfirmDialog("Congratulations!", msg, self).exec()
                        else:
                            ConfirmDialog("Marriage Proposal", msg, self).exec()
                        self.update_ui()
                        self.state_changed.emit()
                elif girl.is_co_owner:
                    UIAudio.play_dialogue()
                    ConfirmDialog("Married Life", f"{girl.name} kisses your cheek. \"Let's keep building our life together, darling. I'm so happy to help out in the restaurant.\"", self).exec()
            elif choice == 3:  # Break Up
                if girl.is_partner and not girl.is_co_owner:
                    confirm_dlg = ConfirmDialog("Break Up", f"Are you sure you want to end your relationship with {girl.name}?", self)
                    if confirm_dlg.exec():
                        success, msg = rom.break_up()
                        if success:
                            ConfirmDialog("Single", msg, self).exec()
                            self.update_ui()
                            self.state_changed.emit()
                            UIAudio.play_music("bar")
                            break

    def hire_candidate(self, candidate):
        r = self.state.restaurant
        es = self.state.employees
        p = self.state.player
        
        dlg = ConfirmDialog(
            "Hire Employee",
            f"Do you want to hire {candidate.name}?\n\n"
            f"Daily Wage: ${candidate.daily_salary:.2f}/day\n"
            f"Skill: {candidate.skill:.2f} | Reliability: {candidate.reliability:.2f}\n"
            f"Experience: {candidate.experience} years",
            self
        )
        if dlg.exec():
            success, msg = es.hire_employee(candidate.name, r.current_config.max_employees)
            if success:
                UIAudio.play_success()
                ConfirmDialog("Hired!", msg, self).exec()
                self.update_ui()
                self.state_changed.emit()
            else:
                ConfirmDialog("Recruitment Failed", msg, self).exec()

    def update_ui(self):
        # 1. Update Tavern Socializing Column
        # Clear layout
        while self.girls_scroll_layout.count():
            item = self.girls_scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        girls = self.state.romance.get_characters_available(self.state.day_name)
        if not girls:
            no_girls_lbl = QLabel("The Tavern is quiet tonight.\nNobody you know is here.", self)
            no_girls_lbl.setAlignment(Qt.AlignCenter)
            no_girls_lbl.setStyleSheet("font-style: italic; color: #666666; padding: 20px;")
            self.girls_scroll_layout.addWidget(no_girls_lbl)
        else:
            for g in girls:
                g_frame = QFrame(self.girls_content)
                g_frame.setFrameShape(QFrame.StyledPanel)
                g_frame.setObjectName("card-frame")
                
                g_layout = QHBoxLayout(g_frame)
                g_layout.setContentsMargins(6, 6, 6, 6)
                g_layout.setSpacing(10)
                
                g_lbl_layout = QVBoxLayout()
                g_lbl_layout.setContentsMargins(0, 0, 0, 0)
                g_lbl_layout.setSpacing(2)
                
                rel_str = ""
                if self.state.romance.active_partner_name == g.name:
                    rel_str = " ❤️"
                    if g.is_co_owner:
                        rel_str = " 💍 Married"
                
                name_lbl = QLabel(f"<b>{g.name}</b> ({g.archetype}){rel_str}", self)
                desc_lbl = QLabel(f"'{g.description}'", self)
                desc_lbl.setStyleSheet("font-size: 14px; color: #555555; font-style: italic;")
                
                rom_bar = QProgressBar(self)
                rom_bar.setRange(0, 100)
                rom_bar.setValue(int(g.romance_level))
                rom_bar.setFormat("Romance: %v/100")
                rom_bar.setStyleSheet("height: 14px; font-size: 14px;")
                
                g_lbl_layout.addWidget(name_lbl)
                g_lbl_layout.addWidget(desc_lbl)
                g_lbl_layout.addWidget(rom_bar)
                
                g_layout.addLayout(g_lbl_layout)
                
                interact_btn = QPushButton("Interact", self)
                interact_btn.setObjectName("primary-action-btn")
                interact_btn.clicked.connect(lambda checked=False, target_girl=g: self.interact_girl(target_girl))
                g_layout.addWidget(interact_btn, alignment=Qt.AlignRight)
                
                self.girls_scroll_layout.addWidget(g_frame)
                
        # 2. Update Candidates Column
        # Clear layout
        while self.cand_scroll_layout.count():
            item = self.cand_scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        candidates = self.state.employees.candidates
        if not candidates:
            no_cand_lbl = QLabel("No job applicants hanging out tonight.", self)
            no_cand_lbl.setAlignment(Qt.AlignCenter)
            no_cand_lbl.setStyleSheet("font-style: italic; color: #666666; padding: 20px;")
            self.cand_scroll_layout.addWidget(no_cand_lbl)
        else:
            for c in candidates:
                c_frame = QFrame(self.cand_content)
                c_frame.setFrameShape(QFrame.StyledPanel)
                c_frame.setObjectName("card-frame")
                
                c_layout = QHBoxLayout(c_frame)
                c_layout.setContentsMargins(6, 6, 6, 6)
                c_layout.setSpacing(10)
                
                c_lbl_layout = QVBoxLayout()
                c_lbl_layout.setContentsMargins(0, 0, 0, 0)
                c_lbl_layout.setSpacing(2)
                
                name_lbl = QLabel(f"<b>{c.name}</b>", self)
                stats_lbl = QLabel(
                    f"Skill: {c.skill:.2f} | Reliability: {c.reliability:.2f}<br/>"
                    f"Wage: <b>${c.daily_salary:.2f}/day</b> | Exp: {c.experience} yrs",
                    self
                )
                stats_lbl.setStyleSheet("font-size: 14px; color: #555555;")
                
                c_lbl_layout.addWidget(name_lbl)
                c_lbl_layout.addWidget(stats_lbl)
                
                c_layout.addLayout(c_lbl_layout)
                
                hire_btn = QPushButton("Hire", self)
                hire_btn.setObjectName("primary-action-btn")
                max_emp = self.state.restaurant.current_config.max_employees
                hire_btn.setEnabled(len(self.state.employees.hired) < max_emp)
                hire_btn.clicked.connect(lambda checked=False, target_cand=c: self.hire_candidate(target_cand))
                c_layout.addWidget(hire_btn, alignment=Qt.AlignRight)
                
                self.cand_scroll_layout.addWidget(c_frame)
