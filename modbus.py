'''
modbus通讯模块使用说明
为便于python进行modbus通讯模块的调用操作，预先在底层进行了封装为动态连接库。
并进一步使用ctypes模块封装为普通的python模块，具体代码可以看c++和qt代码实现。
注意：
1.为便于使用，该模块只提供连接和操作一台基础通讯模块的功能，且所有函数均可重复调用。
2.该项目使用的基础通讯模块基于RS485串口通信，因此在边缘计算网关系统上可直接使用cutecom程序
来进行硬件的调试和设置，本集成模块不包含设置功能。具体请参考设备文档和cutecom程序使用说明。
3.只有在cutecom与通讯模块通讯正常的基础上，本模块才能使用。
4.linux系统下，访问串口需要权限，因此请使用chmod指定串口权限或者提升到root权限使用本模块。
'''

#利用ctypes加载动态链接库
from ctypes import *
import time
import os
# 注意根据实际情况更改动态库所在路径
__libFile = "/ssd/libmod/libmodbusEasy.so.1.0.0"
__libc = cdll.LoadLibrary(__libFile)

# initModbus()
# 初始化通讯模块的功能，使用该模块其他函数前必须调用该函数
#无参数 无返回值
def initModbus():
    __libc.initModbus()


# freeModbus()
# 释放通讯模块占用的内存资源，释放后必须重新初始化其他函数才能工作
#无参数 无返回值
def freeModbus():
    __libc.freeModbus() 


# openModBus(portName,baudRate)
# 打开串口通信，打开成功后方可通信
# portName 串口地址，如 /dev/ttyTHS2
# baudRate 串口波特率，如 57600
# 返回bool值 True/False
def openModBus(portName, baudRate):
    charPointer = bytes(portName, "utf-8")
    __libc.openModBus.restype = c_bool
    ok = __libc.openModBus(charPointer, baudRate)
    return ok

# closeModBus()
# 关闭串口通信，关闭后需要重新打开才能通信
# 无参数，无返回值
def closeModBus():
    __libc.closeModBus()

# readIo()
#  按8位无符号整数形式获取所有IO端口的当前值(输出端口获取的将永远是0)
# 无参数
# 成功返回8位无符号整数（每一位代表一个端口号）  ；失败返回None
def readIo():
    __libc.readIo.restype = c_bool
    pv = c_ubyte()
    ok = __libc.readIo(byref(pv))
    if ok:
        return pv.value
    else:
        return None

# writeIo(alue)
# 按8位无符号整数形式设置所有IO端口的当前值(输入端口的设置将被忽略)
# 参数为0-255的8位无符号整数（每一位代表一个端口号）
# 返回bool值 True/False
def writeIo(value):
    __libc.writeIo.restype = c_bool
    pv = c_ubyte(value)
    ok = __libc.writeIo(pv)
    return ok

# readIoChannel(channelIndex)
# 读取第channelIndex个IO端口的状态
# 参数channelIndex为IO端口索引，0-7，超出范围无效
# 成功返回端口状态bool值，True高电平 False低电平；失败返回None
def readIoChannel(channelIndex):
    __libc.readIoChannel.restype = c_bool
    pv = c_bool()
    ok = __libc.readIoChannel(channelIndex, byref(pv))
    if ok:
        return pv.value
    else:
        return None

# writeIoChannel(channelIndex, value)
# 设置第channelIndex个IO端口的状态
# 参数channelIndex为IO端口索引，0-7，超出范围无效
# 参数alue为bool值，True高电平 False低电平
# 返回bool值，成功返回True，失败返回None
def writeIoChannel(channelIndex, value):
    __libc.writeIoChannel.restype = c_bool
    pv = c_bool(value)
    ok = __libc.writeIoChannel(channelIndex, pv)
    return ok


# modbus功能测试函数
def modbus_test():
    initModbus()
    ok = openModBus("/dev/ttyTHS2", 57600)
    if ok:
        print("open is ok")
        v = readIo()
        if v is None:
            print("readIo call fialed")
        else:
            print(v)
            writeIo(128)
            print(readIoChannel(7))
            time.sleep(3)
            writeIoChannel(7, False)
            print("it'ok")
            closeModBus()
    else:
        print("open error")
    freeModbus()


# modbus_test()