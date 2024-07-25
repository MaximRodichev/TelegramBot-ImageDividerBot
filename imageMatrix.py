from PIL import Image, ImageDraw
import numpy as np
# from termcolor import colored
import uuid
import os

class DiagonalException(Exception):
    def __init__(self,message=None):
        self.message = message
        super().__init__("Diagonal Not Found a Picture.")
        # super().__init__(colored("Diagonal Not Found a Picture.", "red", "on_white"))
class LineException(Exception):
    def __init__(self,message=None):
        self.message = message
        super().__init__("Line Data is Empty.")
        # super().__init__(colored("Line Data is Empty.", "red", "on_white"))
class IncorrectType(Exception):
    def __init__(self,type=None):
        self.message = "Not a PNG Format" if type==None else f"Not a PNG Format. Input format is {type}"
        super().__init__(self.message)


def image_to_matrix(img):
    # Convert the image to a NumPy array
    img_array = np.array(img)
    
    # Extract the alpha channel
    alpha_channel = img_array[:, :, 3]
    
    # Create a matrix with values from 0 to 255 based on the alpha channel
    matrix = (alpha_channel).astype(np.uint8)
    
    return matrix

def save_matrix_as_image(matrix, output_image_path):
    # Create an image from the matrix
    img = Image.fromarray(matrix, mode='L') 
    
    # Save the image
    img.save(output_image_path)

def save_matrix_as_text(matrix, output_text_path):
    # Save the matrix as a text file
    np.savetxt(output_text_path, matrix, fmt='%d', delimiter='\t')          

def trimImage(imagePath, side = ""):
    orig = Image.open(imagePath).convert('RGBA')
    mass = np.array(orig)[:,:,3]

    if side == 'left' or side == "":
        index = GetTrimIndex(mass,"left")
        orig.crop((index, 0, orig.width, orig.height)).save(imagePath)
        return index
    if side == 'right' or side == "":
        index = GetTrimIndex(mass, 'right')
        orig.crop((0, 0, index, orig.height)).save(imagePath)
    if side == 'top' or side == "":
        index = GetTrimIndex(mass, 'top')
        orig.crop((0, index, orig.width, orig.height)).save(imagePath)
    if side == 'bottom' or side == "":
        index = GetTrimIndex(mass, 'bottom')
        orig.crop((0, 0, orig.width, index)).save(imagePath)

def GetTrimIndex(mass, direct):
    if direct == 'left':
        start, end, step = 0, len(mass[0]), 1
    elif direct == 'right':
        start, end, step = len(mass[0]), 0, -1
    elif direct == 'top':
        start, end, step = 0, len(mass), 1
    elif direct == 'bottom':
        start, end, step = len(mass), 0, -1
    else:
        raise ValueError("Invalid direct param")

    for index in range(start, end, step):
        subMas = mass[:,index] if direct in ['left', 'right'] else mass[index]
        checkSum = np.sum(subMas)
        if np.any(checkSum>0):
            return index

#####################
#help function's
# Expand matrix and add 00000 columns and rows at start and end
def ExpandMatrix(matrix):
    row = np.zeros(matrix.shape[1],dtype=matrix.dtype)
    matrix = np.vstack([matrix,row])
    column = np.zeros((matrix.shape[0],1), dtype=matrix.dtype)
    matrix = np.hstack([matrix,column])
    # row = np.zeros(matrix.shape[1],dtype=matrix.dtype)
    # column = np.zeros((matrix.shape[0],1), dtype=matrix.dtype)
    row = np.zeros(matrix.shape[1],dtype=matrix.dtype)
    matrix = np.vstack([row,matrix])
    column = np.zeros((matrix.shape[0],1), dtype=matrix.dtype)
    matrix = np.hstack([column,matrix])
    return matrix
