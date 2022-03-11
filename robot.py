'''
机械臂模块使用说明
为便于python进行机械臂的调用操作，预先在底层进行了封装为动态连接库。
并进一步使用ctypes模块封装为普通的python模块，具体代码可以看c++和qt代码实现。
注意：
1.为便于使用，该模块只提供连接和操作一台机械臂的功能，且所有函数均可重复调用。
2.该项目使用的机械臂通讯模块基于usb转RS232串口进行通信，且机械臂厂家提供了可在windows下使用的专用软件
来进行硬件的调试，本集成模块仅仅包含必要的功能。更多功能请参考设备文档和c++和Qt代码。
3.只有在机械臂工作正常的基础上，本模块才能使用。
4.linux系统下，访问串口需要权限，因此请使用chmod指定串口权限或者提升到root权限使用本模块。
'''

#利用ctypes加载动态链接库
from ctypes import *
from PyQt5.QtWidgets import qApp
import time,os
# 注意根据实际情况更改动态库所在路径
__libFile = "/ssd/libmod/librobotControl.so.1.0.0"
__libc = cdll.LoadLibrary(__libFile)
__delayTime = 0.05



# freeRobot()
# 释放该模块使用的一切资源，释放后需要重新初始化
# 无参数，无返回值
def freeRobot():
    __libc.freeRobot()

# initRobot()
# 初始化该模块所需的资源，初始化后方可使用其他函数
# 无参数，无返回值
def initRobot():
    __libc.initRobot()

# closeRobotControl()
# 关闭与机器人的通信，关闭后需要重新打开方可通信
#  无参数，无返回值
def closeRobotControl():
    __libc.closeRobotControl()



# clearControlQuenes()
# 清空器械臂剩余未执行的对列指令，当前正在执行的指令会继续执行
#  无参数
# 返回bool值，True /False 表明函数是否执行成功
def clearControlQuenes():
    __libc.clearControlQuenes.restype = c_bool
    ok = __libc.clearControlQuenes()
    time.sleep(__delayTime)
    return ok

# robotIsError()
# 检查机械臂是否处于故障状态
# 无参数
# 返回bool值，True/False ，Ture表示有故障
def robotIsError():
    __libc.robotIsError.restype = c_bool
    ok = __libc.robotIsError()
    time.sleep(__delayTime)
    return ok

# openRobotControl(portName,baudRate)
# 打开和机械臂的串口通信，打开成功后方可通信
# portName 串口地址，/dev/ttyUSB4或者/dev/ttyUSB5
# baudRate 串口波特率， 115200
# 返回bool值 True/False
def openRobotControl(portName, baudRate):
    charPointer = bytes(portName, "utf-8")
    __libc.openRobotControl.restype = c_bool
    ok = __libc.openRobotControl(charPointer, baudRate)
    time.sleep(__delayTime)
    return ok

# setV12IoValue(value)
# 设置机械臂抓手吸盘的工作状态
# value为bool值，True表示高电平工作状态
# 返回bool值 True/False,True表示通信成功，指令正确发送给机械臂，否则False
def setV12IoValue(value):
    v = c_bool(value)
    __libc.setV12IoValue.restype = c_bool
    ok = __libc.setV12IoValue(v)
    time.sleep(__delayTime)
    return ok

# setRAngel(r360)
# 设置机械臂抓手吸盘的旋转角度
# value为float值，范围0-360，表示抓手舵机的旋转角度
# 返回bool值 True/False,True表示通信成功，指令正确发送给机械臂，否则False
# 注意，舵机的旋转角度是无法读取的，只能设置
def setRAngel(value):
    v = c_float(value)
    __libc.setRAngel.restype = c_bool
    ok = __libc.setRAngel(v)
    time.sleep(__delayTime)
    return ok

# setEnabledMotor(bool EnOrDisMotor , bool isqueue)
# 设置机械臂电机工作状态，用于清除已有的故障或者停止机械臂工作
# EnOrDisMotor 为bool值，是否工作
#  isqueue 为bool值，表示是否立即执行还是队列执行
# 返回bool值 True/False,True表示通信成功，指令正确发送给机械臂，否则False
def setEnabledMotor(enOrDisMotor, isqueue):
    e = c_bool(enOrDisMotor)
    q = c_bool(isqueue)
    __libc.setEnabledMotor.restype = c_bool
    ok = __libc.setEnabledMotor(e, q)
    time.sleep(__delayTime)
    return ok

# moveJByXYZ(float x ,float y ,float z ,float speed,bool isqueue)
# 给机械臂发送指令，让其运动到指定的位置
# 参数x，y，z表示三维坐标；speed表示运动速度，isqueue为bool类型表示是否加入到队列中
# 返回bool值 True/False,True表示通信成功，指令正确发送给机械臂，否则False
# 注意：x,y,z,speed均为float类型，且均有不同的有效取值范围，超出范围后机械臂可能无法执行，具体范围可以查阅厂家资料
def moveJByXYZ(x, y, z, speed, isqueue=True):
    vx = c_float(x)
    vy = c_float(y)
    vz = c_float(z)
    vs = c_float(speed)
    q = c_bool(isqueue)
    __libc.moveJByXYZ.restype = c_bool
    ok = __libc.moveJByXYZ(vx, vy, vz, vs, q)
    time.sleep(__delayTime)
    return ok

# getCurentPosition()
# 获取机械臂的当前坐标位置
# 无参数
# 成功返回数据字典，失败返回None
# 返回字段说明：
# x,y,z三维坐标；axis1，axis1为两个运动轴的角度，r值该款机械臂无效
def getCurentPosition():
    x = c_float()
    y = c_float()
    z = c_float()
    ax1 = c_float()
    ax2 = c_float()
    r = c_float()
    __libc.getCurentPosition.restype = c_bool
    ok = __libc.getCurentPosition(byref(x), byref(
        y), byref(z), byref(ax1), byref(ax2), byref(r))
    time.sleep(__delayTime)
    if ok:
        return {'x': x.value, 'y': y.value, 'z': z.value, 'axis1': ax1.value, 'axis2': ax2.value, 'r': r.value}
    else:
        return None

# waitForPos（x,y,z)
# 阻塞程序继续执行，直到机械臂运动到指定坐标后才返回
# 参数xyz为float类型的具体坐标
# 返回类型要么为True 表示机器人已经到达指定位置，为False表示机器人故障了
# 注意：该函数会阻塞程序运行，且如果给定的坐标不合理，机器人没法运动到指定位置，可能会引起无限阻塞
def waitForPos(x,y,z):
    while True:
        if robotIsError():
            print("机器臂处于故障状态")
            return None
        else:
            v=getCurentPosition()
            if v is None:
                time.sleep(0.1)
                print("获取机器人位置失败！")
                qApp.processEvents()
                continue
            if (abs(v['x'] - x)<1 and abs(v['y'] - y)<1 and abs(v['z'] - z)<1):
                    return True
            else:
                    time.sleep(0.1)
                    qApp.processEvents()
    

#   机械臂模块测试函数
def robot_test():
    initRobot()
    ok = openRobotControl("/dev/ttyUSB5", 115200)
    if ok == False:
        print("open robot fail")
    else:
        ok = robotIsError()
        if ok:
            setEnabledMotor(True, False)
        print("robot has error ", ok)
        v = getCurentPosition()
        if v is None:
            print("get pos error")
        else:
            print(v)
            ok = moveJByXYZ(v['x'], v['y'], 60.0, 50.0, True)
            print(ok)
    time.sleep(2)
    closeRobotControl()
    freeRobot()

# robot_test()