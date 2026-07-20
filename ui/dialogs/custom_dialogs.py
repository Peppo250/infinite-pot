# ui/dialogs/custom_dialogs.py
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider, QLineEdit, QDoubleSpinBox, QFrame, QComboBox, QScrollArea, QWidget, QProgressBar
from PySide6.QtCore import Qt
from ui.theme import ThemeManager
from ui.audio import UIAudio

class GameDialog(QDialog):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Outer container frame for styling
        self.container = QFrame(self)
        self.container.setObjectName("card-frame")
        self.container.setStyleSheet(f"""
            QFrame#card-frame {{
                background-color: {ThemeManager.CREAM};
                border: 3px solid {ThemeManager.DARK_BROWN};
                border-radius: 16px;
            }}
        """)
        
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        
        # Header title
        self.title_label = QLabel(title, self)
        self.title_label.setObjectName("title-label")
        self.title_label.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {ThemeManager.DARK_BROWN};")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)
        
        # Window layout setup
        window_layout = QVBoxLayout(self)
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.addWidget(self.container)

class ConfirmDialog(GameDialog):
    def __init__(self, title: str, message: str, parent=None):
        super().__init__(title, parent)
        
        self.msg_label = QLabel(message, self)
        self.msg_label.setWordWrap(True)
        self.msg_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.msg_label)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        self.yes_btn = QPushButton("Yes", self)
        self.yes_btn.setObjectName("primary-action-btn")
        self.yes_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.yes_btn)
        
        self.no_btn = QPushButton("No", self)
        self.no_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.no_btn)
        
        self.layout.addLayout(btn_layout)

    def accept(self):
        UIAudio.play_click()
        super().accept()

    def reject(self):
        UIAudio.play_click()
        super().reject()

class TextInputDialog(GameDialog):
    def __init__(self, title: str, label_text: str, default_val: str = "", parent=None):
        super().__init__(title, parent)
        
        self.lbl = QLabel(label_text, self)
        self.layout.addWidget(self.lbl)
        
        self.input_field = QLineEdit(self)
        self.input_field.setText(default_val)
        self.layout.addWidget(self.input_field)
        
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("Confirm", self)
        self.ok_btn.setObjectName("primary-action-btn")
        self.ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.ok_btn)
        
        self.cancel_btn = QPushButton("Cancel", self)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        self.layout.addLayout(btn_layout)

    def get_text(self) -> str:
        return self.input_field.text().strip()

    def accept(self):
        if self.get_text():
            UIAudio.play_click()
            super().accept()

class PriceSliderDialog(GameDialog):
    def __init__(self, current_price: float, min_p: float, max_p: float, parent=None):
        super().__init__("Set Meal Price", parent)
        
        self.min_p = min_p
        self.max_p = max_p
        
        self.info_label = QLabel(f"Recommended price range: ${min_p:.2f} - ${max_p:.2f}", self)
        self.info_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.info_label)
        
        # Display of currently selected price
        self.price_display = QLabel(f"${current_price:.2f}", self)
        self.price_display.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {ThemeManager.DARK_BROWN};")
        self.price_display.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.price_display)
        
        # Slider setup (using integers for precision, scaling by 100)
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setMinimum(int(max(0.5, min_p - 5.0) * 100))
        self.slider.setMaximum(int((max_p + 10.0) * 100))
        self.slider.setValue(int(current_price * 100))
        self.slider.valueChanged.connect(self.on_slider_changed)
        self.layout.addWidget(self.slider)
        
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save Price", self)
        self.save_btn.setObjectName("primary-action-btn")
        self.save_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("Cancel", self)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        self.layout.addLayout(btn_layout)

    def on_slider_changed(self, val: int):
        price = val / 100.0
        self.price_display.setText(f"${price:.2f}")
        
        # Color warning if pricing is excessively above max
        if price > self.max_p:
            self.price_display.setStyleSheet("font-size: 24px; font-weight: bold; color: #E25E3E;")
        else:
            self.price_display.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {ThemeManager.DARK_BROWN};")

    def get_price(self) -> float:
        return self.slider.value() / 100.0

    def accept(self):
        UIAudio.play_coin()
        super().accept()

