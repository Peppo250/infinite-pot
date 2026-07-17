from dataclasses import dataclass, field
from typing import Any

@dataclass
class RomanceSystem:
    partner_name: str = "Valerie"
    partner_occupation: str = "Local Florist"
    romance_level: float = 0.0  # 0 to 100
    relationship_stage_index: int = 0
    stages: list[str] = field(default_factory=list)
    milestones: list[float] = field(default_factory=list)
    date_cost: float = 80.0
    energy_cost_for_date: float = 25.0
    is_co_owner: bool = False
    dates_had: int = 0

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "RomanceSystem":
        rom_cfg = config.get("romance", {})
        return cls(
            partner_name=rom_cfg.get("partner_name", "Valerie"),
            partner_occupation=rom_cfg.get("partner_occupation", "Local Florist"),
            romance_level=0.0,
            relationship_stage_index=0,
            stages=rom_cfg.get("relationship_stages", [
                "Stranger", "Acquaintance", "Close Friend", "Partner", "Partner & Business Co-Owner"
            ]),
            milestones=rom_cfg.get("romance_level_milestones", [0, 25, 50, 75, 100]),
            date_cost=rom_cfg.get("date_cost", 80.0),
            energy_cost_for_date=rom_cfg.get("energy_cost_for_date", 25.0)
        )

    @property
    def stage_name(self) -> str:
        if self.is_co_owner:
            return self.stages[-1]
        return self.stages[self.relationship_stage_index]

    def go_on_date(self, current_cash: float, current_energy: float, progress_multiplier: float = 1.0) -> tuple[bool, str, float, float]:
        """Runs a date. Returns (success, message, cash_spent, energy_spent)."""
        if current_cash < self.date_cost:
            return False, f"Insufficient cash for a date! Need ${self.date_cost:.2f}.", 0.0, 0.0
        if current_energy < self.energy_cost_for_date:
            return False, f"Too tired for a date! Need {self.energy_cost_for_date} energy.", 0.0, 0.0

        # Calculate progression
        self.dates_had += 1
        base_progress = 10.0 + (5.0 if self.dates_had <= 3 else 2.0)  # slightly faster early on
        actual_progress = base_progress * progress_multiplier
        self.romance_level = min(100.0, self.romance_level + actual_progress)
        
        # Check stage progression
        self.update_stage()

        msg = f"You had a wonderful date with {self.partner_name} at the local park. (+{actual_progress:.1f} Romance)"
        return True, msg, self.date_cost, self.energy_cost_for_date

    def update_stage(self) -> None:
        """Updates the relationship stage based on romance level (ignoring co-owner which is manual)."""
        if self.is_co_owner:
            self.relationship_stage_index = len(self.stages) - 1
            return

        # Find the highest milestone we've passed
        new_stage = 0
        for i, milestone in enumerate(self.milestones):
            if self.romance_level >= milestone:
                new_stage = i
        
        # Keep it capped at "Partner" (index 3) before asking to co-own (index 4)
        if new_stage >= len(self.stages) - 1:
            new_stage = len(self.stages) - 2

        self.relationship_stage_index = new_stage

    def ask_to_co_own(self, has_house: bool) -> tuple[bool, str]:
        """Player asks Valerie to move in and co-own the business."""
        if self.is_co_owner:
            return False, f"{self.partner_name} is already your partner and business co-owner!"
        
        if self.romance_level < 75.0 or self.relationship_stage_index < 3:
            return False, f"Your relationship isn't close enough yet. (Need stage: 'Partner')"

        if not has_house:
            return False, f"{self.partner_name} appreciates the gesture, but feels you two need a proper house of your own before taking this step."

        self.is_co_owner = True
        self.relationship_stage_index = len(self.stages) - 1
        return True, f"{self.partner_name} happily accepts! She moves into your house and joins the restaurant as a Co-Owner!"
