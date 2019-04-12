#-*-encoding:utf-8-*-
import pytesseract
from PIL import Image
import os

testlist=[]
text=[]
threshold = 235
table = []
# 分别记录jpg格式红外图和bmp位图中方框温度所在位置
croplist=[[525, 196, 600, 230],[503, 227, 607, 257]]
#最适合的阈值进行图像二值化
for i in range(256):
    if i < threshold:
        table.append(0)
    else:
        table.append(1)

#读取一个文件夹内的所有jpg格式和bmp格式图像
rootdir = 'C:\\Users\\zhy\\Desktop\\JZ25-1SCEP红外图像'
all=os.walk(rootdir)
for path,dir,filelist in all:
    for filename in filelist:
        if filename.endswith('JPG') or filename.endswith('BMP'):
            testlist.append(filename)

for filename in testlist:
    if filename.endswith('JPG'):
        cropparameter=croplist[0]
    else:
        cropparameter=croplist[1]
    img = Image.open(os.path.join(rootdir,filename))
    # 特定位置截取
    img_c= img.crop(cropparameter)
    # 灰度化
    img_cL = img_c.convert("L")
    #二值化
    img_cL1 = img_cL.point(table, '1')
    #img_cL1.save(filename+".jpg")
    # 读取数字，使用自制num字库,只识别0-9
    # 无视小数点是因为防止噪声被误识别为小数点导致混乱
    text1 = pytesseract.image_to_string(img_cL1, lang='num', config='-psm 6 -c tessedit_char_whitelist="0123456789"')
    # 小数点部分可能被识别为空格或无，手动替换
    try:
        text.append(text1.split()[0] + "." + text1.split()[1] + "°C")
    except:
        if len(text)>1:
            text.append(text1[0:-1]+"."+text1[-1]+ "°C")
        else:
            # 可能有图片没有温度记录，直接保存为空
            text.append(text1)
# 记录图像文件名和对应识别温度
f = open(os.path.join(rootdir,"result.txt"), "w",encoding='utf-8')
for i in range (0,len(testlist)):
    f.write(str(testlist[i])+"\t"+str(text[i])+"\n")
f.close()