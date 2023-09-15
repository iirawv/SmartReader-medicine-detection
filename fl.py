from flask import Flask, render_template, request
import cv2
import numpy as np
import knn_classifier

app = Flask(__name__)

def rgb2hsv(r, g, b):
    # from RGB to HSV color space
    # R, G, B values are [0, 255]. H value is [0, 360]. S, V values are [0, 1]

    r = r / 255.0
    g = g / 255.0
    b = b / 255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx-mn
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g-b)/df) + 360) % 360
    elif mx == g:
        h = (60 * ((b-r)/df) + 120) % 360
    elif mx == b:
        h = (60 * ((r-g)/df) + 240) % 360
    if mx == 0:
        s = 0
    else:
        s = df/mx
    v = mx
    return h, s, v

def detectShape(path):
    # for detecting the contour of the pill and its length, and the pill's predicted color

    img= cv2.imread(path,1)
    imgheight= img.shape[0]
    imgwidth = img.shape[1]
    img = cv2.resize(img, (int(imgwidth * (480 / imgheight)), 480))
    img = cv2.GaussianBlur(img, (3,3), 0) # Gaussian blurring to remove noise in the image 
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    # img = cv2.filter2D(img, -1, kernel)

    drugShape = 'UNDEFINED' # initializing the drug shape
    edges = cv2.Canny(img,100,200) # detecting the edges to identify the pill
    contours, hierarchy = cv2.findContours(edges,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE) # finding the contours in the image

    areas = np.array([cv2.contourArea(c) for c in contours]) # array of the areas of all contours
    contours = np.array(contours) # array of all contours in the image 
    arr1inds = areas.argsort() # sorting contours
    contours = contours[arr1inds[::-1]] # descendingly, as the pill will be tha largest contour

    approx = cv2.approxPolyDP(contours[0], 0.01*cv2.arcLength(contours[0],True), True)    
    x,y,w,h = cv2.boundingRect(contours[0]) # offsets - with this you get 'mask'

    cv2.drawContours(img, [contours[0]], 0,(255,0,0), 2)

    # to get the average of the colors inside the largest contour "inside the pill"
    newIM = img[y:y+h,x:x+w]
