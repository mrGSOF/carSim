import time
import numpy as np
import cv2
from astar.search import AStar


def resize(img, width=None, height=None):
    imgWidth = img.shape[1]
    imgHeight = img.shape[0]
    if width == None and height == None:
        width = imgWidth
        height = imgHeight
    if width == None:
        scale = (height/imgHeight)
        width = scale*imgWidth
    else:
        scale = (width/imgWidth)
        height = scale*imgHeight
    
    img = cv2.resize(img, (int(width), int(height)))
    return(img, scale)
        

def findPath(img, pos, targetPos, paddingSize = 2, dev=False):
    
    
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    img, scale = resize(img, width = 150)
    targetPos = (int(targetPos[0]*scale), int(targetPos[1]*scale))
    pos = (int(pos[0]*scale), int(pos[1]*scale))

    img = np.where(img<112, 1, 0).astype(np.uint8)

    
    imgWithPadding = np.zeros(img.shape, dtype=np.uint8)
    for rowIndex, row in enumerate(img):
        for columnIndex, item in enumerate(row):
            if item == 1:
                imgWithPadding[rowIndex-paddingSize:rowIndex+paddingSize+1,columnIndex-paddingSize:columnIndex+paddingSize+1] = 1
    imgTmp = np.where(imgWithPadding==1, 1, 255).astype(np.uint8)
    imgTmp = cv2.circle(imgTmp, (targetPos[0], targetPos[1]), radius=3, color=(112), thickness=-1)
    # cv2.imshow("path", imgTmp)
    # cv2.waitKey(1)
    # time.sleep(5)
    path = AStar(imgWithPadding).search((pos[1], pos[0]), (targetPos[1], targetPos[0]))
    
    if dev and path != None:
        img = np.where(img==0, 255, 0).astype(np.uint8)
        for dot in path:
            img = cv2.circle(img, (dot[1], dot[0]), radius=0, color=(0, 255, 0), thickness=-1)
        # print(np.where((img != 1) & (img != 0)))
        # print(img[int(720/2)-1, int(519)-1])
        cv2.imshow("path", img)
        cv2.waitKey(1)
    
    scaledPath = []
    for i in range(2, len(path), 2):
        p = path[i]
        scaledPath.append((p[1]/scale, p[0]/scale))
    return(scaledPath)

if __name__ == "__main__":
    path = findPath(cv2.imread("./images/reference.png"), pos=(0,0), targetPos=(350, 400), paddingSize=3, dev=True)
    time.sleep(10)
    print(path)