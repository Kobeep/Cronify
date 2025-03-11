import argparse
from datetime import datetime
from rich.console import Console
from .validator import validate_cron
from .simulator import simulate_schedule
from .utils import load_crontab_file, check_conflicts, check_environment_in_command
from .logger import get_logger

console = Console()
logger = get_logger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Cronify CLI")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--cron", help="Cron expression, e.g. '0 0 * * *'")
    group.add_argument("--file", help="Crontab file (YAML or plain text) with cron jobs")
    parser.add_argument("--command", help="Command for cron, used with --cron")
    parser.add_argument("--simulate", action='store_true', help="Simulate next 5 runs")
    parser.add_argument("--dry-run", action='store_true', help="Dry-run mode")
    args = parser.parse_args()

    if args.cron:
        process_cron(args)
    elif args.file:
        process_file(args)

def process_cron(args):
    expr = args.cron
    cmd = args.command if args.command else ""
    logger.info(f"Validating cron: {expr}")
    if validate_cron(expr):
        console.print(f"[green]Cron '{expr}' valid.[/green]")
        if args.simulate:
            console.print("Simulating 5 runs:")
            times = simulate_schedule(expr, datetime.now())
            for t in times:
                console.print(f" - {t}")
    else:
        console.print(f"[red]Invalid cron: {expr}[/red]")
        exit(1)
    if cmd:
        console.print(f"Cmd: {cmd}")
        check_environment_in_command(cmd)

def process_file(args):
    file_path = args.file
    logger.info(f"Loading file: {file_path}")
    jobs = []
    # Check if file is YAML based on extension
    if file_path.endswith((".yaml", ".yml")):
        try:
            import yaml
        except ImportError:
            console.print("[red]PyYAML not installed.[/red]")
            exit(1)
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            console.print(f"[red]Error reading YAML: {e}[/red]")
            exit(1)
        jobs_list = data.get("jobs", [])
        if not jobs_list:
            console.print("[red]No jobs found in YAML file.[/red]")
            exit(1)
        for job in jobs_list:
            name = job.get("name", "Unnamed job")
            expr = job.get("schedule")
            cmd = job.get("command", "")
            env = job.get("env", {})
            if env and isinstance(env, dict):
                env_assignments = " ".join(f"{k}={v}" for k, v in env.items())
                full_cmd = f"{env_assignments} {cmd}".strip()
            else:
                full_cmd = cmd
            if expr is not None:
                jobs.append((expr, full_cmd))
    else:
        # Fallback: plain text crontab file
        jobs = load_crontab_file(file_path)

    schedules = {}
    for idx, (expr, cmd) in enumerate(jobs):
        job_name = f"job_{idx+1}"
        logger.info(f"Validating {job_name}: {expr}")
        console.print(f"\nValidating {job_name}: {expr} -> {cmd}")
        if not validate_cron(expr):
            console.print(f"[red]Invalid: {expr}[/red]")
            continue
        if args.simulate:
            console.print("Simulating 5 runs:")
            times = simulate_schedule(expr, datetime.now())
            schedules[job_name] = times
            for t in times:
                console.print(f"    {t}")
        check_environment_in_command(cmd)
    if schedules:
        conflicts = check_conflicts(schedules)
        if conflicts:
            console.print("\n[red]Conflicts detected:[/red]")
            for key, jobs in conflicts:
                console.print(f" At {key}: {', '.join(jobs)}")
        else:
            console.print("\n[green]No conflicts.[/green]")
    if args.dry_run:
        console.print("\nDry-run active.")
