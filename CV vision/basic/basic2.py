import cv2

# โหลดภาพ
img = cv2.imread("CV vision/archive/256_ObjectCategories/001.ak47/001_0001.jpg",0)  # 0 หมายถึงโหลดเป็นภาพขาวดำ

# ตรวจสอบว่าภาพโหลดได้ไหม
if img is None:
    print("ไม่สามารถโหลดภาพได้")
else:
    # ย่อขนาดภาพ
    imgresize = cv2.resize(img, (500, 300))

    # แสดงภาพ
    cv2.imshow("output", imgresize)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
