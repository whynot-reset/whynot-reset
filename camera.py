'''
camera相机模块使用说明
为便于python进行相机的调用操作，预先在底层进行了封装为动态连接库。
并进一步使用ctypes模块封装为普通的python模块，具体代码可以看c++和qt代码实现。
注意：
1.为便于使用，该模块只提供连接和操作一个相机的功能，且所有函数均可重复调用。
2.相机厂家提供的配套软件MVS，可以进行相机参数的设置及相机硬件的调试，为了取得
最好的拍照效果，需要使用配套的MVS软件进行设置以确保相机能正确的工作。
3.本模块只有在MVS能正常工作的情况下，方可正常使用。
'''

#利用ctypes加载动态链接库
from ctypes import *
import time,os
# 注意根据实际情况更改动态库所在路径
__libFile = "/ssd/libmod/libhkcameraeasy.so.1.0.0"
__libc = cdll.LoadLibrary(__libFile)

# initCamera()
# 初始化相机模块，使用该模块其他函数前必须初始化
# 无参数，无返回值
def initCamera():
    __libc.initCamera()

# freeCamera()
# 释放相机模块占用的系统资源，释放后必须重新初始化
# 无参数，无返回值
def freeCamera():
    __libc.freeCamera()

# closeCamera()
# 关闭相机通信连接
# 无参数，无返回值
def closeCamera():
    __libc.closeCamera()

# cameraIsOpened()
# 判断相机是否可用
# 无参数
# 返回值为bool值，True/False
def cameraIsOpened():
    __libc.cameraIsOpened.restype = c_bool
    ok = __libc.cameraIsOpened()
    return ok

# openCamera()
# 打开相机通信，调用前必须先调用初始化函数
# 无参数
# 返回值为bool值，True/False
def openCamera():
    __libc.openCamera.restype = c_bool
    ok = __libc.openCamera()
    return ok

# getImage(timeoutMSec)
# 请求在timeoutMSec毫秒内返回一帧图像，以字典信息返回图像信息。
# 如果超时或者请求失败，返回None
# 参数timeoutMSec 超时期限，毫秒
# 返回值字典说明：
# pData，内存中按二进制连续存储的符合BGR888图像存储格式的数据的首地址，注意该内存由模块自动维护，调用方不需要释放该内存
# dataLen，返回的图像数据的内存长度，字节数量，注意外界超出这个长度将产生异常
# w 图像宽度 h图像高度 frameNo相机获取的图像的帧序号
def getImage(timeoutMSec):
    __libc.getImage.restype =  POINTER(c_uint8)
    t=c_uint(timeoutMSec)
    w=c_uint()
    h=c_uint()
    l=c_uint()
    v = __libc.getImage(byref(t),byref(w),byref(h),byref(l))
    if v is not None:
        return {'pData':v,'w':w.value,'h':h.value,'dataLen':l.value,'frameNo':t.value}
    else:
        return None

#  getImageAsFile(timeOutMsec, dir)
#  请求以bmp图像的形式获取一帧图像，并保存到指定的目录中
#   timeoutMSec 超时设置，毫秒
#   dirName 目录名称，必须预先存在且具备增加文件权限，如 /ssd/imgs
#   如果成功，返回图像文件的完整路径，否则返回None
def getImageAsFile(timeoutMSec,dirName):
    dir=dirName.encode("utf-8")
    __libc.getImageAsFile.restype = c_char_p
    n = c_int(timeoutMSec)
    v = __libc.getImageAsFile(byref(n),dir)
    if v is not None:
        return str(v, encoding = "utf-8")  
    else:
        return None

# 相机模块测试函数
def camera_test():
    print("123")
    initCamera()
    openCamera()
    ok = cameraIsOpened()
    if ok:
        img_ifno = getImage(500)
        if img_ifno is None:
            print('get image fial')
        else:
            print(img_ifno)
    else:
        print("camera is not opened")
    closeCamera()
    freeCamera()

#camera_test()
