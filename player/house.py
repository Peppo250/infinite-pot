from dataclasses import dataclass, field
from typing import Any

@dataclass
class HouseUpgrade:
    id: str
    name: str
    cost: float
    energy_recovery_bonus: float
    romance_progress_bonus: float
    description: str

@dataclass
class HouseSystem:
    purchased: bool = False
    cost: float = 3000.0
    daily_maintenance: float = 25.0
    upgrades: list[str] = field(default_factory=list)
    available_upgrades: list[HouseUpgrade] = field(default_factory=list)

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "HouseSystem":
        house_cfg = config.get("house_purchase", {})
        upgrades_cfg = config.get("upgrades", {}).get("house", [])
        
        upgrades_list = [
            HouseUpgrade(
                id=u["id"],
                name=u["name"],
                cost=u["cost"],
                energy_recovery_bonus=u["energy_recovery_bonus"],
                romance_progress_bonus=u["romance_progress_bonus"],
                description=u["description"]
            )
            for u in upgrades_cfg
        ]
        
        return cls(
            purchased=False,
            cost=house_cfg.get("cost", 3000.0),
            daily_maintenance=house_cfg.get("daily_maintenance", 25.0),
            upgrades=[],
            available_upgrades=upgrades_list
        )

    def buy_upgrade(self, upgrade_id: str, current_cash: float) -> tuple[bool, str, float]:
        """Tries to buy a house upgrade. Returns (success, message, cost)."""
        if not self.purchased:
            return False, "You need to purchase a house first!", 0.0
            
        if upgrade_id in self.upgrades:
            return False, "You already own this upgrade.", 0.0

        # Find upgrade
        upgrade = next((u for u in self.available_upgrades if u.id == upgrade_id), None)
        if not upgrade:
            return False, "Upgrade not found.", 0.0

        if current_cash < upgrade.cost:
            return False, f"Insufficient cash! Needs ${upgrade.cost:.2f}.", 0.0

        self.upgrades.append(upgrade_id)
        return True, f"Successfully purchased {upgrade.name}!", upgrade.cost

    def get_energy_recovery_bonus(self) -> float:
        """Returns total energy recovery bonus from purchased upgrades."""
        bonus = 0.0
        for u_id in self.upgrades:
            upgrade = next((u for u in self.available_upgrades if u.id == u_id), None)
            if upgrade:
                bonus += upgrade.energy_recovery_bonus
        return bonus

    def get_romance_progress_bonus(self) -> float:
        """Returns cumulative percentage bonus for romance progress (e.g. 0.15 means +15%)."""
        bonus = 0.0
        for u_id in self.upgrades:
            upgrade = next((u for u in self.available_upgrades if u.id == u_id), None)
            if upgrade:
                bonus += upgrade.romance_progress_bonus
        return bonus
