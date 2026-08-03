import pytest
from engine.state import GameState
from player.romance import RomanticCharacter, Memory

# 1. Parameterize Romance Calculations
# Tests 192 permutations of positive memory strengths, negative memory strengths, trust, and compatibility.
@pytest.mark.parametrize("pos_count", [0, 1, 3, 5])
@pytest.mark.parametrize("neg_count", [0, 1, 2, 4])
@pytest.mark.parametrize("trust", [10, 40, 70, 90])
@pytest.mark.parametrize("compatibility", [15, 50, 80])
def test_emergent_romance_level_formula(pos_count, neg_count, trust, compatibility):
    char = RomanticCharacter(name="Ada", archetype="Scholar")
    char.trust = trust
    char.compatibility = compatibility
    
    # Add memories
    for i in range(pos_count):
        char.memories.append(Memory(title=f"Good {i}", category="Date", emotion="Happy", strength=4.0))
    for i in range(neg_count):
        char.memories.append(Memory(title=f"Bad {i}", category="Shift", emotion="Disappointed", strength=4.0))
        
    romance_val = char.romance_level
    
    # Expected formula evaluated:
    expected = (pos_count * 4.0 * 2.0) - (neg_count * 4.0 * 2.0) + (trust * 0.6) + (compatibility * 0.4)
    expected = max(0.0, min(100.0, expected))
    
    assert romance_val == pytest.approx(expected, abs=0.01)

# 2. Test Overtime Friction Memories
# Parameterize work shift durations: 8 (normal), 9, 10, and 12 hours.
@pytest.mark.parametrize("hours", [8, 9, 10, 12])
def test_overtime_worked_friction(hours):
    state = GameState()
    char = state.romance.characters[0]
    char.is_partner = True
    state.romance.active_partner_name = char.name
    state.house.purchased = True
    
    initial_memories_count = len(char.memories)
    
    # Simulate a business day
    state.simulate_business_day(player_work_hours=hours)
    state.advance_day()
    
    # If hours > 8, it should trigger an Overtime memory
    if hours > 8:
        assert len(char.memories) > initial_memories_count
        new_mems = char.memories[initial_memories_count:]
        assert any(m.emotion == "Disappointed" and ("Overtime" in m.title or "Late" in m.title) for m in new_mems)
    else:
        # Normal shifts should not create disappointed overtime memories
        for mem in char.memories[initial_memories_count:]:
            assert mem.emotion != "Disappointed"

# 3. Test Economic Climate & Household Expenses Scaling
# Permutes diner levels, cottage ownership, and town climates (60 cases)
@pytest.mark.parametrize("level", [0, 1, 2, 3, 4])
@pytest.mark.parametrize("cottage_purchased", [True, False])
@pytest.mark.parametrize("climate", [
    "Stable Season", 
    "Boom", 
    "Economic Slowdown", 
    "Founder's Feast", 
    "Monsoon Week", 
    "Supply Strike"
])
def test_daily_household_and_utilities_expenses_scaling(level, cottage_purchased, climate):
    state = GameState()
    state.restaurant.level = level
    state.house.purchased = cottage_purchased
    state.town.economic_climate = climate
    
    # Baseline expected household expense based on progression stage:
    if cottage_purchased:
        if level >= 4:
            expected_house_exp = 60.0
        else:
            expected_house_exp = 28.0
    else:
        if level == 0:
            expected_house_exp = 5.0
        else:
            expected_house_exp = 12.0
        
    # Baseline expected base utilities:
    base_utilities_map = {0: 0.0, 1: 2.0, 2: 5.0, 3: 20.0, 4: 50.0}
    expected_util = base_utilities_map.get(level, 0.0)
    
    # Climate multiplier multipliers:
    maint_mult = 1.0
    if climate == "Supply Strike":
        maint_mult = 1.25
    elif climate == "Monsoon Week":
        maint_mult = 1.35
    elif climate in ["Founder's Feast", "Festival", "Harvest Festival"]:
        maint_mult = 1.10
        
    expected_util *= maint_mult
    
    # Trigger advance_day overnight ledger updates
    state.player.cash = 1000.0
    state.advance_day()
    
    # Query transactions in history
    history = state.finance.history
    house_tx = next((t for t in reversed(history) if t.category == "Household"), None)
    util_tx = next((t for t in reversed(history) if t.category == "Utilities"), None)
    
    # Assert values match our expected models
    assert house_tx is not None
    assert house_tx.amount == pytest.approx(expected_house_exp, abs=0.01)
    if expected_util > 0.0:
        assert util_tx is not None
        assert util_tx.amount == pytest.approx(expected_util, abs=0.01)

def test_family_court_pardon_redemption():
    state = GameState()
    rom = state.romance
    
    # Trigger cheating scandal
    rom.caught_cheating = True
    assert rom.caught_cheating is True
    
    # Try proposing while barred
    success, msg = rom.propose_relationship("Ada")
    assert success is False
    assert "barred" in msg.lower()
    
    # Pay court pardon fee
    state.player.cash = 600.0
    state.player.adjust_cash(-500.0)
    rom.caught_cheating = False
    state.finance.record_transaction("Misc", 500.0, "Family Court Pardon Fee paid")
    
    assert rom.caught_cheating is False
    assert state.player.cash == 100.0
    
    # Try proposing now that pardon is granted
    char = next((c for c in rom.characters if c.name == "Ada" or c.archetype == "Scholar"), None)
    if char:
        char.romance_level = 65.0
        success, msg = rom.propose_relationship(char.name)
        assert success is True
