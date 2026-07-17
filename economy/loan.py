from dataclasses import dataclass
from typing import Any

@dataclass
class LoanSystem:
    balance: float = 0.0
    interest_rate_annual: float = 0.15
    max_loan_ratio: float = 0.5

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "LoanSystem":
        loans_cfg = config.get("loans", {})
        return cls(
            balance=0.0,
            interest_rate_annual=loans_cfg.get("annual_interest_rate", 0.15),
            max_loan_ratio=loans_cfg.get("max_loan_ratio", 0.5)
        )

    def get_max_borrow_limit(self, restaurant_level: int) -> float:
        """Returns the maximum debt the player can carry based on restaurant level."""
        # Level 0 (Street Peddler): Max loan $0
        # Level 1 (Second-Hand Cart): Max loan $50
        # Level 2 (Own Cart): Max loan $200
        # Level 3 (Edge-of-Town Shop): Max loan $800
        # Level 4 (Town Restaurant): Max loan $2500
        limits = {0: 0.0, 1: 50.0, 2: 200.0, 3: 800.0, 4: 2500.0}
        return limits.get(restaurant_level, 0.0)

    def get_available_borrow_amount(self, restaurant_level: int) -> float:
        """Returns how much more the player can borrow."""
        return max(0.0, self.get_max_borrow_limit(restaurant_level) - self.balance)

    def borrow(self, amount: float, restaurant_level: int) -> tuple[bool, str]:
        """Tries to borrow the specified amount."""
        if amount <= 0:
            return False, "Amount must be greater than zero."
        
        limit = self.get_available_borrow_amount(restaurant_level)
        if amount > limit:
            return False, f"Cannot borrow ${amount:.2f}. Limit exceeded. Max additional borrow: ${limit:.2f}."

        self.balance += amount
        return True, f"Borrowed ${amount:.2f} successfully. Daily interest will be charged."

    def pay_loan(self, amount: float, player_cash: float) -> tuple[bool, str, float]:
        """Tries to pay off part or all of the loan. Returns (success, message, cash_spent)."""
        if amount <= 0:
            return False, "Amount must be greater than zero.", 0.0

        if amount > self.balance:
            amount = self.balance  # Cap payment at current balance

        if player_cash < amount:
            return False, f"Insufficient cash to make a payment of ${amount:.2f}.", 0.0

        self.balance -= amount
        return True, f"Paid ${amount:.2f} off your loan. Remaining balance: ${self.balance:.2f}.", amount

    def apply_daily_interest(self) -> float:
        """Applies daily interest rate to the balance. Returns the interest charged."""
        if self.balance <= 0:
            return 0.0
        
        daily_rate = self.interest_rate_annual / 365.0
        interest = self.balance * daily_rate
        self.balance += interest
        return interest
