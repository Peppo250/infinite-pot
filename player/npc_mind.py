# player/npc_mind.py
import random
from dataclasses import dataclass, field
from typing import Any

@dataclass
class Promise:
    title: str
    target_day: int
    promise_type: str  # "RelaxTomorrow", "SpendMoney", "RenovateShop"
    active: bool = True
    fulfilled: bool = False

@dataclass
class NPCMind:
    name: str
    archetype: str  # "Artist", "Scholar", "Entrepreneur"
    
    # 1. Identity (Permanent traits)
    age: int = 24
    occupation: str = "Unknown"
    birthday: str = "Spring 14"
    education: str = "Apprenticeship"
    family: str = "Mother and younger sister"
    favorite_food: str = "Berry Cobbler"
    favorite_season: str = "Autumn"
    dream: str = "Create a masterwork"
    biggest_fear: str = "Irrelevance"
    love_language: str = "Quality Time"
    humor_style: str = "Sarcastic"
    
    # 2. Personality (Big Five, 0 to 100)
    openness: float = 50.0
    conscientiousness: float = 50.0
    extraversion: float = 50.0
    agreeableness: float = 50.0
    neuroticism: float = 50.0
    
    # 3. Core Values (Permanent, 0 to 100)
    values: dict[str, float] = field(default_factory=dict)
    
    # 4. Dynamic Priorities (0 to 100)
    priorities: dict[str, float] = field(default_factory=dict)
    
    # 5. Emotional State Blend (0 to 100)
    emotions: dict[str, float] = field(default_factory=dict)
    
    # 6. Needs (0 to 100)
    needs: dict[str, float] = field(default_factory=dict)
    
    # 7. Opinions of Player (0 to 100)
    opinions: dict[str, float] = field(default_factory=dict)
    
    # 8. Multidimensional Trust Network (0 to 100)
    trust_network: dict[str, float] = field(default_factory=dict)
    
    # 9. Promises & Dialogue System state
    promises: list[Promise] = field(default_factory=list)
    internal_monologue: list[str] = field(default_factory=list)
    gossip_network: dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        # Configure archetype-specific profiles
        if self.archetype == "Artist":
            self.occupation = "Florist & Painter"
            self.favorite_food = "Berry Cobbler"
            self.favorite_season = "Autumn"
            self.dream = "Paint a mural that captures Oakhaven's soul"
            self.biggest_fear = "Losing creative spark"
            self.love_language = "Quality Time"
            self.humor_style = "Playful & Whimsical"
            
            # Big Five
            self.openness = 85.0
            self.conscientiousness = 35.0
            self.extraversion = 60.0
            self.agreeableness = 70.0
            self.neuroticism = 55.0
            
            self.values = {"Creativity": 95.0, "Family": 80.0, "Freedom": 90.0, "Money": 20.0, "Prestige": 15.0}
            self.priorities = {"Self": 40.0, "Home": 30.0, "Player": 20.0, "Restaurant": 10.0}
            self.needs = {"Attention": 70.0, "Adventure": 60.0, "Romance": 80.0, "Rest": 40.0}
            
        elif self.archetype == "Scholar":
            self.occupation = "Historical Researcher"
            self.favorite_food = "Chamomile Honey Tea"
            self.favorite_season = "Winter"
            self.dream = "Uncover Oakhaven's founding secrets"
            self.biggest_fear = "Making catastrophic factual errors"
            self.love_language = "Acts of Service"
            self.humor_style = "Dry & Wit"
            
            # Big Five
            self.openness = 70.0
            self.conscientiousness = 90.0
            self.extraversion = 30.0
            self.agreeableness = 50.0
            self.neuroticism = 40.0
            
            self.values = {"Tradition": 85.0, "Honesty": 95.0, "Security": 75.0, "Creativity": 50.0, "Prestige": 40.0}
            self.priorities = {"Self": 30.0, "Home": 25.0, "Player": 25.0, "Restaurant": 20.0}
            self.needs = {"Conversation": 80.0, "Security": 75.0, "Rest": 65.0, "Romance": 40.0}
            
        else:  # Entrepreneur
            self.occupation = "Logistics Coordinator"
            self.favorite_food = "Roast Venison"
            self.favorite_season = "Spring"
            self.dream = "Establish Oakhaven's leading trading guild"
            self.biggest_fear = "Bankruptcy & Failure"
            self.love_language = "Words of Affirmation"
            self.humor_style = "Sharp & Direct"
            
            # Big Five
            self.openness = 55.0
            self.conscientiousness = 95.0
            self.extraversion = 80.0
            self.agreeableness = 45.0
            self.neuroticism = 45.0
            
            self.values = {"Career": 95.0, "Money": 90.0, "Prestige": 85.0, "Family": 50.0, "Freedom": 60.0}
            self.priorities = {"Restaurant": 45.0, "Self": 25.0, "Player": 20.0, "Home": 10.0}
            self.needs = {"Achievement": 90.0, "Security": 70.0, "Romance": 50.0, "Attention": 50.0}

        # Initialize base emotions
        self.emotions = {
            "Happy": 50.0, "Stressed": 30.0, "Excited": 40.0, "Lonely": 30.0,
            "Inspired": 50.0, "Proud": 40.0, "Comfortable": 60.0, "Hopeful": 60.0
        }
        
        # Initialize opinions of player
        self.opinions = {
            "Reliable": 50.0, "Kind": 50.0, "Greedy": 20.0, "Funny": 40.0,
            "Hardworking": 50.0, "Selfish": 20.0, "Patient": 50.0, "Creative": 40.0
        }
        
        # Initialize multi-dimensional trust network
        self.trust_network = {
            "Trust": 40.0, "Respect": 40.0, "Comfort": 45.0,
            "Physical Attraction": 50.0, "Admiration": 40.0,
            "Dependency": 20.0, "Friendship": 40.0
        }
        
        # Town connections / Gossip
        self.gossip_network = {
            "Barnaby": "Old Barnaby always slurps his soup too loud, but he has a kind heart.",
            "Arthur": "Arthur knows his way around a kitchen. He gives useful design feedback.",
            "Martha": "Martha has grading folders stacked up to her chin, she needs to rest more."
        }
        
        self.internal_monologue.append(f"Met the new chef today. They seem determined, if a bit quiet.")

    def get_romance_score(self) -> float:
        """Romance emerges from multi-dimensional trust ratings."""
        trust = self.trust_network.get("Trust", 40.0)
        comfort = self.trust_network.get("Comfort", 40.0)
        attraction = self.trust_network.get("Physical Attraction", 50.0)
        respect = self.trust_network.get("Respect", 40.0)
        
        # Emergent blend formula
        score = (trust * 0.3) + (comfort * 0.3) + (attraction * 0.25) + (respect * 0.15)
        return max(0.0, min(100.0, score))

    def update_evening_state(self, state):
        """Simulates internal changes overnight based on diner parameters."""
        # 1. Stress levels increase if the diner is running excessive hours or under competitor threat
        if state.competitor.is_active:
            self.emotions["Stressed"] = min(100.0, self.emotions["Stressed"] + 4.0)
            self.emotions["Comfortable"] = max(0.0, self.emotions["Comfortable"] - 2.0)
        
        # 2. Check broken promises
        day = state.day
        for p in self.promises:
            if p.active and day > p.target_day:
                p.active = False
                # Player failed the promise
                self.trust_network["Trust"] = max(0.0, self.trust_network["Trust"] - 12.0)
                self.trust_network["Respect"] = max(0.0, self.trust_network["Respect"] - 8.0)
                self.opinions["Reliable"] = max(0.0, self.opinions["Reliable"] - 15.0)
                self.internal_monologue.append(f"They broke their promise about '{p.title}'. It hurts when someone says one thing and does another.")
                
        # 3. Rest level decays if they helped in shop
        if state.free_time < 2.0 and "Rest" in self.needs:
            self.needs["Rest"] = min(100.0, self.needs["Rest"] + 10.0)

    def verify_promise(self, promise_type: str, status: bool, state):
        """Called when player satisfies or breaches a promise during the day."""
        for p in self.promises:
            if p.active and p.promise_type == promise_type:
                p.active = False
                p.fulfilled = status
                if status:
                    self.trust_network["Trust"] = min(100.0, self.trust_network["Trust"] + 10.0)
                    self.trust_network["Respect"] = min(100.0, self.trust_network["Respect"] + 5.0)
                    self.opinions["Reliable"] = min(100.0, self.opinions["Reliable"] + 12.0)
                    self.internal_monologue.append(f"They kept their word about '{p.title}'. It makes me feel secure knowing they stand by what they say.")
                else:
                    self.trust_network["Trust"] = max(0.0, self.trust_network["Trust"] - 12.0)
                    self.opinions["Reliable"] = max(0.0, self.opinions["Reliable"] - 15.0)
                    self.internal_monologue.append(f"They failed the promise for '{p.title}'. Trust is hard to rebuild.")

    def generate_conversation(self, state, current_place: str = "Tavern") -> dict[str, Any]:
        """Generates dynamic dialog options based on internal state variables."""
        mood = "Neutral"
        max_em = max(self.emotions.items(), key=lambda x: x[1])
        if max_em[1] > 60.0:
            mood = max_em[0]
            
        time_str = getattr(state, "time_of_day", "Evening")
        weather = state.town.economic_climate
        
        # 1. Greeting builder
        greetings = {
            "Artist": {
                "Happy": ["Hey! I'm so glad you stopped by.", "Hi! Look at the light right now, isn't it beautiful?"],
                "Stressed": ["Oh, hi. Just cleaning up some brushes...", "Hey. It's been a hectic day."],
                "Neutral": ["Hi there. Ready for a chat?", "Hello! Good to see you."]
            },
            "Scholar": {
                "Happy": ["Hello. I just made some interesting notes.", "Ah, there you are. Glad you could make it."],
                "Stressed": ["Hello. Excuse the mess, I am trying to organize these maps.", "Hi. I've been reading for hours, my eyes are strained."],
                "Neutral": ["Greetings. How was your shift today?", "Hello. Always good to take a breather."]
            },
            "Entrepreneur": {
                "Happy": ["Hey! Perfect timing, business is moving.", "Hi! Let's get a drink and talk plans."],
                "Stressed": ["Hey. Sebastian's latest moves have been keeping me up.", "Hi. The ledger reviews today were exhausting."],
                "Neutral": ["Hello. Let's catch up.", "Hi. What's the status of the kitchen today?"]
            }
        }
        
        greet_list = greetings.get(self.archetype, greetings["Artist"]).get(mood, greetings["Artist"]["Neutral"])
        greeting = random.choice(greet_list)
        
        # 2. Context Observation
        observation = ""
        if weather == "Monsoon Week":
            observation = " You must be soaked from that monsoon downpour outside."
        elif weather == "Supply Strike":
            observation = " The strike in the market has everyone talking. Standing firm?"
        elif state.restaurant.meals_served_today > 20:
            observation = " You served so many customers today, you look exhausted."
            
        # 3. Memory Recall
        memory_remark = ""
        romance_score = self.get_romance_score()
        if romance_score > 50.0:
            memory_remark = f" Remember when we shared that porch swing quiet evening? It felt peaceful."
            
        # 4. Archetype Topic Question
        topics = {
            "Artist": [
                ("art", "Have you thought about taking tomorrow off? We could go paint by the river.", "RelaxTomorrow"),
                ("dreams", "Do you think Oakhaven will remember us for the food, or for the warm stove?", None),
                ("home", "A home needs warm lights and soft carpets. Ready to expand our cottage?", "SpendMoney")
            ],
            "Scholar": [
                ("history", "The archives show Oakhaven had economic strikes a century ago. How are you holding up?", None),
                ("books", "I found a ledger on historic restaurant kitchen layouts. Ready to upgrade the shop?", "RenovateShop"),
                ("future", "Safety margins are essential for survival. Are you keeping cash reserves?", None)
            ],
            "Entrepreneur": [
                ("business", "Sebastian is aggressive, but our customer count is growing. What's the goal for tomorrow?", None),
                ("marketing", "We should run a counter-campaign. Are we allocating cash for it?", "SpendMoney"),
                ("prestige", "A Level 4 Restaurant is the only way to get Sebastian's respect. Let's aim high.", "RenovateShop")
            ]
        }
        
        selected_topic = random.choice(topics.get(self.archetype, topics["Artist"]))
        topic_name, question, promise_trigger = selected_topic
        
        full_dialogue = f"{greeting}{observation}{memory_remark} {question}"
        
        # 5. Generate player choices with distinct intents
        choices = []
        if topic_name == "art" or topic_name == "history" or topic_name == "business":
            choices.append({"text": "I would love that. Let's do it.", "intent": "Romantic" if self.archetype == "Artist" else "Ambitious", "promise": promise_trigger})
            choices.append({"text": "Business comes first right now.", "intent": "Practical", "promise": None})
            choices.append({"text": "Let's crack a joke and deflect.", "intent": "Funny", "promise": None})
            choices.append({"text": "Tell me more about what you think.", "intent": "Curious", "promise": None})
        else:
            choices.append({"text": "Yes, I agree completely.", "intent": "Supportive", "promise": promise_trigger})
            choices.append({"text": "We need to save our cash.", "intent": "Practical", "promise": None})
            choices.append({"text": "Honestly, I'm too tired to think about this.", "intent": "Apologetic", "promise": None})
            choices.append({"text": "Silence.", "intent": "Silent", "promise": None})
            
        return {
            "dialogue": full_dialogue,
            "choices": choices,
            "topic": topic_name,
            "promise_trigger": promise_trigger
        }

    def process_reply(self, intent: str, promise_trigger: str, state) -> dict[str, Any]:
        """Calculates NPC reaction based on player intent, mood, values, and personality."""
        # 1. Match reaction output based on Big Five and Core Values
        reaction_text = ""
        trust_change = 0.0
        respect_change = 0.0
        comfort_change = 0.0
        
        monologue_entry = ""
        
        # Base modifiers based on archetype personality
        if self.archetype == "Artist":
            if intent in ["Romantic", "Supportive"]:
                trust_change = 8.0
                comfort_change = 6.0
                reaction_text = "She smiles warmly, her eyes glowing. 'That makes me happy. I feel like you really understand me.'"
                monologue_entry = "They were very supportive today. It feels good to know they care about creativity and peace over just coins."
            elif intent == "Practical":
                trust_change = -2.0
                comfort_change = -3.0
                reaction_text = "She sighs softly. 'I understand we need coins, but sometimes you look right past the beauty of the moment.'"
                monologue_entry = "Always so practical. I worry they are letting the diner consume their entire spirit."
            elif intent == "Funny":
                trust_change = 4.0
                reaction_text = "She laughs, a light and whimsical sound. 'You always know how to make me laugh!'"
                monologue_entry = "Their sense of humor is silly, but it lightens my heart when things get stressful."
            else:
                reaction_text = "She nods quietly, observing your expression."
                monologue_entry = "A quiet exchange today. I wonder what they are thinking."
                
        elif self.archetype == "Scholar":
            if intent == "Curious":
                trust_change = 6.0
                respect_change = 8.0
                reaction_text = "Her eyes light up with intellectual excitement. 'Precisely! It is fascinating how history repeats itself.'"
                monologue_entry = "They showed genuine curiosity today. It is refreshing to have a partner who values learning and dialogue."
            elif intent == "Practical":
                trust_change = 4.0
                respect_change = 6.0
                reaction_text = "She adjusts her glasses and nods. 'Pragmatic. A stable safety margin is logical for Oakhaven right now.'"
                monologue_entry = "Their logical approach is comforting. They don't take uncalculated risks."
            elif intent == "Funny":
                respect_change = -2.0
                reaction_text = "She gives you a dry look. 'Amusing, but let's stay focused on the subject.'"
                monologue_entry = "Always joking, even when we are discussing serious matters. I wish they'd take it more seriously."
            else:
                reaction_text = "She notes your response and continues her reading."
                monologue_entry = "They seemed somewhat distant today."
                
        else:  # Entrepreneur
            if intent == "Ambitious":
                trust_change = 6.0
                respect_change = 9.0
                reaction_text = "She grins confidently. 'Exactly! We will outperform Bistro Gourmet and build an empire here!'"
                monologue_entry = "They have drive. That ambition is exactly what we need to scale this restaurant."
            elif intent == "Supportive":
                trust_change = 8.0
                comfort_change = 4.0
                reaction_text = "She relaxes her shoulders. 'Thanks. Having you stand by my plans makes the hustle worth it.'"
                monologue_entry = "They supported my trading guild ideas today. Having their trust makes me push harder."
            elif intent == "Apologetic":
                comfort_change = 5.0
                reaction_text = "She softens her stance. 'I know. It's been hard on both of us. Let's get through this strike together.'"
                monologue_entry = "They apologized for the stress today. I need to remember to check in on their energy levels."
            elif intent == "Practical":
                respect_change = 5.0
                reaction_text = "She nods in agreement. 'Agreed. Cutting variable expenses is the correct move for the ledger.'"
                monologue_entry = "A smart financial decision today. They understand resource allocation."
            else:
                reaction_text = "She crosses her arms, looking thoughtful."
                monologue_entry = "They were very brief today. Hope they aren't losing their drive."

        # Apply changes to trust network
        self.trust_network["Trust"] = max(0.0, min(100.0, self.trust_network.get("Trust", 40.0) + trust_change))
        self.trust_network["Respect"] = max(0.0, min(100.0, self.trust_network.get("Respect", 40.0) + respect_change))
        self.trust_network["Comfort"] = max(0.0, min(100.0, self.trust_network.get("Comfort", 45.0) + comfort_change))
        
        # 2. Record promise if created
        if promise_trigger:
            new_promise = Promise(
                title=f"Fulfill {promise_trigger} for {self.name}",
                target_day=state.day + 1,
                promise_type=promise_trigger
            )
            self.promises.append(new_promise)
            reaction_text += f"\n*(Promise Created: {new_promise.title})*"
            monologue_entry += f" They made a promise to me. I'll hold them to it."

        if monologue_entry:
            self.internal_monologue.append(monologue_entry)
            
        return {
            "reaction": reaction_text,
            "trust": self.trust_network["Trust"],
            "comfort": self.trust_network["Comfort"],
            "respect": self.trust_network["Respect"],
            "romance": self.get_romance_score()
        }
