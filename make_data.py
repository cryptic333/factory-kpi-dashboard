import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

np.random.seed(42)

machines = ["CNC_1", "CNC_2", "WELD_1", "CUT_1"]

# Machine base production rates (units per 10 mins)
machine_base_rate = {
    "CNC_1": 14,
    "CNC_2": 11,
    "WELD_1": 8,
    "CUT_1": 6
}

# Scrap base probability
machine_scrap_rate = {
    "CNC_1": 0.02,
    "CNC_2": 0.03,
    "WELD_1": 0.04,
    "CUT_1": 0.05
}

stop_reasons = [
    "Changeover",
    "Material Shortage",
    "Maintenance",
    "Sensor Fault",
    "Quality Inspection"
]

start_time = datetime.now() - timedelta(days=14)

rows = []

for i in range(14 * 24 * 6):  # 14 days, every 10 minutes
    timestamp = start_time + timedelta(minutes=10 * i)

    hour = timestamp.hour

    # Shift effect (lower output at night)
    if 0 <= hour < 6:
        shift_multiplier = 0.7
    elif 6 <= hour < 14:
        shift_multiplier = 1.0
    else:
        shift_multiplier = 0.9

    for machine in machines:

        base_rate = machine_base_rate[machine]
        scrap_rate = machine_scrap_rate[machine]

        # Simulate machine wear increasing slowly over time
        wear_factor = 1 + (i / (14 * 24 * 6)) * 0.3
        scrap_probability = scrap_rate * wear_factor

        # Random downtime events (clustered)
        downtime_chance = 0.05
        if random.random() < downtime_chance:
            status = "STOP"
            units = 0
            rejects = 0
            reason = random.choice(stop_reasons)
        else:
            status = "RUN"
            production = base_rate * shift_multiplier
            units = int(np.random.normal(production, 2))
            units = max(units, 0)

            rejects = np.random.binomial(units, scrap_probability)
            reason = ""

        rows.append([
            timestamp,
            machine,
            status,
            reason,
            units,
            rejects
        ])

df = pd.DataFrame(rows, columns=[
    "timestamp",
    "machine",
    "status",
    "stop_reason",
    "units",
    "rejects"
])

df.to_csv("factory_events.csv", index=False)

print("Dataset generated successfully")
print("Rows created:", len(df))
