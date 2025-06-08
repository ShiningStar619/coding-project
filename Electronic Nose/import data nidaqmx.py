# ===================================================================
#   Cyclic Multi-Sensor Reader (60s Work @ 100Hz / 30s Rest)
# ===================================================================
import nidaqmx
import matplotlib.pyplot as plt
from collections import deque
import numpy as np
import time
import csv
from datetime import datetime

# parameters
DAQ_CHANNELS = "Dev1/ai0:2"
LOG_FILE = "sensor_log_cyclic.csv"
SENSOR_NAMES = ["Voltage(MQ-3b)", "Voltage(MQ-3)", "Voltage(MQ-9B)"]
SAMPLING_RATE_HZ = 100
SAMPLES_PER_CHUNK = 100
ACTIVE_DURATION_S = 60
REST_DURATION_S = 30
MAX_GRAPH_POINTS = 500

# csv header
csv_header = ["Timestamp"] + SENSOR_NAMES
try:
    with open(LOG_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(csv_header)
    print(f"ไฟล์ CSV '{LOG_FILE}' ถูกสร้างและพร้อมสำหรับบันทึกข้อมูล")
except IOError as e:
    print(f"ไม่สามารถเขียนไฟล์ CSV ได้: {e}")
    exit()

# graph setup
data_deques = [deque([0] * MAX_GRAPH_POINTS, maxlen=MAX_GRAPH_POINTS) for _ in range(len(SENSOR_NAMES))]
plt.ion()
fig, ax = plt.subplots(figsize=(12, 7))
lines = []
colors = ['dodgerblue', 'red', 'green']
for i in range(len(SENSOR_NAMES)):
    line, = ax.plot(np.arange(MAX_GRAPH_POINTS), data_deques[i], color=colors[i], label=SENSOR_NAMES[i])
    lines.append(line)
ax.set_ylim(0, 5)
ax.set_title("Real-Time Sensor Readings (Cyclic: 60s Work / 30s Rest)", fontsize=16)
ax.set_ylabel("Voltage (V)")
ax.set_xlabel("Samples")
ax.legend()
ax.grid(True)
print("กราฟพร้อมสำหรับการแสดงผล...")

# Loop การทำงานหลักแบบ Cyclic 
cycle_count = 0
try:
    while True:
        cycle_count += 1
        print(f"\n===== เริ่มรอบการทำงานที่ {cycle_count} (ทำงาน {ACTIVE_DURATION_S} วินาที @ {SAMPLING_RATE_HZ}Hz) =====")

        # ===================================
        #   ส่วนที่ 1: ช่วงทำงาน (Active Phase)
        # ===================================
        with nidaqmx.Task() as task:
            task.ai_channels.add_ai_voltage_chan(DAQ_CHANNELS, min_val=0.0, max_val=5.0)
            task.timing.cfg_samp_clk_timing(rate=SAMPLING_RATE_HZ, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
            
            num_chunks_to_read = int((ACTIVE_DURATION_S * SAMPLING_RATE_HZ) / SAMPLES_PER_CHUNK)

            for i in range(num_chunks_to_read):
                data_chunk = task.read(number_of_samples_per_channel=SAMPLES_PER_CHUNK)
                
                # เปลี่ยนโครงสร้างข้อมูลเพื่อความสะดวก
                # จาก [[s1,s1...], [s2,s2...]] เป็น [[s1,s2,s3], [s1,s2,s3]...]
                processed_chunk = np.array(data_chunk).T.tolist()

                for voltages in processed_chunk:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                    with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerow([timestamp] + voltages)
                    for sensor_idx in range(len(SENSOR_NAMES)):
                        data_deques[sensor_idx].append(voltages[sensor_idx])
                
                for sensor_idx in range(len(SENSOR_NAMES)):
                    lines[sensor_idx].set_ydata(data_deques[sensor_idx])
                fig.canvas.draw()
                fig.canvas.flush_events()
                
                print(f"  รอบที่ {cycle_count}: กำลังเก็บข้อมูล... {((i + 1) * SAMPLES_PER_CHUNK) / SAMPLING_RATE_HZ:.0f} / {ACTIVE_DURATION_S} วินาที")
        
        # ==================================
        #   ส่วนที่ 2: ช่วงพัก (Rest Phase)
        # ==================================
        print(f"===== รอบที่ {cycle_count}: เข้าสู่ช่วงพัก {REST_DURATION_S} วินาที =====")
        for remaining_time in range(REST_DURATION_S, 0, -1):
            print(f"  พัก... เหลือเวลาอีก {remaining_time} วินาที")
            time.sleep(1)

except KeyboardInterrupt:
    print("\nผู้ใช้สั่งหยุดโปรแกรม...")
except Exception as e:
    print(f"\nเกิดข้อผิดพลาด: {e}")
finally:
    plt.ioff()
    print("โปรแกรมหยุดทำงานเรียบร้อยแล้ว")
    plt.show()