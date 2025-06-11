# function list
# 1. ทำงานเป็นเวลา 60s ที่ความเร็วในการเก็บข้อมูล 100 hz และพัก 30s และบันทึกค่า(1)
# 2. หลังจากทำงานครบ 60s ที่การ smoothing (moving average) และบันทักค่า(2)
# 3. แสดงข้อมูลเปรียบเทียบก่อนและหลัง smoothing โดยกา่ร plot graph


#import package
import nidaqmx
import matplotlib.pyplot as plt
import nidaqmx.constants
import numpy as np
import time
import csv
from datetime import datetime
import pandas as pd

#setting parameter
Daq_channels = "Dev1/ai0:2" #กำหนด channel connecting
raw_file = "sensor_raw.csv"
smoothed_file = "sensor_smoothed.csv"
sensor_name = ["voltage(MQ-3b)", "voltage(MQ-3)", "voltage(MQ-9b)"]

#setting data collection
sampling_rate = 100 #hz
sampling_per_chuck = 100 #จำนวนการเก็บข้อมูล/รอบ
active_duration = 60 #sec
rest_duration = 30 #sec

#setting smoothing parameter
smoothing_window_size = 15 #จำนวนข้อมูลที่นำมาคำนวนข้อมูลที่จะทำ smoothing

#function processing
def process_and_save_data(raw_data_list, header):
    print("  [Processing] กำลังทำการ Smoothing ข้อมูล...")
    df = pd.DataFrame(raw_data_list, columns= header)
    df_for_smoothing = df.drop(columns=['timestamp'])
    
    for name in sensor_name: # เปลี่ยนชื่อตัวแปรใน loop เพื่อไม่ให้ซ้ำกับ list
        smoothed_col_name = f"smoothed_{name}"
        df[smoothed_col_name] = df_for_smoothing[name].rolling(window=smoothing_window_size, center=True).mean()

    df.to_csv(smoothed_file, index=False, encoding='utf-8') #บันทึกไฟล์ smoothing แล้ว
    print(f"  [Processing] บันทึกข้อมูลที่ปรับเรียบร้อยแล้วลงใน '{smoothed_file}'")
    plot_comparison(df)

#function plot graph
def plot_comparison(df):
    print("  [Processing] กำลังสร้างกราฟเปรียบเทียบ...")
    fig, axes = plt.subplots(len(sensor_name), 1, figsize=(15, 12), sharex=True)
    fig.suptitle('Compare data: raw data vs smoothed data', fontsize=16)
    colors = ['blue', 'red', 'green']

    # ตรวจสอบว่ามีแกนกราฟหลายอันหรือไม่
    ax_list = axes if isinstance(axes, np.ndarray) else [axes]

    for i , name in enumerate(sensor_name):
        ax = ax_list[i]
        smoothed_col_name = f"smoothed_{name}"
        ax.plot(df.index, df[name], color=colors[i], alpha=0.4, label=f'Raw {name}')
        ax.plot(df.index, df[smoothed_col_name], color=colors[i], linewidth = 2, label=f'Smoothed {name}')
        ax.set_ylabel("voltage(V)")
        ax.legend()
        ax.grid(True)
    
    ax_list[-1].set_xlabel("Sample Index")
    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    plt.show()

#prepare loop
csv_header = ["timestamp"] + sensor_name
try:
    with open(raw_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(csv_header)
    print(f"ไฟล์ CSV '{raw_file}' ถูกสร้างและพร้อมสำหรับบันทึกข้อมูลดิบแล้ว")
except IOError as e:
    print(f"ไม่สามารถเขียนไฟล์ได้ : {e}")
    exit()

# loop
cycle_count = 0 
try: 
    while True:
        cycle_count += 1 
        print(f"\n===== เริ่มรอบการทำงานที่ {cycle_count} (ทำงาน {active_duration} วินาที @ {sampling_rate}Hz) =====")

        #active phase 60sec
        raw_data_for_processing = []
        
        with nidaqmx.Task() as task:
            task.ai_channels.add_ai_voltage_chan(Daq_channels, min_val=0.0, max_val=5.0)
            task.timing.cfg_samp_clk_timing(rate=sampling_rate, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
            num_chuck_to_read = int((active_duration*sampling_rate)/sampling_per_chuck)

            for i in range(num_chuck_to_read):
                data_chuck = task.read(number_of_samples_per_channel=sampling_per_chuck)
                processed_chunk = np.array(data_chuck).T.tolist()

                with open(raw_file, mode='a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    for voltages in processed_chunk:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                        data_row = [timestamp] + voltages
                        writer.writerow(data_row)
                        raw_data_for_processing.append(data_row)
                print(f"  รอบที่ {cycle_count}: กำลังเก็บข้อมูล... {((i + 1) * sampling_per_chuck) / sampling_rate:.0f} / {active_duration} วินาที")
        
        # calculation
        if raw_data_for_processing:
            process_and_save_data(raw_data_for_processing, header=csv_header) 

        #rest phase 30s
        print(f"===== รอบที่ {cycle_count}: เข้าสู่ช่วงพัก {rest_duration} วินาที =====")
        for remaining_time in range(rest_duration, 0, -1):
            print(f"  พัก... เหลือเวลาอีก {remaining_time} วินาที") 
            time.sleep(1)

except KeyboardInterrupt:
    print("\nผู้ใช้สั่งหยุดโปรแกรม...")
except Exception as e: 
    print(f"\nเกิดข้อผิดพลาด: {e}")
finally: 
    print("โปรแกรมหยุดทำงานเรียบร้อยแล้ว")