class LoanDialog(GameDialog):
    def __init__(self, action: str, max_amount: float, parent=None):
        title = "Borrow Bank Loan" if action == "borrow" else "Repay Bank Loan"
        super().__init__(title, parent)
        
        self.action = action
        self.max_amount = max_amount
        
        self.info_label = QLabel(f"Available limit: ${max_amount:.2f}", self)
        self.info_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.info_label)
        
        self.amount_box = QDoubleSpinBox(self)
        self.amount_box.setRange(1.0, max_amount)
        self.amount_box.setValue(min(100.0, max_amount))
        self.amount_box.setPrefix("$")
        self.amount_box.setSingleStep(50.0)
        self.layout.addWidget(self.amount_box)
        
        btn_layout = QHBoxLayout()
        self.confirm_btn = QPushButton("Confirm Transaction", self)
        self.confirm_btn.setObjectName("primary-action-btn")
        self.confirm_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.confirm_btn)
        
        self.cancel_btn = QPushButton("Cancel", self)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        self.layout.addLayout(btn_layout)

    def get_amount(self) -> float:
        return self.amount_box.value()

    def accept(self):
        UIAudio.play_coin()
        super().accept()

class ChoicesDialog(GameDialog):
    def __init__(self, title: str, description: str, choices: list[str], parent=None):
        super().__init__(title, parent)
        
        self.desc_label = QLabel(description, self)
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("font-size: 15px; margin-bottom: 10px;")
        self.layout.addWidget(self.desc_label)
        
        self.chosen_index = -1
        
        # Add buttons for choices
        for i, choice_text in enumerate(choices):
            btn = QPushButton(choice_text, self)
            btn.setObjectName("choice-btn")
            btn.setStyleSheet(f"""
                QPushButton#choice-btn {{
                    text-align: left;
                    padding: 12px;
                    border: 2px solid {ThemeManager.WARM_BEIGE};
                    background-color: white;
                }}
                QPushButton#choice-btn:hover {{
                    background-color: {ThemeManager.WARM_BEIGE};
                }}
            """)
            # Use default parameter in lambda to capture index correctly
            btn.clicked.connect(lambda checked=False, idx=i: self.on_choice_selected(idx))
            self.layout.addWidget(btn)
            
        self.cancel_btn = QPushButton("Back / Dismiss", self)
        self.cancel_btn.clicked.connect(self.reject)
        self.layout.addWidget(self.cancel_btn)

    def on_choice_selected(self, index: int):
        UIAudio.play_click()
        self.chosen_index = index
        self.accept()

class ReceiptDialog(GameDialog):
    def __init__(self, daily_report: str, parent=None):
        super().__init__("Daily Financial Ledger", parent)
        
        self.report_label = QLabel(daily_report, self)
        self.report_label.setStyleSheet("font-family: Courier, monospace; font-size: 13px; line-height: 1.3;")
        self.report_label.setWordWrap(True)
        self.layout.addWidget(self.report_label)
        
        self.ok_btn = QPushButton("Acknowledge & Continue", self)
        self.ok_btn.setObjectName("primary-action-btn")
        self.ok_btn.clicked.connect(self.accept)
        self.layout.addWidget(self.ok_btn)

    def accept(self):
        UIAudio.play_click()
        super().accept()

