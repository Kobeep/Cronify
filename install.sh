#!/bin/bash
# Cronify installer

set -e

# Root check
if [ "$(id -u)" -ne 0 ]; then
  echo "Run as root"
  exit 1
fi

# Spinner function
spinner() {
  local pid=$1; local delay=0.1; local spin='|/-\'
  while kill -0 "$pid" 2>/dev/null; do
    for ((i=0; i<${#spin}; i++)); do
      printf "\r[%c] " "${spin:$i:1}"
      sleep "$delay"
    done
  done
  printf "\r"
}

# Run command with spinner
run_cmd() {
  "$@" &>/dev/null &
  pid=$!
  spinner "$pid"
  wait "$pid"
}

# Install package using apt-get or yum
install_pkg() {
  pkg="$1"
  if command -v apt-get &>/dev/null; then
    run_cmd apt-get update
    run_cmd apt-get install -y "$pkg"
  elif command -v yum &>/dev/null; then
    run_cmd yum install -y "$pkg"
  else
    echo "No supported package manager. Install $pkg manually."
    exit 1
  fi
}

# Ensure python3 and pip3 exist
if ! command -v python3 &>/dev/null; then
  echo "Installing python3..."
  install_pkg python3
fi

if ! command -v pip3 &>/dev/null; then
  echo "Installing pip3..."
  install_pkg python3-pip
fi

# Install required Python modules
python3 -c "import croniter" 2>/dev/null || { echo "Installing croniter..."; run_cmd pip3 install croniter; }
python3 -c "import rich" 2>/dev/null || { echo "Installing rich..."; run_cmd pip3 install rich; }

# Define install paths
install_path="/usr/local/bin"
lib_path="/usr/local/lib/cronify"

echo "Installing Cronify..."

# Copy main file (rename to avoid conflict with package folder)
cp cronify_main.py "$install_path/cronify_main.py"
chmod +x "$install_path/cronify_main.py"

# Copy package folder
mkdir -p "$lib_path"
cp -r cronify/* "$lib_path/"

# Create wrapper script 'cronify'
wrapper="$install_path/cronify"
cat << EOF > "$wrapper"
#!/bin/bash
export PYTHONPATH=/usr/local/lib
exec python3 /usr/local/bin/cronify_main.py "\$@"
EOF
chmod +x "$wrapper"

echo "Installed. Run 'cronify --help' to use Cronify."
