from ctypes import *
from os import path
import time,os
import numpy as np
import math
import random
import glob
import cv2

__libFile = "/ssd/libmod/libimgprocess.so.1.0.0"
__libc = cdll.LoadLibrary(__libFile)

	# //使用SVM训练用户自定义的特征；
	# //feaSavefile每一个样本特征保存在文件中的一行
	# //typeSavefile样本的类型，使用OK/NG表示
	# bool train_svm(char *feaSavefile, char *typeSavefile, char *xmlFile);
def train_svm(feaSavefile: str, typeSavefile: str, xmlFile: str) -> bool:
    __libc.train_svm.restype = c_bool
    return __libc.train_svm(bytes(feaSavefile, "utf-8"), bytes(typeSavefile, "utf-8"), bytes(xmlFile, "utf-8"))

	# //根据训练好的特征分类文件xml, 对当前的特征文件feaFile进行分类，结果存储在typeFile中
	# 	bool predict_svm(char *feaFile, char *xml, char *typeFile);
def predict_svm(feaFile: str, xml: str,typeFile: str) -> bool:
    __libc.predict_svm.restype = c_bool
    return __libc.predict_svm(bytes(feaFile, "utf-8"), bytes(xml, "utf-8"), bytes(typeFile, "utf-8"))

#添加椒盐噪声
def sp_noise(image,prob,imgDst):
    '''
    添加椒盐噪声
    prob:噪声比例 
    '''
    img = cv2.imread(image)
    output = np.zeros(img.shape,np.uint8)
    thres = 1 - prob 
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            rdn = random.random()
            if rdn < prob:
                output[i][j] = 0
            elif rdn > thres:
                output[i][j] = 255
            else:
                output[i][j] = img[i][j]
    cv2.imwrite(imgDst,output)
    return True

def gasuss_noise(img, mean, var,imgDst):
    ''' 
        添加高斯噪声
        mean : 均值 0
        var : 方差0.01
    '''
    image=cv2.imread(img)
    image = np.array(image/255, dtype=float)
    noise = np.random.normal(mean, var ** 0.5, image.shape)
    out = image + noise
    if out.min() < 0:
        low_clip = -1.
    else:
        low_clip = 0.
    out = np.clip(out, low_clip, 1.0)
    out = np.uint8(out*255)
    cv2.imwrite(imgDst,out)
    return True

# 模块1、 图像平滑去噪模块
# 01.图像中值平滑滤波
# bool smooth_mediafilter(char *imgSrc, int wndSize, char *imgDst);


def smooth_mediafilter(imgSrc: str, wndSize: int, imgDst: str) -> bool:
    img = cv2.imread(imgSrc,cv2.IMREAD_COLOR)
    if img is None:
        print("smooth_mediafilter()函数 图像为空")
        return False
    print(img)
    imgSmooth = cv2.medianBlur(img,wndSize)
    cv2.imwrite(imgDst,imgSmooth)
    return True



# 02.图像高斯平滑滤波
# bool smooth_gaussianfilter(char *imgSrc, int wndSize, double sigma, char *imgDst);


def smooth_gaussianfilter(imgSrc: str, wndSize: int, sigma: float, imgDst: str) -> bool:
    img = cv2.imread(imgSrc,cv2.IMREAD_COLOR)
    if img is None:
        print("smooth_gaussianfilter()函数 图像为空")
        return False
    imgSmooth = cv2.GaussianBlur(img,(wndSize,wndSize),sigma)
    cv2.imwrite(imgDst,imgSmooth)
    return True
    

# 03.图像均值滤波
def smooth_meanfilter(imgSrc: str, wndSize: int, imgDst: str) -> bool:
    img = cv2.imread(imgSrc, cv2.IMREAD_COLOR)
    if img is None:
        print("smooth_mediafilter()函数 图像为空")
        return False
    imgSmooth=cv2.blur(img,(wndSize,wndSize))
    cv2.imwrite(imgDst,imgSmooth)
    return True


