import cv2
import matplotlib.pyplot as plt
gray_img = cv2.imread("CV vision/basic/archive/256_ObjectCategories/004.baseball-bat/004_0107.jpg", cv2.IMREAD_GRAYSCALE) 

thresh, th1 = cv2.threshold(gray_img,128,255,cv2.THRESH_BINARY)
thresh, th2 = cv2.threshold(gray_img,128,255,cv2.THRESH_BINARY_INV)
thresh, th3 = cv2.threshold(gray_img,128,255,cv2.THRESH_TRUNC)
thresh, th4 = cv2.threshold(gray_img,128,255,cv2.THRESH_TOZERO)
thresh, th5 = cv2.threshold(gray_img,128,255,cv2.THRESH_TOZERO_INV)

#cv2.imshow("Original Image", gray_img)
#cv2.imshow("Binary Threshold", th1)
#cv2.imshow("Binary Inverted Threshold", th2)
#cv2.imshow("Truncated Threshold", th3)
#cv2.imshow("To Zero Threshold", th4)
#cv2.imshow("To Zero Inverted Threshold", th5)
images = [gray_img, th1, th2, th3, th4, th5]
titles = ['Original Image', 'Binary Threshold', 'Binary Inverted Threshold', 'Truncated Threshold', 'To Zero Threshold', 'To Zero Inverted Threshold']

for i in range(len(images)):
    plt.subplot(2,3,i+1)
    plt.imshow(images[i])
    plt.title(titles[i])
    plt.xticks([]), plt.yticks([])
    
plt.show()
