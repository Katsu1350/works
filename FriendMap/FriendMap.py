import numpy as np
import cv2
import urllib.request
import os
import time
from Iterater import Iter

WIN_W = 1280
WIN_H = 960

# 오사카역의 좌표
HOME_LON = 135.496398
HOME_LAT = 34.701704
HOME_ZOOM = 18

min_zoom = 12
max_zoom = 18
TILE_W = TILE_H = 256
fmt = "png"

TILES_DIR = "maptiles/"

spot_imgs = [[] for i in range(8)]

img_size = 50

present_location_img = cv2.imread("img/present_location.png")
for i in range(len(spot_imgs)):
    img_file = "img/spot"
    img_file += str(i + 1) + ".png"
    spot_imgs[i].append(cv2.imread(img_file))
present_location_img = cv2.resize(present_location_img, (img_size, img_size))
for img in spot_imgs:
    img[0] = cv2.resize(img[0], (img_size, img_size))
present_location_img_gray = cv2.cvtColor(present_location_img, cv2.COLOR_BGR2GRAY)
for img in spot_imgs:
    img.append(cv2.cvtColor(img[0], cv2.COLOR_BGR2GRAY))
mask_present_location = cv2.threshold(present_location_img_gray, 0, 255, cv2.THRESH_BINARY)[1]
for img in spot_imgs:
    img.append(cv2.threshold(img[1], 0, 255, cv2.THRESH_BINARY)[1])
mask_pl = cv2.bitwise_not(mask_present_location)
for img in spot_imgs:
    img.append(cv2.bitwise_not(img[2]))
present_location_fg = cv2.bitwise_and(present_location_img, present_location_img, mask = mask_present_location)
for img in spot_imgs:
    img.append(cv2.bitwise_and(img[0], img[0], mask = img[2]))

x_pos = WIN_W//2 - img_size//2
y_pos = WIN_H//2 - img_size

spots = [[] for i in range(7)]
f = open("spot_db.mdb")
s = Iter(f.read())
while s.hasNext():
    spot = []
    key = int(s.next())
    temp = ""
    while s.seeNext() != ",":
        temp += s.next()
    spot.append(eval(temp))
    temp = ""
    s.next()
    while s.seeNext() != ",":
        temp += s.next()
    spot.append(eval(temp))
    temp = ""
    s.next()
    while s.seeNext() != ",":
        temp += s.next()
    spot.append(temp)
    temp = ""
    s.next()
    for i in range(3):
        temp += s.next()
    spot.append(eval(temp))
    spots[key].append(spot)

opened_tiles = {}
white_tiles = {}

recommendation = False

def ll2pix(lon, lat, zoom):
    pix_x = 2 ** (zoom + 7) * (lon / 180 + 1)
    pix_y = 2 ** (zoom + 7) * ( - np.arctanh(np.sin(np.pi / 180 * lat)) / np.pi + 1)
    return pix_x, pix_y

def pix2ll(x, y, zoom):
    lon = 180 * (x / (2 ** (zoom + 7)) - 1)
    lat = 180 / np.pi * (np.arcsin(np.tanh( - np.pi / (2 ** (zoom + 7)) * y + np.pi)))
    return lon, lat

def new_ll(lon_cur, lat_cur, zm, dx, dy):
    x, y = ll2pix(lon_cur, lat_cur, zm)
    return pix2ll(x + dx, y + dy, zm)

def load_win_img(lon, lat, zm):
    global cnt_lon, cnt_lat
    cx, cy = ll2pix(lon, lat, zm)

    win_left=int(cx-WIN_W/2)
    win_top=int(cy-WIN_H/2)

    x_nth = win_left // TILE_W
    y_nth = win_top // TILE_H

    left_offset = win_left % TILE_W
    top_offset = win_top % TILE_H

    vcon_list = []
    tot_height = 0
    tot_height += TILE_H - top_offset
    j = 0
    while True:
        hcon_list = []
        tot_width = 0
        tot_width += TILE_W - left_offset
        i = 0
        while True:
            img_tmp = open_tile_img(x_nth + i, y_nth + j, zm)
            hcon_list.append(img_tmp)
            if tot_width >= WIN_W:
                break
            tot_width += TILE_W
            i += 1
        hcon_img = cv2.hconcat(hcon_list)
        vcon_list.append(hcon_img)
        if tot_height >= WIN_H:
            break
        tot_height += TILE_H
        j += 1
    convined_img = cv2.vconcat(vcon_list)

    return convined_img[top_offset : top_offset + WIN_H, left_offset : left_offset + WIN_W, :]

def tile_file_name(x_nth, y_nth, zm):
#    x_nth = x // TILE_W
#    y_nth = y // TILE_H
    return TILES_DIR + "z%02d/%dx%d_%07d_%07d" % (zm, TILE_W, TILE_H, x_nth, y_nth) + "." + fmt

