# Infinite Pot

## Vision
Infinite Pot is an original simulation game prototype where the player begins with nothing but one magical pot. This pot can cook unlimited food without ingredients. Food is never scarce, and food is never the challenge. Instead, the challenge lies in transforming this impossible advantage into a successful business while building a meaningful personal life.

## Core Fantasy
The player starts with absolutely nothing except one magical pot. Since food is unlimited and free to cook, the player doesn't need to manage ingredient supply. They must leverage this magical advantage to build a restaurant empire, survive the challenges of growth, and ask themselves: *"What am I actually working for?"*

## Core Theme
> **Build a business to build a life.**

Money is not the final objective; it buys opportunity. Opportunity, in turn, creates responsibility. Success does not remove challenge; it changes the nature of the challenge:
* **Bigger restaurant** → Higher operating costs
* **More customers** → More complexity
* **Better reputation** → More expectations
* **Finding love** → Shared responsibilities
* **Buying a house** → Maintenance and living expenses
* **Competition** → Protecting everything you've built

## Prototype Scope (V1)
The V1 prototype is a text-based console application written in Python 3.12+. It focuses entirely on mechanics, game systems, balancing, and progression.
* **Single Town**: The entire game takes place in one town.
* **Linear Progression**:
  1. **Level 1 (Roadside Cart)**: Survive, earn enough money to upgrade, no social life.
  2. **Level 2 (Edge-of-Town Shop)**: Upgrade to a shop, higher expenses, larger customer base, still business-focused.
  3. **Level 3 (Town Restaurant)**: The major milestone. Unlock restaurant customization, hiring employees, meeting people/romance, buying a house, and house customization.
  4. **Relationships & Romance**: Develop a relationship with one romantic partner, who can eventually be asked to work in the restaurant.
  5. **House**: Purchase and customize a house to build a personal life.
  6. **Competitor**: Once the player has a successful restaurant, a romantic partner, and a house, one competitor enters the town to challenge their business and life.
  7. **Survive & Maintain**: Balance the business demands, personal relationships, and competitor threat.

## Architecture & Folder Structure
The codebase is designed to be highly modular, clean, and separated by concerns:

```
infinite-pot/
│
├── main.py                     # Entry point of the application
├── engine/                     # Game loop, state management, and time system
│   ├── game_loop.py            # Main game loop, text interface orchestration
│   ├── state.py                # Global game state container
│   └── time_system.py          # Day/Week/Time progression and scheduling
│
├── business/                   # Restaurant mechanics
│   ├── restaurant.py           # Restaurant state, level, reputation, customization
│   ├── employees.py            # Hiring, wages, skills, reliability
│   └── competitor.py           # Competitor behavior, marketing warfare
│
├── player/                     # Player and personal life progression
│   ├── stats.py                # Player attributes (energy, cash)
│   ├── house.py                # House purchases, upgrades, maintenance
│   └── romance.py              # Romantic relationship progression (emotional depth)
│
├── economy/                    # Financial and balance systems
│   ├── finance.py              # Running costs, daily balance sheet, loans
│   ├── loan.py                 # Bank loans, interest rate, repayment
│   └── transactions.py         # Financial ledger
│
├── world/                      # Environmental state
│   └── town.py                 # Town state, locations, active events
│
├── events/                     # Event system
│   ├── event_system.py         # Event manager, trigger evaluation
│   └── event_definitions.py    # List of random, economic, or narrative events
│
├── data/                       # Balances, configs, data files
│   └── balance_config.json     # JSON-based balancing parameters
│
└── tests/                      # Automated test suite
    └── test_core.py            # Unit tests for core mechanics
```

## How to Run
### Prerequisites
* Python 3.12+ installed.

### Setup & Execution
1. Clone the repository and navigate to the directory:
   ```bash
   git clone <repository_url>
   cd infinite-pot
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the game:
   ```bash
   python main.py
   ```

### Running Tests
To run the automated tests, execute:
```bash
pytest
```
