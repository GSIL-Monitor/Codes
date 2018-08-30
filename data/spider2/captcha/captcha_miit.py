# -*- coding: utf-8 -*-
import os, sys, time
import subprocess
from PIL import Image, ImageDraw, ImageFont
import operator

reload(sys)
sys.setdefaultencoding("utf-8")

BACKGROUND = (255,255,255)

def _add_to_hash(r, p):
    if r.has_key(p):
        r[p] += 1
    else:
        r[p] = 0

def get_background_color(im):
    (width, height) = im.size
    #print width, height
    #data = im.getdata()
    r = {}
    for i in range(0,width):
        p = im.getpixel((i,0))
        _add_to_hash(r,p)
        p = im.getpixel((i,height-1))
        _add_to_hash(r,p)

    for j in range(0,height):
        p = im.getpixel((0,j))
        _add_to_hash(r,p)
        p = im.getpixel((width-1,j))
        _add_to_hash(r,p)

    max = 0
    background = None
    for p in r.keys():
        value = r[p]
        if value>max:
            max = value
            background = p
    #print max, background
    return background


def _calc_distance(p1,p2):
    (x1,x2,x3) = p1
    (y1,y2,y3) = p2
    dis = ((x1-y1)*(x1-y1)+(x2-y2)*(x2-y2)+(x3-y3)*(x3-y3))**0.5
    return dis

def erease_background(im):
    (width, height) = im.size
    background_color = get_background_color(im)
    data1 = []
    data = im.getdata()
    for p in data:
        if p == background_color:
            data1.append(BACKGROUND)
        elif _calc_distance(p, background_color)<=80:
            data1.append(BACKGROUND)
        else:
            data1.append(p)

    bmp = Image.new("RGB", (width, height))
    bmp.putdata(data1)
    #bmp.show()
    return bmp

def _get_close_color_set(color_set, p):
    dis = 255**3
    close_color = None
    for color in color_set:
        center = color["center"]
        dis1 = _calc_distance(center,p)
        if dis1 < 80 and dis1 < dis:
            dis = dis1
            close_color = color
    return close_color

def _adjust_color_set(color, p):
    color["all"].append(p)
    x=0; y=0; z=0; cnt=0
    for p in color["all"]:
        (a,b,c) = p
        x += a
        y += b
        z += c
        cnt += 1
    color["center"] = ((int)(x/cnt), (int)(y/cnt), (int)(z/cnt))

def find_main_color(im):
    (width, height) = im.size
    data = im.getdata()
    color_set = [] # [{"center":(1,2,3), "all":[(1,2,3)]}]
    color_no = 1
    for p in data:
        if p == BACKGROUND:
            continue
        color = _get_close_color_set(color_set, p)
        if color:
            _adjust_color_set(color, p)
        else:
            color_set.append({"center":p, "all":[p]})
    return color_set


def avg_color(data, x, y, width, height):
    pos = y*width + x
    p0 = data[pos]

    p11 = (-1,-1,-1)
    pos11 = pos - width - 1
    if x-1>=0 and y-1>=0:
        p11 = data[pos11]

    p12 = (-1,-1,-1)
    pos12 = pos - width
    if y-1 >= 0:
        p12 = data[pos12]

    p13 = (-1,-1,-1)
    pos13 = pos - width + 1
    if x+1 < width and y-1 >= 0:
        p13 = data[pos13]

    p21 = (-1,-1,-1)
    pos21 = pos -1
    if x-1 >= 0:
        p21 = data[pos21]

    p23 = (-1,-1,-1)
    pos21 = pos -1
    if x+1 < width:
        p21 = data[pos21]

    p31 = (-1,-1,-1)
    pos31 = pos + width - 1
    if x-1 >= 0 and y+1 < height:
        p31 = data[pos31]

    p32 = (-1,-1,-1)
    pos32 = pos + width
    if y+1 < height:
        p32 = data[pos32]

    p33 = (-1,-1,-1)
    pos33 = pos + width + 1
    if x+1 < width and y+1 < height:
        p33 = data[pos33]

    ps = [p11,p12,p13,p21,p0,p23,p31,p32,p33]
    x = 0; y = 0; z = 0;
    cnt = 0
    for p in ps:
        (a, b, c) = p
        if a==-1 and b==-1 and c==-1:
            continue
        if a==255 and b==255 and c==255:
            continue
        x += a
        y += b
        z += c
        cnt += 1

    return ((int)(x/cnt), (int)(y/cnt), (int)(z/cnt))


def fill_main_color(im):
    (width, height) = im.size
    color_set = find_main_color(im)
    #for p in color_set:
    #    print p["center"]
    data1 = []
    data = im.getdata()
    i = 0
    for p in data:
        if p == BACKGROUND:
            data1.append(BACKGROUND)
        else:
            x = (int)(i%width)
            y = (int)(i/width)
            p = avg_color(data, x, y, width, height)
            color = _get_close_color_set(color_set,p)
            if color:
                data1.append(color["center"])
            else:
                data1.append(BACKGROUND)
        i += 1
    bmp = Image.new("RGB", (width, height))
    bmp.putdata(data1)
    # bmp.show()
    return bmp

