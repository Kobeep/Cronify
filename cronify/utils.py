import os
import re

def load_crontab_file(file_path: str):
    jobs = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split()
                if len(parts) < 6:
                    continue
                expr = " ".join(parts[:5])
                cmd = " ".join(parts[5:])
                jobs.append((expr, cmd))
    except Exception:
        pass
    return jobs

def check_conflicts(schedules: dict):
    conflicts = []
    schedule_map = {}
    for job, times in schedules.items():
        for t in times:
            key = (t.year, t.month, t.day, t.hour, t.minute)
            schedule_map.setdefault(key, []).append(job)
    for key, jobs in schedule_map.items():
        if len(jobs) > 1:
            conflicts.append((key, jobs))
    return conflicts

def check_environment_in_command(cmd: str):
    vars_found = re.findall(r'\$([A-Za-z_]\w*)', cmd)
    for var in vars_found:
        if var not in os.environ:
            print(f"Warning: Env var ${var} not set.")
