from dataclasses import dataclass

@dataclass
class UserContext:
    role: str  # 'company' or 'admin'
    company_id: int | None
