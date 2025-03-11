#!/bin/bash
# Uninstall Cronify
set -e
if [ "$(id -u)" -ne 0 ]; then
  echo "Run as root"
  exit 1
fi
spinner() {
  local pid=\$1; local delay=0.1; local spin='|/-\\'
  while kill -0 "\$pid" 2>/dev/null; do
    for ((i=0; i<\${#spin}; i++)); do
      printf "\r[%c] " "\${spin:\$i:1}"
      sleep "\$delay"
    done
  done
  printf "\r"
}
run_cmd() {
  "\$@" &>/dev/null &
  pid=\$!
  spinner "\$pid"
  wait "\$pid"
}
remove_item() {
  item="\$1"
  if [ -e "\$item" ]; then
    run_cmd rm -rf "\$item"
    echo "Removed \$item"
  else
    echo "\$item not found."
  fi
}
echo "Uninstalling Cronify..."
remove_item "/usr/local/bin/cronify"
remove_item "/usr/local/bin/cronify_main.py"
remove_item "/usr/local/lib/cronify"
echo "Uninstalled."