#_____VERSION 2_____#
def DiagonalLine(matrix, startPositionX=0, startPositionY=0, setAlpha=0, direction = "LeftTop", checkFlag = ">"):
    if checkFlag == ">":
        check = lambda x,y:x>y 
    else: check = lambda x,y:x<=y 
    height, width = len(matrix)-1, len(matrix[0])-1
    curPos_X, curPos_Y = 0,0
    # print(colored(f"DiagonalPixel searching at photo with\X: {startPositionX}\Y: {startPositionY}", 'blue'))
    if direction == "LeftTop":
        for pointPos in range(0,min(height-startPositionY,width-startPositionX)+1):
            curPos_Y, curPos_X = startPositionY+pointPos, startPositionX+pointPos
            if (check(matrix[curPos_Y][curPos_X],setAlpha)): return [curPos_X,curPos_Y, True]
    elif direction == "LeftBottom":
        if startPositionY == 0: startPositionY = height
        for pointPos in range(0,min(startPositionY,width-startPositionX)-1):
            curPos_Y, curPos_X = startPositionY-pointPos-1, startPositionX+pointPos
            if (check(matrix[curPos_Y][curPos_X],setAlpha)): return [curPos_X,curPos_Y, True]
    elif direction == "RightTop":
        if startPositionX == 0: startPositionX = width
        for pointPos in range(0,min(height-startPositionY,startPositionX)-1):
            curPos_Y, curPos_X = startPositionY+pointPos, startPositionX-pointPos - 1
            if (check(matrix[curPos_Y][curPos_X],setAlpha)): return [curPos_X,curPos_Y, True]
    elif direction == "RightBottom":
        if startPositionX == 0: startPositionX = width
        if startPositionY == 0: startPositionY = height
        for pointPos in range(0,min(startPositionY,startPositionX)-1):
            curPos_Y, curPos_X = startPositionY-pointPos - 1, startPositionX-pointPos - 1
            if (check(matrix[curPos_Y][curPos_X],setAlpha)): return [curPos_X,curPos_Y, True]
    else:
        raise ValueError("Direction is Incorrect")
    return [curPos_X,curPos_Y, False]

def LinearLine(CheckedLine, setAlpha = 250):
    for x in range(0,len(CheckedLine)):
        if CheckedLine[x]>setAlpha: return x
    return False

#Function to get frame (usage Line + BackLines on row\column)
def GetOneFrame(matrix, direction, checkSum = 0, setAlpha=0, startX = 0, startY = 0):
    # PATH = [[startX,startY]]
    Step = lambda Position,sum,CheckSum_: Position+1 if sum>CheckSum_ else Position
    StepInvertion = lambda Position,sum,CheckSum: Position-1 if sum>CheckSum else Position
    matrix = matrix.tolist()
    matrixTrans = list(map(list, zip(*matrix)))
    PosX, PosY = startX,startY
    massXY = DiagonalLine(matrix=matrix,startPositionX=PosX,startPositionY=PosY,setAlpha=setAlpha,direction=direction, checkFlag= ">")
    if massXY[2] == False: raise DiagonalException()
    setAlpha=0
    PosX,PosY = massXY[0], massXY[1]
    while True:
        # PATH.append([PosX,PosY])
        if matrix[PosY][PosX] > setAlpha:
            PosX, PosY, Flag = DiagonalLine(matrix=matrix,startPositionX=PosX,startPositionY=PosY,setAlpha=setAlpha,direction=direction,checkFlag= '<')
        else:
            sumHorizontal, sumVertical = 0,0
            sumHorizontal = sum([i for i in matrix[PosY][startX:PosX]]) if startX<PosX else sum([i for i in matrix[PosY][PosX:startX]])
            sumVertical = sum([i for i in matrixTrans[PosX][startY:PosY]]) if startY<PosY else sum([i for i in matrixTrans[PosX][PosY:startY]])
            PosX = Step(PosX,sumVertical,checkSum) if startX<PosX else StepInvertion(PosX,sumVertical,checkSum) 
            PosY = Step(PosY,sumHorizontal,checkSum) if startY<PosY else StepInvertion(PosY,sumHorizontal,checkSum)
            if sumHorizontal<=checkSum and sumVertical<=checkSum:
                # return [PosX,PosY,Flag,PATH]
                return [PosX,PosY]
            
