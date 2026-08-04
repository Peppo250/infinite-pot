from dataclasses import dataclass, field
import random
from typing import Any

@dataclass
class Memory:
    title: str
    category: str    # "Date", "Work", "Milestone", "Everyday"
    emotion: str     # "Happy", "Proud", "Sad", "Disappointed", "Excited", "Angry"
    strength: float  # 0.0 to 10.0
    age: int = 0     # in days
    shared: bool = True

@dataclass
class RomanticCharacter:
    name: str
    archetype: str  # "Artist", "Scholar", "Entrepreneur"
    trust: float = 0.0
    compatibility: float = 0.0
    current_mood: str = "Happy"
    decay_rate: float = 2.0
    attraction_boost: float = 0.05
    schedule: list[str] = field(default_factory=list)
    description: str = ""
    is_partner: bool = False
    is_co_owner: bool = False
    memories: list[Memory] = field(default_factory=list)
    life_goals: list[str] = field(default_factory=list)
    mind: Any = None

    def __post_init__(self):
        from player.npc_mind import NPCMind
        self.mind = NPCMind(self.name, self.archetype)
        self.mind.trust_network["Trust"] = self.trust
        self.mind.trust_network["Friendship"] = self.compatibility

    @property
    def romance_level(self) -> float:
        # Emergent romance level calculation based on active memories, trust, and compatibility
        pos_strength = sum(m.strength for m in self.memories if m.emotion in ["Happy", "Proud", "Excited"])
        neg_strength = sum(m.strength for m in self.memories if m.emotion in ["Sad", "Disappointed", "Angry"])
        
        # Sync values with mind
        if hasattr(self, "mind") and self.mind:
            self.mind.trust_network["Trust"] = self.trust
            self.mind.trust_network["Friendship"] = self.compatibility

        val = pos_strength * 2.0 - neg_strength * 2.0 + (self.trust * 0.6) + (self.compatibility * 0.4)
        return max(0.0, min(100.0, val))

    @romance_level.setter
    def romance_level(self, value: float) -> None:
        # For backward compatibility (tests setting romance directly)
        self.trust = max(0.0, min(100.0, value))
        self.compatibility = max(0.0, min(100.0, value))
        self.memories.clear()
        if hasattr(self, "mind") and self.mind:
            self.mind.trust_network["Trust"] = value
            self.mind.trust_network["Comfort"] = value
            self.mind.trust_network["Physical Attraction"] = value
            self.mind.trust_network["Respect"] = value

    def reinforce_memory(self, title: str, boost: float = 3.0) -> bool:
        for m in self.memories:
            if m.title == title:
                m.strength = min(10.0, m.strength + boost)
                return True
        return False

    def interact_talk(self) -> tuple[str, float]:
        """Player talks to the character. Returns (dialogue, romance_gain)."""
        gain = random.uniform(3.0, 6.0)
        self.trust = min(100.0, self.trust + gain * 0.5)
        self.compatibility = min(100.0, self.compatibility + gain * 0.3)
        
        # Add or reinforce memory
        if not self.reinforce_memory("Tavern Talk", boost=1.5):
            self.memories.append(Memory(title="Tavern Talk", category="Everyday", emotion="Happy", strength=2.0))
            
        dialogues = {
            "Artist": [
                f"{self.name} talks passionately about color theory and how food is another canvas. (Memory created: Tavern Talk)",
                f"{self.name} shares a sketch she made of Oakhaven's square. (Memory created: Tavern Talk)",
                f"{self.name} wonders if true beauty lies in fleeting moments or permanent creations. (Memory created: Tavern Talk)"
            ],
            "Scholar": [
                f"{self.name} discusses the history of Oakhaven and old trade logs. (Memory created: Tavern Talk)",
                f"{self.name} explains a complex economic theory about infinite resource dynamics. (Memory created: Tavern Talk)",
                f"{self.name} looks up from her book and shares an interesting quote with you. (Memory created: Tavern Talk)"
            ],
            "Entrepreneur": [
                f"{self.name} analyzes Chef Sebastian's marketing tactics and suggests counter-tactics. (Memory created: Tavern Talk)",
                f"{self.name} talks about her business dreams and the value of hard work. (Memory created: Tavern Talk)",
                f"{self.name} reviews your menu prices and suggests a margin expansion strategy! (Memory created: Tavern Talk)"
            ]
        }
        
        chosen_dialogue = random.choice(dialogues[self.archetype])
        return chosen_dialogue, gain

    def interact_drink(self, drink_cost: float = 25.0) -> tuple[str, float]:
        """Player buys a drink for the character. Returns (dialogue, romance_gain)."""
        mults = {"Artist": 1.2, "Scholar": 1.0, "Entrepreneur": 1.4}
        gain = random.uniform(8.0, 12.0) * mults[self.archetype]
        self.trust = min(100.0, self.trust + gain * 0.6)
        self.compatibility = min(100.0, self.compatibility + gain * 0.4)
        
        # Add or reinforce memory
        if not self.reinforce_memory("Shared a Drink", boost=2.5):
            self.memories.append(Memory(title="Shared a Drink", category="Everyday", emotion="Happy", strength=4.0))
            
        dialogues = {
            "Artist": f"You buy {self.name} a glass of sweet plum wine. She smiles and notes how the candlelight catches the glass. (Memory: Shared a Drink)",
            "Scholar": f"You buy {self.name} a dark stout. She raises her glass and toast to intellectual curiosity. (Memory: Shared a Drink)",
            "Entrepreneur": f"You buy {self.name} a premium champagne. She clinks glasses and says: 'To scaling operations.' (Memory: Shared a Drink)"
        }
        
        return dialogues[self.archetype], gain

    def generate_procedural_dialogue(self, state) -> str:
        """Assembles procedural dialogue based on Trust, Mood, Energy, Climate, and Memories."""
        
        # 1. Greeting
        greetings = []
        if self.trust >= 75:
            greetings = ["Hello my love.", "Oh, you're finally here!", "I was just thinking about you."]
        else:
            greetings = ["Hello.", "Hey there.", "Nice to see you."]
        greeting = random.choice(greetings)
        
        # 2. Current Situation
        situation = ""
        p = state.player
        r = state.restaurant
        if p.energy < 30:
            situation = "You look absolutely exhausted."
        elif state.town.economic_climate == "Monsoon Week":
            situation = "The monsoon rain outside is relentless today."
        elif state.town.economic_climate == "Supply Strike":
            situation = "Everyone in the square is talking about the trade strike."
        elif r.reputation >= 70:
            situation = "I saw a huge line of customers outside your diner earlier."
        else:
            situation = "It seems quiet in Oakhaven today."
            
        # 3. Memory Recall
        memory_recall = ""
        if self.memories:
            mem = max(self.memories, key=lambda m: m.strength)
            if mem.emotion == "Happy":
                memory_recall = f"Remember our date: '{mem.title}'? It was so special."
            elif mem.emotion == "Proud":
                memory_recall = f"I was so proud when we did '{mem.title}'."
            elif mem.emotion == "Disappointed":
                memory_recall = f"I still feel a bit sad thinking about '{mem.title}'."
            else:
                memory_recall = f"I was thinking about '{mem.title}' the other day."
        else:
            memory_recall = "It's nice to share these quiet moments together."
            
        # 4. Question / Goals
        questions = []
        if self.archetype == "Artist":
            questions = [
                "Have you thought about adding more warm decorations to the cottage?",
                "Do you think we'll be able to attend the next Oakhaven flower festival?",
                "What did you think of the new painting I hung up?"
            ]
        elif self.archetype == "Scholar":
            questions = [
                "How are the diner loan repayments coming along?",
                "Did you know Oakhaven library has logs dating back three centuries?",
                "Are we keeping our financial reserve stable?"
            ]
        else: # Entrepreneur
            questions = [
                "Do you think it's time to upgrade to the Town Restaurant level?",
                "Is the competitor, Bistro Gourmet, still putting pressure on our margins?",
                "Have you negotiated part-time shifts with the staff to cut costs?"
            ]
        question = random.choice(questions)
        
        # 5. Reaction
        reactions = []
        if self.trust >= 80:
            reactions = ["I know we can handle anything together.", "I trust your decisions completely."]
        else:
            reactions = ["I just want to make sure we are on the same page.", "I hope we're moving in the right direction."]
        reaction = random.choice(reactions)
        
        # 6. Closing
        closings = ["Take care of yourself.", "I'll see you back home.", "Let's catch up later."]
        if self.is_co_owner:
            closings = ["Let's head home together.", "See you at the cottage, dear.", "I'm heading home now."]
        closing = random.choice(closings)
        
        return f"{greeting} {situation} {memory_recall} {question} {reaction} {closing}"

