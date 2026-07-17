import pytest
from engine.state import GameState
from player.stats import PlayerStats
from player.house import HouseSystem
from player.romance import RomanceSystem
from business.restaurant import Restaurant
from business.employees import EmployeeSystem, Employee
from business.competitor import CompetitorSystem
from economy.loan import LoanSystem
from economy.finance import FinancialSystem
from world.town import Town

def test_player_stats() -> None:
    p = PlayerStats(cash=100.0, energy=100.0, max_energy=100.0, daily_energy_cost=20.0, work_energy_cost_per_hour=5.0, sleep_energy_recovery=80.0)
    assert p.cash == 100.0
    assert p.energy == 100.0
    
    # Test cash adjustment
    success = p.adjust_cash(-50.0)
    assert success is True
    assert p.cash == 50.0
    
    # Test failed cash adjustment (negative balance)
    success = p.adjust_cash(-100.0)
    assert success is False
    assert p.cash == 50.0
    
    # Test energy adjustments
    p.adjust_energy(-40.0)
    assert p.energy == 60.0
    
    p.adjust_energy(100.0)
    assert p.energy == 100.0  # capped at max_energy
    
    p.adjust_energy(-120.0)
    assert p.energy == 0.0    # floor at 0.0

    # Test sleep recovery
    p.energy = 30.0
    p.recover_sleep(bonus=10.0)
    # recovery = sleep_energy_recovery (80) + bonus (10) = 90
    # energy goes 30 -> 100 (cap)
    # then deducts daily_energy_cost (20) -> 80
    assert p.energy == 80.0

def test_house_upgrades() -> None:
    # Build a manual config list to test the system
    config = {
        "house_purchase": {"cost": 3000.0, "daily_maintenance": 25.0},
        "upgrades": {
            "house": [
                {"id": "cozy_couch", "name": "Cozy Couch", "cost": 400.0, "energy_recovery_bonus": 10.0, "romance_progress_bonus": 0.0, "description": "couch"},
                {"id": "table", "name": "Table", "cost": 500.0, "energy_recovery_bonus": 0.0, "romance_progress_bonus": 0.15, "description": "table"}
            ]
        }
    }
    h = HouseSystem.from_config(config)
    assert h.purchased is False
    assert h.cost == 3000.0
    
    # Can't buy upgrade if house not owned
    success, msg, cost = h.buy_upgrade("cozy_couch", 1000.0)
    assert success is False
    assert h.get_energy_recovery_bonus() == 0.0

    # Purchase house
    h.purchased = True
    
    # Fail to buy if cash insufficient
    success, msg, cost = h.buy_upgrade("cozy_couch", 100.0)
    assert success is False
    
    # Buy successfully
    success, msg, cost = h.buy_upgrade("cozy_couch", 500.0)
    assert success is True
    assert cost == 400.0
    assert h.get_energy_recovery_bonus() == 10.0

    # Buy duplicate
    success, msg, cost = h.buy_upgrade("cozy_couch", 500.0)
    assert success is False

def test_romance_milestones() -> None:
    config = {}
    rom = RomanceSystem.from_config(config)
    assert rom.stage_name == "Single"
    assert len(rom.characters) == 3
    
    # Try dating without a partner
    success, msg, c_spent, e_spent = rom.go_on_date(100.0, 100.0)
    assert success is False

    target = rom.characters[0]
    
    # Propose immediately (fails since romance is 0)
    success, msg = rom.propose_relationship(target.name)
    assert success is False
    
    # Talk to character to build romance
    dialogue, gain = target.interact_talk()
    assert target.romance_level > 0.0
    
    # Force romance to 45.0 to propose relationship
    target.romance_level = 45.0
    success, msg = rom.propose_relationship(target.name)
    assert success is True
    assert rom.partner_name == target.name
    assert rom.stage_name == "Partner"
    
    # Try date with insufficient funds
    success, msg, c_spent, e_spent = rom.go_on_date(10.0, 100.0)
    assert success is False
    
    # Successful date
    success, msg, c_spent, e_spent = rom.go_on_date(100.0, 100.0, progress_multiplier=1.0)
    assert success is True
    assert c_spent == 80.0
    assert e_spent == 25.0
    assert rom.romance_level > 45.0
    
    # Co-own ask without house
    rom.romance_level = 80.0
    success, msg = rom.ask_to_co_own(has_house=False)
    assert success is False
    
    # Co-own ask with house
    success, msg = rom.ask_to_co_own(has_house=True)
    assert success is True
    assert rom.is_co_owner is True
    assert "Co-Owner" in rom.stage_name
    
    # Test break up
    success, msg = rom.break_up()
    assert success is True
    assert rom.stage_name == "Single"

