import serial
import time
import csv
from datetime import datetime
import os

# --- การตั้งค่า (สามารถปรับเปลี่ยนได้) ---
SERIAL_PORT = 'COM4'
BAUD_RATE = 9600
CSV_FILE_NAME = 'weight_log.csv'
LOG_INTERVAL_SECONDS = 10 # 1 นาที

# ตัวแปรใหม่: ตำแหน่งทศนิยมของน้ำหนัก (จากข้อมูล 000653 -> 0.653)
DECIMAL_PLACES = 3

# --- จบส่วนการตั้งค่า ---

def parse_weight_data(raw_data_bytes):
    """
    (***แก้ไขครั้งที่ 2***)
    ฟังก์ชันสำหรับแปลงข้อมูลดิบจากตาชั่ง b'\x02+p!000653000000\r'
    ให้กลายเป็นตัวเลขน้ำหนัก (เช่น 0.653)
    """
    try:
        # แปลง bytes เป็น string เราจะไม่ใช้ strip() แล้วเพราะไม่จำเป็น
        data_string = raw_data_bytes.decode('ascii')

        # แก้ไขตำแหน่งการตัด string จาก [3:9] เป็น [4:10]
        # เพื่อให้ได้เฉพาะส่วนตัวเลข '000653'
        weight_str = data_string[4:10] # <--- จุดที่แก้ไข

        # แปลง string '000653' เป็นตัวเลขจำนวนเต็ม 653
        weight_int = int(weight_str)

        # เติมจุดทศนิยมตามที่ตั้งค่าไว้
        final_weight = weight_int / (10 ** DECIMAL_PLACES)
        
        return final_weight
    except (ValueError, IndexError, UnicodeDecodeError) as e:
        print(f"เกิดข้อผิดพลาดในการแยกข้อมูล: {raw_data_bytes} -> {e}")
        return None

def main():
    file_exists = os.path.isfile(CSV_FILE_NAME)

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
        print(f"เชื่อมต่อกับพอร์ตอนุกรม {SERIAL_PORT} สำเร็จแล้ว")

        if not file_exists:
            with open(CSV_FILE_NAME, mode='w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(['timestamp', 'weight_kg'])
            print(f"สร้างไฟล์ {CSV_FILE_NAME} และเขียนหัวข้อตารางเรียบร้อย")

        last_log_time = time.time()
        print("เริ่มต้นการอ่านและบันทึกข้อมูลน้ำหนัก...")

        while True:
            # (***แก้ไขใหม่***)
            # อ่านข้อมูลจนกว่าจะเจอตัวจบสัญญาณ '\r'
            raw_line = ser.read_until(b'\r')

            if raw_line:
                weight = parse_weight_data(raw_line)
                if weight is not None:
                    print(f"อ่านค่าน้ำหนักล่าสุด: {weight:.3f} kg")
                    
                    # ตรวจสอบว่าถึงเวลาที่ต้องบันทึกข้อมูลแล้วหรือยัง
                    if time.time() - last_log_time >= LOG_INTERVAL_SECONDS:
                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        with open(CSV_FILE_NAME, mode='a', newline='') as csv_file:
                            csv_writer = csv.writer(csv_file)
                            csv_writer.writerow([timestamp, weight])
                        
                        print(f"--- บันทึกข้อมูลสำเร็จ: {timestamp}, {weight:.3f} kg ---")
                        last_log_time = time.time()

    except serial.SerialException as e:
        print(f"เกิดข้อผิดพลาด: ไม่สามารถเปิดพอร์ตอนุกรม {SERIAL_PORT} ได้: {e}")
    except KeyboardInterrupt:
        print("\nหยุดการทำงานของโปรแกรม")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("ปิดการเชื่อมต่อพอร์ตอนุกรมแล้ว")

if __name__ == '__main__':
    main()