# ===================================================================
#   Final Integrated Code: Cyclic DAQ with Post-Cycle Smoothing
#   - Acquires data for 60s @ 100Hz, rests for 30s.
#   - After each acquisition cycle, it smooths the data,
#     saves it to a new file, and plots a comparison graph.
# ===================================================================

# 1. Import ไลบรารีที่จำเป็นทั้งหมด
import nidaqmx
import matplotlib.pyplot as plt
import numpy as np
import time
import csv
from datetime import datetime
import pandas as pd

# ===================================================================
# 2. ส่วนของการตั้งค่า (Configuration)
# ===================================================================
# การตั้งค่าอุปกรณ์และไฟล์
DAQ_CHANNELS = "Dev1/ai0:2"
RAW_LOG_FILE = "sensor_log_cyclic_raw.csv"
SMOOTHED_LOG_FILE = "sensor_log_smoothed.csv"
SENSOR_NAMES = ["Voltage(MQ-3b)", "Voltage(MQ-3)", "Voltage(MQ-9B)"]

# การตั้งค่าการเก็บข้อมูล
SAMPLING_RATE_HZ = 100
SAMPLES_PER_CHUNK = 100
ACTIVE_DURATION_S = 60
REST_DURATION_S = 30

# การตั้งค่า Smoothing
SMOOTHING_WINDOW_SIZE = 15

# ===================================================================
# 3. ฟังก์ชันสำหรับประมวลผลข้อมูล
# ===================================================================
def process_and_save_data(raw_data_list, header):
    print("  [Processing] กำลังทำ Smoothing ข้อมูล...")
    df = pd.DataFrame(raw_data_list, columns=header)
    df_for_smoothing = df.drop(columns=['Timestamp'])
    for sensor_name in SENSOR_NAMES:
        smoothed_col_name = f"Smoothed_{sensor_name}"
        df[smoothed_col_name] = df_for_smoothing[sensor_name].rolling(window=SMOOTHING_WINDOW_SIZE, center=True).mean()
    df.to_csv(SMOOTHED_LOG_FILE, index=False, encoding='utf-8')
    print(f"  [Processing] บันทึกข้อมูลที่ปรับเรียบแล้วลงในไฟล์ '{SMOOTHED_LOG_FILE}'")
    plot_comparison(df)

def plot_comparison(df):
    print("  [Processing] กำลังสร้างกราฟเปรียบเทียบ...")
    fig, axes = plt.subplots(len(SENSOR_NAMES), 1, figsize=(15, 12), sharex=True)
    fig.suptitle('Comparison: Raw Data vs. Smoothed Data', fontsize=16)
    colors = ['dodgerblue', 'red', 'green']
    for i, sensor_name in enumerate(SENSOR_NAMES):
        ax = axes[i]
        smoothed_col_name = f"Smoothed_{sensor_name}"
        ax.plot(df.index, df[sensor_name], color=colors[i], alpha=0.4, label=f'Raw {sensor_name}')
        ax.plot(df.index, df[smoothed_col_name], color=colors[i], linewidth=2, label=f'Smoothed {sensor_name}')
        ax.set_ylabel("Voltage (V)")
        ax.legend()
        ax.grid(True)
    axes[-1].set_xlabel("Sample Index")
    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    plt.show()

# ===================================================================
# 4. ส่วนเตรียมการก่อนเริ่ม Loop หลัก
# ===================================================================
csv_header = ["Timestamp"] + SENSOR_NAMES
try:
    with open(RAW_LOG_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(csv_header)
    print(f"ไฟล์ CSV '{RAW_LOG_FILE}' ถูกสร้างและพร้อมสำหรับบันทึกข้อมูลดิบ")
except IOError as e:
    print(f"ไม่สามารถเขียนไฟล์ CSV ได้: {e}")
    exit()

# ===================================================================
# 5. Loop การทำงานหลักแบบ Cyclic
# ===================================================================
cycle_count = 0
try:
    while True:
        cycle_count += 1
        print(f"\n===== เริ่มรอบการทำงานที่ {cycle_count} (ทำงาน {ACTIVE_DURATION_S} วินาที @ {SAMPLING_RATE_HZ}Hz) =====")
        
        raw_data_for_processing = []
        with nidaqmx.Task() as task:
            task.ai_channels.add_ai_voltage_chan(DAQ_CHANNELS, min_val=0.0, max_val=5.0)
            task.timing.cfg_samp_clk_timing(rate=SAMPLING_RATE_HZ, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
            num_chunks_to_read = int((ACTIVE_DURATION_S * SAMPLING_RATE_HZ) / SAMPLES_PER_CHUNK)
            for i in range(num_chunks_to_read):
                data_chunk = task.read(number_of_samples_per_channel=SAMPLES_PER_CHUNK)
                processed_chunk = np.array(data_chunk).T.tolist()
                with open(RAW_LOG_FILE, mode='a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    for voltages in processed_chunk:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                        data_row = [timestamp] + voltages
                        writer.writerow(data_row)
                        raw_data_for_processing.append(data_row)
                print(f"  รอบที่ {cycle_count}: กำลังเก็บข้อมูล... {((i + 1) * SAMPLES_PER_CHUNK) / SAMPLING_RATE_HZ:.0f} / {ACTIVE_DURATION_S} วินาที")
        
        if raw_data_for_processing:
            process_and_save_data(raw_data_for_processing, header=csv_header)
        
        print(f"===== รอบที่ {cycle_count}: เข้าสู่ช่วงพัก {REST_DURATION_S} วินาที =====")
        for remaining_time in range(REST_DURATION_S, 0, -1):
            print(f"  พัก... เหลือเวลาอีก {remaining_time} วินาที")
            time.sleep(1)
            
except KeyboardInterrupt:
    print("\nผู้ใช้สั่งหยุดโปรแกรม...")
except Exception as e:
    print(f"\nเกิดข้อผิดพลาด: {e}")
finally:
    print("โปรแกรมหยุดทำงานเรียบร้อยแล้ว")