from events.event_system import GameEvent, EventOption
import random

def get_default_events() -> list[GameEvent]:
    events = []

    # 1. Charity: Hungry Kids
    def feed_kids_action(state):
        state.player.adjust_energy(-20)
        state.restaurant.adjust_reputation(10)
        state.finance.record_transaction("Misc", 0, "Fed orphanage kids (Energy cost)")
    
    def ignore_kids_action(state):
        pass

    events.append(GameEvent(
        id="charity_kids",
        title="Hungry Kids",
        description=(
            "A group of children from the local orphanage comes by your food cart. "
            "They look hungry but have no money. Since your pot has unlimited food, "
            "you can feed them all for free, but cooking and serving them will take time and energy."
        ),
        options=[
            EventOption(
                text="Feed them (Costs 20 Energy, +10 Reputation)",
                outcome_text="You spend an hour cooking and serving the children. Their smiles warm your heart. The townsfolk notice your generosity. (+10 Reputation, -20 Energy)",
                action=feed_kids_action,
                condition=lambda state: state.player.energy >= 20
            ),
            EventOption(
                text="Politely turn them away (No cost)",
                outcome_text="You tell them you cannot serve them today. They walk away disappointed. (No changes)",
                action=ignore_kids_action
            )
        ],
        trigger_condition=lambda state: state.restaurant.level == 0
    ))

    # 2. Health Inspector
    def inspector_magic_action(state):
        state.restaurant.adjust_reputation(8)
        state.finance.record_transaction("Misc", 0, "Passed inspection via explanation")

    def inspector_pay_action(state):
        state.player.adjust_cash(-50)
        state.finance.record_transaction("Misc", -50, "Paid health inspection compliance fee")

    def inspector_argue_action(state):
        state.player.adjust_cash(-40)
        state.restaurant.adjust_reputation(-10)
        state.finance.record_transaction("Misc", -40, "Health inspection fine")

    events.append(GameEvent(
        id="health_inspector",
        title="Health Inspection",
        description=(
            "A stern-looking government health inspector arrives to check the sanitation of your food prep areas. "
            "Because you use a magical pot, you don't keep ingredients, which confuses them greatly."
        ),
        options=[
            EventOption(
                text="Explain the magical pot (Requires >=40 Reputation, +8 Reputation)",
                outcome_text="You demonstrate the pot. Stunned, the inspector gives you an A+ rating for 'zero raw meat spoilage risk'! (+8 Reputation)",
                action=inspector_magic_action,
                condition=lambda state: state.restaurant.reputation >= 40.0
            ),
            EventOption(
                text="Pay standard 'compliance filing fee' (-$50)",
                outcome_text="You pay the fee to speed up the paperwork. They stamp your permit and leave. (-$50)",
                action=inspector_pay_action,
                condition=lambda state: state.player.cash >= 50.0
            ),
            EventOption(
                text="Argue and refuse to pay (-$40, -10 Reputation)",
                outcome_text="You argue with the inspector. They fine you for 'improper storage record keeping'. (-$40, -10 Reputation)",
                action=inspector_argue_action
            )
        ],
        trigger_condition=lambda state: state.restaurant.level >= 3
    ))

    # 3. The Food Critic
    def critic_serve_action(state):
        state.player.adjust_energy(-15)
        state.restaurant.adjust_reputation(15)
        state.player.adjust_cash(100.0)
        state.finance.record_transaction("Revenue", 100.0, "Food critic tip and prize")

    def critic_staff_action(state):
        active_staff = state.employees.get_active_employees()
        if not active_staff:
            return
        # Find best employee skill
        best_skill = max(e.skill for e in active_staff)
        if best_skill >= 0.7:
            state.restaurant.adjust_reputation(10)
        else:
            state.restaurant.adjust_reputation(-10)

    events.append(GameEvent(
        id="food_critic",
        title="The Food Critic",
        description=(
            "Arthur Pendelton, the most feared food critic in the county, is sitting at a corner table. "
            "He has ordered a plate. Everyone in the dining room is tense."
        ),
        options=[
            EventOption(
                text="Serve him personally (Costs 15 Energy, chance for high reputation and tips)",
                outcome_text="You put your heart into the service. He writes a glowing review: 'An inexplicable culinary miracle!' (+15 Reputation, +$100 tip)",
                action=critic_serve_action,
                condition=lambda state: state.player.energy >= 15
            ),
            EventOption(
                text="Let your staff handle it (Depends on employee skill)",
                outcome_text="Your staff serves him. If they are highly skilled, he writes a professional review. If not, he pans the service as amateurish.",
                action=critic_staff_action,
                condition=lambda state: len(state.employees.get_active_employees()) > 0
            )
        ],
        trigger_condition=lambda state: state.restaurant.level == 4
    ))

    # 4. Partner's Greenhouse Leak
    def valerie_fix_action(state):
        p = state.romance.partner
        name = p.name if p else "partner"
        state.player.adjust_cash(-150)
        state.player.adjust_energy(-30)
        state.romance.romance_level = min(100.0, state.romance.romance_level + 20)
        state.finance.record_transaction("Date", -150, f"Helped {name} fix greenhouse")

    def valerie_rep_action(state):
        p = state.romance.partner
        name = p.name if p else "partner"
        state.player.adjust_cash(-80)
        state.romance.romance_level = min(100.0, state.romance.romance_level + 8)
        state.finance.record_transaction("Date", -80, f"Paid repairman for {name}")

    def valerie_busy_action(state):
        state.romance.romance_level = max(0.0, state.romance.romance_level - 15)

    events.append(GameEvent(
        id="valerie_greenhouse",
        title="Greenhouse Leak",
        description=(
            "Your partner calls you, distressed. A pipe burst in her flower greenhouse, "
            "threatening her rare exotic orchids. She needs help repairing it and buying replacement supplies."
        ),
        options=[
            EventOption(
                text="Go help her personally (Costs $150, 30 Energy, ++Romance)",
                outcome_text="You spend hours in the damp greenhouse, sealing pipes and saving the flowers. She is deeply touched. (+20 Romance, -30 Energy, -$150)",
                action=valerie_fix_action,
                condition=lambda state: state.player.cash >= 150 and state.player.energy >= 30
            ),
            EventOption(
                text="Send a hired repairman instead (-$80, +Romance)",
                outcome_text="You pay a plumber to go help her. She appreciates the assistance. (+8 Romance, -$80)",
                action=valerie_rep_action,
                condition=lambda state: state.player.cash >= 80
            ),
            EventOption(
                text="Tell her you're too busy (--Romance)",
                outcome_text="She sighs and says she understands. You feel a cold distance grow between you. (-15 Romance)",
                action=valerie_busy_action
            )
        ],
        trigger_condition=lambda state: state.restaurant.level >= 4 and state.romance.partner is not None and state.romance.romance_level >= 25 and not state.romance.partner.is_co_owner
    ))

    # 5. Sebastian's Smear Campaign
    def smear_pr_action(state):
        state.player.adjust_cash(-100)
        state.restaurant.adjust_reputation(5)
        state.finance.record_transaction("Marketing", -100, "PR Campaign to counter Sebastian")

    def smear_tasting_action(state):
        state.player.adjust_energy(-30)
        state.restaurant.adjust_reputation(5)
        state.finance.record_transaction("Misc", 0, "Free tasting event (Energy cost)")

    def smear_ignore_action(state):
        state.restaurant.adjust_reputation(-15)

    events.append(GameEvent(
        id="competitor_smear",
        title="Sebastian's Smear Campaign",
        description=(
            "A smear campaign appears in the local Gazette! Chef Sebastian writes an editorial "
            "claiming your food is 'unnatural, processed, and potentially hazardous synthetic goop' "
            "because you never buy raw ingredients."
        ),
        options=[
            EventOption(
                text="Hire a local PR specialist to counter (-$100, +5 Reputation)",
                outcome_text="The specialist runs a 'Clean Pot, Safe Kitchen' campaign. Reputation restored! (+5 Reputation, -$100)",
                action=smear_pr_action,
                condition=lambda state: state.player.cash >= 100
            ),
            EventOption(
                text="Offer free food tastings to prove them wrong (Costs 30 Energy, +5 Reputation)",
                outcome_text="You spend all morning serving free samples. The crowd is convinced your food is safe, but you are exhausted. (+5 Reputation, -30 Energy)",
                action=smear_tasting_action,
                condition=lambda state: state.player.energy >= 30
            ),
            EventOption(
                text="Ignore the rumors (--Reputation)",
                outcome_text="The rumor spreads. People are suspicious about your lack of inventory. (-15 Reputation)",
                action=smear_ignore_action
            )
        ],
        trigger_condition=lambda state: state.competitor.is_active
    ))

    # 6. Sebastian's Poaching Attempt
    def poach_match_action(state):
        hired = state.employees.hired
        if not hired:
            return
        # Increase daily salary of highest skill employee by 25%
        highest = max(hired, key=lambda e: e.skill)
        highest.daily_salary = round(highest.daily_salary * 1.25, 2)
        state.finance.record_transaction("Wages", 0, f"Matched poach offer for {highest.name}")

    def poach_let_go_action(state):
        hired = state.employees.hired
        if not hired:
            return
        highest = max(hired, key=lambda e: e.skill)
        state.employees.fire_employee(highest.name)
        state.finance.record_transaction("Misc", 0, f"Employee {highest.name} left for Bistro Gourmet")

    def poach_loyalty_action(state):
        state.player.adjust_energy(-20)
        hired = state.employees.hired
        if not hired:
            return
        highest = max(hired, key=lambda e: e.skill)
        highest.reliability = min(1.0, highest.reliability + 0.1)

    events.append(GameEvent(
        id="competitor_poaching",
        title="The Poaching Offer",
        description=(
            "Your best employee approaches you. Chef Sebastian has offered them "
            "a 25% salary bump to leave Oakhaven and work at Bistro Gourmet."
        ),
        options=[
            EventOption(
                text="Match the salary bump (Employee wage increases by 25%)",
                outcome_text="They agree to stay, but your operating expenses just went up. (Wages increased by 25%)",
                action=poach_match_action
            ),
            EventOption(
                text="Let them go (They leave your restaurant)",
                outcome_text="They pack their knives and leave for Bistro Gourmet. You are now understaffed.",
                action=poach_let_go_action
            ),
            EventOption(
                text="Appeal to loyalty and work conditions (Costs 20 Energy, employee reliability increases)",
                outcome_text="You have a long heart-to-heart about community and ethics. They decide to stay out of loyalty. (+0.1 Reliability, -20 Energy)",
                action=poach_loyalty_action,
                condition=lambda state: state.player.energy >= 20
            )
        ],
        trigger_condition=lambda state: state.competitor.is_active and len(state.employees.hired) > 0
    ))

    # 7. Burnout Warning (Not random, triggers if energy is low)
    def rest_choice_action(state):
        state.player.adjust_energy(50)
        state.player.adjust_cash(-30)
        state.finance.record_transaction("Misc", -30, "Paid for a relaxing massage and day off")

    def push_through_action(state):
        state.player.adjust_energy(-10)

    # 8. Competitor Sabotage (Official Bribe)
    def sabotage_fee_action(state):
        state.player.adjust_cash(-150)
        state.finance.record_transaction("Misc", -150, "Paid official bribe compliance fee")
        
    def sabotage_inspection_action(state):
        state.restaurant.adjust_reputation(10)
        state.competitor.counter_marketing_active = True

    def sabotage_refuse_action(state):
        state.restaurant.adjust_reputation(-10)
        state.player.adjust_cash(-100)
        state.finance.record_transaction("Misc", -100, "Official licensing fine")

    events.append(GameEvent(
        id="competitor_sabotage",
        title="Official Sabotage",
        description=(
            "An auditor from the town council arrives. They claim Chef Sebastian filed a formal complaint "
            "alleging your operations run without proper local safety certificates. The official hints a "
            "payment could speed up compliance."
        ),
        options=[
            EventOption(
                text="Pay the official a 'compliance fee' (-$150)",
                outcome_text="You pay the fee. They sign off on your licenses and leave. (-$150)",
                action=sabotage_fee_action,
                condition=lambda state: state.player.cash >= 150
            ),
            EventOption(
                text="Demand a public sanitation review (Requires >=65 Reputation, +10 Reputation)",
                outcome_text="The public review is a massive success! Your pot is spotless, and Sebastian's complaints look like petty jealousy. (+10 Reputation, competitor impact minimized today)",
                action=sabotage_inspection_action,
                condition=lambda state: state.restaurant.reputation >= 65
            ),
            EventOption(
                text="Argue and refuse to pay (-$100, -10 Reputation)",
                outcome_text="You refuse to pay. The official fines you for 'delayed certification access' and files a bad report. (-$100, -10 Reputation)",
                action=sabotage_refuse_action,
                condition=lambda state: state.player.cash >= 100
            )
        ],
        trigger_condition=lambda state: state.competitor.is_active
    ))

    # 9. Autumn Festival Sponsorship
    def festival_gold_action(state):
        state.player.adjust_cash(-200)
        state.restaurant.adjust_reputation(15)
        state.finance.record_transaction("Marketing", -200, "Sponsored Autumn Festival")
        
    def festival_volunteer_action(state):
        state.player.adjust_energy(-30)
        state.restaurant.adjust_reputation(8)
        state.finance.record_transaction("Misc", 0, "Fed volunteers (Energy cost)")

    def festival_decline_action(state):
        pass

    events.append(GameEvent(
        id="autumn_festival",
        title="Festival Sponsorship",
        description=(
            "The Oakhaven Autumn Festival committee approaches you. They want to know if you'd like to "
            "sponsor this year's harvest event to display your brand name in Oakhaven square."
        ),
        options=[
            EventOption(
                text="Become a Gold Sponsor (-$200, +15 Reputation)",
                outcome_text="You sponsor the event! A large banner is raised in Oakhaven square. (+15 Reputation, -$200)",
                action=festival_gold_action,
                condition=lambda state: state.player.cash >= 200
            ),
            EventOption(
                text="Volunteer to feed the setup crew (Costs 30 Energy, +8 Reputation)",
                outcome_text="You work all morning cooking and feeding the crew. The organizers thank you warmly. (+8 Reputation, -30 Energy)",
                action=festival_volunteer_action,
                condition=lambda state: state.player.energy >= 30
            ),
            EventOption(
                text="Politely decline",
                outcome_text="You decline sponsorship. The committee moves on to other businesses. (No change)",
                action=festival_decline_action
            )
        ],
        trigger_condition=lambda state: state.restaurant.level >= 3
    ))

    # 10. Relationship Anniversary
    def anniversary_gift_action(state):
        state.player.adjust_cash(-100)
        state.romance.romance_level = min(100.0, state.romance.romance_level + 20)
        state.finance.record_transaction("Date", -100, "Anniversary Gift")

    def anniversary_poem_action(state):
        state.player.adjust_energy(-30)
        state.romance.romance_level = min(100.0, state.romance.romance_level + 12)
        state.finance.record_transaction("Date", 0, "Heartfelt poem (Energy cost)")

    def anniversary_forget_action(state):
        state.romance.romance_level = max(0.0, state.romance.romance_level - 20)

    events.append(GameEvent(
        id="anniversary",
        title="Relationship Anniversary",
        description=(
            "Today is your relationship anniversary! Your partner expects a meaningful gesture to "
            "celebrate your time together."
        ),
        options=[
            EventOption(
                text="Buy a luxury gift basket & dinner (-$100, +20 Romance)",
                outcome_text="You spend the evening dining. She is thrilled and touched by the gift. (+20 Romance, -$100)",
                action=anniversary_gift_action,
                condition=lambda state: state.player.cash >= 100
            ),
            EventOption(
                text="Write her a heartfelt love poem (Costs 30 Energy, +12 Romance)",
                outcome_text="You recite the poem you spent all night writing. She finds it incredibly sweet and romantic. (+12 Romance, -30 Energy)",
                action=anniversary_poem_action,
                condition=lambda state: state.player.energy >= 30
            ),
            EventOption(
                text="Forget it and work late (--Romance)",
                outcome_text="You forgot! She spends the evening quiet and hurt. (-20 Romance)",
                action=anniversary_forget_action
            )
        ],
        trigger_condition=lambda state: state.romance.partner is not None and state.romance.partner.is_partner
    ))

    # 11. The Scholar's Inquiry
    def scholar_accept_action(state):
        state.player.adjust_cash(400)
        state.player.adjust_energy(-30)
        state.restaurant.adjust_reputation(-8)
        state.finance.record_transaction("Misc", 400, "Scholar research grant")

    def scholar_refuse_action(state):
        pass

    events.append(GameEvent(
        id="scholar_pot_inquiry",
        title="The Scholar's Inquiry",
        description=(
            "A traveling scholar from the Capital Academy visits your shop. They offer you $400 "
            "to analyze your magical pot for a research journal on anomalous physics."
        ),
        options=[
            EventOption(
                text="Allow the study (Costs 30 Energy, +$400, -8 Reputation)",
                outcome_text="They run measurements on the pot. Customers are suspicious of the scientific gear, but the scholar pays you handsomely. (+$400, -8 Reputation, -30 Energy)",
                action=scholar_accept_action,
                condition=lambda state: state.player.energy >= 30
            ),
            EventOption(
                text="Refuse the inquiry",
                outcome_text="You decline. The scholar leaves disappointed. The mystery of your magical pot remains secure. (No change)",
                action=scholar_refuse_action
            )
        ],
        trigger_condition=lambda state: state.restaurant.level >= 2
    ))

    return events
