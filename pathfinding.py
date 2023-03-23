import time
import numpy as np
import cv2
from astar.search import AStar

def imgToGrid(img, line_color=(0, 255, 0), thickness=1, type_=cv2.LINE_AA, pxstep=10):
  '''(ndarray, 3-tuple, int, int) -> void
  draw gridlines on img
  line_color:
      BGR representation of color
  thickness:
      line thickness
  type:
      8, 4 or cv2.LINE_AA
  pxstep:
      grid line frequency in pixels
  '''
  rows = []
  grid = []
  x = 0
  while x+pxstep <= img.shape[0]:
    rows.append(img[x:x+pxstep,:,:])
    # cv2.line(img, (x, 0), (x, img.shape[0]), color=line_color, lineType=type_, thickness=thickness)
    x += pxstep
  
  print(len(rows))
  for row in rows:
    y = 0
    while y+pxstep <= row.shape[1]:
      grid.append(row[:,y:y+pxstep,:])
      y += pxstep
  
  return(grid)

def resize(img, width=None, height=None):
    imgWidth = img.shape[1]
    imgHeight = img.shape[0]
    if width == None and height == None:
        width = imgWidth
        height = imgHeight
    if width == None:
        width = (height/imgHeight)*imgWidth
    else:
        height = (width/imgWidth)*imgHeight
    
    img = cv2.resize(img, (int(width), int(height)))
    return(img)
        

def getPath(img, dev=False):
    targetPos = (100, 100)
    
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    img = resize(img, width = 150)

    print(img.shape)

    img = np.where(img<112, 1, 0).astype(np.uint8)
    
    # print("finding path...")
    path = AStar(img).search((0,0), targetPos)
    # print("found path")
    
    if dev:
        img = np.where(img==0, 255, 0).astype(np.uint8)
        if path != None:
            for dot in path:
                img = cv2.circle(img, (dot[1], dot[0]), radius=0, color=(0, 255, 0), thickness=-1)
            # print(np.where((img != 1) & (img != 0)))
            # print(img[int(720/2)-1, int(519)-1])
            cv2.imshow("path", img)
            cv2.waitKey(1)


    return(path)

path = getPath(cv2.imread("./images/reference.png"), dev=True)
time.sleep(10)
print(path)