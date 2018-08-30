#!/opt/py-env/bin/python
# -*- coding: UTF-8 -*-
import random
from PIL import Image

width=260; height=116

def align_image(img):
    bmp =  Image.new("RGB", (width,height))
    pos = [157, 145, 265, 277,181, 169, 241, 253, 109, 97, 289, 301, 85, 73, 25, 37, 13, 1, 121, 133, 61, 49, 217, 229, 205, 193,
    145, 157, 277, 265, 169, 181, 253, 241, 97, 109, 301, 289, 73, 85, 37, 25, 1, 13, 133, 121, 49, 61, 229, 217, 193, 205]

    dx = 0; dy = 0; sy = 58
    for p in pos:
        p -= 1
        box1 = (dx, dy, dx+10, dy+58)
        box2 = (p, sy, p+10, sy+58)
        region = img.crop(box2)
        bmp.paste(region, box1)
        dx += 10
        if dx == width:
            dx = 0; dy = 58; sy = 0
    return bmp


def get_position_x(img_bg, img_fullbg):
    bg = list(img_bg.getdata())
    full = list(img_fullbg.getdata())

    diff = []
    for i in range(0, len(bg)):
        r1,g1,b1 = bg[i]
        r2,g2,b2 = full[i]
        diff.append((abs(r1-r2),abs(g1-g2),abs(b1-b2)))
    #print diff

    bmp =  Image.new("RGB", (width,height))
    bmp.putdata(diff)
    bmp.show()

    w = width
    histgram = [0 for i in range(0,width)]
    histsum = [0 for i in range(0,width)]

    for y in range(0, height-1):
        for x in range(0, width-1):
            i00 = x + y * width
            i11 = i00 + width + 1
            i01 = i00 + 1
            i10 = i00 + width
            # histgram[x] +=  (abs(diff[i00][0] - diff[i11][0]) + abs(diff[i01][0] - diff[i10][0])) + \
            #                 (abs(diff[i00][1] - diff[i11][1]) + abs(diff[i01][1] - diff[i10][1])) + \
            #                 (abs(diff[i00][2] - diff[i11][2]) + abs(diff[i01][2] - diff[i10][2]))
            histgram[x] += diff[i00][0] + diff[i00][1] + diff[i00][2]
    #print histgram

    # Find xpos
    ww=42; max_value = -1
    for i in range(0,ww):
        histsum[0] += histgram[i]

    for x in range(1,width-ww):
        histsum[x] = histsum[x-1] + histgram[x+ww-1] - histgram[x-1]
        if histsum[x] > max_value:
            xpos = x
            max_value = histsum[x]

    return xpos-6

def get_actions(xpos):
    acts = []
    for i in range(0,4):
        act = {"pos":xpos}
        action = generate3(xpos)
        print action
        act["action"] = encrypt(action)
        # pt = 0
        # for a in action:
        #     pt += a[2]
        # act["passtime"] = pt
        act["passtime"] = action[-1][2]
        acts.append(act)
    return acts

def generate3(length):
    arr = []
    y = -4
    t = 150
    arr.append((0, y, 0))
    x=random.randint(1,3)
    while length-x>=5:
        arr.append( (x,y,t) )
        length=length-x
        x=random.randint(1,3)
        t += random.randint(10,50)*10
    arr.append( (x-length,y,t))
    return arr


def generate(xpos):
    xpos += 0.0
    sx = random.randint(15,30-1)
    sy = random.randint(15,30-1)
    arr = []
    arr.append((-sx,-sy,0))
    arr.append((0,0,0))
    maxCount = 100 # max len 100
    x = 0.0
    lx = xpos - x
    while abs(lx) > 0.8 and maxCount > 0:
        maxCount -= 1
        rn = random.random()
        dx = rn * lx * 0.6
        if abs(dx) < 0.5:
            continue
        dt = random.random() *  (rn * 80 + 50)+ 10

        rn = random.random()
        dy = 0
        if rn < 0.2 and dx > 10:
            # dy = rn * 20.0
            dy = rn * 10.0
            if abs(dy) > 5:
                dy = dy % 5

            if rn < 0.05:
                dy = -rn * 80

        x += dx
        arr.append( ((int)(dx + 0.5), (int)(dy + 0.5), (int)(dt + 0.5)) )
        lx = xpos - x

    dtlast = 500.0 * random.random() + 100.0
    arr.append( (0, 0, (int)(dtlast)) )
    return arr