def crop_image(im, start, end):
    (width, height) = im.size
    data = im.getdata()
    data1 = []
    h = 0
    for j in range(height):
        need = False
        for i in range(start,end):
            if data[j*width + i] != BACKGROUND:
                need = True
                break
        if need:
            h += 1
            for i in range(start,end):
                data1.append(data[j*width + i])
    bmp = Image.new("RGB", (end-start, h))
    bmp.putdata(data1)
    return bmp

def split_numbers(im):
    images = []
    (width, height) = im.size
    data = im.getdata()
    splits = [0 for i in range(width)]
    for i in range(width):
        value = 0
        for j in range(height):
            (x,y,z) = data[j*width + i]
            if x==255 and y==255 and z==255:
                continue
            value += 1
        splits[i] = value

    for i in range(width):
        if splits[i] <= 3:
            splits[i] = 0

    start = -1
    end = 0
    for i in range(width):
        if start == -1 and splits[i] > 0:
            start = i
            end = -1
        if end == -1 and splits[i] == 0:
            end = i
            # print start, end
            num_img = crop_image(im,start,end)
            (w,h) = num_img.size
            if w>=3 and h>10:
                images.append(num_img)
                # num_img.show()
            start = -1

    if len(images) == 6:
        return images

    _images = []
    if len(images) < 6:
        for image in images:
            #image.show()
            x,y = image.size
            if x < 20:
                _images.append(image)
                continue

            colors = find_important_colors(image)
            if len(colors) > 1:
                #image.show()
                candidate_imgs = []
                for color in colors:
                    img = pick_color_image(image, color)
                    #img.show()
                    candidate_imgs.append(img)
                candidate_imgs = sort_candidate_imgs(candidate_imgs)
                for img in candidate_imgs:
                    _images.append(img)
            else:
                _images.append(image)

    return _images

def sort_candidate_imgs(candidate_imgs):
    sort = {}
    for index in range(len(candidate_imgs)):
        img = candidate_imgs[index]
        (width, height) = img.size
        sum=0; cnt=0
        for j in range(height):
            for i in range(width):
                p = img.getpixel((i,j))
                if p != BACKGROUND:
                    cnt += 1
                    sum += i
        avg = (int)(sum/cnt)
        sort[index] = avg
    print sort
    sorted_x = sorted(sort.iteritems(), key=operator.itemgetter(1))
    print sorted_x
    _candidate_imgs=[]
    for index,avg in sorted_x:
        _candidate_imgs.append(candidate_imgs[index])
    return _candidate_imgs


def pick_color_image(im, color):
    (width, height) = im.size
    data = im.getdata()
    data1 = []
    for p in data:
        if p == color:
            data1.append(p)
        else:
            data1.append(BACKGROUND)
    bmp = Image.new("RGB", (width, height))
    bmp.putdata(data1)
    # bmp.show()
    return bmp


def find_important_colors(im):
    (width, height) = im.size
    data = im.getdata()
    colors = {}
    for p in data:
        if p == BACKGROUND:
            continue
        if colors.has_key(p):
            colors[p] += 1
        else:
            colors[p] = 1
    num = len(colors)
    total = 0
    for p in colors.keys():
        total += colors[p]
    avg = total/num

    important_colors = []
    for p in colors.keys():
        if colors[p] > avg/2:
            important_colors.append(p)

    return important_colors

def erease_line(im):
    (width, height) = im.size
    white = (255,255,255)
    data1 = []
    data = im.getdata()
    n = 0
    for p in data:
        line = False
        i = (int)(n % width)
        j = (int)(n / width)
        # print i,j
        if im.getpixel((i,j)) != white:
            ps = [im.getpixel((i,mj)) for mj in [j-2,j-1,j,j+1,j+2] if mj>=0 and mj<=height-1]
            # print ps
            if len(ps) == 5:
                # if ps[0]==white and ps[4]==white and white in [ps[1],ps[3]] and ps[2] in [ps[1],ps[3]]:
                if ps[0]==white and ps[4]==white and white in [ps[1],ps[3]]:
                    #print i,j,ps
                    line = True
                elif ps[1] == white and ps[3] == white:
                    line = True
            # elif len(ps) == 4:
            #     if ps.count(white) >= 2 and ps.count(im.getpixel((i, j))) >= 1:
            #         line = True
            elif ps.count(white) >= 2:
                    #print i,j,ps
                    line = True
        if line is False:
            data1.append(p)
        else:
            data1.append(white)

        n += 1

    bmp = Image.new("RGB", (width, height))
    bmp.putdata(data1)
    return bmp

