import cv2
import numpy as np
import os
#parameter
input = '_DSC0156.JPG'
output_folder = 'เมล็ดดีสั้นกลม'

#funtions
print("start processing")
if not os.path.exists(output_folder ):
    os.makedirs(output_folder )
    print(f"genertate folder :'{output_folder }")

origin = cv2.imread(input)
if origin is None:
    print(f"!error '{input}")
    print("pls input your file in a same folder")
else:
    print(f"load '{input}' complete... prepare for process")
    final_result=origin.copy()

    #gray scale + Enhanced
    gray_img = cv2.cvtColor(origin, cv2.COLOR_BGR2GRAY)
    enhanced_img = cv2.equalizeHist(gray_img)
    print(' ...comfig img quaity (Enhanced image) 👍 ')

    #Segmentation
    ret, mask = cv2.threshold(enhanced_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU) #// THRESH_BINART is black,white , THRESH_OTSU is auto-mode for find point of division between object and background
    print("Mask complete")

    #find & crop img
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"finding mask {len(contours)}")

#Features
object_count = 0
for contour in contours:
    if cv2.contourArea(contours) > 100: #if area img > 100pixel can continue
        x, y, w, h = cv2.boundingRect(contour)
        cropped_object = origin[y:y+h, x:x+w]
        output_path = os.path.join(output_folder, f"seed_{object_count}.jpg")
        cv2.imwrite(output_path, cropped_object)
        cv2.rectangle(final_result, (x,y), (x+w, y+h), (0, 255, 0), 2)
        object_count += 1
    print(f" crop and save img {object_count}.jpg in '{output_folder}' 👌")

#display & clearup
final_result_text = final_result.copy()
cv2.putText(final_result_text, f"Found {object_count} seeds", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
cv2.imshow("1.Original img", origin)
cv2.imshow("2.Enhanced img", enhanced_img)
cv2.imshow("3.Mask", mask)
cv2.imshow("4.Final result", final_result_text)

print("\n--- all procees is complete")
print("all img is save")
print("Press any button on the image window to close all programs.")

cv2.waitKey(0)
cv2.destroyAllWindows()