class PlaceUpgradesDialog(GameDialog):
    def __init__(self, state, parent=None):
        super().__init__("Place Upgrades & Modifications", parent)
        self.state = state
        self.resize(500, 520)
        
        # 1. Modify Shop Name
        name_frame = QFrame(self)
        name_frame.setStyleSheet("border: 2px solid #5B3923; padding: 5px;")
        name_layout = QHBoxLayout(name_frame)
        name_layout.addWidget(QLabel("Diner Name:", self))
        self.name_edit = QLineEdit(self.state.restaurant.name, self)
        self.name_edit.setStyleSheet("background-color: white; border: 2px solid #5B3923; font-size: 16px; padding: 3px;")
        name_layout.addWidget(self.name_edit)
        save_name_btn = QPushButton("Save Name", self)
        save_name_btn.clicked.connect(self.on_save_name)
        name_layout.addWidget(save_name_btn)
        self.layout.addWidget(name_frame)
        
        # 2. Location upgrades
        loc_frame = QFrame(self)
        loc_frame.setStyleSheet("border: 2px solid #5B3923; padding: 5px;")
        loc_layout = QVBoxLayout(loc_frame)
        self.loc_lbl = QLabel(self)
        loc_layout.addWidget(self.loc_lbl)
        self.loc_btn = QPushButton(self)
        self.loc_btn.clicked.connect(self.on_upgrade_location)
        loc_layout.addWidget(self.loc_btn)
        self.layout.addWidget(loc_frame)

        # 2.5 House purchase section
        self.house_frame = QFrame(self)
        self.house_frame.setStyleSheet("border: 2px solid #5B3923; padding: 5px;")
        house_layout = QVBoxLayout(self.house_frame)
        self.house_lbl = QLabel(self)
        house_layout.addWidget(self.house_lbl)
        self.house_btn = QPushButton("Purchase Cottage (-$2500.00)", self)
        self.house_btn.clicked.connect(self.on_purchase_house)
        house_layout.addWidget(self.house_btn)
        self.layout.addWidget(self.house_frame)
        
        # 3. Buyable shop upgrades list (Scroll area)
        up_lbl = QLabel("<b>Available Diner Upgrades:</b>", self)
        self.layout.addWidget(up_lbl)
        
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(5)
        self.scroll.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll)
        
        # Add Close button
        close_btn = QPushButton("Close Upgrades", self)
        close_btn.clicked.connect(self.accept)
        self.layout.addWidget(close_btn)
        
        self.update_ui()
        
    def on_save_name(self):
        new_name = self.name_edit.text().strip()
        if new_name:
            self.state.restaurant.name = new_name
            UIAudio.play_success()
            ConfirmDialog("Success", f"Restaurant renamed to '{new_name}'!", self).exec()
            p_win = self.parent()
            while p_win and not hasattr(p_win, 'update_hud'):
                p_win = p_win.parent()
            if p_win and hasattr(p_win, 'update_hud'):
                p_win.update_hud()
                
    def on_purchase_house(self):
        p = self.state.player
        h = self.state.house
        if p.cash >= 2500.0:
            p.adjust_cash(-2500.0)
            h.purchased = True
            p.has_house = True
            self.state.finance.record_transaction("Upgrade", 2500.0, "Purchased cottage")
            UIAudio.play_coin()
            ConfirmDialog("Success", "Congratulations! You purchased a cozy cottage. Home navigation is now unlocked!", self).exec()
            self.update_ui()
            p_win = self.parent()
            while p_win and not hasattr(p_win, 'update_hud'):
                p_win = p_win.parent()
            if p_win and hasattr(p_win, 'update_hud'):
                p_win.update_hud()
            
    def update_ui(self):
        r = self.state.restaurant
        p = self.state.player
        h = self.state.house
        partner = self.state.romance.partner
        
        # Location details
        lvl = r.level
        max_level = 4
        if lvl < max_level:
            next_lvl = lvl + 1
            level_names = {
                1: "Second-Hand Roadside Cart",
                2: "Own Roadside Cart",
                3: "Edge-of-Town Shop",
                4: "Town Restaurant"
            }
            costs = {1: 100.0, 2: 300.0, 3: 900.0, 4: 2500.0}
            cost = costs.get(next_lvl, 99999.0)
            self.loc_lbl.setText(f"Current Location: <b>Level {lvl} - {r.current_config.name}</b><br/>Next Tier: <b>Level {next_lvl} - {level_names[next_lvl]}</b>")
            self.loc_btn.setText(f"Upgrade to Level {next_lvl} (-${cost:.2f})")
            self.loc_btn.setEnabled(p.cash >= cost)
        else:
            self.loc_lbl.setText(f"Location: <b>Level {lvl} - {r.current_config.name}</b> (MAX TIER)")
            self.loc_btn.setText("Max Location Reached")
            self.loc_btn.setEnabled(False)
            
        # Update house details
        if h.purchased:
            self.house_lbl.setText("House Status: <b>Cozy Cottage Purchased</b> 🏡")
            self.house_btn.setText("Cottage Purchased")
            self.house_btn.setEnabled(False)
        else:
            if partner is None:
                self.house_lbl.setText("House Status: <b>Locked</b><br/>(Requires a romantic relationship first!)")
                self.house_btn.setEnabled(False)
                self.house_btn.setText("Purchase Cottage")
            else:
                self.house_lbl.setText("House Status: <b>Cottage Available</b> 🏡")
                self.house_btn.setEnabled(p.cash >= 2500.0)
                self.house_btn.setText("Purchase Cottage (-$2500.00)")
                
        # Scroll list
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Load shop upgrades
        upgrades = self.state.config.get("upgrades", {}).get("business", [])
        for item_data in upgrades:
            item_id = item_data["id"]
            if item_id in r.upgrades:
                continue # Already owned
            if lvl < item_data.get("min_level", 0):
                continue # Unlocked at higher levels
                
            f = QFrame(self.scroll_content)
            f.setStyleSheet("border: 1px solid #5B3923; padding: 4px;")
            fl = QHBoxLayout(f)
            fl.setContentsMargins(4,4,4,4)
            
            lbl = QLabel(f"<b>{item_data['name']}</b><br/><font size='11'>{item_data['description']}</font>", self)
            fl.addWidget(lbl, stretch=3)
            
            btn = QPushButton(f"Buy\n-${item_data['cost']:.0f}", self)
            btn.clicked.connect(lambda chk=False, data=item_data: self.buy_upgrade(data))
            btn.setEnabled(p.cash >= item_data["cost"])
            fl.addWidget(btn, stretch=1)
            
            self.scroll_layout.addWidget(f)
            
    def buy_upgrade(self, data):
        p = self.state.player
        r = self.state.restaurant
        cost = data["cost"]
        if p.cash >= cost:
            p.adjust_cash(-cost)
            r.upgrades.append(data["id"])
            self.state.finance.record_transaction("Upgrade", cost, f"Purchased upgrade {data['name']}")
            UIAudio.play_success()
            ConfirmDialog("Success", f"Purchased {data['name']}!", self).exec()
            self.update_ui()
            p_win = self.parent()
            while p_win and not hasattr(p_win, 'update_hud'):
                p_win = p_win.parent()
            if p_win and hasattr(p_win, 'update_hud'):
                p_win.update_hud()
            
    def on_upgrade_location(self):
        r = self.state.restaurant
        p = self.state.player
        next_lvl = r.level + 1
        costs = {1: 100.0, 2: 300.0, 3: 900.0, 4: 2500.0}
        cost = costs.get(next_lvl, 99999.0)
        if p.cash >= cost:
            p.adjust_cash(-cost)
            r.level = next_lvl
            self.state.finance.record_transaction("Upgrade", cost, f"Upgraded diner to Level {next_lvl}")
            UIAudio.play_success()
            ConfirmDialog("Success", f"Upgraded to level {next_lvl}!", self).exec()
            self.update_ui()
            p_win = self.parent()
            while p_win and not hasattr(p_win, 'update_hud'):
                p_win = p_win.parent()
            if p_win and hasattr(p_win, 'update_hud'):
                p_win.update_hud()
                p_win = p_win.parent()
            if p_win and hasattr(p_win, 'update_hud'):
                p_win.update_hud()

