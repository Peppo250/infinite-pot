from dataclasses import dataclass, field

@dataclass
class PlayerStats:
    cash: float
    energy: float
    max_energy: float = 100.0
    daily_energy_cost: float = 20.0
    work_energy_cost_per_hour: float = 5.0
    sleep_energy_recovery: float = 80.0
    has_house: bool = False
    house_upgrades: list[str] = field(default_factory=list)
    romance_level: float = 0.0  # 0 to 100
    relationship_stage_index: int = 0
    days_worked: int = 0

    def adjust_cash(self, amount: float) -> bool:
        """Adjusts player's cash. Returns True if successful, False if insufficient cash."""
        if self.cash + amount < 0:
            return False
        self.cash += amount
        return True

    def adjust_energy(self, amount: float) -> None:
        """Adjusts energy, keeping it bounded between 0 and max_energy."""
        self.energy = max(0.0, min(self.max_energy, self.energy + amount))

    def recover_sleep(self, bonus: float = 0.0) -> None:
        """Recovers energy at the end of the day."""
        recovery = self.sleep_energy_recovery + bonus
        self.adjust_energy(recovery)
        # Deduct a base daily cost of living from energy (representing fatigue buildup)
        self.adjust_energy(-self.daily_energy_cost)
