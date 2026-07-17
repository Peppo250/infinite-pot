from dataclasses import dataclass, field
from typing import Callable, Any

@dataclass
class EventOption:
    text: str
    outcome_text: str
    action: Callable[[Any], None]  # takes state and applies changes
    condition: Callable[[Any], bool] = lambda state: True

@dataclass
class GameEvent:
    id: str
    title: str
    description: str
    options: list[EventOption]
    trigger_condition: Callable[[Any], bool] = lambda state: True
    is_triggered: bool = False

@dataclass
class EventSystem:
    events: list[GameEvent] = field(default_factory=list)
    active_event: GameEvent | None = None

    def add_event(self, event: GameEvent) -> None:
        self.events.append(event)

    def check_and_trigger_event(self, state: Any) -> GameEvent | None:
        """Finds all events that satisfy trigger conditions, filters out already triggered ones,
        picks one randomly, and sets it as the active event.
        """
        # If there's already an active event, don't trigger another
        if self.active_event:
            return self.active_event

        import random
        # Find candidates
        candidates = [
            e for e in self.events 
            if not e.is_triggered and e.trigger_condition(state)
        ]
        
        if not candidates:
            return None

        # Determine if we should trigger an event today (e.g., 25% chance of random event)
        # Some critical events might be 100% or conditional
        if random.random() < 0.30:
            selected = random.choice(candidates)
            self.active_event = selected
            selected.is_triggered = True
            return selected
            
        return None

    def resolve_event(self, option_index: int, state: Any) -> tuple[str, str]:
        """Resolves the active event with the chosen option. Returns (option_text, outcome_text)."""
        if not self.active_event:
            return "No active event", "Nothing happened."

        event = self.active_event
        # Filter options that are visible/valid for current state
        valid_options = [o for o in event.options if o.condition(state)]
        
        if option_index < 0 or option_index >= len(valid_options):
            # Fallback to first option if index is invalid
            option_index = 0

        chosen_option = valid_options[option_index]
        
        # Apply action to state
        chosen_option.action(state)
        
        # Clear active event
        self.active_event = None
        
        return chosen_option.text, chosen_option.outcome_text
