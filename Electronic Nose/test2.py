# ===================================================================
#   Real-time Multi-Graph Sensor Dashboard
#   - Displays 4 graphs: 3 individual comparisons and 1 combined.
#   - Operates at a lower sampling rate for smooth visualization.
# ===================================================================
import nidaqmx
import matplotlib.pyplot as plt
from collections import deque
import numpy as np
import time
import csv
from datetime import datetime

# ===================================================================
# 1. ส่วนของการตั้งค่า (Configuration)
# ===================================================================
# การตั้งค่าอุปกรณ์และไฟล์
DAQ_CHANNELS = "Dev1/ai0:2"
LOG_FILE = "sensor_dashboard_log.csv" # สร้างไฟล์ Log ใหม่สำหรับ Dashboard นี้
SENSOR_NAMES = ["MQ-3b", "MQ-3", "MQ-9B"]

# !!! การตั้งค่าที่สำคัญ !!!
# ลดความเร็วลงเพื่อให้วาดกราฟทัน
SAMPLING_INTERVAL_S = 0.2 # 0.2 วินาทีต่อ 1 sample = 5 Hz

# การตั้งค่ากราฟและ Smoothing
MAX_GRAPH_POINTS = 100 # แสดงข้อมูลย้อนหลัง 100 จุด
SMOOTHING_WINDOW_SIZE = 10 # ขนาดหน้าต่างสำหรับทำ Smoothing (ปรับได้)

# ===================================================================
# 2. ส่วนเตรียมการ (Setup)
# ===================================================================
# เตรียมไฟล์ CSV
csv_header = ["Timestamp"] + [f"Raw_{s}" for s in SENSOR_NAMES] + [f"Smoothed_{s}" for s in SENSOR_NAMES]
try:
    with open(LOG_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(csv_header)
    print(f"ไฟล์ CSV '{LOG_FILE}' ถูกสร้างและพร้อมสำหรับบันทึกข้อมูล")
except IOError as e:
    print(f"ไม่สามารถเขียนไฟล์ CSV ได้: {e}")
    exit()

# --- เตรียมข้อมูลและกราฟ ---
# สร้างที่เก็บข้อมูลสำหรับ Raw และ Smoothed ของแต่ละเซ็นเซอร์
raw_data_deques = [deque([0.0]*MAX_GRAPH_POINTS, maxlen=MAX_GRAPH_POINTS) for _ in SENSOR_NAMES]
smoothed_data_deques = [deque([0.0]*MAX_GRAPH_POINTS, maxlen=MAX_GRAPH_POINTS) for _ in SENSOR_NAMES]

# สร้างหน้าต่างและแกนกราฟ 4 ช่อง (2x2)
plt.ion()
fig, axes = plt.subplots(2, 2, figsize=(16, 9))
fig.suptitle("Real-time Sensor Dashboard", fontsize=16)
ax_flat = axes.flatten() # แปลง axes 2x2 ให้เป็น list 1x4 เพื่อง่ายต่อการวนลูป

# เตรียมเส้นกราฟทั้งหมด
lines = {}
colors = ['dodgerblue', 'red', 'green']

# สร้าง 3 กราฟเปรียบเทียบ
for i, sensor_name in enumerate(SENSOR_NAMES):
    ax = ax_flat[i]
    # เส้นข้อมูลดิบ (จางๆ)
    lines[f'raw_{i}'], = ax.plot(raw_data_deques[i], color=colors[i], alpha=0.5, label=f'Raw {sensor_name}')
    # เส้นข้อมูลที่ปรับเรียบแล้ว (เข้มๆ)
    lines[f'smooth_{i}'], = ax.plot(smoothed_data_deques[i], color=colors[i], linewidth=2, label=f'Smoothed {sensor_name}')
    ax.set_title(f'{sensor_name} Readings')
    ax.set_ylim(0, 5)
    ax.legend(loc='upper left')
    ax.grid(True)

# สร้างกราฟที่ 4 (กราฟรวม)
ax_combined = ax_flat[3]
ax_combined.set_title("Combined Smoothed Signals")
for i, sensor_name in enumerate(SENSOR_NAMES):
    # ในกราฟรวม เราจะแสดงเฉพาะเส้นที่ปรับเรียบแล้ว
    lines[f'combined_{i}'], = ax_combined.plot(smoothed_data_deques[i], color=colors[i], linewidth=2, label=sensor_name)
ax_combined.set_ylim(0, 5)
ax_combined.legend(loc='upper left')
ax_combined.grid(True)

plt.tight_layout(rect=[0, 0, 1, 0.96])


# ===================================================================
# 3. Loop การทำงานหลัก (Main Loop)
# ===================================================================
try:
    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan(DAQ_CHANNELS)

        while True:
            # อ่านค่าจากเซ็นเซอร์ 3 ตัว
            voltages = task.read()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            
            smoothed_voltages = []

            # วนลูปเพื่อประมวลผลทีละเซ็นเซอร์
            for i in range(len(SENSOR_NAMES)):
                # 1. เพิ่มข้อมูลดิบใหม่เข้าไป
                raw_data_deques[i].append(voltages[i])

                # 2. คำนวณค่า Smoothed ใหม่จากข้อมูลล่าสุด
                # โดยใช้ข้อมูล N ตัวสุดท้ายใน deque ของข้อมูลดิบ
                current_window = list(raw_data_deques[i])[-SMOOTHING_WINDOW_SIZE:]
                smoothed_value = np.mean(current_window)
                smoothed_voltages.append(smoothed_value)
                
                # 3. เพิ่มข้อมูล Smoothed ใหม่เข้าไป
                smoothed_data_deques[i].append(smoothed_value)

            # บันทึกข้อมูลทั้งหมดลง CSV
            with open(LOG_FILE, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp] + voltages + smoothed_voltages)

            # อัปเดตเส้นกราฟทั้งหมด
            # อัปเดต 3 กราฟเปรียบเทียบ
            for i in range(len(SENSOR_NAMES)):
                lines[f'raw_{i}'].set_ydata(raw_data_deques[i])
                lines[f'smooth_{i}'].set_ydata(smoothed_data_deques[i])

            # อัปเดตกราฟรวม
            for i in range(len(SENSOR_NAMES)):
                lines[f'combined_{i}'].set_ydata(smoothed_data_deques[i])

            # สั่งให้วาดใหม่ทั้งหมด
            fig.canvas.draw()
            fig.canvas.flush_events()

            # แสดงผลใน Terminal
            print(f"[{timestamp}] Raw: [{voltages[0]:.2f}, {voltages[1]:.2f}, {voltages[2]:.2f}] V | Smoothed: [{smoothed_voltages[0]:.2f}, {smoothed_voltages[1]:.2f}, {smoothed_voltages[2]:.2f}] V")

            # หน่วงเวลา
            time.sleep(SAMPLING_INTERVAL_S)

except KeyboardInterrupt:
    print("\nผู้ใช้สั่งหยุดโปรแกรม...")
finally:
    plt.ioff()
    print("โปรแกรมหยุดทำงานเรียบร้อยแล้ว")
    # ทำให้กราฟค้างไว้เมื่อจบโปรแกรม
    print("กดปิดหน้าต่างกราฟเพื่อจบการทำงานอย่างสมบูรณ์")
    plt.show()