@dataclass
class RomanceSystem:
    characters: list[RomanticCharacter] = field(default_factory=list)
    active_partner_name: str | None = None
    has_ring: bool = False
    wedding_tier: str = "None"
    caught_cheating: bool = False
    date_cost: float = 100.0
    energy_cost_for_date: float = 25.0

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "RomanceSystem":
        r_cfg = config.get("romance", {})
        d_cost = r_cfg.get("date_cost", 80.0)
        e_cost = r_cfg.get("energy_cost_for_date", 25.0)
        
        names_artist = ["Clara", "Maya", "Elena", "Sophie", "Chloe"]
        names_scholar = ["Sarah", "Ada", "Grace", "Evelyn", "Zoe"]
        names_entrepreneur = ["Victoria", "Roxanne", "Samantha", "Iris", "Diana"]
        
        c1 = RomanticCharacter(
            name=random.choice(names_artist),
            archetype="Artist",
            decay_rate=4.0,
            attraction_boost=0.06,
            schedule=["Tuesday", "Thursday", "Saturday"],
            description="A creative florist and painter who values emotional connection and deep conversations.",
            memories=[Memory(title="First Conversation", category="Everyday", emotion="Happy", strength=3.0)],
            life_goals=["Decorate cottage together", "Attend spring festival", "Own a cozy greenhouse"]
        )
        c2 = RomanticCharacter(
            name=random.choice(names_scholar),
            archetype="Scholar",
            decay_rate=2.0,
            attraction_boost=0.09,
            schedule=["Monday", "Wednesday", "Friday"],
            description="An independent researcher studying Oakhaven's history, pragmatic and intellectually driven.",
            memories=[Memory(title="First Conversation", category="Everyday", emotion="Happy", strength=3.0)],
            life_goals=["Build financial safety margin", "Read in the library together", "Contribute to community standing"]
        )
        c3 = RomanticCharacter(
            name=random.choice(names_entrepreneur),
            archetype="Entrepreneur",
            decay_rate=6.0,
            attraction_boost=0.16,
            schedule=["Wednesday", "Friday", "Sunday"],
            description="A high-energy logistics manager looking to start her own business, ambitious and demanding.",
            memories=[Memory(title="First Conversation", category="Everyday", emotion="Happy", strength=3.0)],
            life_goals=["Scale to Town Restaurant", "Employ helper staff", "Outperform Bistro Gourmet"]
        )
        
        return cls(
            characters=[c1, c2, c3],
            active_partner_name=None,
            has_ring=False,
            wedding_tier="None",
            caught_cheating=False,
            date_cost=d_cost,
            energy_cost_for_date=e_cost
        )

    @property
    def partner(self) -> RomanticCharacter | None:
        spouse = next((c for c in self.characters if c.is_co_owner), None)
        if spouse:
            return spouse
        partner = next((c for c in self.characters if c.is_partner), None)
        if partner:
            return partner
        if self.active_partner_name:
            return next((c for c in self.characters if c.name == self.active_partner_name), None)
        return None

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
        bar_girls = []
        for c in self.characters:
            if c.is_co_owner or day_name in c.schedule:
                bar_girls.append(c)
        return bar_girls

    def get_helping_characters(self, day_name: str) -> list[RomanticCharacter]:
        helpers = []
        for c in self.characters:
            if c.is_co_owner:
                helpers.append(c)
            elif c.is_partner and day_name in c.schedule:
                helpers.append(c)
        return helpers

    def get_present_characters_at_place(self, place_name: str, day_name: str) -> list[RomanticCharacter]:
        if place_name == "Restaurant":
            return self.get_helping_characters(day_name)
        elif place_name in ["Bar", "Tavern"]:
            return self.get_characters_available(day_name)
        elif place_name == "Home":
            return [c for c in self.characters if c.is_co_owner]
        return []

    def trigger_cheating_scandal(self, state=None) -> str:
        self.caught_cheating = True
        ex_names = [c.name for c in self.characters if c.is_partner or c.is_co_owner]
        if not ex_names:
            ex_names = [c.name for c in self.characters if c.romance_level >= 40.0]
            
        for c in self.characters:
            c.is_partner = False
            c.is_co_owner = False
            c.memories.clear()
            c.trust = 0.0
            c.compatibility = 0.0
            
        self.active_partner_name = None
        self.has_ring = False
        self.wedding_tier = "None"
        
        alimony_msg = ""
        if state:
            h = getattr(state, "house", None)
            p = getattr(state, "player", None)
            f = getattr(state, "finance", None)
            
            if h:
                h.purchased = False
                h.upgrades.clear()
            if p:
                p.has_house = False
                alimony_total = max(1500.0, p.cash * 0.50)
                p.adjust_cash(-alimony_total)
                alimony_msg = f" Ordered ${alimony_total:.2f} in lump-sum alimony paid to your exes."
                if f:
                    f.record_transaction("Misc", -alimony_total, "Seized cash & lump-sum alimony paid to exes under court order")
                    
        names_str = " and ".join(ex_names) if ex_names else "Your partners"
        return (
            f"⚖️ CHEATING SCANDAL & PROPERTY SEIZURE!\n\n"
            f"{names_str} discovered you were dating multiple partners simultaneously!\n"
            f"All partners left you immediately, Oakhaven Family Court seized your cottage and home furnishings,{alimony_msg} "
            f"You are legally barred from future relationships!"
        )

    def propose_relationship(self, name: str, day_name: str = None, state=None, current_place: str = "Bar") -> tuple[bool, str]:
        if self.caught_cheating:
            return False, "You were caught cheating and are legally barred from proposing relationships under Oakhaven family court orders!"

        char = next((c_item for c_item in self.characters if c_item.name == name), None)
        if not char:
            return False, "Character not found."

        if char.is_partner or char.is_co_owner:
            return False, f"You are already in a relationship with {char.name}!"

        if char.romance_level < 40.0:
            return False, f"{char.name} likes you, but feels it is too early to commit. (Need 40.0 Romance, currently {char.romance_level:.1f})"

        if day_name:
            present_girls = self.get_present_characters_at_place(current_place, day_name)
            other_present_partners = [g for g in present_girls if g.name != name and (g.is_partner or g.is_co_owner)]
            if other_present_partners:
                scandal_msg = self.trigger_cheating_scandal(state)
                return False, scandal_msg

        if 40.0 <= char.romance_level < 60.0:
            if random.random() < 0.5:
                char.trust = max(0.0, char.trust - 10.0)
                return False, f"{char.name} hesitates. 'I like you, but I don't feel ready to commit yet.' (Try building romance to 60.0 for a guaranteed yes!)"

        char.is_partner = True
        self.active_partner_name = char.name
        
        # Add milestone memory
        char.memories.append(Memory(title="Became Partners", category="Milestone", emotion="Happy", strength=8.0))
        
        return True, f"You ask {char.name} to be your partner, and she happily agrees! (Memory created: Became Partners)"

    def break_up(self, target_name: str = None) -> tuple[bool, str]:
        if target_name:
            p = next((c for c in self.characters if c.name == target_name and (c.is_partner or c.is_co_owner)), None)
        else:
            p = self.partner
            
        if not p:
            return False, "You are not in a relationship with this person."

        old_name = p.name
        p.is_partner = False
        p.is_co_owner = False
        p.trust = max(0.0, p.trust - 30.0)
        p.compatibility = max(0.0, p.compatibility - 20.0)
        p.memories.clear() # clear good memories, leaves a clean break
        
        next_partner = next((c for c in self.characters if c.is_partner or c.is_co_owner), None)
        self.active_partner_name = next_partner.name if next_partner else None
        
        if not next_partner:
            self.has_ring = False
            self.wedding_tier = "None"
        return True, f"You broke up with {old_name}."

    def ask_to_co_own(self, has_house: bool, state=None) -> tuple[bool, str]:
        if self.caught_cheating:
            return False, "You were caught cheating and are legally barred from proposing marriage under Oakhaven family court orders!"

        p = self.partner
        if not p:
            return False, "You do not have a partner to propose to!"

        if p.is_co_owner:
            return False, f"{p.name} is already your co-owner!"

        if p.romance_level < 75.0:
            return False, f"Your relationship isn't close enough yet. (Need 75.0 Romance, currently {p.romance_level:.1f})"

        if not has_house:
            return False, f"{p.name} appreciates the gesture, but feels you need a proper cottage before taking this step."

        if not self.has_ring:
            return False, f"You need to purchase a Diamond Engagement Ring first!"

        if 75.0 <= p.romance_level < 90.0:
            if random.random() < 0.5:
                p.trust = max(0.0, p.trust - 15.0)
                return False, f"{p.name} looks at the diamond ring, but shakes her head gently. 'I'm not sure if we're ready for marriage yet, let's take it slow.' (Try building romance to 90.0 for a guaranteed yes!)"

        p.is_co_owner = True
        p.is_partner = True
        
        # Add wedding memory
        p.memories.append(Memory(title="Wedding Day", category="Milestone", emotion="Proud", strength=10.0))
        
        return True, f"{p.name} gasps as you open the velvet box. 'Yes! A thousand times yes!' She moves into your cottage as your wife and Co-Owner! (Memory created: Wedding Day)"

    def apply_jealousy(self, active_girl_name: str, day_name: str, state=None, current_place: str = "Bar") -> list[str]:
        notices = []
        active_girl = next((c for c in self.characters if c.name == active_girl_name), None)
        present_girls = self.get_present_characters_at_place(current_place, day_name)
        
        if active_girl and (active_girl.is_partner or active_girl.is_co_owner):
            other_present_partners = [g for g in present_girls if g.name != active_girl_name and (g.is_partner or g.is_co_owner)]
            if other_present_partners:
                scandal_msg = self.trigger_cheating_scandal(state)
                notices.append(scandal_msg)
                return notices

        for g in present_girls:
            if g.name == active_girl_name:
                continue
            if g.is_partner or g.is_co_owner or g.romance_level > 20.0:
                mults = {"Artist": 1.3, "Scholar": 0.8, "Entrepreneur": 1.6}
                base_drop = 6.0 if (g.is_partner or g.is_co_owner) else 3.5
                loss = (base_drop + (g.romance_level * 0.12)) * mults[g.archetype]
                
                old_val = g.romance_level
                g.trust = max(0.0, g.trust - loss * 1.5)
                g.compatibility = max(0.0, g.compatibility - loss * 0.8)
                
                # Create a negative memory
                g.memories.append(Memory(title=f"Caught Flirting with {active_girl_name}", category="Difficult", emotion="Disappointed", strength=6.0))
                
                notices.append(
                    f"💔 {g.name} ({g.archetype}) saw you flirting with {active_girl_name} at the {current_place}! "
                    f"Romance with {g.name} dropped. (Memory created: Caught Flirting)"
                )
        return notices

    def decay_without_house(self) -> str:
        p = self.partner
        if not p or p.is_co_owner:
            return ""

        old_val = p.romance_level
        p.trust = max(0.0, p.trust - p.decay_rate)
        p.compatibility = max(0.0, p.compatibility - p.decay_rate * 0.5)
        
        # Add small everyday friction memory
        if random.random() < 0.3:
            p.memories.append(Memory(title="No cottage to share", category="Difficult", emotion="Disappointed", strength=3.0))
            
        reasons = {
            "Artist": "needs a stable home environment to feel secure.",
            "Scholar": "wonders when you two will establish a permanent home.",
            "Entrepreneur": "expects you to have a house if you are serious about a life together."
        }
        
        return f"Relation Decay: {p.name}'s trust dropped due to lack of a cottage. She {reasons[p.archetype]}"

    def go_on_date(self, current_cash: float, current_energy: float, progress_multiplier: float = 1.0) -> tuple[bool, str, float, float]:
        p = self.partner
        if not p:
            return False, "You do not have an active partner to go on a date with!", 0.0, 0.0
            
        date_cost = self.date_cost
        energy_cost_for_date = self.energy_cost_for_date
        
        if current_cash < date_cost:
            return False, f"Insufficient cash for a date! Need ${date_cost:.2f}.", 0.0, 0.0
        if current_energy < energy_cost_for_date:
            return False, f"Too tired for a date! Need {energy_cost_for_date} energy.", 0.0, 0.0

        p.trust = min(100.0, p.trust + 8.0 * progress_multiplier)
        p.compatibility = min(100.0, p.compatibility + 5.0 * progress_multiplier)
        
        # Choose procedural date template title
        templates = ["Stroll in Oakhaven Park", "Candlelit Cottage Dinner", "Picnic by the Delta River", "Walk in the Summer Rain"]
        date_title = random.choice(templates)
        
        # Add or reinforce memory
        if not p.reinforce_memory(date_title, boost=3.5 * progress_multiplier):
            p.memories.append(Memory(title=date_title, category="Date", emotion="Happy", strength=6.0))
            
        msg = f"You had a wonderful date: '{date_title}' with {p.name}."
        return True, msg, date_cost, energy_cost_for_date