# 04.图像双边滤波
def smooth_bilateralfilter(imgSrc: str, d: int, sigmaColor: float, sigmaSpace: float, imgDst: str) -> bool:
    img = cv2.imread(imgSrc,0)
    if img is None:
        print("smooth_bilateralfilter()函数 图像为空")
        return False
    imgSmooth = cv2.bilateralFilter(img,d,sigmaColor,sigmaSpace)
    cv2.imwrite(imgDst,imgSmooth)
    return True

# 模块2、 图像增强模块
# 05.图像光照均衡增强
def unevenLightCompensate_core(img,blockSize):
    if img.ndim == 3:
	    imgDst = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
 	    imgDst = img.copy()
    print(imgDst[0])
    average = cv2.mean(imgDst)[0]
    rows = imgDst.shape[0]
    cols = imgDst.shape[1]
    rows_new = math.ceil(rows)//blockSize
    cols_new = math.ceil(cols)//blockSize
    #创建全0矩阵
    blockImage = np.zeros((rows_new,cols_new),dtype=np.float32)
    for i in range(0,rows_new):
        for j in range(0,cols_new):
            rowmin = i*blockSize
            rowmax = (i+1)*blockSize
            if rowmax > rows:
                rowmax = rows
            colmin = j * blockSize
            colmax = (j+1)*blockSize
            if colmax > cols:
                colmax = cols
            imageROI = imgDst[rowmin:rowmax,colmin:colmax]
            temaver = np.mean(imageROI)
            blockImage[i,j]=temaver
    blockImage = blockImage - average
    blockImage2 = cv2.resize(blockImage,(cols,rows),cv2.INTER_CUBIC)
    image2 = imgDst.astype(np.float32)
    dst = image2 - blockImage2
    dst = dst.astype(np.uint8)
    return dst
    
        
def unevenLightCompensate(imgSrc:str, blockSize:int,imgDst:str):
    img=cv2.imread(imgSrc,cv2.IMREAD_COLOR)
    if img is None:
        print("unevenLightCompensate()函数 图像为空")
        return False
    if len(img.shape) == 2:		
        matimgDst = unevenLightCompensate_core(img,blockSize)
    elif  len(img.shape) == 3:	
        channels = img.shape[2]	#第三维度表示通道，应为3
        #rgb图像转换为hsv图像
        image_hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
        #分离hsv彩色图像的h,s,v三通道
        channels = cv2.split(image_hsv)
        channels1 = channels[0]
        channels2 = channels[1]
        channels3 = channels[2]
        #只对v通道亮度空间进行光照均衡
        channel_new=unevenLightCompensate_core(channels3, blockSize)
        img=cv2.merge([channels1,channels2,channel_new])
        matimgDst = cv2.cvtColor(img,cv2.COLOR_HSV2BGR)
    else:	#异常维度，不是图片了
        return False
    cv2.imwrite(imgDst,matimgDst)
    return True




# 06.图像laplas算子增强
# bool enhance_laplas(char *imgSrc, char *imgDst);


def enhance_laplas(imgSrc: str, imgDst: str) -> bool:
    img = cv2.imread(imgSrc,0)   
    dst = cv2.Laplacian(img,cv2.CV_16S,ksize=3)   
    dst = cv2.convertScaleAbs(dst)
    cv2.imwrite(imgDst,dst)
    return True
# 07.图像对数log增强
# bool enhance_log(char *imgSrc, char *imgDst);


def enhance_log(img: str, c,imgDst: str) -> bool:
    imgSrc = cv2.imread(img)
    imgSrc = imgSrc.astype(np.float32)
    output_img = c*np.log(1.0+imgSrc)
    output_img = np.uint8(output_img+0.5)
    cv2.imwrite(imgDst,output_img)
    return True

