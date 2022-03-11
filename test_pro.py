from PyQt5.QtCore import QObject,Qt,pyqtSignal,pyqtSlot,QTimer,QSize,QTime
from PyQt5.QtWidgets import QApplication,QWidget,QVBoxLayout,QHBoxLayout,QFormLayout,QFrame,QPushButton,QGridLayout
from PyQt5.QtWidgets import QSizePolicy,QComboBox,QLabel,QSpinBox,qApp,QTextEdit,QDoubleSpinBox
from PyQt5.QtGui import QTextCursor,QPixmap
from pathlib import Path 
import pymodules.modbus as bus
import pymodules.robot as robot
import pymodules.camera as camera
import pymodules.imgproc as  imgproc
import numpy as np
import cv2,sys,datetime
import test_ui,test_methods
import matplotlib.pyplot as plt
import cv2
import os
import time


#继承默认ui类，完成所有基本功能
class MainWidget(test_ui.MyWidget):
    def __init__(self):
        super().__init__()
        # self.setWindowFlag(Qt.FramelessWindowHint)
        self.connectUsrAct()
        bus.initModbus()
        robot.initRobot()
        camera.initCamera()

    def __del__(self):
        bus.freeModbus()
        robot.freeRobot()
        camera.freeCamera()
        super().deleteLater()
    #通过文件名来设置一个QLabel的图像
    def setLabelImage(self,label:QLabel,imageFile:str):
        bmp=QPixmap()
        if bmp.load(imageFile):
            label.setPixmap(bmp.scaledToWidth(label.width()-2))
        else:
            label.setText('加载失败:'+imageFile)
        label.repaint()
    #输出日志记录
    def addLog(self,logMsg):
        if self.editLog.document().lineCount()>300:
            self.editLog.clear()
        self.editLog.append(logMsg)
        self.editLog.moveCursor(QTextCursor.End)
    #打开所有设备
    def openAllDevice(self)->bool:
        if (self.cmbModbus.currentIndex()<0) or (self.cmbRobot.currentIndex()<0):
            self.addLog("请选择正确的通讯端口")
            return False
        ok=bus.openModBus(self.cmbModbus.currentText(),57600)
        if not ok:
            self.addLog("ModBus连接失败")
            return False
        ok= robot.openRobotControl(self.cmbRobot.currentText(),115200)
        if not ok:
            self.addLog("机器人连接失败")
            return False    
        ok= camera.openCamera()
        if not ok:
            self.addLog("摄像头连接失败")
            return False
        return  True      
    #以文件形式获取一帧图像并将其显示到labelPicOne，返回值为文件名
    def captureImg(self,saveDir)->str:
        #首先清空日志
        self.editLog.clear()
        imgFile=camera.getImageAsFile(1000,saveDir)
        if imgFile is None:
            self.addLog("获取图形失败")
            return None
        else:
            self.addLog("图像保存为:%s" % imgFile)
            self.setLabelImage(self.labelPicOne,imgFile)
            return imgFile
    #点击[手动拍照]按钮后的响应
    def actBtnCapture(self):  
        open("/ssd/libmod/result.txt", 'w').close()     
        ok= camera.openCamera()
        tt = time.perf_counter()
        rectangleImg = "/ssd/Test02/%2f.bmp"%(tt)
        if not ok:
            self.addLog("摄像头连接失败")
            #加到此处是为了没有摄像头也可以测试------------
            cameraPic="/ssd/libmod/test.bmp"
            if True:
                self.setLabelImage(self.labelPicOne,cameraPic)
                resultTestFile,pcbImgFile=self.processImg(cameraPic)
                if resultTestFile is None:
                    return
                self.processTestResult(pcbImgFile,resultTestFile,rectangleImg)
                #-------------------------------
            return
        else:
            self.addLog("摄像头连接成功")
            cameraPic=self.captureImg("/ssd/imgs")
            #这里为TRUE是为了能在手动拍照的时候也检测图片--------------
            if True:
                self.setLabelImage(self.labelPicOne,cameraPic)
                resultTestFile,pcbImgFile=self.processImg(cameraPic)
                if resultTestFile is None:
                    return
                self.processTestResult(pcbImgFile,resultTestFile,rectangleImg)
            #-----------------------

    #点击[开始]按钮后的响应
    def actBtnStart(self):
        ok=self.openAllDevice()
        if not ok:
            print("1")
            return
        bus.writeIoChannel(5,False)
        bus.writeIoChannel(7,True)
        bus.writeIoChannel(6,False)
        time.sleep(0.1)
        bus.writeIoChannel(6,True)
        time.sleep(0.1)
        bus.writeIoChannel(6,False)
        self.lastProcessTime=0
        self.checkTimer.start(500)
    #点击[停止]按钮后的响应
    def actBtnStop(self):
        self.checkTimer.stop()
        bus.writeIo(0)
    #定时器响应函数
    def onTimerCheck(self):
        self.checkTimer.stop()
        #读取IO状态 各状态代表意义如下
        # 0 相机下传感器,输入,2 机器取件传感器，输入,
        # 5 阻挡汽缸，输出,6 pcl上料，输出,7 皮带转动，输出
        v=bus.readIo()
        if v is None:
            self.addLog("modbus io读取失败，终止任务")
            return
        needCapture= (v&1)==1
        needRobotAct=((v>>2)&1)==1 
        if(needCapture  and  time.time()-self.lastProcessTime>20):
            self.lastProcessTime=time.time()
            bus.writeIoChannel(5,True)
            time.sleep(5)
            bus.writeIoChannel(7,False)
            time.sleep(0.2)
            open("/ssd/libmod/result.txt", 'w').close()   
            camera.openCamera()
            tt = time.perf_counter()
            cameraPic=self.captureImg("/ssd/imgs")
            rectangleImg = "/ssd/Test02/%2f.bmp"%(tt)
            if cameraPic is  None:
                self.addLog("获取图像失败，终止任务")
                return
            _time=time.time()
            resultTestFile,pcbImgFile=self.processImg(cameraPic)
            if resultTestFile is None:
                return
            ok=self.processTestResult(pcbImgFile,resultTestFile,rectangleImg)
            if not ok:
                self.addLog("图像处理失败，终止任务")
                return
            self.addLog("图像处理执行完毕,共花费%.3f" % ( time.time() - _time))
            qApp.processEvents()
            #让流水线继续运动
            bus.writeIoChannel(5,False)
            bus.writeIoChannel(7,True)
            self.checkTimer.start(500)
            return
        #如果需要机器人抓取
        if(needRobotAct):
            bus.writeIoChannel(7,False)
            v=self.waitForRobotGet()
            if v is None:
                self.addLog("机器人抓取失败，终止任务")
                return
            self.addLog("机器人抓取完毕")
            bus.writeIoChannel(7,True)
            #通知PLC继续上料
            bus.writeIoChannel(6,True)
            time.sleep(0.1)
            bus.writeIoChannel(6,False)
        #重新开始定时器
        self.checkTimer.start(500)

    #机器人根据NG结果抓取并投放
    def waitForRobotGet(self):
        self.addLog("机器人获取当前位置并垂直提升")
        v=robot.getCurentPosition()
        i=0
        while v is None:
            if i>5:
                self.addLog("连续5次获取机器人当前位置失败，终止任务")
                return None
            v=robot.getCurentPosition()
            i+=1
        robot.moveJByXYZ(v['x'],v['y'],70,80)
        robot.waitForPos(v['x'],v['y'],70)
        x,y,z=0,0,0
        if v['axis2']<0:
            robot.setRAngel(177)
            robot.moveJByXYZ(126,-80,70,60)
            x,y=185,79
        else:
            robot.setRAngel(132)
            robot.moveJByXYZ(44,166,70,60)
            x,y=185,79
        robot.moveJByXYZ(x,y,70,60)
        robot.moveJByXYZ(x,y,45,60,True)
        robot.waitForPos(x,y,45)
        robot.setV12IoValue(True)
        time.sleep(0.2)
        robot.moveJByXYZ(x,y,70,50,True)
        if self.lastProcessResult == 1:
            x,y = 24,-166
            robot.moveJByXYZ(111,27,70,80,True)
            robot.moveJByXYZ(24,-166,70,80,True)
            robot.waitForPos(x,y,70) 
            robot.setRAngel(115)
            x,y,z=24,-166,-6
        else:
            x,y = 44,166
            robot.moveJByXYZ(52,98,68,80,True)
            robot.moveJByXYZ(44,166,70,80,True)
            robot.waitForPos(x,y,70) 
            robot.setRAngel(66)
            x,y,z=44,166,-6
        robot.moveJByXYZ(x,y,z,80,True)
        robot.waitForPos(x,y,z)
        robot.setV12IoValue(False)
        robot.moveJByXYZ(x,y,70,100,True)
        return True
    #连接信号槽函数
    def connectUsrAct(self):
        self.lastProcessResult=1
        self.checkTimer=QTimer()
        self.checkTimer.timeout.connect(self.onTimerCheck)
        self.btnExit.clicked.connect(self.close)
        self.btnCapture.clicked.connect(self.actBtnCapture)
        self.btnStart.clicked.connect(self.actBtnStart)
        self.btnStop.clicked.connect(self.actBtnStop)

    # processTestResult根据检测结果进行图像显示等处理过程
    # pcbImgFile 原始pcb图像,输入
    # resultTestFile 保存了检测结果的文本文件，输入
    # resultImgFile 最终输出图像，输出
    # 返回值为成功或者失败
    def processTestResult(self,pcbImgFile,resultTestFile,resultImgFile)->bool:
        img = cv2.imread(pcbImgFile,cv2.IMREAD_COLOR)
        #读取判别的结果文件，每一行代表一个矩形区域及检测结果，逗号分割的5个元素，1代表ok，其他代表缺陷
        results =np.loadtxt(resultTestFile,dtype=int,delimiter=',')
        if results.size<5 : #如果数组个数小于5，则无效
            self.addLog("检测结果无效")
            return False
        if results.size==5 : #如果等于5则转为2维数组
            results=results.reshape(-1,5)
        ok=0
        ng=0
        #遍历并根据结果画图
        for rect in results:
            if(1 == rect[4]):
                ok+=1
                cv2.rectangle(img,(rect[0],rect[1]),(rect[0]+rect[2],rect[1]+rect[3]),  (0, 255, 0),5)
            else:
                #保存检测结果以便后续设置机器人的运动路径,只要有一个缺陷就认为pcb存在缺陷
                ng+=1
                cv2.rectangle(img,(rect[0],rect[1]),(rect[0]+rect[2],rect[1]+rect[3]),  (0, 0, 255),5)
        if ng == 0:
            self.lastProcessResult =1
        else:
            self.lastProcessResult = 2
        sumResult = ng
        self.addLog("当前pcb板缺陷总数为%d"%(sumResult))
        cv2.imwrite(resultImgFile, img)
        # 将结果图像显示到界面上
        self.setLabelImage(self.labelPicFour,resultImgFile)
        time.sleep(0.1)
        # 将结果显示到labelImg
        plt.close()
        plt.bar(x = 0, height = ok, width = 0.2, label = "ok",color='g')
        plt.bar(x = 0.2, height = ng, width = 0.2, label =  "ng",color='r')
        plt.legend()
        plt.savefig("info.jpg")
        # labels = ['ok','ng']
        # sizes = [ok,ng]
        # explode = (0,0.1)
        # plt.pie(sizes,explode=explode,labels=labels,autopct='%1.1f%%',shadow=False,startangle=150)
        # plt.legend()
        plt.savefig("info.jpg")
        self.setLabelImage(self.labelImg,"info.jpg")
        # 将结果显示到labelInfo
        self.labelInfo.setText("ok=%d，ng=%d"%(ok,ng))
        t= time.perf_counter()
        #保存程序截图
        bmp=QPixmap(self.size())
        self.render(bmp)
        saveimg = "/ssd/Test02/%2f.bmp"%(t)
        bmp.save(saveimg)
        time.sleep(0.1)
        return True
    # processImg图像处理过程
    # cameraPic 原始相机图像，输入
    # 返回值如果不为None，第一个表示检测结果的txt文件名称，第二个表示剪裁后的pcb图像名称
    def processImg(self,cameraPic)->(str,str):
        if not Path(cameraPic).is_file():
            self.addLog("图像文件%s不存在，终止任务" % cameraPic)
            return None,None

        #此处省略 具体应该是检测分割后再保存为 pcbImgFile
        pcbImgFile="/ssd/libmod/pcb.bmp"
        bRet = imgproc.match_pcb(cameraPic,"/ssd/libmod/Configures/mark.bmp",0.7,-1113,-1866,2802,2046,pcbImgFile)
        if bRet==False :
            print("PCB板定位失败！")
            return None
        # #此处不做剪裁，所以直接赋值，如果前面分割启用了，这一行就不要了，相当于摄像头图片cameraPic经过分割变成pcbImgFile
        # pcbImgFile=cameraPic
        # 1.专门的图像处理考点:将定位取出来的pcb图像转成灰度图后显示其颜色直方图
        # gray=cv2.imread(pcbImgFile,cv2.IMREAD_GRAYSCALE)
        # cv2.imwrite("gray.bmp",gray)
        # hist = cv2.calcHist([gray], [0], None, [128], [0, 255])
        # plt.close()
        # plt.plot(hist, color='r')
        # plt.savefig("gray_hist.jpg")
        self.setLabelImage(self.labelPicTwo,"/ssd/Test01/1.bmp")
        # # 2.专门的图像处理考点:显示定位出来的ocb图像的灰度图均衡后的直方图
        # equ = cv2.equalizeHist(gray) # 灰度图均衡化
        # hist = cv2.calcHist([equ], [0], None, [128], [0, 255])
        # plt.close()
        # plt.plot(hist, color='g')
        # plt.savefig("gray_equ_hist.jpg")
        self.setLabelImage(self.labelPicThree,"/ssd/Test01/2.bmp")
        #以下为图像检测过程
        needTrain=True #本次是否需要训练
        testResult=[] #用于保存检测结果
        self.lastProcessResult=1 #先将结果设置为1成功，后续检测到缺陷再修改为2
        resultFile="/ssd/libmod/result.txt" #用于汇总最终检测结果

       
        #part1
        # 特征提取.定义ok, ng两种类型训练数据路径
        imgOk = "/ssd/libmod/Configures/part1/ok/"
        imgNG = "/ssd/libmod/Configures/part1/ng/" 
        imgdst = "/ssd/libmod/unevenLightCompensate.bmp"
        imgproc.unevenLightCompensate(pcbImgFile,15,imgdst)
        # true 为重新训练，否则使用已经训练好的模型参数
        if False:
            imgproc.train_knn_histgram(imgOk, imgNG, "/ssd/libmod/knn_histgram1.xml")
        # 读取离线标定好的零件2的位置,
        rectTxt = "/ssd/libmod/Configures/roi/rect1.txt"
        t1= time.perf_counter()
        resultbmp = "/ssd/Test02/%2f.bmp"%(t1)
        # 加载离线训练好的模型
        bRet=imgproc.predict(imgdst, rectTxt, "/ssd/libmod/knn_histgram1.xml", "knn", "histgram", resultbmp, resultFile)
        time.sleep(0.1)
        if (False == bRet):
            print("PCB检测part1失败!")
            return None,None
        #part2
        imgOk = "/ssd/libmod/Configures/part2/ok/"
        imgNG = "/ssd/libmod/Configures/part2/ng/"
        imgDst = "/ssd/libmod/Canny.bmp"
        imgproc.edge_canny(pcbImgFile,40,80,imgDst)

        # true 为重新训练，否则使用已经训练好的模型参数
        if False:
            imgproc.train_svm_glcm(imgOk, imgNG, "/ssd/libmod/svm_glcm2.xml")
        # 读取离线标定好的零件2的位置,
        rectTxt = "/ssd/libmod/Configures/roi/rect2.txt"
        t2= time.perf_counter()
        resultbmp = "/ssd/Test02/%2f.bmp"%(t2)
        # 加载离线训练好的模型
        bRet=imgproc.predict(imgDst, rectTxt, "/ssd/libmod/svm_glcm2.xml", "svm", "glcm", resultbmp, resultFile)
        time.sleep(0.1)
        if (False == bRet):
            print("PCB检测part2失败!")
            return None,None
    
        
        #  # 3.此处用自定义的特帧提取方法来进行训练和检测，并将结果统一到图像处理接口一致的样式后保存到 resultFile后返回
        # # 学生可以参照该模式拓展自己的特帧定义方法来达到更好的效果
        imgOk = "/ssd/libmod/Configures/part3/ok"
        imgNG = "/ssd/libmod/Configures/part3/ng"
        featureFile = "/ssd/libmod/custom_feature3.txt"
        typesFile = "/ssd/libmod/custom_types3.txt"
        xmlFile="/ssd/libmod/Direction_feature3.xml"
        rectTxt = "/ssd/libmod/Configures/roi/rect3.txt"
        result="/ssd/libmod/Result3.txt"
        if False:
            #首先用自定义提取特帧方法提取样板所有文件的特帧到featureFile, typesFile
            test_methods.Get_Feature_Direction(imgOk, imgNG, featureFile, typesFile)
            #用svm分类器对提取的特帧进行训练得到模型文件xmlFile
            imgproc.train_svm(featureFile, typesFile,xmlFile )
        #计算待识别的图像特征，保存到临时文件
        test_methods.GetDirection(imgDst, rectTxt, "tmp.txt")
        #读取图像的特征文件，加载离线训练好的分类器文件 xmlFile
        #输出检测的结果 custom_result
        imgproc.predict_svm("tmp.txt", xmlFile,result)
        #将两个不在一起的结果合并为图像处理模块一致的标准结果
        #读取判别的结果文件
        typeIds =np.loadtxt(result,dtype=int)
        rects=np.loadtxt(rectTxt,dtype=int,delimiter=',')
        #合并结果集
        rects=np.insert(rects,4,typeIds,axis=1)
        # img = cv2.imread(pcbImgFile,cv2.IMREAD_COLOR)
        # if rects.size<5 : #如果数组个数小于5，则无效
        #     self.addLog("检测结果无效")
        #     return None,None
        # if rects.size==5 : #如果等于5则转为2维数组
        #     rets=rects.reshape(-1,5)
        # #遍历并根据结果画图
        # for rect in rects:
        #     if (rect[4] ==1):
        #         image = cv2.rectangle(img,(rect[0],rect[0]+rect[2]),(rect[1],rect[1]+rect[3]),(0,255,255),3)
        #     else:
        #         image = cv2.rectangle(img,(rect[0],rect[0]+rect[2]),(rect[1],rect[1]+rect[3]),(0,0,255),3)
        with open (resultFile,"ta") as f:
            for i in range(0,len(rects)):
                f.write("%d,%d,%d,%d,%d\n"%(rects[i][0],rects[i][1],rects[i][2],rects[i][3],rects[i][4]))

        #将结果集保存到文件
        # np.savetxt(resultFile, rects, fmt="%d",delimiter=",")
        time.sleep(0.1)
        imgOk = "/ssd/libmod/Configures/part4/ok/"
        imgNG = "/ssd/libmod/Configures/part4/ng/"
    

        # true 为重新训练，否则使用已经训练好的模型参数
        if False:
            imgproc.train_knn_histgram(imgOk, imgNG, "/ssd/libmod/knn_histgram4.xml")
        # 读取离线标定好的零件2的位置,
        rectTxt = "/ssd/libmod/Configures/roi/rect4.txt"
        t4= time.perf_counter()
        resultbmp = "/ssd/Test02/%2f.bmp"%(t4)
        # 加载离线训练好的模型
        bRet=imgproc.predict(pcbImgFile, rectTxt, "/ssd/libmod/knn_histgram4.xml", "knn", "histgram", resultbmp, resultFile)
        time.sleep(0.1)
        if (False == bRet):
            print("PCB检测part4失败!")
            return None,None
        imgOk = "/ssd/libmod/Configures/part5/ok/"
        imgNG = "/ssd/libmod/Configures/part5/ng/"
        # true 为重新训练，否则使用已经训练好的模型参数
        if False:
            imgproc.train_svm_hog(imgOk, imgNG, "/ssd/libmod/svm_hog5.xml")
        # 读取离线标定好的零件2的位置,
        rectTxt = "/ssd/libmod/Configures/roi/rect5.txt"
        t5= time.perf_counter()
        resultbmp = "/ssd/Test02/%2f.bmp"%(t5)
        # 加载离线训练好的模型
        bRet=imgproc.predict(imgDst, rectTxt, "/ssd/libmod/svm_hog5.xml", "svm", "hog", resultbmp, resultFile)
        time.sleep(0.1)
        if (False == bRet):
            print("PCB检测part5失败!")
            return None,None
        imgOk = "/ssd/libmod/Configures/part6/ok/"
        imgNG = "/ssd/libmod/Configures/part6/ng/"
        # true 为重新训练，否则使用已经训练好的模型参数
        if False:
            imgproc.train_knn_histgram(imgOk, imgNG, "/ssd/libmod/knn_hisgram6.xml")
        # 读取离线标定好的零件2的位置,
        rectTxt = "/ssd/libmod/Configures/roi/rect6.txt"
        t6= time.perf_counter()
        resultbmp = "/ssd/Test02/%2f.bmp"%(t6)
        # 加载离线训练好的模型
        bRet=imgproc.predict(imgDst, rectTxt, "/ssd/libmod/knn_hisgram6.xml", "knn", "histgram", resultbmp, resultFile)
        time.sleep(0.1)
        if (False == bRet):
            print("PCB检测part6失败!")
            return None,None
        imgOk = "/ssd/libmod/Configures/part7/ok/"
        imgNG = "/ssd/libmod/Configures/part7/ng/"
        # true 为重新训练，否则使用已经训练好的模型参数
        if False:
            imgproc.train_knn_histgram(imgOk, imgNG, "/ssd/libmod/knn_histgram7.xml")
        # 读取离线标定好的零件2的位置,
        rectTxt = "/ssd/libmod/Configures/roi/rect7.txt"
        t7= time.perf_counter()
        resultbmp = "/ssd/Test02/%2f.bmp"%(t7)
        # 加载离线训练好的模型
        bRet=imgproc.predict(imgDst, rectTxt, "/ssd/libmod/knn_histgram7.xml", "knn", "histgram", resultbmp, resultFile)
        time.sleep(0.1)
        if (False == bRet):
            print("PCB检测part7失败!")
            return None,None



        return resultFile,pcbImgFile
    


def main():
    app = QApplication(sys.argv)
    w = MainWidget()
    w.resize(1024, 768)
    w.show()
    sys.exit(app.exec_())


main()