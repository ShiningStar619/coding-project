# video capture
import cv2

cam = cv2.VideoCapture(0)  # 0 for the default camera
fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Define the codec

result = cv2.VideoWriter("output_demo.avi", fourcc, 30.0, (640, 480))  # Create a VideoWriter object



while (cam.isOpened()):  # Check if the camera is opened
    ref,frame  = cam.read()  # Capture frame-by-frame

    if ref == True:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert the frame to grayscale
        cv2.imshow("output", frame)  # Show the original frame
        result.write(frame)

        if cv2.waitKey(1) & 0xFF == ord("e"):  # Press 'e' to exit
            break
    
result.release
cam.release()  # Release the camera
cv2.destroyAllWindows()  # Close all OpenCV windows