#Function Capture Image in matrix, return x,y,width,heigh
def CaptureImage(matrix, startPositionX=0, startPositionY=0, checkSum=0, setAlpha=0, direction="LeftTop"):
    DirectCommunication = { "LeftTop": "RightBottom",
                            "RightBottom": "LeftTop",
                            "LeftBottom": "RightTop",
                            "RightTop": "LeftBottom"}
 
    LastX, LastY = GetOneFrame(matrix=matrix,direction=direction,startX=startPositionX,startY=startPositionY,checkSum=checkSum,setAlpha = setAlpha)     
    
    StartX, StartY = GetOneFrame(matrix=matrix,direction=DirectCommunication[direction],startX=LastX,startY=LastY,checkSum=checkSum,setAlpha = setAlpha)  
    
    LastX, LastY = GetOneFrame(matrix=matrix,direction=direction,startX=StartX,startY=StartY,checkSum=checkSum,setAlpha = setAlpha)            
    # input(len(matrix[StartY:LastY]))
    # input(len(matrix[StartY]))
    # input(len(matrix[StartY][StartX:LastX]))
    if sum([i[LastX] for i in matrix[StartY:LastY]]) > checkSum or sum([i[StartX] for i in matrix[StartY:LastY]]) > checkSum or sum([i for i in matrix[StartY][StartX:LastX]]) > checkSum or sum([i for i in matrix[LastY][StartX:LastX]]) > checkSum:
        # print("CHEKC")
        StartX, StartY = GetOneFrame(matrix=matrix,direction=DirectCommunication[direction],startX=LastX,startY=LastY,checkSum=checkSum,setAlpha = setAlpha)   

    #CapImage
    if direction == "LeftTop": return [StartX,StartY,LastX,LastY]
    if direction == "RightTop": return [LastX,StartY,StartX,LastY]
    if direction == "LeftBottom": return [StartX,LastY,LastX,StartY]
    if direction == "RightBottom": return [LastX,LastY,StartX,StartY]
    # #CapImage
    # if direction == "LeftTop": return [StartX,StartY,LastX,LastY,PATH_IN,PATH_OUT]
    # if direction == "RightTop": return [LastX,StartY,StartX,LastY,PATH_IN,PATH_OUT]
    # if direction == "LeftBottom": return [StartX,LastY,LastX,StartY,PATH_IN,PATH_OUT]
    # if direction == "RightBottom": return [LastX,LastY,StartX,StartY,PATH_IN,PATH_OUT]

#Function to DrawLines from Massive(PATH)
def DrawLine(massive, matrix=[], width=0, image=0, color="red"):
    if not image:
        height,width = matrix.shape
        image = Image.new("RGBA", (width,height),color=(0,0,0,0))
    draw = ImageDraw.Draw(image)
    for x in range(0,len(massive)-1):
        draw.line([(massive[x][0], massive[x][1]),(massive[x+1][0], massive[x+1][1])], fill=color, width=2)
    del draw
    return image

#Function to Logic Remove from matrix founded image
def LogicalCut(matrix,massive):
    x,y,width,height = massive[0],massive[1],massive[2],massive[3]
    if width<x and height<y: matrix[height:y,width:x]=0
    elif width<x: matrix[y:height,width:x] = 0
    elif height<y: matrix[height:y,x:width] = 0
    else: matrix[y:height,x:width]=0
    return matrix

