import os
import sys
import time
import random
from typing import Any

from colorama import init, Fore, Back, Style
from engine.state import GameState

# Initialize colorama
init(autoreset=True)

class GameLoop:
    def __init__(self, state: GameState) -> None:
        self.state = state
        self.game_over = False
        self.victory = False
        self.days_survived_competitor = 0
        
    def clear_screen(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")

    def print_header(self, text: str, color: str = Fore.CYAN) -> None:
        border = "=" * 50
        print(color + border)
        print(color + f" {text.upper().center(48)} ")
        print(color + border)

    def print_status(self) -> None:
        s = self.state
        p = s.player
        r = s.restaurant
        c = s.competitor
        rom = s.romance
        h = s.house

        # Time and Economy
        time_str = f"Day {s.day} ({s.day_name}), Week {s.week}"
        econ_str = f"Economy: {s.town.economic_climate}"
        print(Fore.YELLOW + f"📅 {time_str:<25} 📈 {econ_str}")
        print(Fore.WHITE + "-" * 50)

        # Player stats
        cash_color = Fore.GREEN if p.cash >= 0 else Fore.RED
        print(f"💰 Cash: {cash_color}${p.cash:.2f}{Fore.RESET:<18} "
              f"⚡ Energy: {Fore.BLUE}{p.energy:.1f}/{p.max_energy}{Fore.RESET}")
        
        if s.loan.balance > 0:
            print(f"🏦 Bank Loan Debt: {Fore.RED}${s.loan.balance:.2f}{Fore.RESET:<15} "
                  f"Max Borrow: {Fore.YELLOW}${s.loan.get_max_borrow_limit(r.level):.2f}")
        print(Fore.WHITE + "-" * 50)

        # Business stats
        print(f"🏪 Establishment: {Fore.CYAN}{r.current_config.name} (Level {r.level}){Fore.RESET}")
        print(f"⭐ Reputation: {Fore.YELLOW}{r.reputation:.1f}/100.0{Fore.RESET:<16} "
              f"🍽️ Menu Price: {Fore.GREEN}${r.menu_price:.2f}")
        
        # Staff list
        staff_names = [e.name + ("" if e.is_active else " (Sick)") for e in s.employees.hired]
        staff_str = ", ".join(staff_names) if staff_names else "None"
        print(f"👥 Employees: {Fore.WHITE}{staff_str}{Fore.RESET} (Max: {r.current_config.max_employees})")
        
        # Customizations
        if r.upgrades:
            print(f"🛠️ Upgrades: {Fore.WHITE}{', '.join(r.upgrades)}{Fore.RESET}")

        # Personal Life (Unlocked at Level 4)
        if r.level >= 4:
            print(Fore.WHITE + "-" * 50)
            house_str = f"House: Owned (${h.daily_maintenance}/day)" if h.purchased else "House: Renting (No assets)"
            print(f"🏠 {house_str:<27} 🌹 Partner: {Fore.MAGENTA}{rom.partner_name} ({rom.stage_name}){Fore.RESET}")
            if rom.romance_level > 0:
                print(f"   Romance Progress: {Fore.MAGENTA}{rom.romance_level:.1f}/100.0{Fore.RESET}")
            if h.purchased and h.upgrades:
                print(f"   House Customizations: {Fore.WHITE}{', '.join(h.upgrades)}{Fore.RESET}")

        # Competitor Alert
        if c.is_active:
            print(Fore.WHITE + "-" * 50)
            marketing_status = f"{Fore.GREEN}Countered" if c.counter_marketing_active else f"{Fore.RED}Active"
            print(f"🚨 Competitor: {Fore.RED}{c.name}{Fore.RESET} ({c.owner}) | Marketing: {marketing_status}")
            print(f"   Survival Days: {Fore.YELLOW}{self.days_survived_competitor}/10 days{Fore.RESET} needed to secure your life.")

        print(Fore.WHITE + "=" * 50)
        self.print_objectives()
        print(Fore.WHITE + "=" * 50)

    def print_objectives(self) -> None:
        s = self.state
        r = s.restaurant
        rom = s.romance
        h = s.house
        c = s.competitor

        print(Fore.WHITE + "🎯 Current Objectives:")
        
        if r.level == 0:
            print(f"  [ ] Save {Fore.GREEN}$100.00{Fore.RESET} to buy a Second-Hand Roadside Cart (Current: ${s.player.cash:.2f})")
            print("  [ ] Serve hungry passersby directly on the street.")
        elif r.level == 1:
            print(f"  [ ] Save {Fore.GREEN}$250.00{Fore.RESET} to upgrade to your Own Roadside Cart (Current: ${s.player.cash:.2f})")
            print("  [ ] Get your business off the ground with a basic set of wheels.")
        elif r.level == 2:
            print(f"  [ ] Save {Fore.GREEN}$800.00{Fore.RESET} to upgrade to an Edge-of-Town Shop (Current: ${s.player.cash:.2f})")
            print("  [ ] Build up capital with your first proper cart.")
        elif r.level == 3:
            print(f"  [ ] Save {Fore.GREEN}$2000.00{Fore.RESET} to upgrade to a Town Restaurant (Current: ${s.player.cash:.2f})")
            print("  [ ] Optionally hire an employee to help with the rising shop workload.")
        elif r.level == 4 and not h.purchased:
            print(f"  [ ] Save {Fore.GREEN}$3000.00{Fore.RESET} to purchase your first House (Current: ${s.player.cash:.2f})")
            print(f"  [ ] Visit and go on dates with Valerie at the park (Raise Romance)")
        elif r.level == 4 and h.purchased and not rom.is_co_owner:
            print(f"  [ ] Build relationship with Valerie to 'Partner' stage (Romance >= 75)")
            print(f"  [ ] Ask Valerie to move in and co-own the business (Requires Romance >= 75)")
        elif c.is_active:
            print(f"  [ ] Protect your business and life from Chef Sebastian's aggressive marketing!")
            print(f"  [ ] Keep Reputation >= 60.0 and Romance >= 80.0")
            print(f"  [ ] Survive for {Fore.YELLOW}{10 - self.days_survived_competitor}{Fore.RESET} more days under competitor threat.")

    def run(self) -> None:
        self.clear_screen()
        print(Fore.CYAN + "=== WELCOME TO THE INFINITE POT PROTOTYPE ===")
        print("A simulation about cooking magic food and figuring out what you are working for.\n")
        input("Press Enter to start your journey...")

        while not self.game_over:
            # 1. Start of Day Screen
            self.clear_screen()
            self.print_status()

            # 2. Check for bankruptcies or burnout before actions
            if self.state.player.cash < 0:
                print(Fore.RED + "🚨 CRITICAL: You have run out of money and your accounts are frozen!")
                borrow_limit = self.state.loan.get_available_borrow_amount(self.state.restaurant.level)
                if borrow_limit > 0 and borrow_limit >= abs(self.state.player.cash):
                    print(Fore.YELLOW + f"You can borrow up to ${borrow_limit:.2f} from the bank to cover your deficit.")
                    choice = input("Would you like to take a loan to cover your debts? (y/n): ").lower()
                    if choice == "y":
                        borrow_amt = abs(self.state.player.cash) + 20.0  # borrow enough + $20 cushion
                        borrow_amt = min(borrow_amt, borrow_limit)
                        success, msg = self.state.loan.borrow(borrow_amt, self.state.restaurant.level)
                        if success:
                            self.state.player.adjust_cash(borrow_amt)
                            print(Fore.GREEN + f"Bank approved loan! Account is back in the black. {msg}")
                            input("\nPress Enter to continue...")
                            continue
                
                print(Back.RED + Fore.WHITE + "\n GAME OVER - BANKRUPTCY ")
                print("Your business assets have been seized, and your dream of building a life has crumbled.")
                print("Perhaps you pushed too fast, or priced too high, or neglected your overheads.")
                self.game_over = True
                break

            # 3. Main Menu choices
            print("What would you like to do this morning?")
            print("1. Manage Business (Pricing, Upgrades, Staff, Loans)")
            if self.state.restaurant.level >= 4:
                print("2. Personal Life (Dating, House upgrades)")
            print("3. Open Restaurant for the day")
            print("Q. Quit Prototype")

            choice = input("\nSelect an option: ").strip().lower()

            if choice == "1":
                self.menu_manage_business()
            elif choice == "2" and self.state.restaurant.level >= 4:
                self.menu_personal_life()
            elif choice == "3":
                self.run_business_day()
            elif choice == "q":
                confirm = input("Are you sure you want to quit? (y/n): ").lower()
                if confirm == "y":
                    self.game_over = True
            else:
                print(Fore.RED + "Invalid option. Press Enter to retry.")
                input()

        self.clear_screen()
        if self.victory:
            self.print_header("Victory!", Fore.GREEN)
            print("\nCongratulations! You have completed the V1 Prototype of Infinite Pot.")
            print(f"You successfully upgraded to a full Town Restaurant, bought a cozy home,")
            print(f"found romance with Valerie, and successfully defended your life and business")
            print(f"against Chef Sebastian's attempts to run you out of town.")
            print("\nThrough it all, you cooked unlimited food with a single pot,")
            print("yet food was never the challenge. Balancing bills, relationships, employees,")
            print("and rivals was the real challenge.")
            print("\nAt the end of your journey, you sit on the couch with Valerie, looking at the restaurant.")
            print(Fore.YELLOW + '"What are we actually working for?"' + " she asks softly.")
            print("You smile, but the game leaves the answer to you.")
        else:
            print("\nThank you for playing the Infinite Pot V1 Prototype!")

    def menu_manage_business(self) -> None:
        while True:
            self.clear_screen()
            self.print_header("Business Management")
            r = self.state.restaurant
            p = self.state.player
            
            print(f"Current Menu Price: ${r.menu_price:.2f}")
            min_p, max_p = r.current_config.price_per_meal_range
            print(f"Recommended Price Range: ${min_p:.2f} - ${max_p:.2f}")
            print("-" * 50)
            print("1. Set Menu Meal Price")
            print("2. Buy Upgrades & Customizations")
            print("3. Manage Bank Loans")
            print("4. Staffing (Hire/Fire Employees)")
            if self.state.competitor.is_active:
                marketing_cost = self.state.competitor.marketing_counteraction_cost
                counter_str = " (Active)" if self.state.competitor.counter_marketing_active else ""
                print(f"5. Counter Competitor Marketing (-${marketing_cost:.2f}){counter_str}")
            if r.level < 4:
                next_cfg = r.level_configs.get(r.level + 1)
                if next_cfg:
                    print(f"U. UPGRADE Restaurant to '{next_cfg.name}' (-${next_cfg.upgrade_cost:.2f})")
            print("B. Back to Main Menu")

            choice = input("\nSelect: ").strip().lower()
            if choice == "1":
                try:
                    price = float(input(f"Enter new price per meal (Current: ${r.menu_price:.2f}): "))
                    if price <= 0:
                        print(Fore.RED + "Price must be positive.")
                    else:
                        r.menu_price = round(price, 2)
                        print(Fore.GREEN + f"Meal price set to ${r.menu_price:.2f}.")
                except ValueError:
                    print(Fore.RED + "Invalid number format.")
                input("\nPress Enter to continue...")
            elif choice == "2":
                self.submenu_business_upgrades()
            elif choice == "3":
                self.submenu_loans()
            elif choice == "4":
                self.submenu_staffing()
            elif choice == "5" and self.state.competitor.is_active:
                success, msg, cost = self.state.competitor.activate_counter_marketing(p.cash)
                if success:
                    p.adjust_cash(-cost)
                    self.state.finance.record_transaction("Marketing", cost, "Counter marketing flyer run")
                    print(Fore.GREEN + msg)
                else:
                    print(Fore.RED + msg)
                input("\nPress Enter to continue...")
            elif choice == "u" and r.level < 4:
                success, msg, cost = r.upgrade_level(p.cash)
                if success:
                    p.adjust_cash(-cost)
                    self.state.finance.record_transaction("Upgrade", cost, f"Upgraded restaurant to Level {r.level}")
                    print(Fore.GREEN + msg)
                else:
                    print(Fore.RED + msg)
                input("\nPress Enter to continue...")
            elif choice == "b":
                break

    def submenu_business_upgrades(self) -> None:
        while True:
            self.clear_screen()
            self.print_header("Business Upgrades")
            r = self.state.restaurant
            p = self.state.player

            print(f"Available Cash: ${p.cash:.2f}\n")
            
            # Filter upgrades suitable for current level
            available = [u for u in r.available_upgrades if u.id not in r.upgrades]
            
            if not available:
                print("All available upgrades purchased!")
            else:
                for i, u in enumerate(available, 1):
                    lvl_req = r.level_configs[u.min_level].name
                    req_color = Fore.GREEN if r.level >= u.min_level else Fore.RED
                    owned_str = " (Owned)" if u.id in r.upgrades else ""
                    print(f"{i}. {u.name} - ${u.cost:.2f}{owned_str}")
                    print(f"   Effect: +{int(u.attraction_bonus*100)}% Customer Attraction | Maint: ${u.daily_maintenance}/day")
                    print(f"   Req: {req_color}{lvl_req} (Level {u.min_level}){Fore.RESET}")
                    print(f"   '{u.description}'\n")

            print("B. Back")
            choice = input("Select upgrade to buy: ").strip().lower()
            if choice == "b":
                break
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(available):
                    target = available[idx]
                    success, msg, cost = r.buy_upgrade(target.id, p.cash)
                    if success:
                        p.adjust_cash(-cost)
                        self.state.finance.record_transaction("Upgrade", cost, f"Bought business upgrade: {target.name}")
                        print(Fore.GREEN + msg)
                    else:
                        print(Fore.RED + msg)
                else:
                    print(Fore.RED + "Invalid selection.")
            except ValueError:
                print(Fore.RED + "Invalid input.")
            input("\nPress Enter to continue...")

    def submenu_loans(self) -> None:
        while True:
            self.clear_screen()
            self.print_header("Bank Loans & Debt")
            l = self.state.loan
            p = self.state.player
            r = self.state.restaurant

            print(f"Current Cash: ${p.cash:.2f}")
            print(f"Current Loan Balance: ${l.balance:.2f}")
            print(f"Annual Interest Rate: {int(l.interest_rate_annual*100)}% (Accrues daily)")
            print(f"Maximum Borrow Limit for Level {r.level}: ${l.get_max_borrow_limit(r.level):.2f}")
            print(f"Available Credit: ${l.get_available_borrow_amount(r.level):.2f}")
            print("-" * 50)
            print("1. Borrow Money")
            print("2. Repay Loan Principal")
            print("B. Back")

            choice = input("\nSelect: ").strip().lower()
            if choice == "1":
                try:
                    amount = float(input("Enter amount to borrow: "))
                    success, msg = l.borrow(amount, r.level)
                    if success:
                        p.adjust_cash(amount)
                        print(Fore.GREEN + msg)
                    else:
                        print(Fore.RED + msg)
                except ValueError:
                    print(Fore.RED + "Invalid number format.")
                input("\nPress Enter to continue...")
            elif choice == "2":
                if l.balance <= 0:
                    print(Fore.YELLOW + "You have no outstanding loans to repay.")
                    input("\nPress Enter to continue...")
                    continue
                try:
                    amount = float(input(f"Enter amount to repay (Max: ${l.balance:.2f}): "))
                    success, msg, cash_spent = l.pay_loan(amount, p.cash)
                    if success:
                        p.adjust_cash(-cash_spent)
                        self.state.finance.record_transaction("Misc", -cash_spent, f"Repaid loan principal")
                        print(Fore.GREEN + msg)
                    else:
                        print(Fore.RED + msg)
                except ValueError:
                    print(Fore.RED + "Invalid number format.")
                input("\nPress Enter to continue...")
            elif choice == "b":
                break

    def submenu_staffing(self) -> None:
        while True:
            self.clear_screen()
            self.print_header("Staff Management")
            es = self.state.employees
            r = self.state.restaurant
            
            print(f"Current Hired Staff ({len(es.hired)}/{r.current_config.max_employees}):")
            if not es.hired:
                print("  No employees hired.")
            else:
                for e in es.hired:
                    print(f"  - {e.name} | Skill: {e.skill:.2f} | Reliability: {e.reliability:.2f} | Salary: ${e.daily_salary:.2f}/day | Exp: {e.experience} yrs")
            
            print("-" * 50)
            print("Available Candidates for Hire:")
            if not es.candidates:
                print("  No candidates available.")
            else:
                for i, c in enumerate(es.candidates, 1):
                    print(f"  {i}. {c.name} | Skill: {c.skill:.2f} | Reliability: {c.reliability:.2f} | Salary: ${c.daily_salary:.2f}/day | Exp: {c.experience} yrs")
            
            print("-" * 50)
            print("1. Hire a Candidate")
            print("2. Fire an Employee")
            print("B. Back")

            choice = input("\nSelect: ").strip().lower()
            if choice == "1":
                if not es.candidates:
                    print(Fore.YELLOW + "No candidates available.")
                    input("\nPress Enter...")
                    continue
                name_input = input("Enter candidate name to hire: ").strip()
                success, msg = es.hire_employee(name_input, r.current_config.max_employees)
                if success:
                    print(Fore.GREEN + msg)
                else:
                    print(Fore.RED + msg)
                input("\nPress Enter to continue...")
            elif choice == "2":
                if not es.hired:
                    print(Fore.YELLOW + "No employees to fire.")
                    input("\nPress Enter...")
                    continue
                name_input = input("Enter employee name to fire: ").strip()
                success, msg = es.fire_employee(name_input)
                if success:
                    print(Fore.GREEN + msg)
                else:
                    print(Fore.RED + msg)
                input("\nPress Enter to continue...")
            elif choice == "b":
                break

    def menu_personal_life(self) -> None:
        while True:
            self.clear_screen()
            self.print_header("Personal Life")
            p = self.state.player
            rom = self.state.romance
            h = self.state.house

            print(f"Available Cash: ${p.cash:.2f} | Energy: {p.energy:.1f}/{p.max_energy}")
            print(f"Relationship with {rom.partner_name} ({rom.partner_occupation}):")
            print(f"  Stage: {rom.stage_name} | Progress: {rom.romance_level:.1f}/100.0")
            print(f"House Ownership: " + ("Owned" if h.purchased else "None"))
            print("-" * 50)
            
            print("1. Go on a Date with Valerie (Costs $80.00, 25 Energy)")
            
            if not h.purchased:
                print(f"2. Purchase a House (-${h.cost:.2f})")
            else:
                print("2. Customize and Upgrade House")
                
            if not rom.is_co_owner:
                print("3. Propose Valerie to co-own business & move in")
            else:
                print(Fore.MAGENTA + "💚 Valerie lives with you and co-owns the restaurant!")

            print("B. Back")

            choice = input("\nSelect: ").strip().lower()
            if choice == "1":
                mult = 1.0 + h.get_romance_progress_bonus()
                success, msg, cash_spent, energy_spent = rom.go_on_date(p.cash, p.energy, progress_multiplier=mult)
                if success:
                    p.adjust_cash(-cash_spent)
                    p.adjust_energy(-energy_spent)
                    self.state.finance.record_transaction("Date", cash_spent, "Went on date with Valerie")
                    print(Fore.GREEN + msg)
                else:
                    print(Fore.RED + msg)
                input("\nPress Enter to continue...")
            elif choice == "2":
                if not h.purchased:
                    if p.cash >= h.cost:
                        p.adjust_cash(-h.cost)
                        h.purchased = True
                        p.has_house = True
                        self.state.finance.record_transaction("Upgrade", h.cost, "Purchased house")
                        print(Fore.GREEN + f"Congratulations! You bought a house. You now have a space of your own. (${h.daily_maintenance}/day maintenance)")
                    else:
                        print(Fore.RED + f"Insufficient cash! Buying a house requires ${h.cost:.2f}.")
                else:
                    self.submenu_house_upgrades()
                input("\nPress Enter to continue...")
            elif choice == "3" and not rom.is_co_owner:
                success, msg = rom.ask_to_co_own(h.purchased)
                if success:
                    print(Fore.GREEN + msg)
                else:
                    print(Fore.RED + msg)
                input("\nPress Enter to continue...")
            elif choice == "b":
                break

    def submenu_house_upgrades(self) -> None:
        while True:
            self.clear_screen()
            self.print_header("House Upgrades")
            h = self.state.house
            p = self.state.player

            print(f"Available Cash: ${p.cash:.2f}\n")
            
            available = [u for u in h.available_upgrades if u.id not in h.upgrades]
            
            if not available:
                print("All house upgrades purchased!")
            else:
                for i, u in enumerate(available, 1):
                    owned_str = " (Owned)" if u.id in h.upgrades else ""
                    print(f"{i}. {u.name} - ${u.cost:.2f}{owned_str}")
                    print(f"   Effect: +{u.energy_recovery_bonus} Energy recovery/night | +{int(u.romance_progress_bonus*100)}% Romance speed boost")
                    print(f"   '{u.description}'\n")

            print("B. Back")
            choice = input("Select upgrade to buy: ").strip().lower()
            if choice == "b":
                break
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(available):
                    target = available[idx]
                    success, msg, cost = h.buy_upgrade(target.id, p.cash)
                    if success:
                        p.adjust_cash(-cost)
                        self.state.finance.record_transaction("Upgrade", cost, f"Bought house upgrade: {target.name}")
                        print(Fore.GREEN + msg)
                    else:
                        print(Fore.RED + msg)
                else:
                    print(Fore.RED + "Invalid selection.")
            except ValueError:
                print(Fore.RED + "Invalid input.")
            input("\nPress Enter to continue...")

    def run_business_day(self) -> None:
        self.clear_screen()
        self.print_header("Opening the Restaurant")
        p = self.state.player
        r = self.state.restaurant
        
        # 1. Ask player for hours to work
        print(f"Your Current Energy: {p.energy:.1f}/{p.max_energy}")
        print("Each hour you work costs 5 Energy and serves 3 customers.")
        active_staff = self.state.employees.get_active_employees()
        if active_staff:
            print("Your hired employees are working and will serve customers automatically.")
        if self.state.romance.is_co_owner:
            print("Valerie is helping in the restaurant today!")
            
        work_hours = 0
        while True:
            try:
                ans = input("How many hours do you want to work today? (0-8): ").strip()
                work_hours = int(ans)
                if 0 <= work_hours <= 8:
                    energy_needed = work_hours * p.work_energy_cost_per_hour
                    if p.energy < energy_needed:
                        print(Fore.RED + f"You don't have enough energy to work {work_hours} hours. You need {energy_needed} energy.")
                    else:
                        break
                else:
                    print(Fore.RED + "Hours must be between 0 and 8.")
            except ValueError:
                print(Fore.RED + "Invalid input. Please enter a number between 0 and 8.")

        # 2. Run simulation
        self.clear_screen()
        print("🍳 Fire up the Infinite Pot...")
        time.sleep(0.5)
        print("🚪 Open the doors...")
        time.sleep(0.5)
        print("🍽️ Customers are arriving...")
        time.sleep(0.8)
        
        sim = self.state.simulate_business_day(work_hours)
        
        self.clear_screen()
        self.print_header("End of Business Day")
        print(f"Menu Price Charged: ${sim['meal_price']:.2f}")
        print(f"Total Customer Interest: {sim['potential_customers']} customers arrived.")
        print(f"Actual Served: {Fore.GREEN}{sim['actual_served']}{Fore.RESET} customers.")
        if sim['turned_away'] > 0:
            print(Fore.RED + f"⚠️ Turned Away: {sim['turned_away']} customers (Insufficient staff or capacity!)")
        
        print("-" * 50)
        print(f"Revenue:                 +${sim['revenue']:.2f}")
        print(f"Tips:                    +${sim['tips']:.2f}")
        print(f"Total Income:            {Fore.GREEN}+${sim['total_income']:.2f}{Fore.RESET}")
        print(f"Your Energy Spent:       -{sim['energy_spent']:.1f} Energy")
        
        rep_sign = "+" if sim['rep_change'] >= 0 else "-"
        rep_color = Fore.GREEN if sim['rep_change'] >= 0 else Fore.RED
        print(f"Reputation Change:       {rep_color}{rep_sign}{abs(sim['rep_change']):.2f}{Fore.RESET} points")
        
        print("\nPress Enter to proceed to evening and review expenses...")
        input()

        # 3. Night phase / Overnight adjustments
        self.clear_screen()
        self.print_header("Overnight Ledger")
        
        # Display the financial report for today
        print(self.state.finance.get_daily_report())
        
        # Check and trigger random events BEFORE sleep
        triggered_event = self.state.events.check_and_trigger_event(self.state)
        if triggered_event:
            self.handle_triggered_event(triggered_event)

        # Advance day
        notifications = self.state.advance_day()
        
        if notifications:
            print(Fore.YELLOW + "\nNotifications:")
            for note in notifications:
                print(f"  • {note}")

        # Competitor survival logic
        if self.state.competitor.is_active:
            if self.state.restaurant.reputation >= 60.0 and self.state.romance.romance_level >= 80.0:
                self.days_survived_competitor += 1
                if self.days_survived_competitor >= 10:
                    self.victory = True
                    self.game_over = True
            else:
                # resets if they drop below the survival threshold
                if self.days_survived_competitor > 0:
                    self.days_survived_competitor = 0
                    print(Fore.RED + "\n⚠️ You lost your focus! Sebastian's marketing is eroding your lifestyle. Survival days reset.")

        print("\nPress Enter to sleep and start the next day...")
        input()

    def handle_triggered_event(self, event: Any) -> None:
        self.clear_screen()
        self.print_header(f"EVENT: {event.title}", Fore.MAGENTA)
        print(event.description + "\n")
        
        # Filter choices based on condition
        valid_options = [o for o in event.options if o.condition(self.state)]
        
        for i, opt in enumerate(valid_options, 1):
            print(f"{i}. {opt.text}")
            
        choice = 0
        while True:
            try:
                ans = input("\nMake your decision: ").strip()
                choice = int(ans) - 1
                if 0 <= choice < len(valid_options):
                    break
                else:
                    print(Fore.RED + "Invalid choice.")
            except ValueError:
                print(Fore.RED + "Please enter a valid choice number.")

        chosen_text, outcome_text = self.state.events.resolve_event(choice, self.state)
        
        self.clear_screen()
        self.print_header("Event Resolution", Fore.MAGENTA)
        print(f"You chose: {chosen_text}\n")
        print(Fore.GREEN + outcome_text)
        input("\nPress Enter to continue...")
