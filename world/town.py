from dataclasses import dataclass, field
import random

@dataclass
class Town:
    name: str = "Oakhaven"
    economic_climate: str = "Stable Season"
    economic_multiplier: float = 1.0
    active_event_description: str = "A quiet, peaceful day in Oakhaven."
    days_since_climate_change: int = 0

    def roll_economic_climate(self) -> str:
        """Randomly changes or updates the economic climate of the town.
        Climates last for several days to a week.
        """
        self.days_since_climate_change += 1
        
        # Only change climate occasionally
        if self.days_since_climate_change >= 4 and random.random() < 0.15:
            climates = ["Stable Season", "Boom", "Economic Slowdown", "Founder's Feast", "Monsoon Week", "Supply Strike"]
            weights = [0.40, 0.15, 0.15, 0.10, 0.10, 0.10]
            new_climate = random.choices(climates, weights=weights)[0]
            
            if new_climate != self.economic_climate:
                self.economic_climate = new_climate
                self.days_since_climate_change = 0
                
                if new_climate == "Stable Season":
                    self.economic_multiplier = 1.0
                    self.active_event_description = "The weather is stable and Oakhaven commerce is quiet."
                elif new_climate == "Boom":
                    self.economic_multiplier = 1.25
                    self.active_event_description = "A surge in local commerce has everyone spending freely!"
                elif new_climate == "Economic Slowdown":
                    self.economic_multiplier = 0.80
                    self.active_event_description = "A slowdown in trade makes the townsfolk pinch pennies."
                elif new_climate == "Founder's Feast":
                    self.economic_multiplier = 1.40
                    self.active_event_description = "The annual Oakhaven Founder's Feast is underway! Tourists flood the square."
                elif new_climate == "Monsoon Week":
                    self.economic_multiplier = 0.90
                    self.active_event_description = "Relentless monsoon rains flood the valley and limit dining cart traffic."
                elif new_climate == "Supply Strike":
                    self.economic_multiplier = 1.0
                    self.active_event_description = "A local parts strike has caused material and maintenance fees to rise."
                
                return f"Notice: The economic climate in Oakhaven has shifted to {new_climate}! {self.active_event_description}"
        
        return ""
