import cv2
import numpy as np
import os

# --- พารามิเตอร์ ---
# Tip: เปลี่ยนชื่อตัวแปร input เป็นชื่อที่สื่อความหมายมากขึ้น
input_filename = "short&round_1.JPG"
output_folder = "Testing"

# --- ฟังก์ชันการทำงาน ---
print("start processing")
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    print(f"genertate folder :'{output_folder}'")

# ใช้ตัวแปรใหม่ในการอ่านไฟล์
origin = cv2.imread(input_filename)
if origin is None:
    print(f"!error reading '{input_filename}'")
    print("pls input your file in a same folder")
else:
    # ==========================================================
    # Correction 1: โค้ดทั้งหมดต่อจากนี้ต้องอยู่ภายใต้ else
    # ==========================================================
    print(f"load '{input_filename}' complete... prepare for process")
    final_result = origin.copy()

    #gray scale + Enhanced
    gray_img = cv2.cvtColor(origin, cv2.COLOR_BGR2GRAY)
    enhanced_img = cv2.equalizeHist(gray_img)
    print(' ...config img quality (Enhanced image) 👍 ')

    #Segmentation
    ret, mask = cv2.threshold(enhanced_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    print("Mask complete")

    #find & crop img
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"finding mask {len(contours)} objects")

    #Features
    object_count = 0
    for contour in contours:
        # ==========================================================
        # Correction 2: ใช้ตัวแปร 'contour' (เอกพจน์) ในฟังก์ชันนี้
        # ==========================================================
        if cv2.contourArea(contour) > 100: #if area img > 100pixel can continue
            x, y, w, h = cv2.boundingRect(contour)
            cropped_object = origin[y:y+h, x:x+w]
            output_path = os.path.join(output_folder, f"seed_{object_count}.jpg")
            cv2.imwrite(output_path, cropped_object)
            cv2.rectangle(final_result, (x,y), (x+w, y+h), (0, 255, 0), 2)
            object_count += 1
            
    # Tip: ย้าย print ออกมานอก loop เพื่อสรุปผลครั้งเดียว
    print(f"crop and save img {object_count} images in '{output_folder}' 👌")

    #display & clearup
    final_result_text = final_result.copy()
    cv2.putText(final_result_text, f"Found {object_count} seeds", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("1.Original img", origin)
    cv2.imshow("2.Enhanced img", enhanced_img)
    cv2.imshow("3.Mask", mask)
    cv2.imshow("4.Final result", final_result_text)

    print("\n--- all process is complete")
    print("all img is save")
    print("Press any button on the image window to close all programs.")

    cv2.waitKey(0)
    cv2.destroyAllWindows()