import sys
import pytest
from PySide6.QtWidgets import QApplication
from engine.state import GameState
from ui.renderer import SceneComposer
from player.romance import RomanticCharacter, Memory

@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

# Generate 480 test cases mapping every permutation of:
# diner level, time of day, season, and weather climate.
@pytest.mark.parametrize("level", [0, 1, 2, 3, 4])
@pytest.mark.parametrize("time_of_day", ["Morning", "Afternoon", "Evening", "Night"])
@pytest.mark.parametrize("season", ["Spring", "Summer", "Autumn", "Winter"])
@pytest.mark.parametrize("climate", [
    "Stable Season", 
    "Boom", 
    "Economic Slowdown", 
    "Founder's Feast", 
    "Monsoon Week", 
    "Supply Strike"
])
def test_composed_restaurant_rendering_permutations(qapp, level, time_of_day, season, climate):
    state = GameState()
    state.restaurant.level = level
    state.time_of_day = time_of_day
    state.season = season
    state.town.economic_climate = climate
    
    # Render with normal composer
    pixmap = SceneComposer.compose_restaurant(state, evening_phase=False)
    assert pixmap is not None
    assert not pixmap.isNull()
    assert pixmap.width() == 1000
    assert pixmap.height() == 700
    
    # Render with forced evening phase
    pixmap_eve = SceneComposer.compose_restaurant(state, evening_phase=True)
    assert pixmap_eve is not None
    assert not pixmap_eve.isNull()

# Generate 16 test cases covering cottage upgrade permutations
@pytest.mark.parametrize("fireplace", [True, False])
@pytest.mark.parametrize("dining_table", [True, False])
@pytest.mark.parametrize("has_partner", [True, False])
@pytest.mark.parametrize("has_anniversary_mem", [True, False])
def test_composed_house_rendering_permutations(qapp, fireplace, dining_table, has_partner, has_anniversary_mem):
    state = GameState()
    state.house.purchased = True
    
    if fireplace:
        state.house.upgrades.append("fireplace")
    if dining_table:
        state.house.upgrades.append("dining_table")
        
    if has_partner:
        char = state.romance.characters[0]
        char.is_partner = True
        state.romance.active_partner_name = char.name
        if has_anniversary_mem:
            char.memories.append(Memory(
                title="Appreciated a Quiet Evening Together",
                category="Everyday",
                emotion="Happy",
                strength=4.0
            ))
            
    pixmap = SceneComposer.compose_house(state)
    assert pixmap is not None
    assert not pixmap.isNull()
    assert pixmap.width() == 1000
    assert pixmap.height() == 700

# Test tavern layout rendering
def test_composed_tavern_rendering(qapp):
    state = GameState()
    pixmap = SceneComposer.compose_tavern(state)
    assert pixmap is not None
    assert not pixmap.isNull()
    assert pixmap.width() == 1000
    assert pixmap.height() == 700
