# ui/screens/personal_life_menu.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar, QFrame, QScrollArea
from PySide6.QtCore import Qt, Signal
from ui.theme import ThemeManager
from ui.audio import UIAudio
from ui.dialogs.custom_dialogs import ConfirmDialog

class PersonalLifeScreen(QWidget):
    go_back = Signal()
    state_changed = Signal()  # Emitted when upgrades or relationships shift
    open_wedding_planner = Signal()
    
    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.state = state
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header with Back button
        header_layout = QHBoxLayout()
        self.back_btn = QPushButton("← Back to Hub", self)
        self.back_btn.clicked.connect(self.go_back.emit)
        header_layout.addWidget(self.back_btn)
        
        self.title = QLabel("Personal Life", self)
        self.title.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {ThemeManager.DARK_BROWN};")
        header_layout.addWidget(self.title, alignment=Qt.AlignRight)
        main_layout.addLayout(header_layout)
        
        # Split layout for Romance and House
        split_layout = QHBoxLayout()
        split_layout.setSpacing(20)
        
        # LEFT COLUMN: Romance & Relationships
        self.romance_card = QFrame(self)
        self.romance_card.setObjectName("card-frame")
        self.rom_layout = QVBoxLayout(self.romance_card)
        self.rom_layout.setSpacing(12)
        
        rom_title = QLabel("🌹 Dating & Romance", self)
        rom_title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {ThemeManager.DARK_BROWN};")
        self.rom_layout.addWidget(rom_title)
        
        self.rom_lbl = QLabel("You are currently single.", self)
        self.rom_lbl.setWordWrap(True)
        self.rom_lbl.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.rom_layout.addWidget(self.rom_lbl)
        
        # Romance meter / Progress Bar
        self.rom_progress = QProgressBar(self)
        self.rom_progress.setRange(0, 100)
        self.rom_layout.addWidget(self.rom_progress)
        
        # Action Buttons
        self.date_btn = QPushButton("💖 Go on a Date (-$100.00 | 25 Energy)", self)
        self.date_btn.setObjectName("primary-action-btn")
        self.date_btn.clicked.connect(self.on_go_date)
        self.rom_layout.addWidget(self.date_btn)
        
        self.ring_btn = QPushButton("💍 Buy Diamond Engagement Ring (-$2500.00)", self)
        self.ring_btn.clicked.connect(self.on_buy_ring)
        self.rom_layout.addWidget(self.ring_btn)
        
        self.propose_btn = QPushButton("Propose Marriage & Co-Ownership", self)
        self.propose_btn.clicked.connect(self.on_propose)
        self.rom_layout.addWidget(self.propose_btn)
        
        self.wedding_btn = QPushButton("💒 Plan and Host Wedding Ceremony", self)
        self.wedding_btn.setObjectName("primary-action-btn")
        self.wedding_btn.clicked.connect(self.open_wedding_planner.emit)
        self.rom_layout.addWidget(self.wedding_btn)
        
        self.break_btn = QPushButton("Break Up", self)
        self.break_btn.setObjectName("quit-btn")
        self.break_btn.clicked.connect(self.on_break_up)
        self.rom_layout.addWidget(self.break_btn)
        
        self.rom_layout.addStretch()
        split_layout.addWidget(self.romance_card, stretch=1)
        
        # RIGHT COLUMN: Home & Real Estate
        self.house_card = QFrame(self)
        self.house_card.setObjectName("card-frame")
        self.house_layout = QVBoxLayout(self.house_card)
        self.house_layout.setSpacing(12)
        
        house_title = QLabel("🏡 Home & Real Estate", self)
        house_title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {ThemeManager.DARK_BROWN};")
        self.house_layout.addWidget(house_title)
        
        self.house_lbl = QLabel("You sleep on the floor of your shop.", self)
        self.house_lbl.setWordWrap(True)
        self.house_lbl.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.house_layout.addWidget(self.house_lbl)
        
        self.buy_house_btn = QPushButton("Purchase Cottage (-$4000.00)", self)
        self.buy_house_btn.setObjectName("primary-action-btn")
        self.buy_house_btn.clicked.connect(self.on_buy_house)
        self.house_layout.addWidget(self.buy_house_btn)
        
        # Scroll area for house upgrades
        self.upgrades_lbl = QLabel("Available Home Furnishings & Addons:", self)
        self.house_layout.addWidget(self.upgrades_lbl)
        
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        self.house_layout.addWidget(self.scroll)
        
        self.house_layout.addStretch()
        split_layout.addWidget(self.house_card, stretch=1)
        
        main_layout.addLayout(split_layout)
        
        self.update_ui()

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
            self.update_ui()
            self.state_changed.emit()
        else:
            ConfirmDialog("Cannot Date", msg, self).exec()

    def on_buy_ring(self):
        p = self.state.player
        rom = self.state.romance
        if p.cash < 2500.0:
            ConfirmDialog("Insufficient Cash", "A Diamond Engagement Ring costs $2,500.00.", self).exec()
            return
            
        p.adjust_cash(-2500.0)
        rom.has_ring = True
        self.state.finance.record_transaction("Upgrade", 2500.0, "Bought Diamond Engagement Ring")
        UIAudio.play_coin()
        UIAudio.play_success()
        ConfirmDialog("Engagement Ring", f"You purchased a stunning Diamond Engagement Ring for {rom.partner_name}!", self).exec()
        self.update_ui()
        self.state_changed.emit()

    def on_propose(self):
        h = self.state.house
        rom = self.state.romance
        success, msg = rom.ask_to_co_own(h.purchased)
        if success:
            UIAudio.play_success()
            ConfirmDialog("Proposal Accepted!", msg, self).exec()
            self.update_ui()
            self.state_changed.emit()
        else:
            ConfirmDialog("Proposal Declined", msg, self).exec()

    def on_buy_house(self):
        p = self.state.player
        h = self.state.house
        if p.cash < h.cost:
            ConfirmDialog("Insufficient Cash", f"Buying a house requires ${h.cost:.2f}.", self).exec()
            return
            
        p.adjust_cash(-h.cost)
        h.purchased = True
        p.has_house = True
        self.state.finance.record_transaction("Upgrade", h.cost, "Purchased cottage")
        UIAudio.play_coin()
        UIAudio.play_success()
        ConfirmDialog("House Purchased!", f"Congratulations! You bought a cozy cottage on the edge of town! (${h.daily_maintenance:.1f}/day maintenance)", self).exec()
        self.update_ui()
        self.state_changed.emit()

    def on_break_up(self):
        rom = self.state.romance
        dlg = ConfirmDialog("Break Up", f"Are you sure you want to break up with {rom.partner_name}?\nThis is permanent and will severely impact romance levels.", self)
        if dlg.exec():
            success, msg = rom.break_up()
            if success:
                UIAudio.play_click()
                ConfirmDialog("Single", msg, self).exec()
                self.update_ui()
                self.state_changed.emit()

    def buy_house_upgrade(self, upgrade_id: str):
        p = self.state.player
        h = self.state.house
        success, msg, cost = h.buy_upgrade(upgrade_id, p.cash)
        if success:
            p.adjust_cash(-cost)
            self.state.finance.record_transaction("Upgrade", cost, f"Purchased home upgrade {upgrade_id}")
            UIAudio.play_success()
            self.update_ui()
            self.state_changed.emit()
        else:
            ConfirmDialog("Upgrade Failed", msg, self).exec()

    def update_ui(self):
        p = self.state.player
        rom = self.state.romance
        h = self.state.house
        partner = rom.partner
        
        # 1. Update Romance Panel
        if not partner:
            self.rom_lbl.setText("You are currently single.\nVisit the Tavern in the evening to socialize and meet people.")
            self.rom_progress.setVisible(False)
            self.date_btn.setVisible(False)
            self.ring_btn.setVisible(False)
            self.propose_btn.setVisible(False)
            self.wedding_btn.setVisible(False)
            self.break_btn.setVisible(False)
        else:
            self.rom_progress.setVisible(True)
            self.rom_progress.setValue(int(partner.romance_level))
            self.break_btn.setVisible(True)
            self.date_btn.setVisible(True)
            
            status_text = f"Relationship with <b>{partner.name}</b> ({partner.archetype}):<br/>"
            status_text += f"Stage: <b>{rom.stage_name}</b> | Romance: {partner.romance_level:.1f}/100.0<br/>"
            
            if not h.purchased:
                status_text += f"<font color='#E25E3E'>⚠️ Dating without a house causes Romance to decay by -{partner.decay_rate} pts/day!</font>"
                self.ring_btn.setVisible(False)
                self.propose_btn.setVisible(True)
                self.propose_btn.setEnabled(False)
                self.propose_btn.setText("Propose Marriage (Requires House & Ring)")
                self.wedding_btn.setVisible(False)
            else:
                if not rom.is_co_owner:
                    self.ring_btn.setVisible(not rom.has_ring)
                    self.propose_btn.setVisible(True)
                    self.propose_btn.setEnabled(rom.has_ring and partner.romance_level >= 75.0)
                    self.propose_btn.setText("Propose Marriage & Co-Ownership" + ("" if rom.has_ring else " (Needs Ring)"))
                    self.wedding_btn.setVisible(False)
                else:
                    self.ring_btn.setVisible(False)
                    self.propose_btn.setVisible(False)
                    self.wedding_btn.setVisible(rom.wedding_tier == "None")
                    status_text += f"<font color='#8ADAB2'>💚 {partner.name} lives with you and co-owns the restaurant!</font>"
                    if rom.wedding_tier != "None":
                        status_text += f"<br/>Wedding: <b>{rom.wedding_tier} Ceremony</b> hosted!"
                        
            self.rom_lbl.setText(status_text)
            
        # 2. Update House Panel
        if not h.purchased:
            self.house_lbl.setText("You are currently homeless. You sleep on the floor of the restaurant.\nResting restores base energy only.")
            self.buy_house_btn.setVisible(True)
            self.buy_house_btn.setEnabled(p.cash >= h.cost)
            self.upgrades_lbl.setVisible(False)
            self.scroll.setVisible(False)
        else:
            self.house_lbl.setText(f"You own a cozy cottage on the edge of town.\nSleeping fully restores energy to 100%.\nMaintenance: ${h.daily_maintenance:.1f}/day")
            self.buy_house_btn.setVisible(False)
            self.upgrades_lbl.setVisible(True)
            self.scroll.setVisible(True)
            
            # Fill scrollable upgrades list
            # First clear layout
            while self.scroll_layout.count():
                item = self.scroll_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
                    
            for u in h.available_upgrades:
                u_frame = QFrame(self.scroll_content)
                u_frame.setFrameShape(QFrame.StyledPanel)
                u_frame.setObjectName("card-frame")
                
                u_layout = QHBoxLayout(u_frame)
                u_lbl_layout = QVBoxLayout()
                
                name_lbl = QLabel(f"<b>{u.name}</b> (${u.cost:.2f})", self)
                desc_lbl = QLabel(u.description, self)
                desc_lbl.setWordWrap(True)
                desc_lbl.setStyleSheet("font-size: 12px; color: #555555;")
                u_lbl_layout.addWidget(name_lbl)
                u_lbl_layout.addWidget(desc_lbl)
                
                u_layout.addLayout(u_lbl_layout)
                
                if u.id in h.upgrades:
                    status_btn = QPushButton("Owned", self)
                    status_btn.setEnabled(False)
                    u_layout.addWidget(status_btn, alignment=Qt.AlignRight)
                else:
                    buy_btn = QPushButton("Purchase", self)
                    buy_btn.setObjectName("primary-action-btn")
                    buy_btn.setEnabled(p.cash >= u.cost)
                    buy_btn.clicked.connect(lambda checked=False, uid=u.id: self.buy_house_upgrade(uid))
                    u_layout.addWidget(buy_btn, alignment=Qt.AlignRight)
                    
                self.scroll_layout.addWidget(u_frame)
