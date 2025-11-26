import serial
import re
import numpy as np
import matplotlib.pyplot as plt
from collections import deque

# -------------------- USER SETTINGS --------------------
SERIAL_PORT = "COM3"       # Tag serial port
BAUD_RATE = 115200

# Anchor positions (meters)
anchors = {
    18: (0.83, 0.08),
    22: (2.24, 0.08),
    26: (2.62, 8.16),
    30: (0.94, 8.16)
}

# Exponential smoothing factor (0 = no smoothing, 1 = extremely smooth/slow)
SMOOTHING = 0.2  

# Outlier rejection threshold (meters difference)
OUTLIER_THRESHOLD = 0.8

# Max number of historical points to keep in trail
TRAIL_LENGTH = 30
# --------------------------------------------------------

# Rolling history for outlier rejection
distance_history = {aid: deque(maxlen=10) for aid in anchors.keys()}

tag_history = deque(maxlen=TRAIL_LENGTH)
last_pos = None


def reject_outliers(aid, distance):
    """Rejects outlier readings if they differ too much from rolling average"""
    history = distance_history[aid]

    if len(history) < 3:
        history.append(distance)
        return distance

    avg = sum(history) / len(history)

    if abs(distance - avg) > OUTLIER_THRESHOLD:
        # Outlier detected → Keep old average
        return avg

    history.append(distance)
    return distance


def estimate_position(distances):
    """Multilateration using least squares"""
    A = []
    b = []

    anchor_ids = list(distances.keys())
    x1, y1 = anchors[anchor_ids[0]]
    d1 = distances[anchor_ids[0]]

    for aid in anchor_ids[1:]:
        x, y = anchors[aid]
        d = distances[aid]

        A.append([2*(x - x1), 2*(y - y1)])
        b.append(d1**2 - d**2 - x1**2 + x**2 - y1**2 + y**2)

    A = np.array(A)
    b = np.array(b)

    try:
        pos = np.linalg.lstsq(A, b, rcond=None)[0]
        return pos[0], pos[1]
    except:
        return None


def smooth_position(new_pos, old_pos):
    """Apply exponential smoothing to tag movement"""
    if old_pos is None:
        return new_pos

    x = old_pos[0] + SMOOTHING * (new_pos[0] - old_pos[0])
    y = old_pos[1] + SMOOTHING * (new_pos[1] - old_pos[1])
    return (x, y)


# ----- Initialize plot -----
serial_port = serial.Serial(SERIAL_PORT, BAUD_RATE)
plt.ion()
fig, ax = plt.subplots(figsize=(7, 5))

# Auto-set axis based on anchor layout
anchor_x = [pos[0] for pos in anchors.values()]
anchor_y = [pos[1] for pos in anchors.values()]

min_x = min(anchor_x) - 1
max_x = max(anchor_x) + 1
min_y = min(anchor_y) - 1
max_y = max(anchor_y) + 1


while True:
    line = serial_port.readline().decode(errors='ignore')

    # Parse lines like: "18 1.032 m 22 3.630 m ..."
    matches = re.findall(r'(\d+)\s+(\d+\.\d+)\s+m', line)

    if len(matches) >= 3:
        raw_dist = {int(a): float(d) for a, d in matches}

        # Apply outlier filter
        distances = {}
        for aid, d in raw_dist.items():
            distances[aid] = reject_outliers(aid, d)

        pos = estimate_position(distances)

        if pos:
            pos = smooth_position(pos, last_pos)
            last_pos = pos
            tag_history.append(pos)

            ax.clear()

            # Draw anchors
            for aid, (x, y) in anchors.items():
                ax.scatter(x, y, color='red', s=80)
                ax.text(x + 0.05, y + 0.05, f"A{aid}", fontsize=10)

            # Draw tag trail
            if len(tag_history) > 1:
                xs, ys = zip(*tag_history)
                ax.plot(xs, ys, color="blue", alpha=0.4)

            # Draw tag
            ax.scatter(pos[0], pos[1], color='blue', s=100)
            ax.text(pos[0] + 0.05, pos[1] + 0.05, "TAG", fontsize=10)

            # Graph appearance
            ax.set_xlim(min_x, max_x)
            ax.set_ylim(min_y, max_y)
            ax.set_aspect('equal')
            ax.grid(True)
            ax.set_title("Real-Time UWB Position Tracking")

            plt.pause(0.01)
