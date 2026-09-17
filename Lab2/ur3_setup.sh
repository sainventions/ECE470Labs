#!/bin/bash
# =============================================================================
# ROS2 Workspace Setup Script
# Usage: source setup.sh  (or: . setup.sh)
# NOTE: Must be sourced, not executed. Running as 'bash setup.sh' will NOT
#       apply environment changes to your current terminal session.
# =============================================================================
# To add a new machine: find your MAC last byte with:
#   cat /sys/class/net/$(ip route get 8.8.8.8 | awk '{print $5; exit}')/address
# Then add an entry to the domain_map below.
# =============================================================================

# --- MAC address → ROS_DOMAIN_ID map ---
# Format: ["MAC_LAST_BYTE"]="DOMAIN_ID"
declare -A domain_map
domain_map["91"]=51
domain_map["97"]=52
domain_map["8f"]=53
domain_map["7f"]=54
domain_map["7d"]=55
domain_map["e1"]=56
domain_map["95"]=57
domain_map["41"]=58
# domain_map["xx"]=YY   # Add your machine here

# --- Get the MAC address of the active network interface ---
ACTIVE_IFACE=$(ip route get 8.8.8.8 2>/dev/null | awk '{print $5; exit}')

if [ -z "$ACTIVE_IFACE" ]; then
    echo "[setup.sh] ERROR: Could not detect active network interface."
    return 1
fi

MAC=$(cat /sys/class/net/"$ACTIVE_IFACE"/address 2>/dev/null)

if [ -z "$MAC" ]; then
    echo "[setup.sh] ERROR: Could not read MAC address for interface '$ACTIVE_IFACE'."
    return 1
fi

# Extract the last byte of the MAC address (lowercase)
LAST_BYTE=$(echo "$MAC" | tr '[:upper:]' '[:lower:]' | awk -F: '{print $NF}')

# --- Lookup domain ID ---
DOMAIN_ID="${domain_map[$LAST_BYTE]}"

if [ -z "$DOMAIN_ID" ]; then
    echo "[setup.sh] ERROR: Unknown MAC last byte '${LAST_BYTE}' (full MAC: ${MAC}, interface: ${ACTIVE_IFACE})"
    echo "[setup.sh] Add an entry to the domain_map in setup.sh to register this machine."
    return 1
fi

# --- Source ROS2 and workspace ---
source /opt/ros/jazzy/setup.bash
source install/setup.bash

# --- Export domain ID ---
export ROS_DOMAIN_ID=$DOMAIN_ID

echo "[setup.sh] ROS2 environment ready."
echo "  Interface : $ACTIVE_IFACE"
echo "  MAC       : $MAC"
echo "  Domain ID : $ROS_DOMAIN_ID"
