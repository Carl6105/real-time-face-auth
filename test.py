import cv2

cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imshow("Test Camera", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
        break
cap.release()
cv2.destroyAllWindows()