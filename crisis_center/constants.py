# Constants for the crisis center application
import os

MIN_ROOM_WIDTH = 170
MIN_ROOM_HEIGHT = 150
MAX_LABELS_PER_COLUMN = 5

# Layout breakpoints
DESKTOP_WIDTH = 900
TABLET_WIDTH = 600
MIN_LOG_HEIGHT = 180

# Minimum application dimensions
APP_MIN_WIDTH = 400
APP_MIN_HEIGHT = MIN_ROOM_HEIGHT + MIN_LOG_HEIGHT

# Colors
APP_BG = "#2d2759"
LOG_BG = "#ecebed"
LOCATION_BG = "white"
BUTTON_BG = "#ea4338"
BUTTON_FG = "white"

# Button padding and fonts
BUTTON_PADX = 8
BUTTON_PADY = 6
BUTTON_FONT = ("TkDefaultFont", 10, "bold")
CLIENT_FONT = ("TkDefaultFont", 10)

CLIENTS_FILE = "clients.json"
LOG_DIR = "logs"

PROPERTY_KEYS = ["Tray", "Medical", "Bin", "Sharps", "Hot Room", "Money"]

SHOWER_TIMEOUT_MS = 20 * 60 * 1000  # 20 minutes

# List of all bed assignments available in the facility
BED_OPTIONS = (
    [f"MD {i}" for i in range(1, 10)]
    + [f"FD {i}" for i in range(1, 8)]
    + [f"XD {i}" for i in range(1, 3)]
    + [f"CR {i}" for i in range(1, 3)]
)
