#เปิดกล้องด้วย OpenCV
import cv2

cam = cv2.VideoCapture(0)  # 0 for the default camera
while (cam.isOpened()):  # Check if the camera is opened
    ref,frame  = cam.read()  # Capture frame-by-frame

    if ref == True:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert the frame to grayscale
        cv2.imshow("output",gray)
        if cv2.waitKey(1) & 0xFF == ord("e"):  # Press 'e' to exit
            break
    else : 
        break

cam.release()  # Release the camera
cv2.destroyAllWindows()  # Close all OpenCV windows