def open_tile_img(x_nth, y_nth,zm):
    if (zm, x_nth, y_nth) in opened_tiles:
        print("opened_tiles(%d,%d,%d)" % (zm, x_nth, y_nth))
        return opened_tiles[(zm, x_nth, y_nth)]

    fname = tile_file_name(x_nth, y_nth, zm)
    if os.path.exists(fname):
        print("opening tile(%d,%d,%d)" % (zm, x_nth, y_nth) + " -> " + fname)
    else:
        url = "http://tile.openstreetmap.jp/%d/%d/%d.png" % (zm, x_nth, y_nth)
        print("Downloading... ")
        print(url)
        print(" -> " + fname)
        try:
            urllib.request.urlretrieve(url, fname)
        except Exception as e:
            print(e)
            print("Download faild -> blank")
            if (TILE_W,TILE_H) in white_tiles:
                return white_tiles[(TILE_W, TILE_H)]
            else:
                white=np.zeros([TILE_H, TILE_W, 3], dtype=np.uint8)
                white[:,:,:] = 255
                white_tiles[(TILE_W, TILE_H)] = white
                return white
    opened_tiles[(zm, x_nth, y_nth)] = cv2.imread(fname)
    return opened_tiles[(zm, x_nth, y_nth)]

def doRecom(x_pos, y_pos, c_lon, c_lat, z, spots, key):
    size = [2**i for i in range(6, -1, -1)]
    r = [2**i * 100 for i in range(6, -1, -1)]
    recommend = []
    x1, y1 = ll2pix(c_lon, c_lat, z)
    for spot in spots[key]:
        x2, y2 = ll2pix(spot[0], spot[1], z)
        d = ((x1 - x2)**2 + (y1 - y2)**2)**0.5 * r[z-12]
        if d <= r[z-12]*200:
            recommend.append(spot)
    sorted(recommend, key = lambda x: x[3])
    if len(recommend) >= (19 - z) * 5:
        return recommend
    else:
        return recommend[:(19 - z) * 5]

def print_spot(x_pos, y_pos, c_lon, c_lat, z, spots, spot_imgs, win_img, key):
    recommend = doRecom(x_pos, y_pos, c_lon, c_lat, z, spots, key)
    x1, y1 = ll2pix(c_lon, c_lat, z)
    for spot in recommend:
        x2, y2 = ll2pix(spot[0], spot[1], z)
        d_x = int(x2 - x1 + x_pos)
        d_y = int(y2 - y1 + y_pos)
        if d_x >= 0 and d_x <= WIN_W - img_size and d_y >= 0 and d_y <= WIN_H - img_size:
            roi = win_img[d_y:d_y + img_size, d_x:d_x + img_size]
            temp_bg = cv2.bitwise_and(roi, roi, mask = spot_imgs[key][3])
            temp_img = cv2.add(temp_bg, spot_imgs[key][4])
            win_img[d_y:d_y + img_size, d_x:d_x + img_size] = temp_img
    return win_img
    
c_lon = HOME_LON
c_lat = HOME_LAT
zoom = HOME_ZOOM
cv2.namedWindow("Friend Map", cv2.WINDOW_AUTOSIZE)

c_lon_bak = -1
c_lat_bak = -1
zoom_bak = -1

#mainloop
while True:
    if c_lon_bak != c_lon or c_lat_bak != c_lat or zoom_bak != zoom:
        win_img = load_win_img(c_lon, c_lat, zoom)
        if recommendation:
            win_img = print_spot(x_pos, y_pos, c_lon, c_lat, zoom, spots, spot_imgs, win_img, key)
        roi = win_img[y_pos:y_pos + img_size, x_pos:x_pos + img_size]
        present_location_bg = cv2.bitwise_and(roi, roi, mask = mask_pl)
        present_location_img2 = cv2.add(present_location_bg, present_location_fg)
        win_img[y_pos:y_pos + img_size, x_pos:x_pos + img_size] = present_location_img2
        cv2.imshow("Friend Map", win_img)
    c_lon_bak = c_lon
    c_lat_bak = c_lat
    zoom_bak = zoom

    k = cv2.waitKey(20) & 0xff
    if k == ord('+'):
        if zoom < max_zoom: 
            zoom += 1
    elif k == ord('-'):
        if zoom > min_zoom: 
            zoom -= 1
    elif k == ord('a'):
        c_lon, c_lat = new_ll(c_lon, c_lat, zoom, -5, 0)
    elif k == ord('s'):
        c_lon, c_lat = new_ll(c_lon, c_lat, zoom, 0, +5)
    elif k == ord('d'):
        c_lon, c_lat = new_ll(c_lon, c_lat, zoom, +5, 0)
    elif k == ord('w'):
        c_lon, c_lat = new_ll(c_lon, c_lat, zoom, 0, -5)
    elif k == 49:
        key = 0
    elif k == 50:
        key = 1
    elif k == 51:
        key = 2
    elif k == 52:
        key = 3
    elif k == 53:
        key = 4
    elif k == 54:
        key = 5
    elif k == 55:
        key = 6
    elif k == ord("c"):
        recommendation = not recommendation
    elif k == ord("q") or k == 27:
        break
cv2.destroyAllWindows()