# 08.图像gamma增强  gamma = [0, 10]
def enhance_gamma(imgSrc: str, gamma: float, imgDst: str) -> bool:
    img = cv2.imread(imgSrc,1)
    if img is None:
        print("enhance_gamma()函数 图像为空")
        return False
    imageGamma= img.astype(np.float32)
    imageGamma=np.clip(imageGamma, 0, 255) 
    img = cv2.pow(imageGamma,gamma)
    imageGamma = img.astype(np.uint8)
    cv2.imwrite(imgDst,imageGamma)
    return True


# 09.图像开运算
def enhance_open(imgSrc: str, size: int, imgDst: str) -> bool:
    img = cv2.imread(imgSrc,1)
    if img is None:
        print("enhance_close()函数 图像为空")
        return False
    element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (size, size))
    dstImage=cv2.morphologyEx(img, cv2.MORPH_OPEN, element)
    cv2.imwrite(imgDst, dstImage)
    return True

# 10.图像闭运算
def enhance_close(imgSrc: str, size: int, imgDst: str) -> bool:
    img = cv2.imread(imgSrc,1)
    if img is None:
        print("enhance_close()函数 图像为空")
        return False
    element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (size, size))
    dstImage=cv2.morphologyEx(img, cv2.MORPH_CLOSE, element)
    cv2.imwrite(imgDst, dstImage)
    return True


# 模块3、 图像边缘轮廓检测模块
# 11.图像Canny算子边缘检测
def edge_canny(imgSrc: str, lowTh: float, highTh: float, imgDst: str):
    img = cv2.imread(imgSrc,0)
    if img is None:
        print("edge_canny()函数 图像为空")
        return False
    imgEdge = cv2.Canny(img,lowTh,highTh)
    cv2.imwrite(imgDst,imgEdge)
    return True
    

# 12.图像Sobel算子边缘检测
def edge_sobel(imgSrc: str,  imgDst: str) -> bool:
    img = cv2.imread(imgSrc,cv2.IMREAD_COLOR)
    if img is None:
        print("edge_sobel()函数 图像为空")
        return False
    grad_x = cv2.Sobel(img,cv2.CV_16S,1,0)
    abs_grad_x = cv2.convertScaleAbs(grad_x)
    grad_y = cv2.Sobel(img,cv2.CV_16S,0,1)
    abs_grad_y = cv2.convertScaleAbs(grad_y)
    imgEdge = cv2.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)
    cv2.imwrite(imgDst, imgEdge)
    return True

    

    


# 模块4、 特征提取与分类器设计模块
# 4.1 使用4种分类器训练hog特征
# bool train_knn_hog(char *imgOk, char *imgNG, char *xml);


def train_knn_hog(imgOk: str, imgNG: str, xml: str) -> bool:
    __libc.train_knn_hog.restype = c_bool
    return __libc.train_knn_hog(bytes(imgOk, "utf-8"), bytes(imgNG, "utf-8"), bytes(xml, "utf-8"))

# bool train_svm_hog(char *imgOk, char *imgNG, char *xml);


def train_svm_hog(imgOk: str, imgNG: str, xml: str) -> bool:
    __libc.train_svm_hog.restype = c_bool
    return __libc.train_svm_hog(bytes(imgOk, "utf-8"), bytes(imgNG, "utf-8"), bytes(xml, "utf-8"))

# bool train_adaboost_hog(char *imgOk, char *imgNG, char *xml);


def train_adaboost_hog(imgOk: str, imgNG: str, xml: str) -> bool:
    __libc.train_adaboost_hog.restype = c_bool
    return __libc.train_adaboost_hog(bytes(imgOk, "utf-8"), bytes(imgNG, "utf-8"), bytes(xml, "utf-8"))

# bool train_randomTrees_hog(char *imgOk, char *imgNG, char *xml);


def train_randomTrees_hog(imgOk: str, imgNG: str, xml: str) -> bool:
    __libc.train_randomTrees_hog.restype = c_bool
    return __libc.train_randomTrees_hog(bytes(imgOk, "utf-8"), bytes(imgNG, "utf-8"), bytes(xml, "utf-8"))

