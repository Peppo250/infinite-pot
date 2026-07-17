from dataclasses import dataclass, field
import random
from typing import Any

@dataclass
class Employee:
    name: str
    skill: float  # 0.0 to 1.0 (influences quality, tips, service success)
    reliability: float  # 0.0 to 1.0 (chance of showing up, not making mistakes)
    experience: int  # in years
    daily_salary: float
    is_active: bool = True  # Can be disabled if they call in sick

    def roll_attendance(self) -> bool:
        """Determines if the employee shows up today based on reliability.
        Returns True if they show up, False if they call in sick.
        """
        if random.random() > self.reliability:
            self.is_active = False
            return False
        self.is_active = True
        return True

@dataclass
class EmployeeSystem:
    hired: list[Employee] = field(default_factory=list)
    candidates: list[Employee] = field(default_factory=list)

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "EmployeeSystem":
        pool = config.get("employee_pool", [])
        candidates_list = [
            Employee(
                name=c["name"],
                skill=c["skill"],
                reliability=c["reliability"],
                experience=c["experience"],
                daily_salary=c["daily_salary"]
            )
            for c in pool
        ]
        return cls(hired=[], candidates=candidates_list)

    def hire_employee(self, name: str, max_employees: int) -> tuple[bool, str]:
        """Attempts to hire an employee from candidates."""
        if len(self.hired) >= max_employees:
            return False, f"Your restaurant is at capacity! Fire someone first or upgrade your restaurant. (Max: {max_employees})"

        candidate = next((c for c in self.candidates if c.name == name), None)
        if not candidate:
            return False, "Candidate not found."

        self.candidates.remove(candidate)
        self.hired.append(candidate)
        return True, f"Hired {candidate.name}! They will start tomorrow."

    def fire_employee(self, name: str) -> tuple[bool, str]:
        """Fires a hired employee and returns them to the candidates pool."""
        employee = next((e for e in self.hired if e.name == name), None)
        if not employee:
            return False, "Employee not found in your hired staff."

        self.hired.remove(employee)
        # Reset active status and put back into candidate pool
        employee.is_active = True
        self.candidates.append(employee)
        return True, f"Fired {employee.name}. They have left the business."

    def get_active_employees(self) -> list[Employee]:
        """Returns employees who are working today."""
        return [e for e in self.hired if e.is_active]

    def roll_daily_attendance(self) -> list[str]:
        """Rolls attendance for all hired employees. Returns a list of messages about call-ins."""
        notices = []
        for e in self.hired:
            present = e.roll_attendance()
            if not present:
                notices.append(f"Notification: {e.name} called in sick today and won't be working.")
        return notices

    def calculate_daily_wages(self) -> float:
        """Returns the total wages due for the day (only paid for employees who work)."""
        return sum(e.daily_salary for e in self.get_active_employees())
