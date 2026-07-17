# ui/screens/business_menu.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget, QScrollArea, QFrame, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt, Signal
from ui.theme import ThemeManager
from ui.audio import UIAudio
from ui.dialogs.custom_dialogs import PriceSliderDialog, LoanDialog, ConfirmDialog

class BusinessMenuScreen(QWidget):
    go_back = Signal()
    state_changed = Signal()  # Emitted when state is modified (e.g. bought upgrade, took loan)
    
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
        
        self.title = QLabel("Business Management", self)
        self.title.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {ThemeManager.DARK_BROWN};")
        header_layout.addWidget(self.title, alignment=Qt.AlignRight)
        main_layout.addLayout(header_layout)
        
        # Tab Widget
        self.tabs = QTabWidget(self)
        
        # TAB 1: Upgrades & Pricing
        self.upgrades_tab = QWidget()
        self.init_upgrades_tab()
        self.tabs.addTab(self.upgrades_tab, "Upgrades & Pricing")
        
        # TAB 2: Staffing
        self.staff_tab = QWidget()
        self.init_staff_tab()
        self.tabs.addTab(self.staff_tab, "Staff & Payroll")
        
        # TAB 3: Loans
        self.loans_tab = QWidget()
        self.init_loans_tab()
        self.tabs.addTab(self.loans_tab, "Bank & Loans")
        
        # TAB 4: Marketing (Competitor)
        self.marketing_tab = QWidget()
        self.init_marketing_tab()
        self.tabs.addTab(self.marketing_tab, "Marketing")
        
        main_layout.addWidget(self.tabs)
        
        self.update_ui()

    def init_upgrades_tab(self):
        layout = QVBoxLayout(self.upgrades_tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Pricing Control Row
        pricing_card = QFrame(self)
        pricing_card.setObjectName("card-frame")
        pricing_layout = QHBoxLayout(pricing_card)
        
        self.pricing_lbl = QLabel("Menu Meal Price: $2.50\nRange: $2.50 - $4.00", self)
        self.pricing_lbl.setStyleSheet("font-weight: bold;")
        pricing_layout.addWidget(self.pricing_lbl)
        
        self.adjust_price_btn = QPushButton("Set Meal Price", self)
        self.adjust_price_btn.setObjectName("primary-action-btn")
        self.adjust_price_btn.clicked.connect(self.on_adjust_price)
        pricing_layout.addWidget(self.adjust_price_btn, alignment=Qt.AlignRight)
        
        layout.addWidget(pricing_card)
        
        # Level Upgrade Row
        lvl_card = QFrame(self)
        lvl_card.setObjectName("card-frame")
        lvl_layout = QHBoxLayout(lvl_card)
        
        self.lvl_lbl = QLabel("Current Tier: Level 0 - Peddler", self)
        self.lvl_lbl.setStyleSheet("font-weight: bold;")
        lvl_layout.addWidget(self.lvl_lbl)
        
        self.upgrade_lvl_btn = QPushButton("Upgrade Level", self)
        self.upgrade_lvl_btn.clicked.connect(self.on_upgrade_level)
        lvl_layout.addWidget(self.upgrade_lvl_btn, alignment=Qt.AlignRight)
        
        layout.addWidget(lvl_card)
        
        # Scroll Area for Business Upgrades
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        
        scroll.setWidget(self.scroll_content)
        layout.addWidget(QLabel("Available Equipment & Customizations:", self))
        layout.addWidget(scroll)

    def init_staff_tab(self):
        layout = QVBoxLayout(self.staff_tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        self.staff_summary = QLabel("Hired Staff: 0/1 | Total Salary: $0.00/day", self)
        self.staff_summary.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.staff_summary)
        
        # Hired staff list
        self.staff_list = QListWidget(self)
        layout.addWidget(self.staff_list)
        
        # Recruitment alert
        rec_lbl = QLabel("💡 New candidate applicants are available at the local Tavern in the evening.", self)
        rec_lbl.setStyleSheet("font-style: italic; color: #666666;")
        layout.addWidget(rec_lbl)

    def init_loans_tab(self):
        layout = QVBoxLayout(self.loans_tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        loans_card = QFrame(self)
        loans_card.setObjectName("card-frame")
        self.loans_layout = QVBoxLayout(loans_card)
        self.loans_layout.setSpacing(10)
        
        self.loans_lbl = QLabel("Outstanding Loan: $0.00\nDaily Interest: 15% APR\nRequired Minimum Payment: $0.00/day", self)
        self.loans_lbl.setStyleSheet("font-size: 15px; font-weight: bold; line-height: 1.5;")
        self.loans_layout.addWidget(self.loans_lbl)
        
        btn_layout = QHBoxLayout()
        self.borrow_btn = QPushButton("Borrow Cash", self)
        self.borrow_btn.setObjectName("primary-action-btn")
        self.borrow_btn.clicked.connect(self.on_borrow_loan)
        btn_layout.addWidget(self.borrow_btn)
        
        self.repay_btn = QPushButton("Repay Loan", self)
        self.repay_btn.clicked.connect(self.on_repay_loan)
        btn_layout.addWidget(self.repay_btn)
        
        self.loans_layout.addLayout(btn_layout)
        layout.addWidget(loans_card)

    def init_marketing_tab(self):
        layout = QVBoxLayout(self.marketing_tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        marketing_card = QFrame(self)
        marketing_card.setObjectName("card-frame")
        self.mktg_layout = QVBoxLayout(marketing_card)
        self.mktg_layout.setSpacing(12)
        
        self.mktg_lbl = QLabel("Chef Sebastian is currently inactive.", self)
        self.mktg_lbl.setStyleSheet("font-size: 15px; font-weight: bold;")
        self.mktg_layout.addWidget(self.mktg_lbl)
        
        self.counter_btn = QPushButton("Run Counter-Marketing Campaign (-$40.00)", self)
        self.counter_btn.setObjectName("primary-action-btn")
        self.counter_btn.clicked.connect(self.on_counter_marketing)
        self.mktg_layout.addWidget(self.counter_btn)
        
        layout.addWidget(marketing_card)

    def on_adjust_price(self):
        r = self.state.restaurant
        min_p, max_p = r.price_per_meal_range
        dlg = PriceSliderDialog(r.menu_price, min_p, max_p, self)
        if dlg.exec():
            r.menu_price = dlg.get_price()
            self.update_ui()
            self.state_changed.emit()

    def on_upgrade_level(self):
        r = self.state.restaurant
        p = self.state.player
        next_lvl = r.level + 1
        if next_lvl not in r.level_configs:
            return
            
        next_cfg = r.level_configs[next_lvl]
        dlg = ConfirmDialog(
            "Upgrade Restaurant Level",
            f"Are you sure you want to upgrade to Level {next_lvl} - {next_cfg.name}?\n\n"
            f"Cost: ${next_cfg.upgrade_cost:.2f}\n"
            f"Allowed Pricing: ${next_cfg.price_per_meal_range[0]:.2f} - ${next_cfg.price_per_meal_range[1]:.2f}\n"
            f"Max Employees: {next_cfg.max_employees}\n"
            f"Capacity: {next_cfg.customer_capacity} seats",
            self
        )
        if dlg.exec():
            success, msg, cost = r.upgrade_level(p.cash)
            if success:
                p.adjust_cash(-cost)
                self.state.finance.record_transaction("Upgrade", cost, f"Upgraded to Level {next_lvl}")
                UIAudio.play_success()
                self.update_ui()
                self.state_changed.emit()

    def on_borrow_loan(self):
        p = self.state.player
        r = self.state.restaurant
        loan = self.state.loan
        max_borrow = loan.get_available_borrow_amount(r.level)
        if max_borrow <= 0:
            ConfirmDialog("Bank Limit", "You have reached your maximum borrowing limit based on assets.", self).exec()
            return
            
        dlg = LoanDialog("borrow", max_borrow, self)
        if dlg.exec():
            amount = dlg.get_amount()
            success, msg = loan.borrow(amount, r.level)
            if success:
                p.adjust_cash(amount)
                self.state.finance.record_transaction("Loan", amount, "Borrowed bank loan")
                self.update_ui()
                self.state_changed.emit()
            else:
                ConfirmDialog("Transaction Refused", msg, self).exec()

    def on_repay_loan(self):
        p = self.state.player
        loan = self.state.loan
        bal = loan.balance
        if bal <= 0:
            ConfirmDialog("Debt Free", "You do not have any outstanding loan balance to repay.", self).exec()
            return
            
        max_repay = min(p.cash, bal)
        if max_repay <= 0:
            ConfirmDialog("No Cash", "You do not have enough cash to make any loan repayments.", self).exec()
            return
            
        dlg = LoanDialog("repay", max_repay, self)
        if dlg.exec():
            amount = dlg.get_amount()
            success, msg, cash_spent = loan.pay_loan(amount, p.cash)
            if success:
                p.adjust_cash(-cash_spent)
                self.state.finance.record_transaction("Loan", cash_spent, "Repaid bank loan")
                self.update_ui()
                self.state_changed.emit()
            else:
                ConfirmDialog("Transaction Refused", msg, self).exec()

    def on_counter_marketing(self):
        p = self.state.player
        c = self.state.competitor
        cost = c.marketing_counteraction_cost
        if p.cash < cost:
            ConfirmDialog("Insufficient Funds", f"You need ${cost:.2f} to launch counter marketing.", self).exec()
            return
            
        p.adjust_cash(-cost)
        c.counter_marketing_active = True
        self.state.finance.record_transaction("Marketing", cost, "Countered Sebastian's marketing campaign")
        UIAudio.play_success()
        self.update_ui()
        self.state_changed.emit()

    def buy_upgrade(self, upgrade_id: str):
        p = self.state.player
        r = self.state.restaurant
        success, msg, cost = r.buy_upgrade(upgrade_id, p.cash)
        if success:
            p.adjust_cash(-cost)
            self.state.finance.record_transaction("Upgrade", cost, f"Purchased upgrade {upgrade_id}")
            UIAudio.play_success()
            self.update_ui()
            self.state_changed.emit()
        else:
            ConfirmDialog("Purchase Failed", msg, self).exec()

    def fire_staff(self, name: str):
        dlg = ConfirmDialog("Fire Employee", f"Are you sure you want to fire {name}?", self)
        if dlg.exec():
            success, msg = self.state.employees.fire_employee(name)
            if success:
                UIAudio.play_click()
                self.update_ui()
                self.state_changed.emit()

    def update_ui(self):
        p = self.state.player
        r = self.state.restaurant
        es = self.state.employees
        loans = self.state.loan
        c = self.state.competitor
        
        # 1. Update Pricing Tab Info
        min_p, max_p = r.price_per_meal_range
        self.pricing_lbl.setText(f"Menu Meal Price: ${r.menu_price:.2f}\nRecommended Price Range: ${min_p:.2f} - ${max_p:.2f}")
        
        # Level Upgrade Info
        next_lvl = r.level + 1
        if next_lvl in r.level_configs:
            self.lvl_lbl.setText(f"Current Tier: Level {r.level} - {r.current_config.name}\nNext Tier Upgrade Cost: ${r.level_configs[next_lvl].upgrade_cost:.2f}")
            self.upgrade_lvl_btn.setEnabled(p.cash >= r.level_configs[next_lvl].upgrade_cost)
            self.upgrade_lvl_btn.setText(f"Upgrade Level (${r.level_configs[next_lvl].upgrade_cost:.1f})")
        else:
            self.lvl_lbl.setText(f"Current Tier: Level {r.level} - {r.current_config.name}\n(Maximum Level Reached!)")
            self.upgrade_lvl_btn.setEnabled(False)
            self.upgrade_lvl_btn.setText("Maximum Level")
            
        # Draw Scrollable Business Upgrades
        # First clear layout
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Fill upgrades list
        for u in r.available_upgrades:
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
            
            # Action button
            if u.id in r.upgrades:
                status_btn = QPushButton("Purchased", self)
                status_btn.setEnabled(False)
                u_layout.addWidget(status_btn, alignment=Qt.AlignRight)
            else:
                buy_btn = QPushButton("Buy Upgrade", self)
                buy_btn.setObjectName("primary-action-btn")
                buy_btn.setEnabled(p.cash >= u.cost and r.level >= u.min_level)
                # Use default param to bind upgrade.id correctly
                buy_btn.clicked.connect(lambda checked=False, uid=u.id: self.buy_upgrade(uid))
                u_layout.addWidget(buy_btn, alignment=Qt.AlignRight)
                
            self.scroll_layout.addWidget(u_frame)
            
        # 2. Update Staffing Tab Info
        max_emp = r.current_config.max_employees
        self.staff_summary.setText(f"Hired Staff: {len(es.hired)}/{max_emp} | Total Salary: ${es.calculate_daily_payroll():.2f}/day")
        self.staff_list.clear()
        for emp in es.hired:
            item = QListWidgetItem(self.staff_list)
            # Custom widget for employee item
            emp_widget = QWidget()
            emp_layout = QHBoxLayout(emp_widget)
            emp_layout.setContentsMargins(5, 5, 5, 5)
            
            txt_layout = QVBoxLayout()
            name_lbl = QLabel(f"<b>{emp.name}</b> (Salary: ${emp.daily_salary:.2f}/day)", self)
            stat_lbl = QLabel(f"Skill: {emp.skill:.2f} | Reliability: {emp.reliability:.2f} | Exp: {emp.experience} yrs", self)
            stat_lbl.setStyleSheet("font-size: 12px; color: #555555;")
            txt_layout.addWidget(name_lbl)
            txt_layout.addWidget(stat_lbl)
            
            emp_layout.addLayout(txt_layout)
            
            fire_btn = QPushButton("Fire", self)
            fire_btn.setObjectName("quit-btn")
            fire_btn.clicked.connect(lambda checked=False, ename=emp.name: self.fire_staff(ename))
            emp_layout.addWidget(fire_btn, alignment=Qt.AlignRight)
            
            item.setSizeHint(emp_widget.sizeHint())
            self.staff_list.addItem(item)
            self.staff_list.setItemWidget(item, emp_widget)
            
        # 3. Update Loans Tab Info
        self.loans_lbl.setText(
            f"Outstanding Balance: ${loans.balance:.2f}\n"
            f"Interest Rate: {loans.interest_rate_annual*100:.1f}% APR (${loans.balance*(loans.interest_rate_annual/365.0):.2f}/day accrue)"
        )
        self.repay_btn.setEnabled(loans.balance > 0 and p.cash > 0)
        
        # 4. Update Marketing Tab Info
        if c.is_active:
            self.tabs.setTabEnabled(3, True)
            if c.counter_marketing_active:
                self.mktg_lbl.setText("Sebastian is running an active campaign, but you have deployed Counter-Marketing for today!")
                self.counter_btn.setEnabled(False)
                self.counter_btn.setText("Counter Campaign Active")
            else:
                self.mktg_lbl.setText(f"Chef Sebastian is actively draining your market share! (-1.0 reputation/day)\nCampaign Counteraction Cost: ${c.marketing_counteraction_cost:.2f}")
                self.counter_btn.setEnabled(p.cash >= c.marketing_counteraction_cost)
                self.counter_btn.setText(f"Run Counter-Marketing Campaign (-${c.marketing_counteraction_cost:.1f})")
        else:
            self.tabs.setTabEnabled(3, False)
            self.mktg_lbl.setText("Chef Sebastian is currently quiet. No competitive threats present.")
            self.counter_btn.setEnabled(False)