def GetStartsPositions(matrix, step, direction = "LeftTop"):
    MassiveOfStartsLINEAR = []
    MassiveOfStartsINVERSION = []
    # matrix = [[1,2,3,1,2,3,1,2,3,1,2,3],[1,2,3,1,2,3],[31,2,3,1,2,3],[1,2,3,1,2,3]]
    #Examlpe: (0,0) (0,1) (0,2) ... (0, height) (1,height) ... (width,height)
    x,y=0,0
    height,width = matrix.shape
    for y in range(step,height,step):
        MassiveOfStartsLINEAR.append([x,y])
    y = height
    for x in range(step-(height - MassiveOfStartsLINEAR[-1][1]), width,step):
        MassiveOfStartsLINEAR.append([x,y])
    for x in range(step,width,step):
        MassiveOfStartsINVERSION.append([x,0])
    x = width
    for y in range(step-(width - MassiveOfStartsINVERSION[-1][0]), height, step):
        MassiveOfStartsINVERSION.append([x,y])
    if direction == "LeftTop": return [MassiveOfStartsLINEAR, MassiveOfStartsINVERSION]
    if direction == "LeftBottom": return [[[x,height-y] for x,y in MassiveOfStartsLINEAR], [[x,height-y] for x,y in MassiveOfStartsINVERSION]]
    if direction == "RightTop": return [[[width - x,y] for x,y in MassiveOfStartsLINEAR], [[width - x,y] for x,y in MassiveOfStartsINVERSION]]
    if direction == "RightBottom":
        return [[MassiveOfStartsLINEAR[x] for x in range(len(MassiveOfStartsLINEAR)-1,0,-1)], [MassiveOfStartsINVERSION[x] for x in range(len(MassiveOfStartsINVERSION)-1,0,-1)]]



#One of Main Functions to Show Cutterize Image (Lines on Original)
def CheckLine(Line, dir):
    if dir == "Linear":
        for x in range(0,len(Line)):
            if Line[x] > 250:
                return x
    if dir == "Invers":
        for x in range(len(Line)-1,0, -1):
            if Line[x] > 250:
                return x
    return False
def Cutter(matrix,direction="Left",setAlpha=0,checkSum=0,step=5):
    height,width = matrix.shape
    PointsWeight = height*width / 100
    Percent = 40
    CutterizeINFO = []
    config = {"Left": {"CheckLine":"Linear","CaptureImage": "LeftTop"}}
    for StartY in range(0, height, step):
        StartX = CheckLine(Line=matrix[StartY], dir = config[direction]["CheckLine"])
        if StartX == False: continue
        while True:
            try:
                temp = CaptureImage(matrix, StartX, StartY, checkSum, setAlpha, direction=config[direction]["CaptureImage"])            
            except Exception as e:
                # print(e)
                break
                    
            ImageToAllPoints = abs((temp[2] - temp[0]) * (temp[3] - temp[1])) / PointsWeight
            if ImageToAllPoints > Percent: 
                print(f"ImageLarge in % of original (UP POW): {ImageToAllPoints} | ChkSum: {checkSum}"); checkSum += 10
            else: 
                matrix = LogicalCut(matrix=matrix, massive=temp)
                CutterizeINFO.append(temp)
                StartY-=step
                checkSum=0
                break
 
    if np.sum(matrix)/255/PointsWeight*100 > 30:
        for x in Cutter(matrix, direction,setAlpha,checkSum, step=1):
            CutterizeINFO.append(x)     
    return CutterizeINFO

def GetCrops(image, CutterInfo):
    imageWithRectangles = image
    draw = ImageDraw.Draw(imageWithRectangles)
    for mass in CutterInfo:
        x , y, width, height = mass[0], mass[1], mass[2], mass[3]
        draw.rectangle([x,y,width,height],outline="red",width=3)
    return imageWithRectangles

def GetListImages(Cutterize, image: Image.Image):
    ImageList = []
    for Data in Cutterize:
        x , y, width, height = Data[0], Data[1], Data[2], Data[3]
        box = (x, y, width, height)
        ImageList.append(image.crop(box))
    return ImageList