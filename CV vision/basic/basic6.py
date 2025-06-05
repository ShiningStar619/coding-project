import cv2

cap = cv2.VideoCapture(0)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

while (cap.isOpened()):
    ret, frame = cap.read()
    if ret == True:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the frame 
        scaleFactor = 1.2
        minNeighbors = 5
        face_detect = face_cascade.detectMultiScale(gray, scaleFactor, minNeighbors)
        for (x,y,w,h) in face_detect:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), thickness=5)
            cv2.imshow('frame', frame)  

        if cv2.waitKey(1) & 0xFF == ord('e'):
            break
    else:
        break
cap.release()
cv2.destroyAllWindows()
