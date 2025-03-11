import os
import re
import shlex

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

def check_command_file(cmd: str):
    # Split command while skipping env assignments
    tokens = shlex.split(cmd)
    exe = None
    for token in tokens:
        if "=" in token:
            continue
        else:
            exe = token
            break
    if exe is None:
        print("Warning: No executable found in command.")
        return
    if not os.path.isfile(exe):
        print(f"Warning: Executable '{exe}' not found.")
        return
    if not os.access(exe, os.X_OK):
        print(f"Warning: File '{exe}' is not executable.")