# 4.2 使用4种分类器训练颜色直方图特征
# bool train_knn_histgram(char *imgOk, char *imgNG, char *xml);


def train_knn_histgram(imgOk: str, imgNG: str, xml: str) -> bool:
    __libc.train_knn_histgram.restype = c_bool
    return __libc.train_knn_histgram(bytes(imgOk, "utf-8"), bytes(imgNG, "utf-8"), bytes(xml, "utf-8"))

# bool train_svm_histgram(char *imgOk, char *imgNG, char *xml);


def train_svm_histgram(imgOk: str, imgNG: str, xml: str) -> bool:
    __libc.train_svm_histgram.restype = c_bool
    return __libc.train_svm_histgram(bytes(imgOk, "utf-8"), bytes(imgNG, "utf-8"), bytes(xml, "utf-8"))

# bool train_adaboost_histgram(char *imgOk, char *imgNG, char *xml);


def train_adaboost_histgram(imgOk: str, imgNG: str, xml: str) -> bool:
    __libc.train_adaboost_histgram.restype = c_bool
    return __libc.train_adaboost_histgram(bytes(imgOk, "utf-8"), bytes(imgNG, "utf-8"), bytes(xml, "utf-8"))

# bool train_randomTrees_histgram(char *imgOk, char *imgNG, char *xml);


def train_randomTrees_histgram(imgOk: str, imgNG: str, xml: str) -> bool:
    __libc.train_randomTrees_histgram.restype = c_bool
    return __libc.train_randomTrees_histgram(bytes(imgOk, "utf-8"), bytes(imgNG, "utf-8"), bytes(xml, "utf-8"))

# 4.3 使用4种分类器训练glcm纹理特征
# bool train_knn_glcm(char *imgOk, char *imgNG, char *xml);


def train_knn_glcm(imgOk: str, imgNG: str, xml: str) -> bool:
    __libc.train_knn_glcm.restype = c_bool
    return __libc.train_knn_glcm(bytes(imgOk, "utf-8"), bytes(imgNG, "utf-8"), bytes(xml, "utf-8"))

# bool train_svm_glcm(char *imgOk, char *imgNG, char *xml);


def train_svm_glcm(imgOk: str, imgNG: str, xml: str) -> bool:
    __libc.train_svm_glcm.restype = c_bool
    return __libc.train_svm_glcm(bytes(imgOk, "utf-8"), bytes(imgNG, "utf-8"), bytes(xml, "utf-8"))

# bool train_adaboost_glcm(char *imgOk, char *imgNG, char *xml);


def train_adaboost_glcm(imgOk: str, imgNG: str, xml: str) -> bool:
    __libc.train_adaboost_glcm.restype = c_bool
    return __libc.train_adaboost_glcm(bytes(imgOk, "utf-8"), bytes(imgNG, "utf-8"), bytes(xml, "utf-8"))

# bool train_randomTrees_glcm(char *imgOk, char *imgNG, char *xml);


def train_randomTrees_glcm(imgOk: str, imgNG: str, xml: str) -> bool:
    __libc.train_randomTrees_glcm.restype = c_bool
    return __libc.train_randomTrees_glcm(bytes(imgOk, "utf-8"), bytes(imgNG, "utf-8"), bytes(xml, "utf-8"))

# 4.4 使用4种分类器训练elbp局部二值模式特征
# bool train_knn_elbp(char *imgOk, char *imgNG, char *xml);


def train_knn_elbp(imgOk: str, imgNG: str, xml: str) -> bool:
    __libc.train_knn_elbp.restype = c_bool
    return __libc.train_knn_elbp(bytes(imgOk, "utf-8"), bytes(imgNG, "utf-8"), bytes(xml, "utf-8"))

# bool train_svm_elbp(char *imgOk, char *imgNG, char *xml);


def train_svm_elbp(imgOk: str, imgNG: str, xml: str) -> bool:
    __libc.train_svm_elbp.restype = c_bool
    return __libc.train_svm_elbp(bytes(imgOk, "utf-8"), bytes(imgNG, "utf-8"), bytes(xml, "utf-8"))