class MoneyMgmtDialog(GameDialog):
    def __init__(self, state, parent=None):
        super().__init__("Money Management", parent)
        self.state = state
        self.resize(500, 500)
        
        # 1. Price slider
        price_frame = QFrame(self)
        price_frame.setStyleSheet("border: 2px solid #5B3923; padding: 5px;")
        price_layout = QVBoxLayout(price_frame)
        price_layout.addWidget(QLabel("<b>Set Meal Price:</b>", self))
        
        r = self.state.restaurant
        min_p, max_p = r.price_per_meal_range
        
        self.price_val_lbl = QLabel(f"Current Price: <b>${r.menu_price:.2f}</b> (Range: ${min_p:.2f} - ${max_p:.2f})", self)
        price_layout.addWidget(self.price_val_lbl)
        
        self.price_slider = QSlider(Qt.Horizontal, self)
        self.price_slider.setRange(int(min_p * 10), int(max_p * 10))
        self.price_slider.setValue(int(r.menu_price * 10))
        self.price_slider.valueChanged.connect(self.on_price_changed)
        price_layout.addWidget(self.price_slider)
        self.layout.addWidget(price_frame)
        
        # 2. Loans
        loan_frame = QFrame(self)
        loan_frame.setStyleSheet("border: 2px solid #5B3923; padding: 5px;")
        loan_layout = QVBoxLayout(loan_frame)
        self.loan_lbl = QLabel(self)
        loan_layout.addWidget(self.loan_lbl)
        
        loan_btn_layout = QHBoxLayout()
        self.borrow_btn = QPushButton("Borrow More", self)
        self.borrow_btn.clicked.connect(self.on_borrow)
        loan_btn_layout.addWidget(self.borrow_btn)
        
        self.repay_btn = QPushButton("Repay Principal", self)
        self.repay_btn.clicked.connect(self.on_repay)
        loan_btn_layout.addWidget(self.repay_btn)
        loan_layout.addLayout(loan_btn_layout)
        self.layout.addWidget(loan_frame)
        
        # 3. Buy/Sell Assets
        asset_lbl = QLabel("<b>Financial & Business Assets:</b>", self)
        self.layout.addWidget(asset_lbl)
        
        self.asset_scroll = QScrollArea(self)
        self.asset_scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(5)
        self.asset_scroll.setWidget(self.scroll_content)
        self.layout.addWidget(self.asset_scroll)
        
        # Assets definitions
        self.assets_catalog = [
            {"id": "spices", "name": "Rare Spices Chest", "buy_price": 120.0, "sell_price": 90.0, "desc": "Improves your dish margins and stores value."},
            {"id": "candelabra", "name": "Silver Candelabra", "buy_price": 250.0, "sell_price": 180.0, "desc": "Adds a vintage gleam to your shop. Sellable in pinch."},
            {"id": "barrel", "name": "Vintage Oak Barrel", "buy_price": 450.0, "sell_price": 340.0, "desc": "Highly sought-after aging oak wood. Holds cash value."},
            {"id": "mirror", "name": "Gilded Wall Mirror", "buy_price": 800.0, "sell_price": 600.0, "desc": "A heavy golden mirror. A strong asset buffer."}
        ]
        
        # Close button
        close_btn = QPushButton("Close Money Manager", self)
        close_btn.clicked.connect(self.accept)
        self.layout.addWidget(close_btn)
        
        self.update_ui()
        
    def on_price_changed(self, val):
        self.state.restaurant.menu_price = val / 10.0
        r = self.state.restaurant
        min_p, max_p = r.price_per_meal_range
        self.price_val_lbl.setText(f"Current Price: <b>${r.menu_price:.2f}</b> (Range: ${min_p:.2f} - ${max_p:.2f})")
        
    def update_ui(self):
        p = self.state.player
        r = self.state.restaurant
        loan = self.state.loan
        
        # Loan details
        max_borrow = loan.get_max_borrow_limit(r.level)
        avail_borrow = loan.get_available_borrow_amount(r.level)
        self.loan_lbl.setText(f"Current Loan Debt: <b>${loan.balance:.2f}</b> (Limit: ${max_borrow:.2f})<br/>Interest: {loan.interest_rate_annual*100:.0f}% annual")
        self.borrow_btn.setEnabled(avail_borrow > 0)
        self.repay_btn.setEnabled(loan.balance > 0 and p.cash > 0)
        
        # Assets list
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        for asset in self.assets_catalog:
            own_count = self.state.player_assets.count(asset["id"])
            af = QFrame(self.scroll_content)
            af.setStyleSheet("border: 1px solid #5B3923; padding: 4px;")
            a_layout = QHBoxLayout(af)
            a_layout.setContentsMargins(4,4,4,4)
            
            lbl = QLabel(f"<b>{asset['name']}</b> (Owned: {own_count})<br/><font size='11'>{asset['desc']}</font>", self)
            a_layout.addWidget(lbl, stretch=3)
            
            btn_box = QVBoxLayout()
            buy_btn = QPushButton(f"Buy\n-${asset['buy_price']:.0f}", self)
            buy_btn.clicked.connect(lambda chk=False, a=asset: self.buy_asset(a))
            buy_btn.setEnabled(p.cash >= asset["buy_price"])
            btn_box.addWidget(buy_btn)
            
            sell_btn = QPushButton(f"Sell\n+${asset['sell_price']:.0f}", self)
            sell_btn.clicked.connect(lambda chk=False, a=asset: self.sell_asset(a))
            sell_btn.setEnabled(own_count > 0)
            btn_box.addWidget(sell_btn)
            
            a_layout.addLayout(btn_box, stretch=1)
            self.scroll_layout.addWidget(af)
            
    def buy_asset(self, asset):
        p = self.state.player
        price = asset["buy_price"]
        if p.cash >= price:
            p.adjust_cash(-price)
            self.state.player_assets.append(asset["id"])
            self.state.finance.record_transaction("Misc", -price, f"Bought asset: {asset['name']}")
            UIAudio.play_success()
            ConfirmDialog("Success", f"Purchased {asset['name']}!", self).exec()
            self.update_ui()
            p_win = self.parent()
            while p_win and not hasattr(p_win, 'update_hud'):
                p_win = p_win.parent()
            if p_win and hasattr(p_win, 'update_hud'):
                p_win.update_hud()
            
    def sell_asset(self, asset):
        p = self.state.player
        price = asset["sell_price"]
        if asset["id"] in self.state.player_assets:
            self.state.player_assets.remove(asset["id"])
            p.adjust_cash(price)
            self.state.finance.record_transaction("Misc", price, f"Sold asset: {asset['name']}")
            UIAudio.play_coin()
            ConfirmDialog("Success", f"Sold {asset['name']} for ${price:.2f}!", self).exec()
            self.update_ui()
            p_win = self.parent()
            while p_win and not hasattr(p_win, 'update_hud'):
                p_win = p_win.parent()
            if p_win and hasattr(p_win, 'update_hud'):
                p_win.update_hud()
            
    def on_borrow(self):
        from ui.dialogs.custom_dialogs import LoanDialog
        r = self.state.restaurant
        loan = self.state.loan
        avail = loan.get_available_borrow_amount(r.level)
        dlg = LoanDialog("borrow", avail, self)
        if dlg.exec():
            amt = dlg.get_amount()
            success, msg = loan.borrow(amt, r.level)
            if success:
                self.state.player.adjust_cash(amt)
                self.state.finance.record_transaction("Loan", amt, "Borrowed bank loan")
                UIAudio.play_coin()
                ConfirmDialog("Success", msg, self).exec()
                self.update_ui()
                p_win = self.parent()
                while p_win and not hasattr(p_win, 'update_hud'):
                    p_win = p_win.parent()
                if p_win and hasattr(p_win, 'update_hud'):
                    p_win.update_hud()
            else:
                ConfirmDialog("Failed", msg, self).exec()
                
    def on_repay(self):
        from ui.dialogs.custom_dialogs import LoanDialog
        loan = self.state.loan
        p = self.state.player
        max_repay = min(loan.balance, p.cash)
        dlg = LoanDialog("repay", max_repay, self)
        if dlg.exec():
            amt = dlg.get_amount()
            success, msg, cash_spent = loan.pay_loan(amt, p.cash)
            if success:
                p.adjust_cash(-cash_spent)
                self.state.finance.record_transaction("Loan", cash_spent, "Repaid bank loan")
                UIAudio.play_click()
                ConfirmDialog("Success", msg, self).exec()
                self.update_ui()
                p_win = self.parent()
                while p_win and not hasattr(p_win, 'update_hud'):
                    p_win = p_win.parent()
                if p_win and hasattr(p_win, 'update_hud'):
                    p_win.update_hud()
            else:
                ConfirmDialog("Failed", msg, self).exec()

