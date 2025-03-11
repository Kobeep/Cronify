from croniter import croniter

def validate_cron(expr: str) -> bool:
    try:
        croniter(expr)
        return True
    except Exception:
        return False