# bool train_adaboost_elbp(char *imgOk, char *imgNG, char *xml);


def train_adaboost_elbp(imgOk: str, imgNG: str, xml: str) -> bool:
    __libc.train_adaboost_elbp.restype = c_bool
    return __libc.train_adaboost_elbp(bytes(imgOk, "utf-8"), bytes(imgNG, "utf-8"), bytes(xml, "utf-8"))

# bool train_randomTrees_elbp(char *imgOk, char *imgNG, char *xml);


def train_randomTrees_elbp(imgOk: str, imgNG: str, xml: str) -> bool:
    __libc.train_randomTrees_elbp.restype = c_bool
    return __libc.train_randomTrees_elbp(bytes(imgOk, "utf-8"), bytes(imgNG, "utf-8"), bytes(xml, "utf-8"))

# 4.5 使用4种分类器训练gabor纹理特征
# bool train_knn_garbor(char *imgOk, char *imgNG, char *xml);


def train_knn_garbor(imgOk: str, imgNG: str, xml: str) -> bool:
    __libc.train_knn_garbor.restype = c_bool
    return __libc.train_knn_garbor(bytes(imgOk, "utf-8"), bytes(imgNG, "utf-8"), bytes(xml, "utf-8"))

# bool train_svm_garbor(char *imgOk, char *imgNG, char *xml);


def train_svm_garbor(imgOk: str, imgNG: str, xml: str) -> bool:
    __libc.train_svm_garbor.restype = c_bool
    return __libc.train_svm_garbor(bytes(imgOk, "utf-8"), bytes(imgNG, "utf-8"), bytes(xml, "utf-8"))

# bool train_adaboost_garbor(char *imgOk, char *imgNG, char *xml);


def train_adaboost_garbor(imgOk: str, imgNG: str, xml: str) -> bool:
    __libc.train_adaboost_garbor.restype = c_bool
    return __libc.train_adaboost_garbor(bytes(imgOk, "utf-8"), bytes(imgNG, "utf-8"), bytes(xml, "utf-8"))

# bool train_randomTrees_garbor(char *imgOk, char *imgNG, char *xml);


def train_randomTrees_garbor(imgOk: str, imgNG: str, xml: str) -> bool:
    __libc.train_randomTrees_garbor.restype = c_bool
    return __libc.train_randomTrees_garbor(bytes(imgOk, "utf-8"), bytes(imgNG, "utf-8"), bytes(xml, "utf-8"))

# 原始图像，模板图像，相似度，定位到的PCB图像
# 	bool pcb_location(	char *imgSrc, 	char *imgTemplate,	double similar, 	const int xshift,	const int yshift,	const int width,	const int height,	char *imgPCB);


def match_pcb(img:str,template:str,threshold:int,xshift:int,yshift:int,twudth,hh,imgDst):
    imgSrc=cv2.imread(img)
    imgtemplate=cv2.imread(template)
    #执行模板匹配，采用的匹配方式cv2.TM_SQDIFF_NORMED
    result = cv2.matchTemplate(imgSrc,imgtemplate,cv2.TM_CCOEFF_NORMED )
    #寻找矩阵（一维数组当做向量，用Mat定义）中的最大值和最小值的匹配结果及其位置
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if max_val < threshold:
        return False
    else:
        #匹配值转换为字符串
        #对于cv2.TM_SQDIFF及cv2.TM_SQDIFF_NORMED方法min_val越趋近与0匹配度越好，匹配位置取min_loc
        #对于其他方法max_val越趋近于1匹配度越好，匹配位置取max_loc
        strmin_val = str(max_val)
        imgSrc = imgSrc[max_loc[1]+yshift:max_loc[1]+yshift+hh,max_loc[0]+xshift:max_loc[0]+xshift+twudth]
        cv2.imwrite(imgDst,imgSrc)
        return True




