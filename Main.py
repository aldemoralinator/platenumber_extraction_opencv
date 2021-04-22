# Main.py

import cv2
import numpy as np
import os

import DetectChars
import DetectPlates
import PossiblePlate 

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore 

import picamera
import time
import io

from datetime import datetime


SCALAR_BLACK = (0.0, 0.0, 0.0)
SCALAR_WHITE = (255.0, 255.0, 255.0)
SCALAR_YELLOW = (0.0, 255.0, 255.0)
SCALAR_GREEN = (0.0, 255.0, 0.0)
SCALAR_RED = (0.0, 0.0, 255.0)

showSteps = False

registeredPlateNumbers = []

# DB = None

class RegisteredPlateNumber:
 
    def __init__(
        self, 
        address, 
        brand, 
        color, 
        contactNumber, 
        email, 
        imgUrl, 
        lastDetected, 
        lastDetectedLocation, 
        model, 
        owner,
        plateNumber,
        registeredDate,
        status ):
        self.address = address 
        self.brand = brand 
        self.color = color 
        self.contactNumber = contactNumber 
        self.email = email 
        self.imgUrl = imgUrl 
        self.lastDetected = lastDetected 
        self.lastDetectedLocation = lastDetectedLocation
        self.model = model 
        self.owner = owner 
        self.plateNumber = plateNumber 
        self.registeredDate = registeredDate 
        self.status = status  

###################################################################################################
def main():

    cred = credentials.Certificate("./platenumbermobile-firebase-adminsdk-q15ir-6d4f05f68b.json")
    firebase_admin.initialize_app(cred)

    DB = firestore.client()

    platenumber_ref = DB.collection(u'platenumber')
    docs = platenumber_ref.stream()

    for doc in docs:
        DetectChars.listOfRegisteredPlates.append(str(doc.id))
        
        newRegisteredPlateNumber = RegisteredPlateNumber( 
            doc.get("address"), 
            doc.get("brand"), 
            doc.get("color"), 
            doc.get("contactNumber"), 
            doc.get("email"), 
            doc.get("imgUrl"), 
            doc.get("lastDetected"), 
            doc.get("lastDetectedLocation"), 
            doc.get("model"), 
            doc.get("owner"),
            doc.get("plateNumber"),
            doc.get("registeredDate"),
            doc.get("status") 
        )
        registeredPlateNumbers.append(newRegisteredPlateNumber) 
         
    try:
        with picamera.PiCamera() as camera: 
            camera.rotation = 180
            camera.resolution = (1000, 750)

            detectByPiCamera(camera, DB) 
    except:
        print("program stopped")
        return

    return

def find(arr, id):
    for x in arr:
        if x["plateNumber"] == id:
            return x

def detectByPiCamera(camera, DB):
 
    stream = io.BytesIO()
    camera.capture(stream, format='jpeg', use_video_port=True)
    data = np.frombuffer(stream.getvalue(), dtype=np.uint8)
    img = cv2.imdecode(data, 1)

    platenumbers = extractPlateNumber(img)  
    print("  location: Marilao, Bulacan    time: " + str(datetime.now()) + "\n")   

    if len(platenumbers) < 1:
        print("  none detected...")

    for platenumber in platenumbers:
        doc_ref = DB.collection(u'platenumber').document(str(platenumber.strChars))
        doc_ref.update({
            u'lastDetectedLocation': u'Marilao, Bulacan',
            u'lastDetected': firestore.SERVER_TIMESTAMP
        })

        for registeredPlateNumber in registeredPlateNumbers:  
            if registeredPlateNumber.plateNumber == str(platenumber.strChars): 
                print("  .-------------------------------------------.")
                print("  |- detected plate: " + str(registeredPlateNumber.plateNumber) + " -----------------| ")
                print("  |-------------------------------------------|")
                print("  |- address: " + registeredPlateNumber.address) 
                print("  |- brand: " + registeredPlateNumber.brand) 
                print("  |- color: " + registeredPlateNumber.color) 
                print("  |- contactNumber: " + registeredPlateNumber.contactNumber) 
                print("  |- email: " + registeredPlateNumber.email) 
                # print("  |- imgUrl: " + registeredPlateNumber.imgUrl) 
                print("  |- lastDetected: " + str(datetime.now())) 
                print("  |- lastDetectedLocation: Marilao, Bulacan") 
                print("  |- model: " + registeredPlateNumber.model) 
                print("  |- owner: " + registeredPlateNumber.owner)
                print("  |- plateNumber: " + registeredPlateNumber.plateNumber)
                print("  |- registeredDate: " + str(registeredPlateNumber.registeredDate))
                print("  |- status: " + registeredPlateNumber.status)
                print("  .-------------------------------------------.") 
                print("\n")

        #    print('updated' + str(platenumber.strChars)) 

    print("\n")
    detectByPiCamera(camera, DB)

    return

