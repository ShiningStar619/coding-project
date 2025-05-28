import nidaqmx
import matplotlib.pyplot as plt
from collections import deque
import time
import csv
from datetime import datetime

# กำหนดค่าพื้นฐาน
channel_name = "Dev1/ai0"  
log_file = "alcohol_log.csv"
sampling_interval = 0.1  # หน่วยเป็นวินาที (10 Hz)
max_points = 100  # จำนวนจุดบนกราฟ

# เตรียมไฟล์ CSV
with open(log_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "Voltage (V)"])

# เตรียมกราฟ
data = deque([0] * max_points, maxlen=max_points)
plt.ion()
fig, ax = plt.subplots()
line, = ax.plot(data)
ax.set_ylim(0, 5)
ax.set_title("Alcohol Sensor (MQ-3B) - Real-Time")
ax.set_ylabel("Voltage (V)")
ax.set_xlabel("Sample")

# อ่านข้อมูลจาก DAQ และบันทึก
with nidaqmx.Task() as task:
    task.ai_channels.add_ai_voltage_chan(channel_name)

    while True:
        try:
            value = task.read()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            print(f"[{timestamp}] Value: {value:.3f} V")

            # บันทึกลง CSV
            with open(log_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, value])

            # อัปเดตกกราฟ
            data.append(value)
            line.set_ydata(data)
            line.set_xdata(range(len(data)))
            fig.canvas.draw()
            fig.canvas.flush_events()

            time.sleep(sampling_interval)

        except KeyboardInterrupt:
            print("หยุดการเก็บข้อมูล")
            break
