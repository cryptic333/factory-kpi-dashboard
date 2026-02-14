
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)
machines = ["CNC_1", "CNC_2", "WELD_1", "CUT_1"]
stop_reasons = ["Changeover", "Material shortage", "Sensor fault", "Maintenance", "Quality check"]

start = datetime.now() - timedelta(days=7)
rows = []

for i in range(7 * 24 * 6):  # 7 days, every 10 minutes
    ts = start + timedelta(minutes=10 * i)
    machine = np.random.choice(machines)

     # 85% running, 15% stopped
    running = np.random.rand() < 0.85
    status = "RUN" if running else "STOP"
 
    units = int(np.random.normal(12, 3)) if running else 0
    units = max(units, 0)

    rejects = int(np.random.binomial(units, 0.03)) if running else 0  # ~3% scrap
    reason = "" if running else np.random.choice(stop_reasons)
 
    rows.append([ts, machine, status, reason, units, rejects])
 
    df = pd.DataFrame(rows, columns=["timestamp", "machine", "status", "stop_reason", "units", "rejects"])
    df.to_csv("factory_events.csv", index=False)
print("✅ Created factory_events.csv with", len(df), "rows")
