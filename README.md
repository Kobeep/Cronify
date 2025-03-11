# Cronify

Cronify is a YAML-driven tool for managing, validating, and deploying cron jobs.

## Features
- YAML configuration for cron jobs.
- Cron expression validation.
- Simulation of next 5 run times.
- Environment variable checks.
- Crontab deployment.
- Rich logging and colored output.

## Structure
- **cronify_main.py**: Main entry.
- **cronify/**: Package with modules.
  - __init__.py
  - cli.py: CLI interface.
  - logger.py: Logging.
  - simulator.py: Schedule simulation.
  - validator.py: Cron validation.
  - utils.py: Utility functions.
- **install.bash**: Installer.
- **uninstall.bash**: Uninstaller.
- **README.md**: This file.

## Installation
Clone the repo and run:
\`\`\`bash
sudo ./install.bash
\`\`\`

## Usage
Run:
\`\`\`bash
cronify --help
\`\`\`

## Uninstallation
Run:
\`\`\`bash
sudo ./uninstall.bash
\`\`\`

## License

Distributed under the GNU GPLv3 License. See `LICENSE` for more information.
