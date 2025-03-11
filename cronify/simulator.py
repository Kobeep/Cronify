from croniter import croniter
from datetime import datetime

def simulate_schedule(expr: str, start_time: datetime, count: int = 5):
    try:
        itr = croniter(expr, start_time)
        return [itr.get_next(datetime) for _ in range(count)]
    except Exception:
        return []