def detectByImportingImage():
 
    DetectChars.listOfRegisteredPlates = ["NDV2275","NCH8591","A6F086","SGY514","UJY883","SAA7998","AKA8408","AAN4628","ZBA391","NAB6206"]
    # DetectChars.listOfRegisteredPlates = data + ["DAN5649","DCP4250","VDV402","XEW161","DAN3044","DAG7707","NCV5062", "DAG6675", "NAO5547", "DCP5626"]
    # DetectChars.listOfRegisteredPlates = ["NAG4598", "NDI9422", "NCV1423"]
    # DetectChars.listOfRegisteredPlates = ["WEH979", "NCJ5689", "NCW5742", "AAY6891", "NAS9380"]

    # imageList = ["car1.png","car2.png","car3.png","car4.png","car5.png","car6.png","car7.png","car8.png","car9.png","car10.png","car11.png","car12.png","car13.png","car14.png"]
    imageList = ["1.jpg", "2.jpg", "3.jpg", "4.jpg", "5.jpg", "6.jpg", "7.jpg", "8.jpg", "9.jpg","10.jpg"]
    # imageList = imageList + ["11.jpg", "12.jpg", "13.jpg", "14.jpg", "15.jpg", "16.jpg", "17.jpg"]
    # imageList = ["26.jpg"]

    masterListOfPossitiveDetectedPlateNumber = []
        
    for image in imageList:

        imgOriginalScene  = cv2.imread("LicPlateImages/G/" + image)

        if imgOriginalScene is None:
            print("error: image not read from file")
            continue 

        listOfPossitiveDetectedPlateNumber = extractPlateNumber(imgOriginalScene)
        for plateNumber in listOfPossitiveDetectedPlateNumber:
            masterListOfPossitiveDetectedPlateNumber.append(plateNumber)

    for platenumber in masterListOfPossitiveDetectedPlateNumber:
        print(platenumber.strChars)

    return

def extractPlateNumber(imgOriginalScene):
    
    listOfPossiblePlates = DetectPlates.detectPlatesInScene(imgOriginalScene)           # detect plates

    listOfPossiblePlates = DetectChars.detectCharsInPlates(listOfPossiblePlates)        # detect chars in plates

    listOfPossitiveDetectedPlateNumbers = []
    # plateCount = 0
    for possiblePlate in listOfPossiblePlates:
        # plateCount = plateCount + 1
        if len(possiblePlate.strChars) > 0:
            # print(possiblePlate.strChars)
            listOfPossitiveDetectedPlateNumbers.append(possiblePlate)

    return listOfPossitiveDetectedPlateNumbers

###################################################################################################
def drawRedRectangleAroundPlate(imgOriginalScene, licPlate):

    p2fRectPoints = cv2.boxPoints(licPlate.rrLocationOfPlateInScene)            # get 4 vertices of rotated rect

    cv2.line(imgOriginalScene, tuple(p2fRectPoints[0]), tuple(p2fRectPoints[1]), SCALAR_RED, 2)         # draw 4 red lines
    cv2.line(imgOriginalScene, tuple(p2fRectPoints[1]), tuple(p2fRectPoints[2]), SCALAR_RED, 2)
    cv2.line(imgOriginalScene, tuple(p2fRectPoints[2]), tuple(p2fRectPoints[3]), SCALAR_RED, 2)
    cv2.line(imgOriginalScene, tuple(p2fRectPoints[3]), tuple(p2fRectPoints[0]), SCALAR_RED, 2)
# end function

###################################################################################################
def writeLicensePlateCharsOnImage(imgOriginalScene, licPlate):
    ptCenterOfTextAreaX = 0                             # this will be the center of the area the text will be written to
    ptCenterOfTextAreaY = 0

    ptLowerLeftTextOriginX = 0                          # this will be the bottom left of the area that the text will be written to
    ptLowerLeftTextOriginY = 0

    sceneHeight, sceneWidth, sceneNumChannels = imgOriginalScene.shape
    plateHeight, plateWidth, plateNumChannels = licPlate.imgPlate.shape

    intFontFace = cv2.FONT_HERSHEY_SIMPLEX                      # choose a plain jane font
    fltFontScale = float(plateHeight) / 30.0                    # base font scale on height of plate area
    intFontThickness = int(round(fltFontScale * 1.5))           # base font thickness on font scale

    textSize, baseline = cv2.getTextSize(licPlate.strChars, intFontFace, fltFontScale, intFontThickness)        # call getTextSize

            # unpack roatated rect into center point, width and height, and angle
    ( (intPlateCenterX, intPlateCenterY), (intPlateWidth, intPlateHeight), fltCorrectionAngleInDeg ) = licPlate.rrLocationOfPlateInScene

    intPlateCenterX = int(intPlateCenterX)              # make sure center is an integer
    intPlateCenterY = int(intPlateCenterY)

    ptCenterOfTextAreaX = int(intPlateCenterX)         # the horizontal location of the text area is the same as the plate

    if intPlateCenterY < (sceneHeight * 0.75):                                                  # if the license plate is in the upper 3/4 of the image
        ptCenterOfTextAreaY = int(round(intPlateCenterY)) + int(round(plateHeight * 1.6))      # write the chars in below the plate
    else:                                                                                       # else if the license plate is in the lower 1/4 of the image
        ptCenterOfTextAreaY = int(round(intPlateCenterY)) - int(round(plateHeight * 1.6))      # write the chars in above the plate
    # end if

    textSizeWidth, textSizeHeight = textSize                # unpack text size width and height

    ptLowerLeftTextOriginX = int(ptCenterOfTextAreaX - (textSizeWidth / 2))           # calculate the lower left origin of the text area
    ptLowerLeftTextOriginY = int(ptCenterOfTextAreaY + (textSizeHeight / 2))          # based on the text area center, width, and height

            # write the text on the image
    cv2.putText(imgOriginalScene, licPlate.strChars, (ptLowerLeftTextOriginX, ptLowerLeftTextOriginY), intFontFace, fltFontScale, SCALAR_YELLOW, intFontThickness)
# end function

###################################################################################################
if __name__ == "__main__":
    main()


