# 识别当前图像是否存在缺陷，选择的特征提取方法featureName, 分类器classfyName
# classfyName 分类器类型 “knn”  “svm”      “adaboost”  “randomtrees”
# featureName 特征类型   “hog”  “histgram” “glcm”  “elbp”   “garbor”
# bool predict(char *imgSrc, char *rectTxt, char *xml, char *classfyName, char *featureName, char *saveBMPfile, char *posFile);


def predict(imgSrc: str, rectTxt: str, xml: str, classfyName: str, featureName: str, saveBMPfile: str, posFile: str) -> bool:
    __libc.predict.restype = c_bool
    return __libc.predict(bytes(imgSrc, "utf-8"), bytes(rectTxt, "utf-8"), bytes(xml, "utf-8"), bytes(classfyName, "utf-8"), bytes(featureName, "utf-8"), bytes(saveBMPfile, "utf-8"), bytes(posFile, "utf-8"))



def imgProc(img1):
    # 步骤1：读取PCB图像,图像预处理，光照均衡等操作。此处省略
    # 步骤2： 模板匹配定位到PCB
    t1= time.perf_counter()
    imgPCB = "/ssd/libmod/pcb.bmp"
    img2 = "/ssd/libmod/Configures/img_template.bmp"
    bRet = match_pcb(img1,img2,-1106,-1951,2900,2128,imgPCB)
    t2=time.perf_counter()
    print("pcb定位用时 %6.3f"% (t2-t1))
    if bRet==False :
        print("PCB板定位失败！")
        return None
    # 判读零件1的缺陷,使用  （knn - histgram）组合
    if  True:
        # 特征提取.定义ok, ng两种类型训练数据路径
        imgOk = "/ssd/libmod/Configures/part1/ok/"
        imgNG = "/ssd/libmod/Configures/part1/ng/"
        # 使用knn训练hog特征
        xmlFile = "/ssd/libmod/knn_histgram.xml"

        # true 为重新训练，否则使用已经训练好的模型参数
        if False:
            # 使用knn训练histgram颜色直方图特征
            train_knn_histgram(imgOk, imgNG, xmlFile)
           
        # 读取离线标定好的零件1的位置,
        rectTxt = "/ssd/libmod/Configures/roi/rect1.txt"
        posName="/ssd/libmod/%6d.txt"% (t1)
        # 加载离线训练好的模型
        bRet=predict(imgPCB, rectTxt, xmlFile, "knn", "histgram", "/ssd/libmod/results1.bmp", posName)    
        if (False == bRet):
            print("PCB检测part2失败!")
            return None

    return  "/ssd/libmod/results1.bmp",posName
    # print("part用时 %6.3f"% (t3-t2))
	#判读零件2的缺陷,使用  （svm_histgram）组合
    # if True:
    #     # 特征提取.定义ok, ng两种类型训练数据路径
    #     imgOk = "/ssd/libmod/Configures/part2/ok/"
    #     imgNG = "/ssd/libmod/Configures/part2/ng/"
    #     # 使用svm训练hog特征
    #     xmlFile = "/ssd/libmod/svm_histgram.xml"

    #     # true 为重新训练，否则使用已经训练好的模型参数
    #     if True:
    #         # 使用svm训练hog特征
    #         train_svm_histgram(imgOk, imgNG, xmlFile)

    #     # 读取离线标定好的零件2的位置,
    #     rectTxt = "/ssd/libmod/Configures/roi/rect2.txt"
    #     posName="/ssd/libmod/%6d.txt"% (t1)
    #     # 加载离线训练好的模型
    #     bRet=predict(imgPCB, rectTxt, xmlFile, "svm", "histgram", "/ssd/libmod/results2.bmp", posName)
    #     if (False == bRet):
    #         print("PCB检测part1失败!")
    #         return None
    t4=time.perf_counter()
    print("part2用时 %6.3f ,图像处理整体用时%6.3f"% (t4-t3,t4-t1))

    return  "/ssd/libmod/results1.bmp",posName