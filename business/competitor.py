from dataclasses import dataclass
from typing import Any

@dataclass
class CompetitorSystem:
    name: str = "Bistro Gourmet"
    owner: str = "Chef Sebastian"
    is_active: bool = False
    base_marketing_budget: float = 50.0
    base_market_share_drain: float = 0.15
    marketing_counteraction_cost: float = 40.0
    reputation_impact_factor: float = 0.2
    counter_marketing_active: bool = False
    times_encountered: int = 0

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "CompetitorSystem":
        comp_cfg = config.get("competitor", {})
        return cls(
            name=comp_cfg.get("name", "Bistro Gourmet"),
            owner=comp_cfg.get("owner", "Chef Sebastian"),
            is_active=False,
            base_marketing_budget=comp_cfg.get("base_marketing_budget", 50.0),
            base_market_share_drain=comp_cfg.get("base_market_share_drain", 0.15),
            marketing_counteraction_cost=comp_cfg.get("marketing_counteraction_cost", 40.0),
            reputation_impact_factor=comp_cfg.get("reputation_impact_factor", 0.2)
        )

    def check_unlock_conditions(self, restaurant_level: int, has_partner: bool, has_house: bool) -> bool:
        """Determines if the competitor should unlock today."""
        if self.is_active:
            return False
        
        # Unlocks when player has level 4 restaurant, a partner (relationship level >= 3), and a house
        if restaurant_level >= 4 and has_partner and has_house:
            self.is_active = True
            return True
        return False

    def activate_counter_marketing(self, current_cash: float) -> tuple[bool, str, float]:
        """Player pays to counter the competitor's marketing for the day."""
        if not self.is_active:
            return False, "There is no competitor in town to market against yet.", 0.0

        if self.counter_marketing_active:
            return False, "You have already set up counter-marketing for today.", 0.0

        if current_cash < self.marketing_counteraction_cost:
            return False, f"Insufficient cash! Need ${self.marketing_counteraction_cost:.2f} for counter-marketing.", 0.0

        self.counter_marketing_active = True
        return True, f"Counter-marketing active! You set up local flyers and special promotions to offset {self.name}'s presence.", self.marketing_counteraction_cost

    def get_attraction_drain(self) -> float:
        """Returns the reduction in the player's attraction coefficient caused by the competitor."""
        if not self.is_active:
            return 0.0
        
        if self.counter_marketing_active:
            # Counter-marketing reduces competitor impact by 80%
            return self.base_market_share_drain * 0.2
        else:
            return self.base_market_share_drain

    def reset_day(self) -> None:
        """Resets daily actions (like player's counter marketing) for the next day."""
        self.counter_marketing_active = False
