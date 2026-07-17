from dataclasses import dataclass, field
from typing import Any

@dataclass
class BusinessUpgrade:
    id: str
    name: str
    cost: float
    attraction_bonus: float
    daily_maintenance: float
    min_level: int
    description: str

@dataclass
class RestaurantLevelConfig:
    level: int
    name: str
    upgrade_cost: float
    daily_maintenance: float
    customer_capacity: int
    max_employees: int
    price_per_meal_range: tuple[float, float]
    base_attraction: float

@dataclass
class Restaurant:
    level: int = 0
    reputation: float = 20.0  # 0 to 100
    menu_price: float = 2.0
    upgrades: list[str] = field(default_factory=list)
    available_upgrades: list[BusinessUpgrade] = field(default_factory=list)
    level_configs: dict[int, RestaurantLevelConfig] = field(default_factory=dict)
    meals_served_today: int = 0
    revenue_today: float = 0.0
    custom_name: str = ""

    @property
    def name(self) -> str:
        return self.custom_name if self.custom_name else self.current_config.name

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "Restaurant":
        lvls_cfg = config.get("restaurant_levels", {})
        upgrades_cfg = config.get("upgrades", {}).get("business", [])
        
        configs = {}
        for lvl_str, cfg in lvls_cfg.items():
            lvl = int(lvl_str)
            configs[lvl] = RestaurantLevelConfig(
                level=lvl,
                name=cfg["name"],
                upgrade_cost=cfg["upgrade_cost"],
                daily_maintenance=cfg["daily_maintenance"],
                customer_capacity=cfg["customer_capacity"],
                max_employees=cfg["max_employees"],
                price_per_meal_range=tuple(cfg["price_per_meal_range"]),
                base_attraction=cfg["base_attraction"]
            )
            
        upgrades_list = [
            BusinessUpgrade(
                id=u["id"],
                name=u["name"],
                cost=u["cost"],
                attraction_bonus=u["attraction_bonus"],
                daily_maintenance=u["daily_maintenance"],
                min_level=u["min_level"],
                description=u["description"]
            )
            for u in upgrades_cfg
        ]
        
        # Start at lowest level, default price is mid-range of that level
        start_lvl = min(configs.keys()) if configs else 0
        start_cfg = configs[start_lvl]
        default_price = sum(start_cfg.price_per_meal_range) / 2.0

        return cls(
            level=start_lvl,
            reputation=20.0,
            menu_price=round(default_price, 2),
            upgrades=[],
            available_upgrades=upgrades_list,
            level_configs=configs
        )

    @property
    def current_config(self) -> RestaurantLevelConfig:
        return self.level_configs[self.level]

    @property
    def customer_capacity(self) -> int:
        base_cap = self.current_config.customer_capacity
        if "super_cooker" in self.upgrades:
            base_cap += 30
        return base_cap

    @property
    def price_per_meal_range(self) -> tuple[float, float]:
        min_p, max_p = self.current_config.price_per_meal_range
        if "sebastian_recipes" in self.upgrades:
            max_p = max_p + 5.0
        return min_p, max_p

    def upgrade_level(self, player_cash: float) -> tuple[bool, str, float]:
        """Tries to upgrade to the next level. Returns (success, message, cost)."""
        next_lvl = self.level + 1
        if next_lvl not in self.level_configs:
            return False, "You have reached the maximum restaurant level!", 0.0

        next_cfg = self.level_configs[next_lvl]
        if player_cash < next_cfg.upgrade_cost:
            return False, f"Insufficient funds to upgrade! Need ${next_cfg.upgrade_cost:.2f}.", 0.0

        self.level = next_lvl
        # Adjust default menu price to the new level's mid range
        mid_price = sum(next_cfg.price_per_meal_range) / 2.0
        self.menu_price = round(mid_price, 2)
        return True, f"Congratulations! Upgraded to level {self.level} - {next_cfg.name}!", next_cfg.upgrade_cost

    def buy_upgrade(self, upgrade_id: str, player_cash: float) -> tuple[bool, str, float]:
        """Tries to purchase a business upgrade. Returns (success, message, cost)."""
        if upgrade_id in self.upgrades:
            return False, "You already have this upgrade.", 0.0

        # Find upgrade
        upgrade = next((u for u in self.available_upgrades if u.id == upgrade_id), None)
        if not upgrade:
            return False, "Upgrade not found.", 0.0

        if self.level < upgrade.min_level:
            return False, f"This upgrade requires {self.level_configs[upgrade.min_level].name} (Level {upgrade.min_level}).", 0.0

        if player_cash < upgrade.cost:
            return False, f"Insufficient funds! Needs ${upgrade.cost:.2f}.", 0.0

        self.upgrades.append(upgrade_id)
        return True, f"Successfully purchased {upgrade.name}!", upgrade.cost

    def calculate_attraction(self, competitor_impact: float = 0.0) -> float:
        """Calculates the total customer attraction rate (chance of a customer arriving)."""
        cfg = self.current_config
        
        # Upgrades bonus
        upgrades_bonus = 0.0
        for u_id in self.upgrades:
            u = next((item for item in self.available_upgrades if item.id == u_id), None)
            if u:
                upgrades_bonus += u.attraction_bonus

        # Reputation bonus (up to +0.20 at 100 reputation, -0.20 at 0 reputation)
        reputation_bonus = (self.reputation - 50.0) / 250.0

        # Pricing impact: check if menu price is out of range
        min_p, max_p = self.price_per_meal_range
        price_impact = 0.0
        if self.menu_price > max_p:
            overprice = self.menu_price - max_p
            # Significant penalty for overpricing
            price_impact = -0.15 * overprice
        elif self.menu_price < min_p:
            underprice = min_p - self.menu_price
            # Minor boost for cheap meals
            price_impact = 0.05 * underprice

        total_attraction = cfg.base_attraction + upgrades_bonus + reputation_bonus + price_impact - competitor_impact
        # Cap attraction between 0.05 (5% minimum) and 1.0 (100% maximum)
        return max(0.05, min(1.0, total_attraction))

    def calculate_daily_maintenance(self) -> float:
        """Calculates daily maintenance costs (base level cost + upgrades cost)."""
        base = self.current_config.daily_maintenance
        upgrades_maintenance = 0.0
        for u_id in self.upgrades:
            u = next((item for item in self.available_upgrades if item.id == u_id), None)
            if u:
                upgrades_maintenance += u.daily_maintenance
        return base + upgrades_maintenance

    def adjust_reputation(self, amount: float) -> None:
        """Adjusts reputation, bounding it between 0.0 and 100.0."""
        self.reputation = max(0.0, min(100.0, self.reputation + amount))
