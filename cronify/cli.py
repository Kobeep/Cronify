import argparse
import sys
import os
import tempfile
from datetime import datetime
from rich.console import Console
from .validator import validate_cron
from .simulator import simulate_schedule
from .utils import load_crontab_file, check_conflicts, check_environment_in_command, check_command_file
from .logger import get_logger

console = Console()
logger = get_logger(__name__)

def main():
    parser = argparse.ArgumentParser(
        description="Cronify CLI - Manage, validate, simulate and deploy cron jobs"
    )
    # Modes: exactly one of these should be provided.
    mode_group = parser.add_mutually_exclusive_group(required=False)
    mode_group.add_argument("--cron", help="Cron expression (e.g., '0 0 * * *')")
    mode_group.add_argument("--file", help="Path to crontab file (YAML or text)")
    mode_group.add_argument("--deploy", help="Path to YAML file for deployment")
    parser.add_argument("--command", help="Command for cron (used with --cron)")
    parser.add_argument("--simulate", action="store_true", help="Simulate next 5 runs or preview crontab")
    parser.add_argument("--dry-run", action="store_true", help="Dry-run mode (no deployment)")

    # Show help if no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    # Ensure exactly one mode is provided
    modes = [args.cron, args.file, args.deploy]
    provided_modes = [m for m in modes if m is not None]
    if len(provided_modes) != 1:
        parser.error("Provide exactly one of --cron, --file, or --deploy")

    if args.cron:
        process_cron(args)
    elif args.file:
        process_file(args)
    elif args.deploy:
        process_deploy(args)

def process_cron(args):
    expr = args.cron
    cmd = args.command if args.command else ""
    logger.info(f"Validating cron: {expr}")
    if validate_cron(expr):
        console.print(f"[green]Cron '{expr}' is valid.[/green]")
        if args.simulate:
            console.print("Simulating 5 runs:")
            for t in simulate_schedule(expr, datetime.now()):
                console.print(f" - {t}")
    else:
        console.print(f"[red]Invalid cron: {expr}[/red]")
        sys.exit(1)
    if cmd:
        console.print(f"Command: {cmd}")
        check_environment_in_command(cmd)
        check_command_file(cmd)

def process_file(args):
    file_path = args.file
    logger.info(f"Loading file: {file_path}")
    jobs = []
    if file_path.endswith((".yaml", ".yml")):
        try:
            import yaml
        except ImportError:
            console.print("[red]PyYAML not installed.[/red]")
            sys.exit(1)
        try:
            with open(file_path, "r") as f:
                data = yaml.safe_load(f)
        except Exception as e:
            console.print(f"[red]Error reading YAML: {e}[/red]")
            sys.exit(1)
        for job in data.get("jobs", []):
            expr = job.get("schedule")
            cmd = job.get("command", "")
            env = job.get("env", {})
            full_cmd = f"{' '.join(f'{k}={v}' for k, v in env.items())} {cmd}".strip() if env else cmd
            if expr is not None:
                jobs.append((expr, full_cmd))
    else:
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
        check_command_file(cmd)
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

def process_deploy(args):
    file_path = args.deploy
    logger.info(f"Deploying from file: {file_path}")
    try:
        import yaml
    except ImportError:
        console.print("[red]PyYAML not installed.[/red]")
        sys.exit(1)
    try:
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        console.print(f"[red]Error reading YAML: {e}[/red]")
        sys.exit(1)
    jobs_list = data.get("jobs", [])
    if not jobs_list:
        console.print("[red]No jobs found in YAML file.[/red]")
        sys.exit(1)
    crontab_content = generate_crontab_content(jobs_list)
    if args.simulate:
        console.print("[yellow]Simulated crontab content:[/yellow]")
        console.print(crontab_content)
    else:
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
            tmp.write(crontab_content)
            tmp_filename = tmp.name
        os.system(f"crontab {tmp_filename}")
        os.remove(tmp_filename)
        console.print("[green]Crontab deployed successfully.[/green]")

def generate_crontab_content(jobs_list):
    lines = []
    header = f"# Cronify deployed on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    lines.append(header)
    lines.append("")
    for job in jobs_list:
        name = job.get("name", "Unnamed job")
        expr = job.get("schedule")
        cmd = job.get("command", "")
        env = job.get("env", {})
        full_cmd = f"{' '.join(f'{k}={v}' for k, v in env.items())} {cmd}".strip() if env else cmd
        lines.append(f"# job: {name}")
        lines.append(f"{expr} {full_cmd}")
        lines.append("")
    return "\n".join(lines)

if __name__ == "__main__":
    main()
