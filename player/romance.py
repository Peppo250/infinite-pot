from dataclasses import dataclass, field
import random
from typing import Any

@dataclass
class RomanticCharacter:
    name: str
    archetype: str  # "Artist", "Scholar", "Entrepreneur"
    romance_level: float = 0.0
    is_partner: bool = False
    is_co_owner: bool = False
    decay_rate: float = 2.0
    attraction_boost: float = 0.05
    schedule: list[str] = field(default_factory=list)
    description: str = ""

    def interact_talk(self) -> tuple[str, float]:
        """Player talks to the character. Returns (dialogue, romance_gain)."""
        gain = random.uniform(3.0, 6.0)
        self.romance_level = min(100.0, self.romance_level + gain)
        
        dialogues = {
            "Artist": [
                f"{self.name} talks passionately about color theory and how food is another canvas. (+{gain:.1f} Romance)",
                f"{self.name} shares a sketch she made of Oakhaven's square. (+{gain:.1f} Romance)",
                f"{self.name} wonders if true beauty lies in fleeting moments or permanent creations. (+{gain:.1f} Romance)"
            ],
            "Scholar": [
                f"{self.name} discusses the history of Oakhaven and old trade logs. (+{gain:.1f} Romance)",
                f"{self.name} explains a complex economic theory about infinite resource dynamics. (+{gain:.1f} Romance)",
                f"{self.name} looks up from her book and shares an interesting quote with you. (+{gain:.1f} Romance)"
            ],
            "Entrepreneur": [
                f"{self.name} analyzes Chef Sebastian's marketing tactics and suggests counter-tactics. (+{gain:.1f} Romance)",
                f"{self.name} talks about her business dreams and the value of hard work. (+{gain:.1f} Romance)",
                f"{self.name} reviews your menu prices and suggests a margin expansion strategy! (+{gain:.1f} Romance)"
            ]
        }
        
        chosen_dialogue = random.choice(dialogues[self.archetype])
        return chosen_dialogue, gain

    def interact_drink(self, drink_cost: float = 25.0) -> tuple[str, float]:
        """Player buys a drink for the character. Returns (dialogue, romance_gain)."""
        # Entrepreneur likes expensive stuff, Artist likes cozy drinks, Scholar likes good coffee/tea
        mults = {"Artist": 1.2, "Scholar": 1.0, "Entrepreneur": 1.4}
        gain = random.uniform(8.0, 12.0) * mults[self.archetype]
        self.romance_level = min(100.0, self.romance_level + gain)
        
        dialogues = {
            "Artist": f"You buy {self.name} a glass of sweet plum wine. She smiles and notes how the candlelight catches the glass. (+{gain:.1f} Romance)",
            "Scholar": f"You buy {self.name} a dark stout. She raises her glass and toast to intellectual curiosity. (+{gain:.1f} Romance)",
            "Entrepreneur": f"You buy {self.name} a premium imported champagne. She clinks glasses and says: 'To scaling operations.' (+{gain:.1f} Romance)"
        }
        
        return dialogues[self.archetype], gain

