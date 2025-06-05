import cv2
import matplotlib.pyplot as plt

img = cv2.imread("CV vision/basic/archive/256_ObjectCategories/004.baseball-bat/004_0107.jpg")
#cv2.imshow("image", img)

plt.imshow(img)
plt.show

#cv2.waitKey(0)
#cv2.destroyAllWindows()