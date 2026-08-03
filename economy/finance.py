from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Transaction:
    timestamp: str
    category: str  # "Revenue", "Wages", "Maintenance", "Loan Interest", "Marketing", "Upgrade", "Date", "Misc"
    amount: float
    description: str

@dataclass
class DailyLedger:
    revenue: float = 0.0
    wages: float = 0.0
    maintenance: float = 0.0      # Diner fixed maintenance / permits
    loan_interest: float = 0.0    # Loan interest & repayment
    marketing: float = 0.0
    misc: float = 0.0
    upgrades_purchased: float = 0.0
    dates: float = 0.0
    household: float = 0.0        # Lifestyle inflation/mortgage
    utilities: float = 0.0        # Base utilities + power
    cleaning: float = 0.0         # Cleaning costs

    def reset(self) -> None:
        self.revenue = 0.0
        self.wages = 0.0
        self.maintenance = 0.0
        self.loan_interest = 0.0
        self.marketing = 0.0
        self.misc = 0.0
        self.upgrades_purchased = 0.0
        self.dates = 0.0
        self.household = 0.0
        self.utilities = 0.0
        self.cleaning = 0.0

    @property
    def total_expenses(self) -> float:
        return (self.wages + self.maintenance + self.loan_interest + 
                self.marketing + self.misc + self.upgrades_purchased + 
                self.dates + self.household + self.utilities + self.cleaning)

    @property
    def net_profit(self) -> float:
        return self.revenue - self.total_expenses

@dataclass
class FinancialSystem:
    daily_ledger: DailyLedger = field(default_factory=DailyLedger)
    history: list[Transaction] = field(default_factory=list)

    def record_transaction(self, category: str, amount: float, description: str) -> None:
        """Records a transaction in the global transaction log and updates the current day's ledger."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history.append(Transaction(timestamp, category, amount, description))
        
        # Update daily ledger (amount can be positive or negative, but we record magnitudes)
        val = abs(amount)
        if category == "Revenue":
            self.daily_ledger.revenue += val
        elif category == "Wages":
            self.daily_ledger.wages += val
        elif category == "Maintenance":
            self.daily_ledger.maintenance += val
        elif category == "Loan Interest":
            self.daily_ledger.loan_interest += val
        elif category == "Marketing":
            self.daily_ledger.marketing += val
        elif category == "Upgrade":
            self.daily_ledger.upgrades_purchased += val
        elif category == "Date":
            self.daily_ledger.dates += val
        elif category == "Household":
            self.daily_ledger.household += val
        elif category == "Utilities":
            self.daily_ledger.utilities += val
        elif category == "Cleaning":
            self.daily_ledger.cleaning += val
        else:
            self.daily_ledger.misc += val

    def get_daily_report(self) -> str:
        """Returns a string formatted daily financial report."""
        dl = self.daily_ledger
        net = dl.net_profit
        sign = "+" if net >= 0 else "-"
        
        report = []
        report.append("=" * 40)
        report.append("         DAILY CASH FLOW STATEMENT       ")
        report.append("=" * 40)
        report.append("  REVENUE:")
        report.append(f"    Meals & Tips:        +${dl.revenue:8.2f}")
        report.append(f"    ----------------------------------")
        report.append(f"    Total Revenue:       +${dl.revenue:8.2f}")
        report.append("")
        
        fixed_sum = dl.maintenance + dl.utilities + dl.loan_interest + dl.household
        report.append("  FIXED EXPENSES:")
        report.append(f"    Rent & Permits:      -${dl.maintenance:8.2f}")
        report.append(f"    Base Utilities:      -${dl.utilities:8.2f}")
        report.append(f"    Loan Servicing:      -${dl.loan_interest:8.2f}")
        report.append(f"    Household Expenses:  -${dl.household:8.2f}")
        report.append(f"    ----------------------------------")
        report.append(f"    Total Fixed:         -${fixed_sum:8.2f}")
        report.append("")
        
        var_sum = dl.wages + dl.cleaning + dl.misc + dl.dates + dl.upgrades_purchased + dl.marketing
        report.append("  VARIABLE EXPENSES:")
        report.append(f"    Employee Wages:      -${dl.wages:8.2f}")
        report.append(f"    Power & Cleaning:    -${dl.cleaning:8.2f}")
        if dl.marketing > 0:
            report.append(f"    Marketing / Promo:   -${dl.marketing:8.2f}")
        if dl.dates > 0:
            report.append(f"    Dates:               -${dl.dates:8.2f}")
        if dl.upgrades_purchased > 0:
            report.append(f"    Upgrades:            -${dl.upgrades_purchased:8.2f}")
        if dl.misc > 0:
            report.append(f"    Unexpected Events:   -${dl.misc:8.2f}")
        report.append(f"    ----------------------------------")
        report.append(f"    Total Variable:      -${var_sum:8.2f}")
        report.append("")
        
        report.append("-" * 40)
        report.append(f"  NET DAILY PROFIT:      {sign}${abs(net):8.2f}")
        report.append("=" * 40)
        return "\n".join(report)

    def start_new_day(self) -> None:
        """Resets the daily ledger for the next business day."""
        self.daily_ledger.reset()
