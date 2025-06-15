from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class Client:
    name: str
    gender: str
    bed: str = ""
    checks: bool = False
    contacts: str = ""
    property: Dict[str, bool] = field(default_factory=dict)
    return_time: Optional[str] = None
    wakeup_time: Optional[str] = None
    shower_after: Optional[int] = None
    label: Any = field(default=None, repr=False, compare=False)