def test_loans() -> None:
    config = {
        "loans": {
            "annual_interest_rate": 0.365,  # 36.5% interest, makes daily 0.1% for easy test math
            "max_loan_ratio": 0.5
        }
    }
    l = LoanSystem.from_config(config)
    assert l.balance == 0.0
    
    # Borrow at level 1 (limit 50)
    success, msg = l.borrow(40.0, 1)
    assert success is True
    assert l.balance == 40.0
    
    # Borrow over limit (40 + 20 = 60, exceeds 50)
    success, msg = l.borrow(20.0, 1)
    assert success is False
    
    # Apply interest (annual 0.365 / 365 = 0.001 daily -> 0.1% interest on 40 = 0.04)
    interest = l.apply_daily_interest()
    assert round(interest, 2) == 0.04
    assert round(l.balance, 2) == 40.04
    
    # Repay loan
    success, msg, spent = l.pay_loan(20.04, 100.0)
    assert success is True
    assert spent == 20.04
    assert round(l.balance, 2) == 20.00

def test_employees() -> None:
    config = {
        "employee_pool": [
            {"name": "TestAlex", "skill": 0.5, "reliability": 1.0, "experience": 1, "daily_salary": 20.0}
        ]
    }
    es = EmployeeSystem.from_config(config)
    assert len(es.candidates) == 1
    assert len(es.hired) == 0
    
    # Hire employee
    success, msg = es.hire_employee("TestAlex", max_employees=1)
    assert success is True
    assert len(es.hired) == 1
    assert len(es.candidates) == 0
    
    # Fire employee
    success, msg = es.fire_employee("TestAlex")
    assert success is True
    assert len(es.hired) == 0
    assert len(es.candidates) == 1

def test_restaurant_logic() -> None:
    config = {
        "restaurant_levels": {
            "1": {"name": "Cart", "upgrade_cost": 0.0, "daily_maintenance": 5.0, "customer_capacity": 10, "max_employees": 0, "price_per_meal_range": [3, 6], "base_attraction": 0.3},
            "2": {"name": "Shop", "upgrade_cost": 200.0, "daily_maintenance": 15.0, "customer_capacity": 20, "max_employees": 1, "price_per_meal_range": [5, 9], "base_attraction": 0.5}
        },
        "upgrades": {
            "business": [
                {"id": "sign", "name": "Sign", "cost": 100.0, "attraction_bonus": 0.1, "daily_maintenance": 1.0, "min_level": 2, "description": "sign"}
            ]
        }
    }
    r = Restaurant.from_config(config)
    assert r.level == 1
    assert r.menu_price == 4.5  # midpoint of [3, 6]
    
    # Upgrade level
    success, msg, cost = r.upgrade_level(100.0) # insufficient cash
    assert success is False
    
    success, msg, cost = r.upgrade_level(300.0) # success
    assert success is True
    assert cost == 200.0
    assert r.level == 2
    assert r.menu_price == 7.0  # midpoint of [5, 9]

    # Buy upgrade
    success, msg, cost = r.buy_upgrade("sign", 50.0) # insufficient cash
    assert success is False
    
    success, msg, cost = r.buy_upgrade("sign", 150.0) # success
    assert success is True
    assert cost == 100.0
    assert "sign" in r.upgrades
    
    # Maintenance total = level 2 base (15) + sign (1) = 16
    assert r.calculate_daily_maintenance() == 16.0

def test_game_state_sim() -> None:
    # Verifies game loop simulation run and day advance transitions
    state = GameState()
    # At start, player has 0 cash, energy 100, level 0 restaurant
    assert state.player.cash == 0.0
    assert state.restaurant.level == 0
    
    # Run a business day where player works 4 hours
    sim = state.simulate_business_day(player_work_hours=4)
    assert sim["energy_spent"] == 20.0
    assert state.player.energy == 80.0
    assert state.player.days_worked == 1
    
    # Advance the day
    # Deducts daily cart maintenance for Level 0 ($0.00)
    initial_cash = state.player.cash
    notices = state.advance_day()
    assert state.day == 2
    # Verify maintenance deduction is $0.00
    assert state.player.cash == initial_cash
