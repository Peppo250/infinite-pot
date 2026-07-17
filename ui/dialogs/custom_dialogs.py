# ui/dialogs/custom_dialogs.py
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider, QLineEdit, QDoubleSpinBox, QFrame
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
