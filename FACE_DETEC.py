import cv2
face_model = cv2.CascadeClassifier('/root/Desktop/workspace/TARP/haarcascade_frontalface_default.xml')

cam = cv2.VideoCapture(0)
i = 0

while i<500:
#while True:
    ret, photo = cam.read()
    gphoto = cv2.cvtColor(photo, cv2.COLOR_BGR2GRAY)
    location = face_model.detectMultiScale(gphoto)
    
    if len(location) != 0:
        x1 = location[0][0]
        y1 = location[0][1]
        x2 = location[0][2] + x1
        y2 = location[0][3] + y1
        
        cv2.rectangle(photo, (x1, y1), (x2, y2), (0,255,255),2)
        cv2.imshow('live', photo)
        if cv2.waitKey(1)==13:
            break
        
        if i<=400:
            fphoto = gphoto[x1-70:x2,y1:y2+60]
            
            cv2.imwrite('/root/Desktop/workspace/TARP/images/ishita_{}.png'.format(i), fphoto)
        i += 1
    
           
    else:
        cv2.imshow('live', photo)
        if cv2.waitKey(1)==13:
            break
            
cv2.destroyAllWindows()
cam.release()
