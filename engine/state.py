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
        
        # Event System
        self.events = EventSystem()
        for e in get_default_events():
            self.events.add_event(e)
            
        # Time Management
        self.day: int = 1
        self.week: int = 1
        self.days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
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

    def simulate_business_day(self, player_work_hours: int) -> dict[str, Any]:
        """Simulates the business day based on pricing, staff, and marketing status.
        Updates player cash, energy, and restaurant reputation.
        Returns a dictionary summarizing the day's results.
        """
        p = self.romance.partner
        active_employees = self.employees.get_active_employees()
        
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
            
        # 3. Calculate player energy cost & capacity
        player_capacity = player_work_hours * 3
        player_energy_cost = player_work_hours * self.player.work_energy_cost_per_hour
        self.player.adjust_energy(-player_energy_cost)
        
        # 4. Calculate employees capacity (they work up to min(8, open_hours))
        employee_capacity = sum(int(min(8, open_hours) * (2 + e.skill * 4)) for e in active_employees)
        
        # 5. Calculate partner's capacity (helps serve up to min(8, open_hours) hours, 4 meals/hour)
        partner_capacity = min(8, open_hours) * 4 if partner_helps_today else 0
        
        # 6. Total service capacity
        total_capacity = player_capacity + employee_capacity + partner_capacity
        
        # 7. Actual customers served (capped by seats available throughout the open hours)
        max_daily_capacity = int(capacity * (open_hours / 8.0)) if open_hours > 0 else 0
        actual_served = min(potential_customers, total_capacity, max_daily_capacity)
        turned_away = max(0, potential_customers - total_capacity)
        
        # 8. Revenue & Tips calculation
        revenue = round(actual_served * self.restaurant.menu_price, 2)
        
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

    def advance_day(self) -> list[str]:
        """Transitions the game state to the next day.
        Applies end-of-day math: maintenance costs, loan interest, employee wages.
        Returns a list of notification strings describing overnight events.
        """
        notifications = []
        
        # 1. Apply maintenance and wages
        maint_cost = self.restaurant.calculate_daily_maintenance()
        self.player.adjust_cash(-maint_cost)
        self.finance.record_transaction("Maintenance", maint_cost, f"Daily maintenance for Level {self.restaurant.level} + upgrades")
        
        # If the player has a house, charge house maintenance
        if self.house.purchased:
            house_maint = self.house.daily_maintenance
            self.player.adjust_cash(-house_maint)
            self.finance.record_transaction("Maintenance", house_maint, "Daily house maintenance")

        # Employee Wages
        wages = self.employees.calculate_daily_wages()
        if wages > 0:
            self.player.adjust_cash(-wages)
            self.finance.record_transaction("Wages", wages, f"Wages for hired staff")
            
        # Partner co-owner support
        p = self.romance.partner
        if p and p.is_co_owner:
            self.restaurant.adjust_reputation(1.5)
            notifications.append(f"Co-Owner {p.name}'s support boosted your restaurant's atmosphere! (+1.5 Reputation)")

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

        # 3. Rest Player (energy recovery)
        if self.house.purchased:
            # Sleeping at home fully replenishes energy
            self.player.energy = self.player.max_energy
            notifications.append("You slept in your cozy home. Energy fully restored to 100%!")
        else:
            # Sleeping in the shop restores a base amount
            self.player.recover_sleep(bonus=0.0)
            notifications.append("You slept on a makeshift cot in the shop. Energy partially restored.")
        
        # 4. Economic Climate & Competitor Updates
        econ_msg = self.town.roll_economic_climate()
        if econ_msg:
            notifications.append(econ_msg)
            
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
