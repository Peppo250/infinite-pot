from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QScrollArea, QListWidget, QListWidgetItem, QProgressBar
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QPainter
from ui.theme import ThemeManager
from ui.audio import UIAudio
from ui.dialogs.custom_dialogs import ConfirmDialog, ChoicesDialog

class TavernMenuScreen(QWidget):
    go_back = Signal()
    state_changed = Signal()  # Emitted when candidates hired or relationships change
    
    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.state = state
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(20)
        
        card_style = "QFrame { background-color: rgba(245, 235, 224, 0.92); border: 3px solid #5B3923; border-radius: 8px; }"
        
        # LEFT COLUMN: Socializing & Girls
        self.girls_card = QFrame(self)
        self.girls_card.setStyleSheet(card_style)
        self.girls_layout = QVBoxLayout(self.girls_card)
        self.girls_layout.setSpacing(12)
        
        girls_title = QLabel("🌹 Socializing & Dating", self)
        girls_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #5B3923; border: none; background: transparent;")
        self.girls_layout.addWidget(girls_title)
        
        self.girls_scroll = QScrollArea(self)
        self.girls_scroll.setWidgetResizable(True)
        self.girls_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; } QWidget { background: transparent; }")
        self.girls_content = QWidget()
        self.girls_scroll_layout = QVBoxLayout(self.girls_content)
        self.girls_scroll_layout.setSpacing(10)
        self.girls_scroll_layout.setAlignment(Qt.AlignTop)
        self.girls_scroll.setWidget(self.girls_content)
        self.girls_layout.addWidget(self.girls_scroll)
        
        main_layout.addWidget(self.girls_card, stretch=1)
        
        # RIGHT COLUMN: Job Candidates
        self.candidates_card = QFrame(self)
        self.candidates_card.setStyleSheet(card_style)
        self.cand_layout = QVBoxLayout(self.candidates_card)
        self.cand_layout.setSpacing(12)
        
        cand_title = QLabel("👥 Job Applicants", self)
        cand_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #5B3923; border: none; background: transparent;")
        self.cand_layout.addWidget(cand_title)
        
        self.cand_scroll = QScrollArea(self)
        self.cand_scroll.setWidgetResizable(True)
        self.cand_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; } QWidget { background: transparent; }")
        self.cand_content = QWidget()
        self.cand_scroll_layout = QVBoxLayout(self.cand_content)
        self.cand_scroll_layout.setSpacing(10)
        self.cand_scroll_layout.setAlignment(Qt.AlignTop)
        self.cand_scroll.setWidget(self.cand_content)
        self.cand_layout.addWidget(self.cand_scroll)
        
        main_layout.addWidget(self.candidates_card, stretch=1)
        
        self.update_ui()

    def paintEvent(self, event):
        painter = QPainter(self)
        pixmap = QPixmap("assets/images/tavern_bg.jpg")
        painter.drawPixmap(self.rect(), pixmap)

    def interact_girl(self, girl):
        UIAudio.play_click()
        rom = self.state.romance
        p = self.state.player
        h = self.state.house
        
        # We need to temporarily switch to romance music for the interaction
        UIAudio.play_music("romance")
        
        while True:
            # Build list of options dynamically
            opts = [
                f"Talk to her (Costs 10 Energy) [Current: {p.energy:.1f}]",
                f"Buy her a drink (Costs $25.00, 10 Energy) [Current: ${p.cash:.2f}]"
            ]
            
            if not girl.is_partner and not girl.is_co_owner:
                opts.append("Propose Relationship / Ask to be Partner (Requires >=40 Romance)")
            elif girl.is_partner and not girl.is_co_owner:
                opts.append("Propose Marriage & Co-ownership (Requires >=75 Romance and House)")
                opts.append("Break Up")
            elif girl.is_co_owner:
                opts.append("Speak about your shared life")
                
            dlg = ChoicesDialog(f"Interacting with {girl.name}", f"'{girl.description}'\n\nWhat would you like to do?", opts, self)
            
            if not dlg.exec() or dlg.chosen_index == -1:
                # Return to tavern music when exit dialog
                UIAudio.play_music("bar")
                break
                
            choice = dlg.chosen_index
            if choice == 0:  # Talk (Interactive Dialogue Tree)
                if p.energy < 10:
                    ConfirmDialog("Too Exhausted", "You don't have enough energy (10 required) to hold a conversation.", self).exec()
                else:
                    # Dialogue Tree definition based on romance and archetype
                    talk_trees = {
                        "Artist": {
                            "low": {
                                "prompt": "I'm trying to capture the morning mist over the valley, but the colors feel too cold. What should I add?",
                                "options": [
                                    ("Add a touch of warm saffron yellow; even cold mist needs a heart of light.", 8.0, "She smiles widely, eyes lighting up. 'Exactly! Saffron yellow is the perfect counterpoint!'"),
                                    ("Maybe just paint it later when the sun is fully up.", 3.0, "She shrugs. 'I suppose, but then the mystery of the mist is gone.'"),
                                    ("Color theory doesn't matter, just paint whatever.", -5.0, "She frowns and turns away. 'Art is all about intent. If you don't care, why talk about it?'")
                                ]
                            },
                            "med": {
                                "prompt": "Sometimes I worry my art is just an escape from reality. Am I wasting my life on canvas?",
                                "options": [
                                    ("Art doesn't escape reality; it reveals the beauty that reality hides. Your canvas matters.", 8.0, "She looks touched, her eyes soft. 'Thank you. I needed to hear that today.'"),
                                    ("We all need a hobby. If it makes you happy, it's fine.", 3.0, "She sighs quietly. 'It's more than a hobby to me, but I appreciate the sentiment.'"),
                                    ("Well, you could be doing something more practical, like running a business.", -5.0, "She crosses her arms. 'Practicality is the death of passion. I thought you of all people would understand.'")
                                ]
                            },
                            "high": {
                                "prompt": "When I look at you, I see a spectrum of colors I've never been able to mix on my palette. Do you feel it too?",
                                "options": [
                                    ("I feel like our colors are mixing into a beautiful new masterpiece every day.", 10.0, "She blushes deeply and smiles, stepping closer. 'That's the most poetic thing anyone has ever said to me.'"),
                                    ("That's nice, I'm glad I can be your muse.", 4.0, "She giggles. 'You certainly are. I'll make sure to paint you sometime.'"),
                                    ("You should probably keep your painting and your personal life separate.", -6.0, "She recoils slightly, hurt in her eyes. 'Oh. I... I see. My apologies for overstepping.'")
                                ]
                            }
                        },
                        "Scholar": {
                            "low": {
                                "prompt": "I've been translating the original charter of Oakhaven. It mentions a secret basement under the town square. Fascinating, isn't it?",
                                "options": [
                                    ("Fascinating indeed! Do you think it was used for storing emergency grain or smuggling?", 8.0, "She looks thrilled. 'Yes! And the layout suggests it connects to the river trade route too!'"),
                                    ("Oh, Oakhaven is quite old. I'm sure there are many old cellars.", 3.0, "She nods. 'Yes, but cellars of this size usually imply institutional usage.'"),
                                    ("Sounds like a waste of time. Old papers don't make money.", -5.0, "She sighs. 'Not everything is about revenue. The value of knowledge is intrinsic.'")
                                ]
                            },
                            "med": {
                                "prompt": "The logs show that the local soil has specific mineral deposits that enhance wild herb growth. This explains your pot's efficiency, but the math is still off...",
                                "options": [
                                    ("Perhaps the pot's magic interacts with the soil minerals on a quantum scale. Let's study it together.", 8.0, "Her eyes shine. 'Quantum magic! That's a highly unconventional hypothesis, but it warrants a full study!'"),
                                    ("It's just a magical pot. No need to analyze it to death.", 3.0, "She chuckles. 'Well, curiosity is hard to shut off once it gets going.'"),
                                    ("Stop trying to dissect my business secrets. It's confidential.", -5.0, "She looks taken back. 'I was just interested in the science. I won't ask again.'")
                                ]
                            },
                            "high": {
                                "prompt": "I've spent my life studying the past, but lately, I find myself thinking more about the future. Specifically, a future... with you.",
                                "options": [
                                    ("Let's write our own chapter in history together. The future is ours to research.", 10.0, "She holds your hand, smiling warmly. 'A collaborative research project on life. I like the sound of that.'"),
                                    ("The future is hard to predict, but I'm glad you're in it.", 4.0, "She smiles. 'Statistically, having you in my projections improves my outlook.'"),
                                    ("I don't think we should jump to conclusions. Let's keep it research-focused.", -6.0, "She stiffens, pulling her hand back. 'I see. I made a logical error in assuming reciprocity.'")
                                ]
                            }
                        },
                        "Entrepreneur": {
                            "low": {
                                "prompt": "Chef Sebastian's supply chain is highly centralized. If we disrupt his spice contracts, we can corner the lunch market.",
                                "options": [
                                    ("Brilliant. We can offer a long-term contract to the local spice cooperative and lock him out.", 8.0, "She smirks, highly impressed. 'Exactly! Hit him where it hurts: his margins. I like how you think.'"),
                                    ("Disrupting contracts sounds risky. Maybe just lower our prices.", 3.0, "She shakes her head. 'Price wars are a race to the bottom. We need structural advantage.'"),
                                    ("We shouldn't play dirty. Let's just focus on cooking good food.", -5.0, "She rolls her eyes. 'Good food is only 30% of business. The rest is positioning. Don't be naive.'")
                                ]
                            },
                            "med": {
                                "prompt": "My manager wants me to relocate to the capital for a promotion. The return on investment is high, but... I don't want to leave Oakhaven.",
                                "options": [
                                    ("Stay here. We can merge our operations, build our own empire, and get a better ROI together.", 8.0, "She looks stunned, then a proud smile appears. 'Merge operations? That is... a highly competitive proposal. Deal.'"),
                                    ("A promotion is good. You should do whatever makes more money.", 3.0, "She nods slowly. 'From a purely fiscal standpoint, yes. But some quality-of-life variables are hard to price.'"),
                                    ("You should go. The capital has way better businesses than this small town.", -5.0, "She looks disappointed. 'I see. You view my presence here as low-value. Good to know.'")
                                ]
                            },
                            "high": {
                                "prompt": "I've run the numbers. A partnership between us has an estimated synergy rating of 98%. I'm ready to merge our assets.",
                                "options": [
                                    ("Merger approved. I'm fully invested in you, both in business and in life.", 10.0, "She laughs, her eyes warm. 'Strategic alignment achieved. I am very happy to accept this partnership.'"),
                                    ("Let's start with a trial contract and see how the partnership scales.", 4.0, "She grins. 'A phased rollout. Sensible, though I'm confident in the long-term projection.'"),
                                    ("I'm not looking for a corporate takeover of my personal life.", -6.0, "She looks hurt and icy. 'It was a metaphor for commitment. But if you see it as a hostile takeover, the deal is off.'")
                                ]
                            }
                        }
                    }

                    # Determine romance tier
                    tier = "low"
                    if girl.romance_level >= 75.0:
                        tier = "high"
                    elif girl.romance_level >= 40.0:
                        tier = "med"

                    tree = talk_trees[girl.archetype][tier]
                    opt_texts = [o[0] for o in tree["options"]]

                    # Show conversation option selector dialog
                    opt_dlg = ChoicesDialog(
                        f"Dialogue with {girl.name}",
                        f"{girl.name} asks:\n\n\"{tree['prompt']}\"\n\nChoose your response:",
                        opt_texts,
                        self
                    )
                    if opt_dlg.exec() and opt_dlg.chosen_index != -1:
                        chosen_idx = opt_dlg.chosen_index
                        selected_option = tree["options"][chosen_idx]
                        romance_impact = selected_option[1]
                        reaction = selected_option[2]

                        # Adjust player statistics
                        p.adjust_energy(-10)
                        girl.romance_level = min(100.0, max(0.0, girl.romance_level + romance_impact))
                        UIAudio.play_dialogue()

                        # Present reaction details
                        impact_str = f"Romance +{romance_impact:.1f}" if romance_impact >= 0 else f"Romance {romance_impact:.1f}"
                        ConfirmDialog(
                            f"Talking to {girl.name}",
                            f"{girl.name}'s Reaction:\n\n\"{reaction}\"\n\n({impact_str})",
                            self
                        ).exec()

                        # Apply jealousy factor
                        jealousy_notices = self.state.romance.apply_jealousy(girl.name, self.state.day_name)
                        for notice in jealousy_notices:
                            ConfirmDialog("Jealousy Alert", notice, self).exec()

                        self.update_ui()
                        self.state_changed.emit()
            elif choice == 1:  # Buy Drink
                if p.cash < 25.0:
                    ConfirmDialog("No Cash", "You need $25.00 to buy a drink.", self).exec()
                elif p.energy < 10:
                    ConfirmDialog("Too Exhausted", "You don't have enough energy (10 required) to socialize.", self).exec()
                else:
                    p.adjust_cash(-25.0)
                    p.adjust_energy(-10)
                    self.state.finance.record_transaction("Date", 25.0, f"Bought drink for {girl.name}")
                    dialogue, gain = girl.interact_drink(25.0)
                    UIAudio.play_coin()
                    UIAudio.play_dialogue()
                    ConfirmDialog(f"Bought {girl.name} a Drink", f"You buy a warm cider for {girl.name}.\n\nShe smiles:\n\"{dialogue}\"\n\n(Romance increased by {gain:.1f})", self).exec()
                    self.update_ui()
                    self.state_changed.emit()
            elif choice == 2:  # Relationship or Marriage Propose or shared life
                if not girl.is_partner and not girl.is_co_owner:
                    if p.energy < 10:
                        ConfirmDialog("Too Exhausted", "You need 10 energy to ask her out.", self).exec()
                    else:
                        p.adjust_energy(-10)
                        success, msg = rom.propose_relationship(girl.name)
                        if success:
                            UIAudio.play_success()
                            ConfirmDialog("Success!", msg, self).exec()
                        else:
                            ConfirmDialog("Relationship Proposal", msg, self).exec()
                        self.update_ui()
                        self.state_changed.emit()
                elif girl.is_partner and not girl.is_co_owner:
                    if p.energy < 10:
                        ConfirmDialog("Too Exhausted", "You need 10 energy to propose.", self).exec()
                    else:
                        p.adjust_energy(-10)
                        success, msg = rom.ask_to_co_own(h.purchased)
                        if success:
                            UIAudio.play_success()
                            ConfirmDialog("Congratulations!", msg, self).exec()
                        else:
                            ConfirmDialog("Marriage Proposal", msg, self).exec()
                        self.update_ui()
                        self.state_changed.emit()
                elif girl.is_co_owner:
                    UIAudio.play_dialogue()
                    ConfirmDialog("Married Life", f"{girl.name} kisses your cheek. \"Let's keep building our life together, darling. I'm so happy to help out in the restaurant.\"", self).exec()
            elif choice == 3:  # Break Up
                if girl.is_partner and not girl.is_co_owner:
                    confirm_dlg = ConfirmDialog("Break Up", f"Are you sure you want to end your relationship with {girl.name}?", self)
                    if confirm_dlg.exec():
                        success, msg = rom.break_up()
                        if success:
                            ConfirmDialog("Single", msg, self).exec()
                            self.update_ui()
                            self.state_changed.emit()
                            UIAudio.play_music("bar")
                            break

    def hire_candidate(self, candidate):
        r = self.state.restaurant
        es = self.state.employees
        p = self.state.player
        
        dlg = ConfirmDialog(
            "Hire Employee",
            f"Do you want to hire {candidate.name}?\n\n"
            f"Daily Wage: ${candidate.daily_salary:.2f}/day\n"
            f"Skill: {candidate.skill:.2f} | Reliability: {candidate.reliability:.2f}\n"
            f"Experience: {candidate.experience} years",
            self
        )
        if dlg.exec():
            success, msg = es.hire_employee(candidate.name, r.current_config.max_employees)
            if success:
                UIAudio.play_success()
                ConfirmDialog("Hired!", msg, self).exec()
                self.update_ui()
                self.state_changed.emit()
            else:
                ConfirmDialog("Recruitment Failed", msg, self).exec()

    def update_ui(self):
        # 1. Update Tavern Socializing Column
        # Clear layout
        while self.girls_scroll_layout.count():
            item = self.girls_scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        girls = self.state.romance.get_characters_available(self.state.day_name)
        if not girls:
            no_girls_lbl = QLabel("The Tavern is quiet tonight.\nNobody you know is here.", self)
            no_girls_lbl.setAlignment(Qt.AlignCenter)
            no_girls_lbl.setStyleSheet("font-style: italic; color: #666666; padding: 20px;")
            self.girls_scroll_layout.addWidget(no_girls_lbl)
        else:
            for g in girls:
                g_frame = QFrame(self.girls_content)
                g_frame.setFrameShape(QFrame.StyledPanel)
                g_frame.setObjectName("card-frame")
                
                g_layout = QHBoxLayout(g_frame)
                g_layout.setContentsMargins(6, 6, 6, 6)
                g_layout.setSpacing(10)
                
                g_lbl_layout = QVBoxLayout()
                g_lbl_layout.setContentsMargins(0, 0, 0, 0)
                g_lbl_layout.setSpacing(2)
                
                rel_str = ""
                if self.state.romance.active_partner_name == g.name:
                    rel_str = " ❤️"
                    if g.is_co_owner:
                        rel_str = " 💍 Married"
                
                name_lbl = QLabel(f"<b>{g.name}</b> ({g.archetype}){rel_str}", self)
                desc_lbl = QLabel(f"'{g.description}'", self)
                desc_lbl.setStyleSheet("font-size: 14px; color: #555555; font-style: italic;")
                
                rom_bar = QProgressBar(self)
                rom_bar.setRange(0, 100)
                rom_bar.setValue(int(g.romance_level))
                rom_bar.setFormat("Romance: %v/100")
                rom_bar.setStyleSheet("height: 14px; font-size: 14px;")
                
                g_lbl_layout.addWidget(name_lbl)
                g_lbl_layout.addWidget(desc_lbl)
                g_lbl_layout.addWidget(rom_bar)
                
                g_layout.addLayout(g_lbl_layout)
                
                interact_btn = QPushButton("Interact", self)
                interact_btn.setObjectName("primary-action-btn")
                interact_btn.clicked.connect(lambda checked=False, target_girl=g: self.interact_girl(target_girl))
                g_layout.addWidget(interact_btn, alignment=Qt.AlignRight)
                
                self.girls_scroll_layout.addWidget(g_frame)
                
        # 2. Update Candidates Column
        # Clear layout
        while self.cand_scroll_layout.count():
            item = self.cand_scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        candidates = self.state.employees.candidates
        if not candidates:
            no_cand_lbl = QLabel("No job applicants hanging out tonight.", self)
            no_cand_lbl.setAlignment(Qt.AlignCenter)
            no_cand_lbl.setStyleSheet("font-style: italic; color: #666666; padding: 20px;")
            self.cand_scroll_layout.addWidget(no_cand_lbl)
        else:
            for c in candidates:
                c_frame = QFrame(self.cand_content)
                c_frame.setFrameShape(QFrame.StyledPanel)
                c_frame.setObjectName("card-frame")
                
                c_layout = QHBoxLayout(c_frame)
                c_layout.setContentsMargins(6, 6, 6, 6)
                c_layout.setSpacing(10)
                
                c_lbl_layout = QVBoxLayout()
                c_lbl_layout.setContentsMargins(0, 0, 0, 0)
                c_lbl_layout.setSpacing(2)
                
                name_lbl = QLabel(f"<b>{c.name}</b>", self)
                stats_lbl = QLabel(
                    f"Skill: {c.skill:.2f} | Reliability: {c.reliability:.2f}<br/>"
                    f"Wage: <b>${c.daily_salary:.2f}/day</b> | Exp: {c.experience} yrs",
                    self
                )
                stats_lbl.setStyleSheet("font-size: 14px; color: #555555;")
                
                c_lbl_layout.addWidget(name_lbl)
                c_lbl_layout.addWidget(stats_lbl)
                
                c_layout.addLayout(c_lbl_layout)
                
                hire_btn = QPushButton("Hire", self)
                hire_btn.setObjectName("primary-action-btn")
                max_emp = self.state.restaurant.current_config.max_employees
                hire_btn.setEnabled(len(self.state.employees.hired) < max_emp)
                hire_btn.clicked.connect(lambda checked=False, target_cand=c: self.hire_candidate(target_cand))
                c_layout.addWidget(hire_btn, alignment=Qt.AlignRight)
                
                self.cand_scroll_layout.addWidget(c_frame)