def generate2(xpos):
    xpos += 0.0
    sx = random.randint(15,30-1)
    sy = random.randint(15,30-1)
    arr = []
    arr.append((sx,sy,0))

    maxCount = 100  # max len 100
    mds = 0.25
    speed = random.random() * 0.3 + 0.05
    ds = random.random() * 0.5 * mds
    dsign = 1.0
    x = 0.0
    lx = xpos - x
    while abs(lx) > 1.0 and maxCount > 0:
        maxCount -= 1
        rn = random.random()
        dt = rn * 100 + 10
        if rn < 0.2:
            dt += rn * 200

        speed += ds * dsign
        if speed > 0.25:
            speed = 0.25
        rn = random.random()

        if rn < speed / 0.25:
            dsign = -dsign
        ds = random.random() * mds * 0.5
        if abs(lx) < 10:
            speed *= lx / 20
        elif x < xpos / 3:
            speed *= (x / xpos + 1.0)

        if speed < 0:
            speed = -speed
        dx = speed * dt
        if abs(dx) < 0.6:
            continue

        x += dx
        if x - xpos > 0 and dx > 0:
            speed = -speed
            x -= 2 * dx

        rn = random.random()
        dy = 0
        if rn < 0.1 and dt > 70:
            dy = rn * 30
            if rn < 0.05:
                dy = -rn * 60

        arr.append(((int)(dx+0.5), (int)(dy+0.5),(int)(dt+0.5)))
        lx = xpos - x

    dtlast = (int)(500.0 * random.random() + 100.0)
    arr.append((0,0,dtlast))
    return arr


def encrypt(action):
    d = action
    dx = ""; dy = ""; dt = ""
    for a in d:
        b = replace(a)
        if b != 0:
            dy += b
        else:
            dx += encode(a[0])
            dy += encode(a[1])
        dt += encode(a[2])

    return dx + "!!" + dy + "!!" + dt

def replace(a2):
    bs = [
            (1,0),
            (2,0),
            (1,-1),
            (1,1),
            (0,1),
            (0,-1),
            (3,0),
            (2,-1),
            (2,1)
        ]
    c = "stuvwxyz~"

    d = 0
    for b in bs:
        if a2[0] == b[0] and a2[1] == b[1]:
            return c[d]
        d += 1

    return 0


def encode(n):
    b = "()*,-./0123456789:?@ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqr"
    c = len(b)
    d = 0
    e = abs(n)
    f = e / c
    if f >= c:
        f = c - 1
    if f != 0:
        d = b[f]
        e %= c

    g = ""
    if n < 0:
        g += "!"
    if d != 0:
        g += "$"

    if d == 0:
        d = ""
    return g + d + b[e];

def get_userresponse(posx, challenge):
    ct = challenge[:32]
    if len(ct) < 2:
        return ""

    d = []
    for f in ct:
        f = ord(f)
        if f > 57:
            d.append(f - 87)
        else:
            d.append(f - 48)
    #print "d: ", d
    c = 36 * d[0] + d[1]
    g = posx + c
    #print "g: ", g
    i = [[] for x in range(0,5)]
    j = {}
    k = 0
    for h in ct:
        if (not j.has_key(h)) or (j[h] != 1):
            j[h] = 1
            i[k].append(h)
            k += 1
            k %= 5

    n = g; o = 4
    p = ""
    q = [1, 2, 5, 10, 50]
    while n > 0:
        if n - q[o] >= 0:
            m = random.randint(0, len(i[o])-1)
            p += i[o][m]
            n -= q[o]
        else:
            del i[o]
            del q[o]
            o -= 1
    return p

if __name__ == '__main__':
    fullbg = Image.open("fullbg1.jpg")
    fullbg = align_image(fullbg)
    #fullbg.show()

    bg = Image.open("bg1.jpg")
    bg = align_image(bg)
    #bg.show()

    xpos = get_position_x(bg, fullbg)
    print xpos

    actions = get_actions(xpos)
    for action in actions:
        print action

    challenge = "d67516473b47ccefddbe61404ccf38e5an"
    userresponse = get_userresponse(190, challenge)
    print userresponse