@dataclass
class RomanceSystem:
    characters: list[RomanticCharacter] = field(default_factory=list)
    active_partner_name: str | None = None  # Name of active partner (only one allowed)
    has_ring: bool = False
    wedding_tier: str = "None"  # "None", "Modest", "Elegant", "Royal"
    
    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "RomanceSystem":
        # Generate our 3 unique girls
        names_artist = ["Clara", "Maya", "Elena", "Sophie", "Chloe"]
        names_scholar = ["Sarah", "Ada", "Grace", "Evelyn", "Zoe"]
        names_entrepreneur = ["Victoria", "Roxanne", "Samantha", "Iris", "Diana"]
        
        c1 = RomanticCharacter(
            name=random.choice(names_artist),
            archetype="Artist",
            decay_rate=4.0,
            attraction_boost=0.06,
            schedule=["Tuesday", "Thursday", "Saturday"],
            description="A creative florist and painter who values emotional connection and deep conversations."
        )
        c2 = RomanticCharacter(
            name=random.choice(names_scholar),
            archetype="Scholar",
            decay_rate=2.0,
            attraction_boost=0.09,
            schedule=["Monday", "Wednesday", "Friday"],
            description="An independent researcher studying Oakhaven's history, pragmatic and intellectually driven."
        )
        c3 = RomanticCharacter(
            name=random.choice(names_entrepreneur),
            archetype="Entrepreneur",
            decay_rate=6.0,
            attraction_boost=0.16,
            schedule=["Wednesday", "Friday", "Sunday"],
            description="A high-energy logistics manager looking to start her own business, ambitious and demanding."
        )
        
        return cls(characters=[c1, c2, c3], active_partner_name=None, has_ring=False, wedding_tier="None")

    @property
    def partner(self) -> RomanticCharacter | None:
        """Returns the active romantic partner if any."""
        if not self.active_partner_name:
            return None
        return next((c_item for c_item in self.characters if c_item.name == self.active_partner_name), None)

    @property
    def partner_name(self) -> str:
        p = self.partner
        return p.name if p else "None"

    @property
    def stage_name(self) -> str:
        p = self.partner
        if not p:
            return "Single"
        if p.is_co_owner:
            return "Married & Business Co-Owner"
        if p.is_partner:
            return "Partner"
        return "Single"

    @property
    def romance_level(self) -> float:
        p = self.partner
        return p.romance_level if p else 0.0

    @romance_level.setter
    def romance_level(self, value: float) -> None:
        p = self.partner
        if p:
            p.romance_level = value

    @property
    def is_co_owner(self) -> bool:
        p = self.partner
        return p.is_co_owner if p else False

    def get_characters_available(self, day_name: str) -> list[RomanticCharacter]:
        """Returns characters hanging out at the bar on the current day."""
        return [c_item for c_item in self.characters if day_name in c_item.schedule]

    def propose_relationship(self, name: str) -> tuple[bool, str]:
        """Player asks the character to be their partner."""
        char = next((c_item for c_item in self.characters if c_item.name == name), None)
        if not char:
            return False, "Character not found."

        if self.active_partner_name:
            return False, f"You are already in a relationship with {self.active_partner_name}! You must break up first."

        if char.romance_level < 40.0:
            return False, f"{char.name} likes you, but feels it is too early to commit. (Need 40.0 Romance, currently {char.romance_level:.1f})"

        char.is_partner = True
        self.active_partner_name = char.name
        return True, f"You ask {char.name} to be your partner, and she happily agrees! She is now your partner."

    def break_up(self) -> tuple[bool, str]:
        """Breaks up with the current active partner."""
        p = self.partner
        if not p:
            return False, "You are not in a relationship."

        old_name = p.name
        p.is_partner = False
        p.is_co_owner = False
        p.romance_level = max(0.0, p.romance_level - 30.0)  # Heavy romance hit
        self.active_partner_name = None
        self.has_ring = False
        self.wedding_tier = "None"
        return True, f"You broke up with {old_name}. You are now single."

    def ask_to_co_own(self, has_house: bool) -> tuple[bool, str]:
        """Player asks partner to move in and co-own the business."""
        p = self.partner
        if not p:
            return False, "You do not have a partner to propose to!"

        if p.is_co_owner:
            return False, f"{p.name} is already your co-owner!"

        if p.romance_level < 75.0:
            return False, f"Your relationship isn't close enough yet. (Need 75.0 Romance, currently {p.romance_level:.1f})"

        if not has_house:
            return False, f"{p.name} appreciates the gesture, but feels you need a proper house of your own before taking this step."

        if not self.has_ring:
            return False, f"You need to purchase a Diamond Engagement Ring first!"

        p.is_co_owner = True
        return True, f"{p.name} gasps as you open the velvet box. 'Yes! A thousand times yes!' She moves into your house and joins the restaurant as your wife and Co-Owner!"

    def decay_without_house(self) -> str:
        """Applies daily romance decay if dating without a house. Returns a message if decay occurred."""
        p = self.partner
        if not p or p.is_co_owner:
            return ""

        # Decay romance
        old_val = p.romance_level
        p.romance_level = max(0.0, p.romance_level - p.decay_rate)
        
        # Artist wants emotional security, Entrepreneur has high lifestyle expectations, Scholar is chill
        reasons = {
            "Artist": "needs a stable home environment to feel secure.",
            "Scholar": "wonders when you two will establish a permanent home.",
            "Entrepreneur": "expects you to have a house if you are serious about a life together."
        }
        
        return f"Relation Decay: {p.name}'s romance dropped by {p.decay_rate} pts. She {reasons[p.archetype]} ({old_val:.1f} → {p.romance_level:.1f})"

    def go_on_date(self, current_cash: float, current_energy: float, progress_multiplier: float = 1.0) -> tuple[bool, str, float, float]:
        """Runs a date. Returns (success, message, cash_spent, energy_spent)."""
        p = self.partner
        if not p:
            return False, "You do not have an active partner to go on a date with!", 0.0, 0.0
            
        date_cost = 80.0
        energy_cost_for_date = 25.0
        
        if current_cash < date_cost:
            return False, f"Insufficient cash for a date! Need ${date_cost:.2f}.", 0.0, 0.0
        if current_energy < energy_cost_for_date:
            return False, f"Too tired for a date! Need {energy_cost_for_date} energy.", 0.0, 0.0

        # Calculate progression
        base_progress = 12.0
        actual_progress = base_progress * progress_multiplier
        p.romance_level = min(100.0, p.romance_level + actual_progress)
        
        msg = f"You had a wonderful date with {p.name} at the local park. (+{actual_progress:.1f} Romance)"
        return True, msg, date_cost, energy_cost_for_date
