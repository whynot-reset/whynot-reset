import sys,time, random,datetime
from pathlib import Path
from PyQt5.QtCore import QObject,Qt,pyqtSignal,pyqtSlot,QTimer
from PyQt5.QtWidgets import QApplication,QWidget,QVBoxLayout,QHBoxLayout,QFormLayout,QFrame,QPushButton,QLineEdit
from PyQt5.QtWidgets import QSizePolicy,QComboBox,QLabel,QSpinBox,qApp,QTextEdit,QDoubleSpinBox,QGroupBox,QCheckBox
from PyQt5.QtGui import QTextCursor,QPixmap
from PyQt5.QtSerialPort import QSerialPortInfo
import pymodules.modbus as bus
import pymodules.robot as robot
import pymodules.camera as camera
import pymodules.imgproc as  imgproc



class MainWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setUI()
        self.connectUsrAct()
        bus.initModbus()
        robot.initRobot()
        camera.initCamera()

    def __del__(self):
        bus.freeModbus()
        robot.freeRobot()
        camera.freeCamera()

    def setUI(self):
        mainLayout=QVBoxLayout()
        self.setLayout(mainLayout)
        #modebus测试
        gp=QGroupBox("modbus测试")
        gpLayout=QVBoxLayout()
        gp.setLayout(gpLayout)
        #1
        tmp = QHBoxLayout()
        self.cmb_modbus = QComboBox()
        self.modebusBuate=QSpinBox()
        self.modebusBuate.setRange(0,999999)
        self.modebusBuate.setValue(57600)
        self.btnOpenModbus = QPushButton("打开Modbus")
        self.btnCloseModbus = QPushButton("关闭Modbus")
        self.btnExit = QPushButton("退出程序")
        tmp.addWidget(QLabel("ModBus端口"))
        tmp.addWidget(self.cmb_modbus)
        tmp.addWidget(QLabel("通信速率"))
        tmp.addWidget(self.modebusBuate)
        tmp.addWidget(self.btnOpenModbus)
        tmp.addWidget(self.btnCloseModbus)
        tmp.addStretch()
        tmp.addWidget(self.btnExit)
        gpLayout.addLayout(tmp)
        #2
        tmp = QHBoxLayout()
        tmp.addWidget(QLabel("IO整体读写 7->0"))
        self.lineBusIO7=QSpinBox()
        self.lineBusIO6=QSpinBox()
        self.lineBusIO5=QSpinBox()
        self.lineBusIO4=QSpinBox()
        self.lineBusIO3=QSpinBox()
        self.lineBusIO2=QSpinBox()
        self.lineBusIO1=QSpinBox()
        self.lineBusIO0=QSpinBox()
        tmp.addWidget(self.lineBusIO7)
        tmp.addWidget(self.lineBusIO6)
        tmp.addWidget(self.lineBusIO5)
        tmp.addWidget(self.lineBusIO4)
        tmp.addWidget(self.lineBusIO3)
        tmp.addWidget(self.lineBusIO2)
        tmp.addWidget(self.lineBusIO1)
        tmp.addWidget(self.lineBusIO0)
        self.lineBusIO7.setRange(0,1)
        self.lineBusIO6.setRange(0,1)
        self.lineBusIO5.setRange(0,1)
        self.lineBusIO4.setRange(0,1)
        self.lineBusIO3.setRange(0,1)
        self.lineBusIO2.setRange(0,1)
        self.lineBusIO1.setRange(0,1)
        self.lineBusIO0.setRange(0,1)
        self.btnReadIO = QPushButton("读取")
        self.btnWriteIO = QPushButton("写入")
        tmp.addWidget(self.btnReadIO)
        tmp.addWidget(self.btnWriteIO)
        gpLayout.addLayout(tmp)
        #3
        tmp = QHBoxLayout()
        tmp.addWidget(QLabel("Modebus CRC16   内容："))
        self.crcIn=QLineEdit()
        self.crcIn.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
        self.crcOut=QLineEdit()  
        self.crcOut.setMaximumWidth(60)
        self.btnCrC = QPushButton("校验")
        tmp.addWidget(self.crcIn)
        tmp.addWidget(self.btnCrC)
        tmp.addWidget(QLabel("结果："))
        tmp.addWidget(self.crcOut)
        gpLayout.addLayout(tmp)
        mainLayout.addWidget(gp)
        #机器人测试
        gp=QGroupBox("机械臂测试")
        gpLayout=QVBoxLayout()
        gp.setLayout(gpLayout)
        #1
        tmp = QHBoxLayout()
        self.cmb_robot = QComboBox()
        self.btnRobotOpen = QPushButton("连接机器人")
        self.btnRobotClose = QPushButton("关闭机械臂")
        self.btnRobotReset = QPushButton("清除故障")
        self.btnRobotIOTrue = QPushButton("IO高电平")
        self.btnRobotIOFalse = QPushButton("IO低电平")
        self.robotAngle=QDoubleSpinBox()
        self.robotAngle.setRange(0,360)
        self.btnRobotAngle = QPushButton("设置舵机角度")
        tmp.addWidget(QLabel("机械臂端口"))
        tmp.addWidget(self.cmb_robot)
        tmp.addWidget(self.btnRobotOpen)
        tmp.addWidget(self.btnRobotClose)
        tmp.addSpacing(20)
        tmp.addWidget(self.btnRobotReset)
        tmp.addWidget(self.btnRobotIOTrue)
        tmp.addWidget(self.btnRobotIOFalse)
        tmp.addSpacing(20)
        tmp.addWidget(QLabel("设置舵机角度"))
        tmp.addWidget(self.robotAngle)
        tmp.addWidget(self.btnRobotAngle)
        tmp.addStretch()
        gpLayout.addLayout(tmp)
        #2
        tmp = QHBoxLayout()
        self.robotX=QDoubleSpinBox()
        self.robotX.setRange(-200,200)
        self.robotY=QDoubleSpinBox()
        self.robotY.setRange(-200,200)
        self.robotZ=QDoubleSpinBox()
        self.robotZ.setRange(-200,200)
        self.robotSpeed=QSpinBox()
        self.robotSpeed.setRange(0,200)
        self.robotIsQueue=QCheckBox("队列")
        self.btnRobotPosGet = QPushButton("读取坐标")
        self.btnRobotPosSet = QPushButton("发送移动指令")
        self.btnRobotStatusGet = QPushButton("读取状态")
        self.btnRobotQueue = QPushButton("清空队列")
        tmp.addWidget(QLabel("当前坐标   X:"))
        tmp.addWidget(self.robotX)
        tmp.addWidget(QLabel("Y:"))
        tmp.addWidget(self.robotY)
        tmp.addWidget(QLabel("Z:"))
        tmp.addWidget(self.robotZ)
        tmp.addWidget(QLabel("速度:"))
        tmp.addWidget(self.robotSpeed)
        tmp.addWidget(self.robotIsQueue)
        tmp.addWidget(self.btnRobotPosGet)
        tmp.addWidget(self.btnRobotPosSet)
        tmp.addWidget(self.btnRobotStatusGet)
        tmp.addWidget(self.btnRobotQueue)
        tmp.addStretch()
        gpLayout.addLayout(tmp)
        mainLayout.addWidget(gp)
        #摄像头测试
        gp=QGroupBox("摄像头测试")
        gp.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        gpLayout=QVBoxLayout()
        gp.setLayout(gpLayout)
        #1
        tmp = QHBoxLayout()
        self.btnOpenCarema = QPushButton("打开摄像头")
        self.btnCapture = QPushButton("采集图像")
        self.btnCloseCamera = QPushButton("关闭摄像头")
        self.btnTestDataBase = QPushButton("测试数据库连接")
        tmp.addWidget(self.btnOpenCarema)
        tmp.addWidget(self.btnCapture)
        tmp.addWidget(self.btnCloseCamera)
        tmp.addStretch()
        tmp.addWidget(self.btnTestDataBase)
        gpLayout.addLayout(tmp)
        #2
        self.imgLabel=QLabel("获取的图像")
        self.imgLabel.setAlignment(Qt.AlignCenter)
        gpLayout.addWidget(self.imgLabel)
        mainLayout.addWidget(gp)

        self.logEdit = QTextEdit()
        self.logEdit.setMaximumHeight(120)
        mainLayout.addWidget(self.logEdit)
        all_ports = QSerialPortInfo.availablePorts()
        for item in all_ports:
            self.cmb_modbus.addItem(item.systemLocation())
            self.cmb_robot.addItem(item.systemLocation())
        
    def testDataBase(self):
        db=SqlData.SqlData()
        db.connectToServer()
        ok=db.doSelectSql("select  now() as t")
        if ok is None:
            self.addLog("连接数据库失败，请修改SqlData.py模块中的参数后尝试")
        else:
            self.addLog("数据库联通测试成功")
        
    #输出日志记录
    def addLog(self,logMsg):
        if self.logEdit.document().lineCount()>300:
            self.logEdit.clear()
        self.logEdit.append(logMsg)
        self.logEdit.moveCursor(QTextCursor.End)
    #将界面上输入框的值作为坐标发送给机器人
    def writeRobotPos(self):
        ok=robot.moveJByXYZ(self.robotX.value(),self.robotY.value(),self.robotZ.value(),self.robotSpeed.value(),self.robotIsQueue.isChecked)
        if ok==False:
            self.addLog("发送机械臂移动指令失败")

    #设置界面上modebusIO端口的值
    def  setModbusIOStatus(self,ioStatus):
        self.lineBusIO0.setValue( 1&(ioStatus))
        self.lineBusIO1.setValue( 1&(ioStatus>>1))
        self.lineBusIO2.setValue( 1&(ioStatus>>2))
        self.lineBusIO3.setValue( 1&(ioStatus>>3))
        self.lineBusIO4.setValue( 1&(ioStatus>>4))
        self.lineBusIO5.setValue( 1&(ioStatus>>5))
        self.lineBusIO6.setValue( 1&(ioStatus>>6))
        self.lineBusIO7.setValue( 1&(ioStatus>>7))
    #打开modbus设备通讯
    def openModBus(self):
        portName=self.cmb_modbus.currentText()
        if len(portName)<3:
            self.addLog("请选择Modbus连接的端口名称")
        else:
            ok=bus.openModBus(portName,self.modebusBuate.value())
            self.addLog("ModBus连接"+("成功" if ok else "失败"))
    def closeModBus(self):
        bus.closeModBus()
    #打开机器人通讯
    def openRobot(self):
        portName=self.cmb_robot.currentText()
        if len(portName)<3:
            self.addLog("请选择机器人连接的端口名称")
        else:
            ok= robot.openRobotControl(portName,115200)
            self.addLog("机器人连接"+("成功" if ok else "失败"))      
    def closeRobot(self):
        robot.closeRobotControl()
    def robotResst(self):
        ok=robot.setEnabledMotor(True,False)
        if ok==False:
            self.addLog("机器人故障清除失败")
    def robotIOTrue(self):
        ok=robot.setV12IoValue(True)
        if ok==False:
            self.addLog("机器人IO设置高电平失败")
    def robotIOFalse(self):
        ok=robot.setV12IoValue(False)
        if ok==False:
            self.addLog("机器人IO设置低电平失败")
    def robotSetAngle(self):
        ok=robot.setRAngel(self.robotAngle.value())
        if ok==False:
            self.addLog("机器人舵机角度设置失败")
    def getRobotState(self):
        ok=robot.robotIsError()
        if ok:
            self.addLog("机器人故障")
        else:
            self.addLog("机器人正常")
    def clearRobotQueue(self):
        ok=robot.clearControlQuenes()
        if ok==False:
            self.addLog("机器人清除队列失败")
        
    #打开摄像头通讯
    def openCamera(self):
        ok= camera.openCamera()
        self.addLog("摄像头连接"+("成功" if ok else "失败"))      
    def CloseCamera(self):
        camera.closeCamera()
    #以文件形式获取一帧图像，返回值为文件名
    def captureImg(self):
        v=camera.getImageAsFile(1000,"/ssd/imgs")
        if v is None:
            self.addLog("获取图形失败")
            return None
        else:
            self.addLog("获取图像成功，保存为文件%s" % v)
            bmp=QPixmap()
            if bmp.load(v):
                self.imgLabel.setPixmap(bmp.scaledToHeight(self.imgLabel.height()-5))
                qApp.processEvents()
            
    #读取机器人当前坐标
    def readRobotPos(self):
        v=robot.getCurentPosition()
        if v is None:
            self.addLog("读取机器人坐标失败")
        else:
            self.robotX.setValue(v['x'])
            self.robotY.setValue(v['y'])
            self.robotZ.setValue(v['z'])
    #读取modbusIO端口状态
    def readModBusIO(self):
        v=bus.readIo()
        if v is None:
            self.addLog("读取ModBus IO失败")
        else:
            self.setModbusIOStatus(v)
    
    def doCrC(self):
        crc16fun = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0xFFFF, xorOut=0x0000)
        #调用这个校验函数得到一个16位的整数
        strIN=self.crcIn.text()
        if len(strIN)<2:
            return
        data=bytearray.fromhex(strIN)
        tmp=crc16fun(data)
        #将16位整数高地位逆向组合成一个btyearray并返回
        v= bytearray([tmp & 0xff,(tmp >> 8) & 0xff])
        self.addLog( "输入数据 %s ,附加校验后数据 %s" % (data.hex() ,data.hex()+v.hex() ))
        self.crcOut.setText(v.hex())
    
    def writeModBusIO(self):
        ioStatus=        (self.lineBusIO0.value()) +        (self.lineBusIO1.value()<<1)+        (self.lineBusIO2.value()<<2)+  \
       (self.lineBusIO3.value( )<<3)+        (self.lineBusIO4.value( )<<4)+        (self.lineBusIO5.value( )<<5)+\
        (self.lineBusIO6.value()<<6)+        (self.lineBusIO7.value()<<7)
        v=bus.writeIo(ioStatus)
    #连接信号槽函数
    def connectUsrAct(self):
        self.btnExit.clicked.connect(self.close)
        #modbus
        self.btnOpenModbus.clicked.connect(self.openModBus)
        self.btnCloseModbus.clicked.connect(self.closeModBus )
        self.btnReadIO.clicked.connect(self.readModBusIO)
        self.btnWriteIO.clicked.connect(self.writeModBusIO)
        #robot
        self.btnRobotOpen.clicked.connect(self.openRobot)
        self.btnRobotClose.clicked.connect(self.closeRobot)
        self.btnRobotReset.clicked.connect(self.robotResst)
        self.btnRobotIOTrue.clicked.connect(self.robotIOTrue)
        self.btnRobotIOFalse.clicked.connect(self.robotIOFalse)
        self.btnRobotAngle.clicked.connect(self.robotSetAngle)
        self.btnRobotPosGet.clicked.connect(self.readRobotPos)
        self.btnRobotPosSet.clicked.connect(self.writeRobotPos)
        self.btnRobotStatusGet.clicked.connect(self.getRobotState)
        self.btnRobotQueue.clicked.connect(self.clearRobotQueue)
        #camera
        self.btnOpenCarema.clicked.connect(self.openCamera)
        self.btnCapture.clicked.connect(self.captureImg)
        self.btnCloseCamera.clicked.connect(self.CloseCamera)
        self.btnTestDataBase.clicked.connect(self.testDataBase)
        self.btnCrC.clicked.connect(self.doCrC)


def main():
    app = QApplication(sys.argv)
    w = MainWidget()
    w.setWindowTitle("工况软硬件环境测试程序")
    w.resize(600, 800)
    w.show()
    sys.exit(app.exec_())


main()