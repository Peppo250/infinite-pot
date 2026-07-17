from dataclasses import dataclass, field
import random

@dataclass
class Town:
    name: str = "Oakhaven"
    economic_climate: str = "Normal"  # Normal, Boom, Recession, Festival
    economic_multiplier: float = 1.0
    active_event_description: str = "A quiet, peaceful day in Oakhaven."
    days_since_climate_change: int = 0

    def roll_economic_climate(self) -> str:
        """Randomly changes or updates the economic climate of the town.
        Climates last for several days to a week.
        """
        self.days_since_climate_change += 1
        
        # Only change climate occasionally (e.g. 10% chance after 4 days)
        if self.days_since_climate_change >= 4 and random.random() < 0.15:
            climates = ["Normal", "Boom", "Recession", "Festival"]
            weights = [0.60, 0.15, 0.15, 0.10]
            new_climate = random.choices(climates, weights=weights)[0]
            
            if new_climate != self.economic_climate:
                self.economic_climate = new_climate
                self.days_since_climate_change = 0
                
                if new_climate == "Normal":
                    self.economic_multiplier = 1.0
                    self.active_event_description = "The town economy is stable and quiet."
                elif new_climate == "Boom":
                    self.economic_multiplier = 1.25
                    self.active_event_description = "A surge in local commerce has everyone spending freely!"
                elif new_climate == "Recession":
                    self.economic_multiplier = 0.75
                    self.active_event_description = "A slowdown in trade makes the townsfolk pinch pennies."
                elif new_climate == "Festival":
                    self.economic_multiplier = 1.40
                    self.active_event_description = "The annual Oakhaven Harvest Festival is underway! Tourists flood the streets."
                
                return f"Notice: The economic climate in Oakhaven has shifted to {new_climate}! {self.active_event_description}"
        
        return ""
