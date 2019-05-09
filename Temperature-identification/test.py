#-*-encoding:utf-8-*-
import pytesseract
from PIL import Image
import os
import sys
sys.setrecursionlimit(100000)

testlist=[] #存文件名
text=[] #存温度值

# 分别记录两种字体温度显示位置,各自包括整数位和小数位
croplight=[[581, 196, 600, 230],[525, 196, 577, 230]]
cropbold=[[578, 227, 607, 257],[503, 227, 570, 257]]

#最适合的阈值进行图像二值化
threshold = 235
table = []
for i in range(256):
    if i < threshold:
        table.append(0)
    else:
        table.append(1)

#整体图像温度识别函数
def recognize(img,filename,cropparameter):
    # 特定位置截取整数位和小数位，并识别
    img_c1 = img.crop(cropparameter[0])
    text_c1 = handle(img_c1, filename, "_1")
    img_c2 = img.crop(cropparameter[1])
    text_c2 = handle(img_c2, filename, "_2")
    # 结合小数点
    if text_c1 == "" or text_c2 == "":
        return "无温度"

    else:
        temperature = (text_c2 + "." + text_c1 + "°C").replace(' ', '')
        return temperature

#局部识别处理函数
def handle(img,f,x):
    # 灰度化
    img_L = img.convert("L")
    #二值化
    img_L1 = img_L.point(table, '1')
    #去大面积边界噪声
    for i in range(img_L1.width):
        if img_L1.getpixel((i, 0)) == 1:
            expand(img_L1, i, 0)
        if img_L1.getpixel((i, img_L1.height - 1)) == 1:
            expand(img_L1, i, img_L1.height - 1)
    for j in range(img_L1.height):
        if img_L1.getpixel((0, j)) == 1:
            expand(img_L1, 0, j)
        if img_L1.getpixel((img_L1.width - 1, j)) == 1:
            expand(img_L1, img_L1.width - 1, j)
    #去除内部细粒度噪声
    depoint(img_L1)
    #img_L1.save(f+x+".jpg")
    #利用tesseract工具识别，使用自制num字库识别数字
    return pytesseract.image_to_string(img_L1, lang='num', config='-psm 6 -c tessedit_char_whitelist="-0123456789"')

#大面积边界噪声处理
def examine(img, x, y):
    width = img.width
    height = img.height
    if 0 <= x < width and 0 <= y < height:
        if img.getpixel((x, y)) == 1:
            expand(img, x, y)
def expand(img, x, y):
    img.putpixel((x, y), 0)
    examine(img, x - 1, y)
    examine(img, x + 1, y)
    examine(img, x, y - 1)
    examine(img, x, y + 1)

#内部细粒度噪声处理
def depoint(img):
    pixdata = img.load()
    w,h = img.size
    for y in range(1,h-1):
        for x in range(1,w-1):
            count = 0
            if pixdata[x,y-1] ==0:
                count = count + 1
            if pixdata[x,y+1] ==0:
                count = count + 1
            if pixdata[x-1,y] ==0:
                count = count + 1
            if pixdata[x+1,y] ==0:
                count = count + 1
            if pixdata[x-1, y - 1] == 0:
                count = count + 1
            if pixdata[x+1, y + 1] == 0:
                count = count + 1
            if pixdata[x - 1, y+1] == 0:
                count = count + 1
            if pixdata[x + 1, y-1] == 0:
                count = count + 1
            if count > 5:
                pixdata[x,y] = 0
    return img

#读取一个文件夹内的所有jpg格式和bmp格式图像
rootdir = r'C:\Users\zhy\Desktop\temperature_test'
all=os.walk(rootdir)
for path,dir,filelist in all:
    for filename in filelist:
        if filename.endswith('JPG') or filename.endswith('BMP'):
            testlist.append((path.replace(rootdir,"")+"\\"+filename).strip("\\"))

for filename in testlist:
    print (filename+'\t')
    img = Image.open(os.path.join(rootdir,filename))
    #先按照细体数字的温度显示区域截取
    temperature = recognize(img,filename,croplight)
    if temperature == "无温度":
        #未识别到则按照粗体数字的温度显示区域截取
        temperature = recognize(img, filename, cropbold)
    print (temperature+"\n")
    text.append(temperature)

# 记录图像文件名和对应识别温度，保存至txt文件
f = open(os.path.join(rootdir,"result.txt"), "w",encoding='utf-8')
for i in range (0,len(testlist)):
    f.write(str(testlist[i])+"\t"+str(text[i])+"\n")
f.close()