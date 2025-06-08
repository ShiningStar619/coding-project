import nidaqmx
import numpy as np
import matplotlib.pyplot as plt
from collections import deque
import time
import csv
from datetime import datetime

#setup parameters
DAQ_channel = "Dev1/ai0:2"
log_file = "sensor_data_multi.csv"
Sensor_names = ["Voltage(MQ-3b", "Voltage(MQ-3)", "Voltage(MQ-9B)"]
# graph parameters (ตั้งค่าที่หลัง sample rate = 12sec with 100Hz)
Max_graph_points = 1000
Sample_rate = 1000  # Hz

# setup CSV file
csv_header = ["Timestamp"] + Sensor_names
with open(log_file, mode='w', newline='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(csv_header)

print(f"ไฟล์ CSV ' {log_file}' ถูกสร้างขึ้นแล้ว")

# graph setup
data_deque = [deque([0] * Max_graph_points, maxlen=Max_graph_points) for _ in range(len(Sensor_names))]
plt.ion() 
fig, ax =  plt.subplots(figsize=(12, 7))   

lines = []
colors = ['dodgerblue', 'red', 'green']  
for i in range(len(Sensor_names)):
        line, = ax.plot(np.arange(Max_graph_points), data_deque[i], color=colors[i], label=Sensor_names[i])
        lines.append(line)

ax.set_ylim(0, 5)  # Adjust based on expected sensor values
ax.set_title("Real-time Sensor readings", fontsize=16)
ax.set_ylabel("Voltage (V)", fontsize=14)
ax.set_xlabel("Sample Number", fontsize=14)
ax.legend()
ax.grid(True)