class RelationshipMgmtDialog(GameDialog):
    def __init__(self, state, parent=None):
        super().__init__("Relationship Management", parent)
        self.state = state
        self.resize(500, 480)
        
        self.info_lbl = QLabel(self)
        self.layout.addWidget(self.info_lbl)
        
        self.progress = QProgressBar(self)
        self.progress.setRange(0, 100)
        self.progress.setStyleSheet("QProgressBar::chunk { background-color: #E25E3E; }")
        self.layout.addWidget(self.progress)
        
        # Activities list
        self.layout.addWidget(QLabel("<b>Dating Activities & Gift-giving:</b>", self))
        
        self.act_scroll = QScrollArea(self)
        self.act_scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(5)
        self.act_scroll.setWidget(self.scroll_content)
        self.layout.addWidget(self.act_scroll)
        
        # Close button
        close_btn = QPushButton("Close Relationship Panel", self)
        close_btn.clicked.connect(self.accept)
        self.layout.addWidget(close_btn)
        
        self.update_ui()
        
    def update_ui(self):
        rom = self.state.romance
        p = self.state.player
        h = self.state.house
        partner = rom.partner
        
        if not partner:
            self.info_lbl.setText("You are currently single. Socialize at the Tavern first!")
            self.progress.setVisible(False)
            self.act_scroll.setVisible(False)
            return
            
        self.progress.setVisible(True)
        self.progress.setValue(int(partner.romance_level))
        self.act_scroll.setVisible(True)
        
        status_str = f"Partner: <b>{partner.name}</b> ({partner.archetype})<br/>Stage: <b>{rom.stage_name}</b>"
        self.info_lbl.setText(status_str)
        
        # Clear activities
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # List of activities
        activities = [
            {"id": "date", "name": "Go on Standard Date", "cost": 80.0, "energy": 25.0, "rom_gain": 12.0, "desc": "Stroll through the town park."},
            {"id": "flowers", "name": "Gift Flowers", "cost": 35.0, "energy": 0.0, "rom_gain": 6.0, "desc": "A fresh bouquet of wild roses."},
            {"id": "choc", "name": "Gift Chocolates", "cost": 60.0, "energy": 0.0, "rom_gain": 10.0, "desc": "Imported sweet dark pralines."},
            {"id": "dinner", "name": "Fine Dining", "cost": 150.0, "energy": 15.0, "rom_gain": 22.0, "desc": "A candlelit dinner at the grand hotel."},
            {"id": "poetry", "name": "Recite Love Poetry", "cost": 0.0, "energy": 10.0, "rom_gain": 5.0, "desc": "Write custom couplets (costs energy)."}
        ]
        
        for act in activities:
            af = QFrame(self.scroll_content)
            af.setStyleSheet("border: 1px solid #5B3923; padding: 4px;")
            al = QHBoxLayout(af)
            al.setContentsMargins(4,4,4,4)
            
            lbl = QLabel(f"<b>{act['name']}</b><br/><font size='11'>{act['desc']} (Needs ${act['cost']:.0f}, {act['energy']:.0f} Energy)</font>", self)
            al.addWidget(lbl, stretch=3)
            
            btn = QPushButton(f"Run\n+{act['rom_gain']:.0f} Rom", self)
            btn.clicked.connect(lambda chk=False, a=act: self.run_activity(a))
            btn.setEnabled(p.cash >= act["cost"] and p.energy >= act["energy"])
            al.addWidget(btn, stretch=1)
            self.scroll_layout.addWidget(af)
            
        # Propose buttons
        pf = QFrame(self.scroll_content)
        pf.setStyleSheet("border: 1px solid #E25E3E; padding: 5px;")
        pl = QVBoxLayout(pf)
        pl.addWidget(QLabel("<b>Relationship Proposals:</b>", self))
        
        if not partner.is_partner and not partner.is_co_owner:
            btn_prop = QPushButton("Ask her to be your Partner (Need >=40 Romance)", self)
            btn_prop.clicked.connect(lambda: self.on_propose_dating(partner.name))
            btn_prop.setEnabled(partner.romance_level >= 40.0)
            pl.addWidget(btn_prop)
        elif partner.is_partner and not partner.is_co_owner:
            btn_marry = QPushButton("Propose Marriage (Need >=75 Romance, Ring & House)", self)
            btn_marry.clicked.connect(self.on_propose_marriage)
            btn_marry.setEnabled(rom.has_ring and h.purchased and partner.romance_level >= 75.0)
            pl.addWidget(btn_marry)
        else:
            pl.addWidget(QLabel("🌹 You are happily married!", self))
            
        self.scroll_layout.addWidget(pf)
        
    def run_activity(self, act):
        p = self.state.player
        rom = self.state.romance
        partner = rom.partner
        
        p.adjust_cash(-act["cost"])
        p.adjust_energy(-act["energy"])
        partner.romance_level = min(100.0, partner.romance_level + act["rom_gain"])
        self.state.finance.record_transaction("Date", act["cost"], f"Romance activity: {act['name']}")
        
        UIAudio.play_success()
        ConfirmDialog("Activity Success", f"You chose: {act['name']}.\n\nRomance increased by +{act['rom_gain']:.1f}!", self).exec()
        self.update_ui()
        p_win = self.parent()
        while p_win and not hasattr(p_win, 'update_hud'):
            p_win = p_win.parent()
        if p_win and hasattr(p_win, 'update_hud'):
            p_win.update_hud()
        
    def on_propose_dating(self, name):
        success, msg = self.state.romance.propose_relationship(name)
        if success:
            UIAudio.play_success()
            ConfirmDialog("Success!", msg, self).exec()
        else:
            ConfirmDialog("Rejection", msg, self).exec()
        self.update_ui()
        p_win = self.parent()
        while p_win and not hasattr(p_win, 'update_hud'):
            p_win = p_win.parent()
        if p_win and hasattr(p_win, 'update_hud'):
            p_win.update_hud()
        
    def on_propose_marriage(self):
        h = self.state.house
        success, msg = self.state.romance.ask_to_co_own(h.purchased)
        if success:
            UIAudio.play_success()
            ConfirmDialog("Success!", msg, self).exec()
        else:
            ConfirmDialog("Rejection", msg, self).exec()
        self.update_ui()
        p_win = self.parent()
        while p_win and not hasattr(p_win, 'update_hud'):
            p_win = p_win.parent()
        if p_win and hasattr(p_win, 'update_hud'):
            p_win.update_hud()

