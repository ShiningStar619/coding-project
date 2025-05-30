#การเขียนภาพ
import cv2
import os
path = "d:/year 5/coding project/CV vision/archive/256_ObjectCategories/001.ak47/001_0002.jpg"
print("ไฟล์มีหรือไม่:", os.path.exists(path))
img = cv2.imread(path, 0)
imsize = cv2.resize(img, (500, 300))
#cv2.imshow("output", img)
cv2.imshow("output", imsize)
cv2.waitKey(5000)
cv2.destroyAllWindows()

cv2.imwrite("output_copy.jpg", imsize)