def erease_noise(im, window=9):
    (width, height) = im.size
    white = (255, 255, 255)
    pxs = []
    for i in range(window/2,width-window/2):
        for j in range(window/2,height-window/2):
            bound = 0
            inner = 0
            for mi in [si for si in range(i-window/2,i+window/2+1)]:
                bk = False
                for mj in [sj for sj in range(j-window/2,j+window/2+1)]:
                    p = im.getpixel((mi, mj))
                    dis = _calc_distance(white, p)
                    if mi == i-window/2 or mi == i+window/2 or mj == j-window/2 or mj == j+window/2:
                        if dis > 0:
                            bk = True
                            break
                        bound += dis
                    else:
                        inner += dis
                if bk is True:
                    bound = 1
                    break
            if bound == 0 and inner > 0:
                for mi in [si for si in range(i-window/2+1, i+window/2)]:
                    for mj in [sj for sj in range(j-window/2+1, j+window/2)]:
                        if [mi,mj] not in pxs:
                            pxs.append([mi,mj])
    # print pxs
    bmp = set_white(im,pxs)
    return bmp

def set_white(im, white_pxs):
    (width, height) = im.size
    white = (255, 255, 255)
    data1 = []
    data = im.getdata()
    n = 0
    for p in data:
        i = (int)(n % width)
        j = (int)(n / width)
        if [i,j] in white_pxs:
            # print "to be white!"
            data1.append(white)
        else:
            data1.append(p)
        n += 1
    bmp = Image.new("RGB", (width, height))
    bmp.putdata(data1)
    return bmp


def cut_image_top_bottom_margin(im):
    (width, height) = im.size
    data = im.getdata()
    data1 = []
    h = 0
    for j in range(height):
        need = False
        for i in range(width):
            if data[j*width + i] != BACKGROUND:
                need = True
                break
        if need:
            h += 1
            for i in range(width):
                data1.append(data[j*width + i])
    bmp = Image.new("RGB", (width, h))
    bmp.putdata(data1)
    return bmp


def cut_image_margin(im):
    im = cut_image_top_bottom_margin(im)
    im = im.rotate(90, expand=1)
    im = cut_image_top_bottom_margin(im)
    im = im.rotate(-90, expand=1)
    return im


def black(im):
    (width, height) = im.size
    data = im.getdata()
    data1 = []
    for p in data:
        if p != BACKGROUND:
            data1.append((0,0,0))
            #data1.append(BACKGROUND)
        else:
            data1.append(BACKGROUND)
            #data1.append((0,0,0))
    bmp = Image.new("RGB", (width, height))
    bmp.putdata(data1)
    return bmp

def revert_color(im):
    (width, height) = im.size
    data = im.getdata()
    data1 = []
    for p in data:
        if p != BACKGROUND:
            #data1.append((0,0,0))
            data1.append(BACKGROUND)
        else:
            #data1.append(BACKGROUND)
            data1.append((0,0,0))
    bmp = Image.new("RGB", (width, height))
    bmp.putdata(data1)
    return bmp


def rotate(im):
    (width, height) = im.size
    best = im
    for i in range(-15, 15):
        imnew = revert_color(im)
        imnew = imnew.rotate(i, expand=1)
        imnew = revert_color(imnew)
        imnew = cut_image_margin(imnew)
        #imnew.show()
        (newwidth, newheight) = imnew.size
        if newwidth < width:
            width = newwidth
            best = imnew
    return best


def convert_2_tiff(source, dest):
    os.system("convert %s -bordercolor white -border 10x10 %s" % (source, dest))

def tesseract(img_file):
    os.system("tesseract -l eng -psm 10 %s %s" % (img_file,img_file))

def get_character(img_file):
    f_name = "%s.txt" % img_file
    f = open(f_name)
    content = f.readline()
    f.close()
    if content != "\r":
        return content.strip()
    return None


def process(image_path):
    org_im = Image.open(image_path)
    im = erease_background(org_im)
    im = fill_main_color(im)
    #im.show()
    for i in range(2):
        im = erease_line(im)
        im = im.rotate(90, expand=1)
        im = erease_line(im)
        im = im.rotate(-90, expand=1)
        #im.show()
    im = erease_noise(im)
    #im.show()

    test_image = Image.new("RGB", (400,200))
    test_image.paste((150,150,150),(0,0,400,200))
    test_image.paste(org_im, (0,0))
    images = split_numbers(im)
    i = 0
    flag = True
    result = ""
    for img in images:
        img = cut_image_margin(img)
        img = black(img)
        #img = rotate(img)
        source = "output/%s.png" % (i+1)
        dest = "output/%s.tiff" % (i+1)
        img.save(source)
        convert_2_tiff(source, dest)
        tesseract(dest)
        c = get_character(dest)
        if c is None:
            flag = False
            result += "*"
        else:
            if c == ":":
                c = "B"
            result += c
        #img.show()
        test_image.paste(img, (50*i, 100))
        #time.sleep(1)
        i += 1
        pass

    draw = ImageDraw.Draw(test_image)
    font = ImageFont.truetype('Arial.ttf', 36)
    draw.text((10,150),result, fill=(0,0,0), font=font)
    # test_image.show()

    # if flag:
    #     print "Good: ", result
    # else:
    #     print "Bad: ", result

    return (test_image, result)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        image_path = sys.argv[1]
        test_image, result = process(image_path)
        test_image.show()
    else:
        for i in range(74):
            image_path = "../crawler/beian/vfimg/%s.jpeg" % i
            test_image, result = process(image_path)
            # test_image.save("result/result%02d.png" % i)
            print result


