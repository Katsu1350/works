import sys
import numpy as np
import csv
import cv2
import requests
import base64
import json

def find_contours(img):
    contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    temp = cv2.drawContours(img, contours, -1, (0,255,0), 3)
    areas = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < img.size*0.9:
            epsilon = 0.1*cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            if len(approx) >= 4:
                areas.append(approx)

    img_c = cv2.drawContours(cv2.cvtColor(img, cv2.COLOR_GRAY2BGR), areas, -1, (0,0,255), 3)
    return img_c, areas

def cut_out(mask, origin):
    r, area_margin = find_contours(mask)

    if not area_margin:
        print ("error: no contours found")
        sys.exit(0)

    cropped = []
    for area in area_margin:
        area = sorted(area, key = lambda x: (x[0][0]+x[0][1]))
        if area[1][0][0] < area[2][0][0]:
            area[1], area[2] = area[2], area[1]

        l_top = area[0][0]
        r_top = area[1][0]
        l_btm = area[2][0]
        r_btm = area[3][0]

        top_line   = (abs(r_top[0] - l_top[0]) ^ 2) + (abs(r_top[1] - l_top[1]) ^ 2)
        btm_line   = (abs(r_btm[0] - l_btm[0]) ^ 2) + (abs(r_btm[1] - l_btm[1]) ^ 2)
        left_line  = (abs(l_top[0] - l_btm[0]) ^ 2) + (abs(l_top[1] - l_btm[1]) ^ 2)
        right_line = (abs(r_top[0] - r_btm[0]) ^ 2) + (abs(r_top[1] - r_btm[1]) ^ 2)
        max_x = top_line  if top_line  > btm_line   else btm_line
        max_y = left_line if left_line > right_line else right_line

        pts1 = np.float32(area)
        pts2 = np.float32([[0, 0], [max_x, 0], [0, max_y], [max_x, max_y]])

        M = cv2.getPerspectiveTransform(pts1, pts2)
        cropped.append(cv2.warpPerspective(origin, M, (max_x, max_y)))
    return cropped

def draw(event, x, y, flags, param):
    global ix,iy,drawing,mode,result

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix,iy = x,y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing == True:
            if mode == True:
                cv2.rectangle(select,(ix,iy),(x,y),(0,255,0),-1)
                cv2.rectangle(mask,(ix,iy),(x,y),(255,255,255),-1)
            else:
                cv2.circle(select,(x,y),5,(0,255,0),-1)
                cv2.circle(mask,(x,y),5,(255,255,255),-1)
            result = cv2.addWeighted(sample, 0.6, select, 0.4, 0)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        if mode == True:
            cv2.rectangle(select,(ix,iy),(x,y),(0,255,0),-1)
            cv2.rectangle(mask,(ix,iy),(x,y),(255,255,255),-1)
        else:
            cv2.circle(select,(x,y),5,(0,255,0),-1)
            cv2.circle(mask,(x,y),5,(255,255,255),-1)
        result = cv2.addWeighted(sample, 0.6, select, 0.4, 0)

def request_cloud_vison_api(image_base64):
    api_url = GOOGLE_CLOUD_VISION_API_URL + API_KEY
    req_body = json.dumps({
        'requests': [{
            'image': {
                'content': image_base64.decode('utf-8')
            },
            'features': [{
                'type': 'TEXT_DETECTION',
                'maxResults': 10,
            }]
        }]
    })
    res = requests.post(api_url, data=req_body)
    return res.json()

def img_to_base64(filepath):
    with open(filepath, 'rb') as img:
        img_byte = img.read()
    return base64.b64encode(img_byte)

GOOGLE_CLOUD_VISION_API_URL = 'https://vision.googleapis.com/v1/images:annotate?key='
API_KEY = 'AIzaSyDbUAj1o4-xG3gKrV2ZJvu9Uk-yw8_aukA'

img     = cv2.imread("HomePlus.jpg")
sub = img

