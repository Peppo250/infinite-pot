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
    
    # Dynamic Sebastian Behavior
    active_action: str = "None"  # None, Renovation, Marketing, Live Music
    action_days_left: int = 0
    permanent_attraction_drain: float = 0.0
    reputation_expectation_boost: float = 0.0

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
            self.active_action = "None"
            self.action_days_left = 0
            return True
        return False

    def roll_sebastian_action(self) -> str:
        """Sebastian rolls a new strategy based on his priorities (Luxury 40%, Marketing 35%, Consistency 25%)."""
        if not self.is_active:
            return ""
            
        import random
        choice = random.choices(
            ["Renovation", "Marketing", "Live Music"],
            weights=[40, 35, 25]
        )[0]
        
        self.active_action = choice
        if choice == "Renovation":
            self.action_days_left = 999  # Permanent until player counters
            self.permanent_attraction_drain = 0.05
            self.reputation_expectation_boost = 0.0
            return f"Chef Sebastian renovated Bistro Gourmet's facade to project premium luxury! Your diner's attraction is drained by 5% permanently until you renovate to counter it."
        elif choice == "Marketing":
            self.action_days_left = 4
            self.permanent_attraction_drain = 0.0
            self.reputation_expectation_boost = 0.0
            return f"Chef Sebastian launched an aggressive Bistro Gourmet Advertising Blitz! Your attraction is reduced by 12% for the next 4 days."
        elif choice == "Live Music":
            self.action_days_left = 5
            self.permanent_attraction_drain = 0.0
            self.reputation_expectation_boost = 0.5
            return f"Chef Sebastian hired a premium live harpist, raising local dining standards! You will lose 0.5 reputation daily for the next 5 days due to higher expectations."
            
        return ""

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

    def player_renovate_counter(self, current_cash: float) -> tuple[bool, str, float]:
        """Player pays $200.00 to renovate their diner, countering Sebastian's renovation drain."""
        if not self.is_active:
            return False, "No competitor facade to counter.", 0.0
        if self.permanent_attraction_drain <= 0.0:
            return False, "Your diner's aesthetic is already matching the competition.", 0.0
        if current_cash < 200.0:
            return False, "Insufficient cash! Renovations cost $200.00.", 0.0
            
        self.permanent_attraction_drain = 0.0
        return True, "You renovated your diner, matching Bistro Gourmet's premium look and negating their attraction drain!", 200.0

    def get_attraction_drain(self) -> float:
        """Returns the reduction in the player's attraction coefficient caused by the competitor."""
        if not self.is_active:
            return 0.0
            
        drain = self.base_market_share_drain + self.permanent_attraction_drain
        
        if self.active_action == "Marketing" and self.action_days_left > 0:
            drain += 0.12
            
        if self.counter_marketing_active:
            # Counter-marketing reduces competitor impact by 80%
            return drain * 0.2
        else:
            return drain

    def reset_day(self) -> None:
        """Resets daily actions (like player's counter marketing) and decrements active action durations."""
        self.counter_marketing_active = False
        if self.action_days_left > 0:
            self.action_days_left -= 1
            if self.action_days_left == 0:
                self.active_action = "None"
                self.reputation_expectation_boost = 0.0