class OptionsDialog(GameDialog):
    def __init__(self, parent=None):
        super().__init__("Settings Options", parent)
        self.resize(400, 380)
        
        # 1. Resolutions
        self.layout.addWidget(QLabel("<b>Resolution:</b>", self))
        self.res_combo = QComboBox(self)
        self.res_combo.addItems(["1000 x 700", "1280 x 900", "800 x 600"])
        self.layout.addWidget(self.res_combo)
        
        # 2. Window Mode
        self.layout.addWidget(QLabel("<b>Window Mode:</b>", self))
        self.mode_combo = QComboBox(self)
        self.mode_combo.addItems(["Windowed", "Fullscreen"])
        self.layout.addWidget(self.mode_combo)
        
        # 3. Audio settings
        self.layout.addWidget(QLabel("<b>Music Volume:</b>", self))
        self.music_slider = QSlider(Qt.Horizontal, self)
        self.music_slider.setRange(0, 100)
        self.music_slider.setValue(80)
        self.layout.addWidget(self.music_slider)
        
        self.layout.addWidget(QLabel("<b>Sound Effects Volume:</b>", self))
        self.sfx_slider = QSlider(Qt.Horizontal, self)
        self.sfx_slider.setRange(0, 100)
        self.sfx_slider.setValue(90)
        self.layout.addWidget(self.sfx_slider)
        
        # 3.5. World Speed Settings
        p_win_speed = self.parent()
        while p_win_speed and not hasattr(p_win_speed, 'world_speed'):
            p_win_speed = p_win_speed.parent()
        current_speed = getattr(p_win_speed, "world_speed", 1.0) if p_win_speed else 1.0
        
        self.speed_widget = QWidget(self)
        speed_lay = QHBoxLayout(self.speed_widget)
        speed_lay.setContentsMargins(0, 0, 0, 0)
        self.speed_lbl = QLabel(f"<b>World Speed: {int(current_speed)}x</b>", self)
        self.speed_lbl.setMinimumWidth(150)
        self.speed_slider = QSlider(Qt.Horizontal, self)
        self.speed_slider.setRange(1, 20)
        self.speed_slider.setValue(int(current_speed))
        self.speed_slider.valueChanged.connect(self.on_speed_changed)
        speed_lay.addWidget(self.speed_lbl)
        speed_lay.addWidget(self.speed_slider)
        self.layout.addWidget(self.speed_widget)
        
        # 4. Quit Game
        quit_btn = QPushButton("Quit Game to Desktop", self)
        quit_btn.setObjectName("quit-btn")
        quit_btn.clicked.connect(self.on_quit)
        self.layout.addWidget(quit_btn)
        
        # 5. Apply & Close
        apply_btn = QPushButton("Save Settings", self)
        apply_btn.clicked.connect(self.on_apply)
        self.layout.addWidget(apply_btn)
        
        close_btn = QPushButton("Close Options", self)
        close_btn.clicked.connect(self.accept)
        self.layout.addWidget(close_btn)
        
    def on_speed_changed(self, val):
        self.speed_lbl.setText(f"<b>World Speed: {val}x</b>")
        
    def on_apply(self):
        UIAudio.play_success()
        # Apply resolution
        res_str = self.res_combo.currentText()
        w, h = map(int, res_str.replace(" ", "").split("x"))
        
        # Safely locate MainWindow parent
        p_win = self.parent()
        while p_win and not p_win.isWindow():
            p_win = p_win.parent()
            
        if p_win:
            p_win.resize(w, h)
            # Apply fullscreen
            if self.mode_combo.currentText() == "Fullscreen":
                p_win.showFullScreen()
            else:
                p_win.showNormal()
                
            # Apply world speed
            p_win.world_speed = float(self.speed_slider.value())
            if hasattr(p_win, 'day_clock_timer') and p_win.day_clock_timer.isActive():
                interval_ms = int(10000 / p_win.world_speed)
                p_win.day_clock_timer.start(interval_ms)
            
        ConfirmDialog("Settings Saved", "Graphics, audio, and speed settings applied successfully!", self).exec()
        self.accept()
        
    def on_quit(self):
        confirm = ConfirmDialog("Exit Game", "Are you sure you want to quit the game?", self)
        if confirm.exec():
            p_win = self.parent()
            while p_win and not p_win.isWindow():
                p_win = p_win.parent()
            if p_win:
                p_win.close()
            else:
                self.close()