temp    = cv2.resize(np.zeros((1, 1, 3), np.uint8), (img.shape[1] + 10, img.shape[0] + 10))
temp[np.where((temp == [0,0,0]).all(axis=2))] = [100,0,100]
temp[5:(img.shape[0] + 5), 5:(img.shape[1] + 5)] = img
img     = temp

img     = cv2.GaussianBlur(img, (5, 5), 0)
img     = cv2.bitwise_not(img)
img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
img_hsv = cv2.bitwise_not(img_hsv)
ret, img_thresh = cv2.threshold(img_hsv, 190, 255, cv2.THRESH_BINARY)
img_thresh      = cv2.bitwise_not(img_thresh)
try:
    mask_margin = cv2.inRange(img_thresh, (200,0,0), (255,255,255))
    img_cropped = cut_out(mask_margin, temp)[0]
    mask_margin = cv2.inRange(img_thresh, (0,200,0), (255,255,255))
    img_cropped = cut_out(mask_margin, temp)[0]
    cv2.imwrite('new_img.jpg', img_cropped)
except:
    pass

sample = cv2.resize(img_cropped, dsize=None, fx=1, fy=1)
select, result = cv2.resize(img_cropped, dsize=None, fx=1, fy=1), cv2.resize(img_cropped, dsize=None, fx=1, fy=1)
mask = np.zeros((sample.shape[0],sample.shape[1],3), np.uint8)

drawing = False
mode = True
ix, iy = -1, -1
cv2.namedWindow('select')
cv2.setMouseCallback('select', draw)
while True:
    cv2.imshow('select',result)
    k = cv2.waitKey(20) & 0xff
    if k == 27:
        break
    elif k == ord("c"):
        select = cv2.resize(img_cropped, dsize=None, fx=1, fy=1)
        result = cv2.resize(img_cropped, dsize=None, fx=1, fy=1)
        mask = np.zeros((sample.shape[0],sample.shape[1],3), np.uint8)
    elif k == ord("d"):
        mode = not mode
    elif k == ord("a"):
        img_cropped = sub
        sample = cv2.resize(img_cropped, dsize=None, fx=1, fy=1)
        select = cv2.resize(img_cropped, dsize=None, fx=1, fy=1)
        result = cv2.resize(img_cropped, dsize=None, fx=1, fy=1)
        mask = np.zeros((sample.shape[0],sample.shape[1],3), np.uint8)
cv2.destroyAllWindows()

mask = cv2.resize(mask, (img_cropped.shape[1],img_cropped.shape[0]))
mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)

strings = []

cut_img = cut_out(mask, img_cropped)
for pice in cut_img:
    cv2.imwrite('temp.jpg', pice)

    img_base64 = img_to_base64('temp.jpg')
    result = request_cloud_vison_api(img_base64)

    text_r = result["responses"][0]["fullTextAnnotation"]["text"]
    strings.append(text_r.replace(" ", "").replace(",", "").replace(".", "").rstrip("\n").split('\n'))

result = []
temp = []
lst = []

for i in strings:
    if not str.isdigit(i[0]):
        for j in i:
            result.append({"상품명":j})
for i in strings:
    if str.isdigit(i[0]):
        temp.append(i)

if temp[0][0] >= temp[1][0]:
    for i in range(len(temp[0])):
        result[i]["단가"] = temp[1][i]
        result[i]["금액"] = temp[0][i]
else:
    for i in range(len(temp[0])):
        result[i]["단가"] = temp[0][i]
        result[i]["금액"] = temp[1][i]

datas = []
with open("./DB.csv", "r", encoding = "utf-8_sig", errors="", newline="") as f:
	reader = csv.DictReader(f)
	for row in reader:
		datas.append(row)

for i in result:
    for data in datas:
        if i["상품명"] == data["상품명"] and data["분류"] == "식품":
            con = False
            for j in lst:
                if data["종류"] == j["재료명"]:
                    j["수량"] += eval(i["금액"]) // eval(i["단가"])
                    con = True
                    break
            if con: continue
            lst.append({"재료명": data["종류"], "수량": eval(i["금액"]) // eval(i["단가"])})


