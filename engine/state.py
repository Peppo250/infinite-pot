import json
import os
import random
from typing import Any

from player.stats import PlayerStats
from player.house import HouseSystem
from player.romance import RomanceSystem
from business.restaurant import Restaurant
from business.employees import EmployeeSystem
from business.competitor import CompetitorSystem
from economy.finance import FinancialSystem
from economy.loan import LoanSystem
from world.town import Town
from events.event_system import EventSystem
from events.event_definitions import get_default_events

class GameState:
    def __init__(self, config_path: str = "") -> None:
        if not config_path:
            # Locate relative to this file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, "data", "balance_config.json")
            
        self.config = self._load_config(config_path)
        
        # Core Systems
        p_cfg = self.config.get("player", {})
        self.player = PlayerStats(
            cash=p_cfg.get("starting_cash", 100.0),
            energy=p_cfg.get("starting_energy", 100.0),
            max_energy=p_cfg.get("starting_energy", 100.0),
            daily_energy_cost=p_cfg.get("daily_energy_cost", 20.0),
            work_energy_cost_per_hour=p_cfg.get("work_energy_cost_per_hour", 5.0),
            sleep_energy_recovery=p_cfg.get("sleep_energy_recovery", 80.0)
        )
        
        self.house = HouseSystem.from_config(self.config)
        self.romance = RomanceSystem.from_config(self.config)
        self.restaurant = Restaurant.from_config(self.config)
        self.employees = EmployeeSystem.from_config(self.config)
        self.competitor = CompetitorSystem.from_config(self.config)
        self.finance = FinancialSystem()
        self.loan = LoanSystem.from_config(self.config)
        self.town = Town()
        self.memory = {}
        self.player_assets = []
        self._time_of_day = "Morning"
        self._season = None
        
        # Event System
        self.events = EventSystem()
        for e in get_default_events():
            self.events.add_event(e)
            
        # Time Management
        self.day: int = 1
        self.week: int = 1
        self.days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        # Economy of Life Variables
        self.free_time: float = 4.0
        self.personal_fulfillment: float = 50.0
        self.days_since_competitor_start: int = 0
        self.days_profitable_streak: int = 0
        
    def _load_config(self, path: str) -> dict[str, Any]:
        """Loads balance_config.json securely, falling back to defaults if error occurs."""
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            # Fallback to minimal default config
            return {
                "player": {"starting_cash": 100.0, "starting_energy": 100.0},
                "restaurant_levels": {
                    "1": {"name": "Roadside Cart", "upgrade_cost": 0.0, "daily_maintenance": 5.0, "customer_capacity": 10, "max_employees": 0, "price_per_meal_range": [3, 6], "base_attraction": 0.3},
                    "2": {"name": "Edge Shop", "upgrade_cost": 200.0, "daily_maintenance": 15.0, "customer_capacity": 25, "max_employees": 1, "price_per_meal_range": [5, 9], "base_attraction": 0.5},
                    "3": {"name": "Restaurant", "upgrade_cost": 1000.0, "daily_maintenance": 60.0, "customer_capacity": 60, "max_employees": 3, "price_per_meal_range": [10, 20], "base_attraction": 0.7}
                },
                "upgrades": {"business": [], "house": []},
                "house_purchase": {"cost": 2500.0, "daily_maintenance": 20.0},
                "loans": {"annual_interest_rate": 0.15, "max_loan_ratio": 0.5},
                "romance": {"date_cost": 75.0, "energy_cost_for_date": 20.0},
                "competitor": {"base_marketing_budget": 40.0, "base_market_share_drain": 0.12}
            }

    @property
    def day_name(self) -> str:
        return self.days_of_week[(self.day - 1) % 7]

    @property
    def season(self) -> str:
        """Determines the current season based on the day (30 days per season)."""
        if hasattr(self, '_season') and self._season is not None:
            return self._season
        cycle = (self.day - 1) // 30 % 4
        if cycle == 0:
            return "Spring"
        elif cycle == 1:
            return "Summer"
        elif cycle == 2:
            return "Autumn"
        else:
            return "Winter"

    @season.setter
    def season(self, val: str) -> None:
        self._season = val

    @property
    def time_of_day(self) -> str:
        return self._time_of_day

    @time_of_day.setter
    def time_of_day(self, val: str) -> None:
        self._time_of_day = val

    def get_max_free_time(self) -> float:
        base = 4.0
        # Time-saving upgrades
        if "industrial_dishwasher" in self.restaurant.upgrades:
            base += 1.0
        if "auto_inventory" in self.restaurant.upgrades:
            base += 0.5
        if "self_service_fountain" in self.restaurant.upgrades:
            base += 0.5
        return base

    def simulate_business_day(self, player_work_hours: int) -> dict[str, Any]:
        """Simulates the business day based on pricing, staff, and marketing status.
        Updates player cash, energy, and restaurant reputation.
        Returns a dictionary summarizing the day's results.
        """
        p = self.romance.partner
        active_employees = self.employees.get_active_employees()
        
        # Calculate Free Time for the evening phase
        max_free = self.get_max_free_time()
        overtime_hours = max(0, player_work_hours - 8)
        self.free_time = max(0.0, max_free - overtime_hours)
        
        if player_work_hours > 10:
            self.personal_fulfillment = max(0.0, self.personal_fulfillment - 2.0)
            
        # Overtime relationship friction memory
        if player_work_hours > 8 and p:
            from player.romance import Memory
            if not any(m.title == "Partner Worked Late" for m in p.memories):
                p.memories.append(Memory(
                    title="Partner Worked Late",
                    category="Everyday",
                    emotion="Disappointed",
                    strength=3.0
                ))
                p.trust = max(0.0, p.trust - 2.0)
        
        # Determine if partner helps in the shop today
        partner_helps_today = False
        if p:
            if p.is_co_owner:
                # Wife helps only during weekends (Friday, Saturday, Sunday) or if player works > 8 hours
                if self.day_name in ["Friday", "Saturday", "Sunday"] or player_work_hours > 8:
                    partner_helps_today = True
            elif p.is_partner and (self.day_name in p.schedule):
                partner_helps_today = True
                
        # 1. Determine customer attraction
        partner_boost = p.attraction_boost if partner_helps_today else 0.0
        drain = self.competitor.get_attraction_drain()
        attraction = self.restaurant.calculate_attraction(competitor_impact=drain) + partner_boost
        
        # Determine total open hours for the day
        open_hours = player_work_hours
        if len(active_employees) > 0 or partner_helps_today:
            # Hired staff or partner working forces the shop open for at least a standard 8-hour shift
            open_hours = max(player_work_hours, 8)
            
        # Special case: if level < 3 (no hired employees) and partner is not helping, and player works 0 hours, the business is closed!
        if self.restaurant.level < 3 and not partner_helps_today and player_work_hours == 0:
            open_hours = 0
        
        # 2. Determine potential customers (scales proportionally with open hours)
        capacity = self.restaurant.customer_capacity
        multiplier = self.town.economic_multiplier
        random_factor = random.uniform(0.85, 1.15)
        
        if open_hours > 0:
            hourly_rate = (capacity / 8.0) * attraction * multiplier
            potential_customers = int(hourly_rate * open_hours * random_factor)
            if potential_customers < 1 and attraction > 0:
                potential_customers = 1
        else:
            potential_customers = 0
            
        # 3. Calculate player energy cost & capacity (takes more energy in lower levels, decreases as you hire more people)
        player_capacity = player_work_hours * 3
        
        level_mults = {0: 1.5, 1: 1.3, 2: 1.1, 3: 0.9, 4: 0.7}
        level_mult = level_mults.get(self.restaurant.level, 1.0)
        
        staff_count = len(active_employees)
        staff_mults = {0: 1.0, 1: 0.8, 2: 0.65, 3: 0.5}
        staff_mult = staff_mults.get(staff_count, 0.5 if staff_count > 3 else 1.0)
        
        hourly_energy_cost = self.player.work_energy_cost_per_hour * level_mult * staff_mult
        player_energy_cost = player_work_hours * hourly_energy_cost
        self.player.adjust_energy(-player_energy_cost)
        
        # 4. Calculate employees capacity (they work up to min(8, open_hours), scaled by part-time status)
        employee_capacity = sum(int(min(8, open_hours) * (2 + e.skill * 4) * (0.5 if e.is_part_time else 1.0)) for e in active_employees)
        
        # 5. Calculate partner's capacity (helps serve up to min(8, open_hours) hours, 4 meals/hour)
        partner_capacity = min(8, open_hours) * 4 if partner_helps_today else 0
        
        # 6. Total service capacity
        total_capacity = player_capacity + employee_capacity + partner_capacity
        
        # 7. Actual customers served (capped by seats available throughout the open hours)
        max_daily_capacity = int(capacity * (open_hours / 8.0)) if open_hours > 0 else 0
        actual_served = min(potential_customers, total_capacity, max_daily_capacity)
        turned_away = max(0, potential_customers - total_capacity)
        
        # 8. Revenue & Tips calculation
        # Add Optional Extras
        extra_spend = 0.0
        if "beverage_station" in self.restaurant.upgrades:
            extra_spend += 1.50
        if "dessert_cabinet" in self.restaurant.upgrades:
            extra_spend += 3.00
        if "appetizer_bar" in self.restaurant.upgrades:
            extra_spend += 4.50
            
        revenue = round(actual_served * (self.restaurant.menu_price + extra_spend), 2)
        
        # Calculate worker quality for tips and reputation
        workers_count = (1 if player_work_hours > 0 else 0) + len(active_employees) + (1 if partner_helps_today else 0)
        if workers_count > 0:
            skills_sum = (0.5 if player_work_hours > 0 else 0.0) + sum(e.skill for e in active_employees) + (0.8 if partner_helps_today else 0.0)
            avg_skill = skills_sum / workers_count
        else:
            avg_skill = 0.3  # poor self-service or closed
            
        tips = 0.0
        if actual_served > 0 and workers_count > 0:
            tip_rate = random.uniform(0.0, 1.5) * (self.restaurant.reputation / 100.0) * avg_skill
            tips = round(actual_served * tip_rate, 2)
            
        total_income = round(revenue + tips, 2)
        
        # Apply income to player stats
        self.player.adjust_cash(total_income)
        self.restaurant.meals_served_today = actual_served
        self.restaurant.revenue_today = total_income
        
        # Degrading decor durability: every 10 customers served drains 1.0% durability
        self.restaurant.decor_durability = max(0.0, self.restaurant.decor_durability - actual_served * 0.1)
        
        # Automatic Bank Loan Repayment from daily sales (percentage increases as you upgrade restaurant)
        loan_payment = 0.0
        if self.loan.balance > 0.0 and total_income > 0.0:
            rates = {0: 0.05, 1: 0.07, 2: 0.10, 3: 0.15, 4: 0.20}
            pct = rates.get(self.restaurant.level, 0.05)
            deduction = round(total_income * pct, 2)
            
            # Cap deduction at current balance
            if deduction > self.loan.balance:
                deduction = self.loan.balance
                
            # Perform payment
            success, msg, loan_payment = self.loan.pay_loan(deduction, self.player.cash)
            if success and loan_payment > 0.0:
                self.player.adjust_cash(-loan_payment)
                self.finance.record_transaction("Loan Interest", loan_payment, f"Auto-repayment from sales ({int(pct*100)}%)")
        
        # Record transactions
        if revenue > 0:
            self.finance.record_transaction("Revenue", revenue, f"Served {actual_served} meals")
        if tips > 0:
            self.finance.record_transaction("Revenue", tips, f"Received tips from {actual_served} customers")
            
        # 9. Reputation adjustments (reverted to old rate)
        rep_change = 0.0
        if actual_served > 0:
            # Good service skill increases rep
            rep_change += 0.03 * actual_served * (avg_skill - 0.4)
            
            # Pricing impact
            max_p = self.restaurant.price_per_meal_range[1]
            if self.restaurant.menu_price > max_p:
                overprice = self.restaurant.menu_price - max_p
                rep_change -= 0.6 * overprice * actual_served
        
        # Turned away customer penalty
        if turned_away > 0:
            rep_change -= 0.12 * turned_away
            
        # Competitor sabotage
        if self.competitor.is_active and not self.competitor.counter_marketing_active:
            rep_change -= 1.0
            
        # Wife help reputation bonus
        if partner_helps_today and p and p.is_co_owner:
            rep_change += 2.0
            
        self.restaurant.adjust_reputation(rep_change)
        self.player.days_worked += 1
        
        return {
            "potential_customers": potential_customers,
            "actual_served": actual_served,
            "turned_away": turned_away,
            "meal_price": self.restaurant.menu_price,
            "revenue": revenue,
            "tips": tips,
            "total_income": total_income,
            "energy_spent": player_energy_cost,
            "rep_change": rep_change,
            "avg_skill": avg_skill
        }

    def simulate_one_hour(self, current_hour: int) -> dict[str, Any]:
        """Simulates 1 hour of the business day.
        Deducts hourly energy cost and processes hourly customers and sales.
        """
        p = self.romance.partner
        active_employees = self.employees.get_active_employees()
        
        # Spouse / Partner helper check
        helping_girls = self.romance.get_helping_characters(self.day_name)
        partner_helps_today = len(helping_girls) > 0
                
        partner_boost = sum(g.attraction_boost * (1.5 if g.is_co_owner else 1.0) for g in helping_girls)
        drain = self.competitor.get_attraction_drain()
        attraction = self.restaurant.calculate_attraction(competitor_impact=drain) + partner_boost
        
        # Characteristic boosts from helping partners/wives
        sales_mult = 1.0
        hourly_rep_gain = 0.0
        for h in helping_girls:
            if h.archetype == "Artist":
                hourly_rep_gain += 0.35 if h.is_co_owner else 0.20
                sales_mult += 0.10 if h.is_co_owner else 0.06
            elif h.archetype == "Scholar":
                hourly_rep_gain += 0.20 if h.is_co_owner else 0.12
                sales_mult += 0.16 if h.is_co_owner else 0.10
            elif h.archetype == "Entrepreneur":
                hourly_rep_gain += 0.12 if h.is_co_owner else 0.08
                sales_mult += 0.24 if h.is_co_owner else 0.16

        # Capacity limits
        capacity = self.restaurant.customer_capacity
        multiplier = self.town.economic_multiplier
        random_factor = random.uniform(0.8, 1.2)
        
        # 1 hour calculation
        hourly_rate = (capacity / 8.0) * attraction * multiplier
        potential_customers = max(1, int(hourly_rate * random_factor))
        
        # Servicing capacity in 1 hour
        player_capacity = 3
        employee_capacity = sum(int((2 + e.skill * 4) * (0.5 if e.is_part_time else 1.0)) for e in active_employees)
        partner_capacity = len(helping_girls) * 4
        total_capacity = player_capacity + employee_capacity + partner_capacity
        
        max_hourly_capacity = max(1, capacity // 8)
        actual_served = min(potential_customers, total_capacity, max_hourly_capacity)
        turned_away = max(0, potential_customers - total_capacity)
        
        # Add Optional Extras
        extra_spend = 0.0
        if "beverage_station" in self.restaurant.upgrades:
            extra_spend += 1.50
        if "dessert_cabinet" in self.restaurant.upgrades:
            extra_spend += 3.00
        if "appetizer_bar" in self.restaurant.upgrades:
            extra_spend += 4.50
            
        revenue = round(actual_served * (self.restaurant.menu_price + extra_spend) * sales_mult, 2)
        
        # Tips
        workers_count = 1 + len(active_employees) + len(helping_girls)
        skills_sum = 0.5 + sum(e.skill for e in active_employees) + (len(helping_girls) * 0.8)
        avg_skill = skills_sum / workers_count
        
        tip_rate = random.uniform(0.0, 1.5) * (self.restaurant.reputation / 100.0) * avg_skill
        tips = round(actual_served * tip_rate, 2)
        
        total_income = round(revenue + tips, 2)
        self.player.adjust_cash(total_income)
        
        # Degrading decor durability: every 10 customers served drains 1.0% durability
        self.restaurant.decor_durability = max(0.0, self.restaurant.decor_durability - actual_served * 0.1)
        
        # Record transactions in real-time
        if revenue > 0:
            self.finance.record_transaction("Revenue", revenue, f"Hour {current_hour}: Served {actual_served} meals")
        if tips > 0:
            self.finance.record_transaction("Revenue", tips, f"Hour {current_hour}: Tips received")
            
        # Rep adjustments
        rep_change = hourly_rep_gain
        if actual_served > 0:
            rep_change += 0.03 * actual_served * (avg_skill - 0.4)
            rep_change += 0.004 * actual_served * (avg_skill - 0.4)
            
            max_p = self.restaurant.price_per_meal_range[1]
            if self.restaurant.menu_price > max_p:
                overprice = self.restaurant.menu_price - max_p
                rep_change -= 0.08 * overprice * actual_served
        
        if turned_away > 0:
            rep_change -= 0.015 * turned_away
            
        if self.competitor.is_active and not self.competitor.counter_marketing_active:
            rep_change -= 0.12
            
        if partner_helps_today and p and p.is_co_owner:
            rep_change += 0.25
            
        self.restaurant.adjust_reputation(rep_change)
        
        # Auto loan repayment hourly from sales
        loan_payment = 0.0
        if self.loan.balance > 0.0 and total_income > 0.0:
            rates = {0: 0.05, 1: 0.07, 2: 0.10, 3: 0.15, 4: 0.20}
            pct = rates.get(self.restaurant.level, 0.05)
            deduction = round(total_income * pct, 2)
            if deduction > self.loan.balance:
                deduction = self.loan.balance
            success, msg, loan_payment = self.loan.pay_loan(deduction, self.player.cash)
            if success and loan_payment > 0.0:
                self.player.adjust_cash(-loan_payment)
                self.finance.record_transaction("Loan Interest", loan_payment, f"Auto-repayment ({int(pct*100)}%)")
        
        # Generate narrative soul log event during shifts
        soul_event = None
        if actual_served > 0:
            if random.random() < 0.25:
                npc_dialogues = [
                    "Old Barnaby sits by the window, contentedly slurping his soup.",
                    "Ms. Martha sits at a corner table grading essays, enjoying her warm tea.",
                    "Toby the mail carrier runs in for a quick bite, leaving with a smile.",
                    "Young Lily carefully counts out her coppers to buy a dessert slice.",
                    "Arthur, the retired chef, quietly observes your kitchen layout and nods.",
                    "A couple sitting near the window table are sharing a laugh.",
                    "A warm aroma fills the street, causing passersby to look in with curiosity.",
                    "Rain taps the glass pane as customers snuggle near the warm stove."
                ]
                soul_event = random.choice(npc_dialogues)
                
        return {
            "served": actual_served,
            "revenue": revenue,
            "tips": tips,
            "total_income": total_income,
            "loan_payment": loan_payment,
            "rep_change": rep_change,
            "soul_event": soul_event
        }

    def advance_day(self) -> list[str]:
        """Transitions the game state to the next day.
        Applies end-of-day math: maintenance costs, loan interest, employee wages.
        Returns a list of notification strings describing overnight events.
        """
        notifications = []
        dl = self.finance.daily_ledger
        
        # Track streak of profitable days
        if dl.net_profit > 0:
            self.days_profitable_streak += 1
        else:
            self.days_profitable_streak = 0
            
        # 1. Apply Economic Climate Multipliers
        climate = self.town.economic_climate
        maint_mult = 1.0
        wage_mult = 1.0
        
        if climate == "Supply Strike":
            maint_mult = 1.25
            wage_mult = 1.20
        elif climate == "Monsoon Week":
            maint_mult = 1.35
            wage_mult = 1.0
        elif climate in ["Founder's Feast", "Harvest Festival", "Festival"]:
            maint_mult = 1.10
            wage_mult = 1.10
        elif climate in ["Economic Slowdown", "Recession"]:
            maint_mult = 1.0
            wage_mult = 0.85
            
        # Rent / Diner Fixed Maintenance
        base_maint = self.restaurant.calculate_daily_maintenance() * maint_mult
        self.player.adjust_cash(-base_maint)
        self.finance.record_transaction("Maintenance", base_maint, f"Rent & Permits (Lvl {self.restaurant.level})")
        
        # Base Utilities
        base_utilities_map = {0: 0.0, 1: 2.0, 2: 5.0, 3: 20.0, 4: 50.0}
        base_util = base_utilities_map.get(self.restaurant.level, 0.0) * maint_mult
        
        # Variable Expenses: Power ($0.20/cust) & Cleaning ($0.15/cust)
        served = self.restaurant.meals_served_today
        power_cost = round(served * 0.20, 2)
        cleaning_cost = round(served * 0.15, 2)
        
        self.player.adjust_cash(-power_cost)
        self.player.adjust_cash(-cleaning_cost)
        
        self.finance.record_transaction("Utilities", base_util + power_cost, f"Utilities & Power")
        self.finance.record_transaction("Cleaning", cleaning_cost, f"Cleaning & Sanitization")
        
        # Household Expenses (Lifestyle Inflation)
        if self.house.purchased:
            if self.restaurant.level >= 4:
                household = 60.0  # Luxury Estate
            else:
                household = 28.0  # Cozy Cottage
        else:
            if self.restaurant.level == 0:
                household = 5.0   # Street Vendor
            else:
                household = 12.0  # Small Apartment
        self.player.adjust_cash(-household)
        self.finance.record_transaction("Household", household, f"Household Expenses")

        # Employee Wages
        wages = self.employees.calculate_daily_wages(wage_mult)
        if wages > 0:
            self.player.adjust_cash(-wages)
            self.finance.record_transaction("Wages", wages, f"Staff Wages")
            
        # Decrement temporary salary cuts duration
        for e in self.employees.hired:
            if e.pay_cut_days_left > 0:
                e.pay_cut_days_left -= 1
            
        # Unexpected events (broken sink, healer fee, etc.)
        if random.random() < 0.12:
            repair_events = [
                ("A kitchen sink faucet pipe burst overnight", random.randint(20, 45)),
                ("An oven heating coil burned out during service", random.randint(30, 55)),
                ("A chair leg broke under a heavy customer", random.randint(15, 25)),
                ("Slipped on a wet kitchen floor; local healer's fee", random.randint(20, 35)),
                ("Diner roof tiles slid off during strong winds", random.randint(40, 65))
            ]
            desc, cost = random.choice(repair_events)
            self.player.adjust_cash(-cost)
            self.finance.record_transaction("Misc", cost, desc)
            notifications.append(f"🔧 Unexpected Event: {desc}! Cost: -${cost:.2f}")
            
        # Partner co-owner support
        p = self.romance.partner
        if p and p.is_co_owner:
            self.restaurant.adjust_reputation(1.5)
            notifications.append(f"Co-Owner {p.name}'s support boosted your restaurant's standing! (+1.5 Standing)")

        # Update NPC Minds overnight
        for char in self.romance.characters:
            if hasattr(char, "mind") and char.mind:
                char.mind.update_evening_state(self)

        # Romance Decay if dating without a house
        if p and p.is_partner and not self.house.purchased:
            decay_msg = self.romance.decay_without_house()
            if decay_msg:
                notifications.append(decay_msg)

        # 2. Apply Loan Interest
        interest = self.loan.apply_daily_interest()
        if interest > 0:
            self.finance.record_transaction("Loan Interest", interest, "Daily accrued loan interest")
            notifications.append(f"Bank Loan: Daily interest of ${interest:.2f} was added to your balance.")

        # 3. Rest Player (energy recovery based on house benefits)
        sleep_recovery = self.player.sleep_energy_recovery
        if self.house.purchased:
            sleep_recovery = self.player.max_energy
            # bed / home upgrades recovery bonuses
            for up_id in self.house.upgrades:
                up = next((u for u in self.house.available_upgrades if u.id == up_id), None)
                if up:
                    sleep_recovery += up.energy_recovery_bonus
            self.player.energy = min(self.player.max_energy, sleep_recovery)
            notifications.append("You slept in your cozy cottage. Energy restored!")
        else:
            self.player.recover_sleep(bonus=0.0)
            notifications.append("You slept on a makeshift cot in the shop. Energy partially restored.")

        # 4. Personal Fulfillment Updates overnight
        fulfillment_change = 0.0
        if dl.dates > 0:
            fulfillment_change += 5.0
        if dl.misc > 0:
            fulfillment_change += 2.0
            
        # Day off
        if dl.revenue == 0.0:
            fulfillment_change += 4.0
        
        # Upgrades bonuses
        if self.house.purchased:
            if "backyard_greenhouse" in self.house.upgrades:
                fulfillment_change += 2.0
            if "cozy_couch" in self.house.upgrades:
                fulfillment_change += 1.0
                
        # Relationship neglect check
        if dl.dates > 0 or dl.misc > 0:
            self.days_since_social = 0
        else:
            if not hasattr(self, 'days_since_social'):
                self.days_since_social = 0
            self.days_since_social += 1
            if self.days_since_social >= 7:
                fulfillment_change -= 3.0
                notifications.append("💔 Personal Fulfillment: You've been ignoring your relationships lately. (-3.0 Fulfillment)")
                
        # Hoarding warning
        if self.player.cash > 3000.0 and not self.house.purchased:
            fulfillment_change -= 2.0
            notifications.append("💼 Personal Fulfillment: Money is piling up, but you still sleep in the shop. (-2.0 Fulfillment)")
            
        self.personal_fulfillment = max(0.0, min(100.0, self.personal_fulfillment + fulfillment_change))

        # 5. Economic Climate & Competitor Updates
        econ_msg = self.town.roll_economic_climate()
        if econ_msg:
            notifications.append(econ_msg)
            
        # Competitor Active Logic
        if self.competitor.is_active:
            self.days_since_competitor_start += 1
            
            # Every 5 days, Chef Sebastian launches a new priority action
            if self.days_since_competitor_start % 5 == 0:
                notice = self.competitor.roll_sebastian_action()
                if notice:
                    notifications.append(f"👨‍🍳 Sebastian's Move: {notice}")
            
            # Apply Live Music expectation reputation drain
            if self.competitor.active_action == "Live Music":
                self.restaurant.adjust_reputation(-0.5)
                notifications.append("🎵 Sebastian's Live Harpist has Oakhaven talking, raising local dining standards. (-0.5 Reputation)")
                
        # 6. Old Nostalgic Customers (Standing >= 70 & Day >= 25)
        if self.restaurant.reputation >= 70.0 and self.day >= 25:
            if random.random() < 0.15:
                self.restaurant.adjust_reputation(1.0)
                notifications.append("💬 Standing: A customer smiled and said: 'I've been eating here since you only had a used food cart by the street.' (+1.0 standing)")
            
        # Cheating detection check (technically cheat on a person, got caught logic)
        partners_count = sum(1 for c in self.romance.characters if c.is_partner or c.is_co_owner)
        if partners_count > 1 and not self.romance.caught_cheating:
            # 15% chance to get caught every night
            if random.random() < 0.15:
                self.romance.caught_cheating = True
                
                # Check if married to see if alimony applies
                was_married = any(c.is_co_owner for c in self.romance.characters)
                
                # Seize house/properties
                self.house.purchased = False
                self.player.has_house = False
                self.house.upgrades.clear()
                
                # Wipes relationship progress and breaks up
                for c in self.romance.characters:
                    c.is_partner = False
                    c.is_co_owner = False
                    c.romance_level = max(0.0, c.romance_level - 50.0)
                
                self.romance.active_partner_name = None
                self.romance.has_ring = False
                self.romance.wedding_tier = "None"
                
                if was_married:
                    self.player.adjust_cash(-2000.0)
                    self.finance.record_transaction("Misc", 2000.0, "Alimony settlement fine")
                    notifications.append(
                        "🚨 CAUGHT CHEATING! Your spouse found out about your other partners! "
                        "You have been sued for divorce. The court has seized your cottage, wiped all relationship progress, "
                        "fined you $2,000.00 in alimony, and legally barred you from dating anyone else!"
                    )
                else:
                    notifications.append(
                        "💔 CAUGHT CHEATING! Your partners discovered you were seeing other people! "
                        "They have all broken up with you and your relationship progress has been wiped."
                    )

        # Lead up warnings for Chef Sebastian (foreshadowing)
        if not self.competitor.is_active:
            has_partner_any = any(c.is_partner or c.is_co_owner for c in self.romance.characters)
            # Level 3 & partner warning
            if self.restaurant.level == 3 and has_partner_any:
                if "foreshadow_1" not in self.memory:
                    self.memory["foreshadow_1"] = True
                    notifications.append("👂 Whisper in Oakhaven: Chef Sebastian from the capital is rumored to be looking at real estate in the town center...")
            # Level 4 & partner warning
            if self.restaurant.level >= 4 and has_partner_any and not self.house.purchased:
                if "foreshadow_2" not in self.memory:
                    self.memory["foreshadow_2"] = True
                    notifications.append("📰 Oakhaven Gazette: Chef Sebastian has purchased a large commercial plot for Bistro Gourmet.")
            # Level 4 & house warning
            if self.restaurant.level >= 4 and self.house.purchased and not has_partner_any:
                if "foreshadow_3" not in self.memory:
                    self.memory["foreshadow_3"] = True
                    notifications.append("👤 Talk in town: Chef Sebastian was seen walking around Oakhaven in a fine silk coat, scouting locations.")

        # Competitor check
        competitor_was_active = self.competitor.is_active
        has_partner = self.romance.partner is not None and (self.romance.partner.is_partner or self.romance.is_co_owner)
        unlocked = self.competitor.check_unlock_conditions(
            restaurant_level=self.restaurant.level,
            has_partner=has_partner,
            has_house=self.house.purchased
        )
        if unlocked and not competitor_was_active:
            notifications.append(
                f"🚨 WARNING: {self.competitor.owner} has opened a rival establishment '{self.competitor.name}' in town!\n"
                "   They are launching an aggressive marketing campaign. You must protect what you've built!"
            )
            
        # Reset daily business statistics and marketing counteractions
        self.restaurant.meals_served_today = 0
        self.restaurant.revenue_today = 0.0
        self.competitor.reset_day()
        self.finance.start_new_day()
        
        # 5. Roll employee attendance for tomorrow
        attendance_notices = self.employees.roll_daily_attendance()
        notifications.extend(attendance_notices)
        
        # Increment day
        self.day += 1
        self.week = (self.day - 1) // 7 + 1
        
        return notifications

    def check_retirement_eligibility(self) -> tuple[bool, list[str]]:
        reasons = []
        is_eligible = True
        
        # 1. Level check
        if self.restaurant.level < 3:
            is_eligible = False
            reasons.append("Own an Edge Shop (Level 3) or Town Restaurant (Level 4)")
            
        # 2. House check
        if not self.house.purchased:
            is_eligible = False
            reasons.append("Purchase and own a Cottage")
            
        # 3. Relationship check
        is_married = self.romance.is_co_owner or any(c.is_co_owner for c in self.romance.characters)
        if not is_married:
            is_eligible = False
            reasons.append("Marry your partner (Business Co-Ownership stage)")
            
        # 4. Profit streak
        if self.days_profitable_streak < 7:
            is_eligible = False
            reasons.append("Maintain profitability for 7 consecutive days")
            
        # 5. Competitor survived
        if self.competitor.is_active and self.days_since_competitor_start < 30:
            is_eligible = False
            reasons.append(f"Survive competitor pressure for 30 days ({self.days_since_competitor_start}/30 days)")
            
        return is_eligible, reasons

    def get_retirement_ending(self) -> tuple[str, str]:
        fulfillment = self.personal_fulfillment
        standing = self.restaurant.reputation
        lvl = self.restaurant.level
        partner_name = self.romance.partner_name if self.romance.partner else "Valerie"
        
        if lvl == 3 and fulfillment >= 70 and standing >= 70:
            return (
                "Ending A: The Quiet Life",
                f"You retired peacefully in Oakhaven valley. Sketches of your cozy cottage hang by the fireplace. "
                f"Barnaby continues to enjoy his morning soup at the Edge Shop, now run by a local apprentice. "
                f"You and {partner_name} spend your afternoons reading on the porch. Success gave you options, and you chose peace. "
                f"You sit on the porch swing as the valley rain falls, watching the lights of Oakhaven glow in the distance."
            )
        elif lvl >= 4 and fulfillment >= 50 and standing >= 70:
            return (
                "Ending B: The Respected Tycoon",
                f"You retired at the peak of your career. A framed photo sits on the mantelpiece showing your Town Restaurant staff, "
                f"with {partner_name} smiling next to the mayor holding a landmark award. Chef Sebastian sent a congratulatory letter, "
                f"acknowledging your work. The town carries on, but your story is woven into its streets. "
                f"You sit quietly on the cottage porch swing, content that you balanced grand ambition with personal happiness."
            )
        else:
            return (
                "Ending C: Lonely Success",
                f"You retired with deep pockets, but the cottage feels empty. Your restaurant is a thriving enterprise, "
                f"yet the ledger shows the cost of success: missed evenings, cold meals, and hollow conversations with {partner_name}. "
                f"The town remembers your food, but you sit alone on the porch, looking at the distant valley lights and wondering when enough would have been enough."
            )
