import cv2
import os
import numpy as np

# --- การตั้งค่าที่ปรับได้ ---
IMAGE_PATH = 'D:/year 5/coding project/CV vision/dataset/raw data/1_before_preparation/good/เมล็ดดีเรียวยาว/JPG/เมล็ดดีเรียวยาว_JPG(4).JPG' 
OUTPUT_FOLDER = 'D:/year 5/coding project/CV vision/dataset/raw data/2_after_preparation/good/เมล็ดดีเรียวยาว/set 3'
MIN_SEED_AREA = 150                 # ขนาดพื้นที่ขั้นต่ำของเมล็ด (Pixel) เพื่อกรอง Noise
PADDING = 120                        # ระยะขอบ (padding) ที่จะเพิ่มรอบๆ เมล็ด (pixel)

try:
    with open(IMAGE_PATH, 'rb') as f:
        nparr = np.frombuffer(f.read(), np.uint8)
        original_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
except FileNotFoundError:
    print(f"หาไฟล์ไม่เจอ: {IMAGE_PATH}")
    exit()

gray_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)

blurred_image = cv2.GaussianBlur(gray_image, (7, 7), 0)
binary_image = cv2.adaptiveThreshold(blurred_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,  cv2.THRESH_BINARY_INV, 15, 4)

kernel = np.ones((3, 3), np.uint8)
eroded_image = cv2.erode(binary_image, kernel, iterations=1)
dilated_image = cv2.dilate(eroded_image, kernel, iterations=1)

# 5. ค้นหา Contours (รูปร่างของเมล็ด)
contours, _ = cv2.findContours(dilated_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
print(f"ตรวจพบวัตถุเบื้องต้น {len(contours)} ชิ้น...")

# 6. วนลูปเพื่อตัดและบันทึกแต่ละเมล็ด
saved_count = 0
for contour in contours:
    # กรองวัตถุที่มีขนาดเล็กเกินไปออก
    if cv2.contourArea(contour) > MIN_SEED_AREA:
        # คำนวณกรอบสี่เหลี่ยมรอบวัตถุ (Bounding Box)
        x, y, w, h = cv2.boundingRect(contour)

        y1 = max(0, y - PADDING)
        y2 = min(original_image.shape[0], y + h + PADDING)
        x1 = max(0, x - PADDING)
        x2 = min(original_image.shape[1], x + w + PADDING)

        cropped_seed = original_image[y1:y2, x1:x2]

        # บันทึกไฟล์ภาพที่ตัดแล้ว
        saved_count += 1
        output_path = os.path.join(OUTPUT_FOLDER, f'เมล็ดดีเรียวยาว_{saved_count}.jpg') #กำหนดชื่อไฟล์ที่จะ save
        is_success, im_buf_arr = cv2.imencode(".jpg", cropped_seed)
        im_buf_arr.tofile(output_path)

print(f"ดำเนินการเสร็จสิ้น! บันทึกเมล็ดพืชแล้ว {saved_count} รูป ในโฟลเดอร์ '{OUTPUT_FOLDER}'")

cv2.namedWindow("1. Original Image", cv2.WINDOW_NORMAL)
cv2.namedWindow("2. Grayscale Image", cv2.WINDOW_NORMAL)
cv2.namedWindow("3. Final Binary Image (What the computer sees)", cv2.WINDOW_NORMAL)

cv2.imshow("1. Original Image", original_image)
cv2.imshow("2. Grayscale Image", gray_image)
cv2.imshow("3. Final Binary Image (What the computer sees)", dilated_image)
cv2.waitKey(0)  
cv2.destroyAllWindows()