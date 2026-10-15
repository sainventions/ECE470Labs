#!/usr/bin/env bash

# setup_terminator_four.sh
#
# Creates this Terminator layout:
#
# +----------------------+----------------------+
# |                      |                      |
# |      Left Top        |      Right Top       |
# |                      |                      |
# +----------------------+----------------------+
# |                      |                      |
# |     Left Bottom      |     Right Bottom     |
# |                      |                      |
# +----------------------+----------------------+

set -e

CONFIG_DIR="$HOME/.config/terminator"
CONFIG_FILE="$CONFIG_DIR/config"

# Display dimensions.
SCREEN_WIDTH=1920
SCREEN_HEIGHT=1080

# Use 90% of the screen width and height.
WINDOW_WIDTH=$((SCREEN_WIDTH * 9 / 10))
WINDOW_HEIGHT=$((SCREEN_HEIGHT * 9 / 10))

# Center the Terminator window.
WINDOW_X=$(((SCREEN_WIDTH - WINDOW_WIDTH) / 2))
WINDOW_Y=$(((SCREEN_HEIGHT - WINDOW_HEIGHT) / 2))

# Split the window into equal left and right sections.
LEFT_RIGHT_SPLIT=$((WINDOW_WIDTH / 2))

# Split each side into equal top and bottom sections.
TOP_BOTTOM_SPLIT=$((WINDOW_HEIGHT / 2))

echo "Screen size:         ${SCREEN_WIDTH}x${SCREEN_HEIGHT}"
echo "Terminator size:     ${WINDOW_WIDTH}x${WINDOW_HEIGHT}"
echo "Terminator position: ${WINDOW_X}:${WINDOW_Y}"
echo

# Terminator can write its configuration when it closes.
# Require all Terminator windows to be closed before editing.
# if pgrep -x terminator >/dev/null 2>&1; then
#     echo "Error: Terminator is currently running."
#     echo "Close all Terminator windows and run this script again."
#     exit 1
# fi

# Create the configuration directory if it does not exist.
mkdir -p "$CONFIG_DIR"

# Back up the existing configuration.
if [[ -f "$CONFIG_FILE" ]]; then
    BACKUP_FILE="${CONFIG_FILE}.backup.$(date +%Y%m%d-%H%M%S)"

    cp -a "$CONFIG_FILE" "$BACKUP_FILE"

    echo "Existing configuration backed up to:"
    echo "  $BACKUP_FILE"
    echo
fi

# Write the new Terminator configuration.
cat > "$CONFIG_FILE" <<EOF
[global_config]
[keybindings]
[profiles]
  [[default]]
[layouts]
  [[default]]
    [[[window0]]]
      type = Window
      parent = ""
      order = 0
      position = ${WINDOW_X}:${WINDOW_Y}
      maximised = False
      fullscreen = False
      size = ${WINDOW_WIDTH}, ${WINDOW_HEIGHT}

    [[[split_left_right]]]
      type = HPaned
      parent = window0
      order = 0
      position = ${LEFT_RIGHT_SPLIT}
      ratio = 0.5

    [[[split_left_top_bottom]]]
      type = VPaned
      parent = split_left_right
      order = 0
      position = ${TOP_BOTTOM_SPLIT}
      ratio = 0.5

    [[[terminal_left_top]]]
      type = Terminal
      parent = split_left_top_bottom
      order = 0
      profile = default

    [[[terminal_left_bottom]]]
      type = Terminal
      parent = split_left_top_bottom
      order = 1
      profile = default

    [[[split_right_top_bottom]]]
      type = VPaned
      parent = split_left_right
      order = 1
      position = ${TOP_BOTTOM_SPLIT}
      ratio = 0.5

    [[[terminal_right_top]]]
      type = Terminal
      parent = split_right_top_bottom
      order = 0
      profile = default

    [[[terminal_right_bottom]]]
      type = Terminal
      parent = split_right_top_bottom
      order = 1
      profile = default

[plugins]
EOF

echo "Terminator configuration updated successfully."
echo
echo "Start Terminator with:"
echo "  terminator "
