# -*- coding: utf-8 -*-
import os, sys
from PIL import Image, ImageDraw, ImageFont
from StringIO import StringIO

def gen_stock_image(name, code):
    WIDTH = 200
    size = int(WIDTH/len(name))
    font_file_path = os.path.join(os.path.split(os.path.realpath(__file__))[0], "hylxtj.ttf")
    font = ImageFont.truetype(font_file_path, size)
    im = Image.new("RGB", (WIDTH, WIDTH), (255, 255, 255))
    draw = ImageDraw.Draw(im)
    y = (WIDTH/2-size)*2/3
    draw.text((0, y), name, font=font, fill=(0x05,0xb8,0xbf,0))
    size = int(WIDTH/len(code)*2)
    font = ImageFont.truetype("/data/task-201606/util/hylxtj.ttf", size)
    y = WIDTH/2 + (WIDTH / 2 - size) / 3
    draw.text((0, y), code, font=font, fill=(0x05,0xb8,0xbf,0))
    output = StringIO()
    # im.resize(im.size, Image.ANTIALIAS)
    im.save(output, format="JPEG", quality=95)
    return im,output


if __name__ == '__main__':
    im,o = gen_stock_image(u"佳利达", "870397")
    #im = gen_stock_image(u"ST中搜", "430339")
    #im.show()
    im.resize(im.size, Image.ANTIALIAS)
    im.save("test.jpg", "JPEG", quality=95)