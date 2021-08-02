#include "sys.h"

//====================自己加入的头文件===============================
#include "delay.h"
#include "led.h"
#include "encoder.h"
#include "usart3.h"
#include "timer.h"
#include "pwm.h"
#include "pid.h"
#include "motor.h"
#include <stdio.h>
/*===================================================================
程序功能：直流减速电机的速度闭环控制测试，可同时控制两路，带编码器的直流减速电机
===================================================================*/
int leftSpeedNow  =0;
int rightSpeedNow =0;

int leftSpeeSet   = 300;//mm/s
int rightSpeedSet = 300;//mm/s

int main(void)
{ 

	GPIO_PinRemapConfig(GPIO_Remap_SWJ_Disable,ENABLE);
	GPIO_PinRemapConfig(GPIO_Remap_SWJ_JTAGDisable,ENABLE);//禁用JTAG 启用 SWD
	
	MY_NVIC_PriorityGroupConfig(2);	//=====设置中断分组
	
	delay_init();	    	        //=====延时函数初始化
	LED_Init();                     //=====LED初始化    程序灯	
	
	usart3_init(9600);              //=====串口3初始化  蓝牙 发送调试信息

	Encoder_Init_TIM2();            //=====初始化编码器1接口
	Encoder_Init_TIM4();            //=====初始化编码器2接口
	
	Motor_Init(7199,0);             //=====初始化PWM 10KHZ，用于驱动电机 如需初始化驱动器接口
	
	TIM3_Int_Init(50-1,7200-1);     //=====定时器初始化 5ms一次中断

	PID_Init();						//=====PID参数初始化
	
	//闭环速度控制
	while(1)
	{
		//给速度设定值，想修改速度，就更该leftSpeeSet、rightSpeedSet变量的值
		pid_Task_Letf.speedSet  = leftSpeeSet;
		pid_Task_Right.speedSet = rightSpeedSet;
		
		//给定速度实时值
		pid_Task_Letf.speedNow  = leftSpeedNow;
		pid_Task_Right.speedNow = rightSpeedNow;
		
		//执行PID控制函数
		Pid_Ctrl(&motorLeft,&motorRight);
		
		//根据PID计算的PWM数据进行设置PWM
		Set_Pwm(motorLeft,motorRight);
		
		//打印速度
		printf("%d,%d\r\n",leftSpeedNow,rightSpeedNow);
		delay_ms(2);
	} 
}

//5ms 定时器中断服务函数 --> 计算速度实时值，运行该程序之前，确保自己已经能获得轮速，如果不懂，可看之前电机测速的文章

void TIM3_IRQHandler(void)                            //TIM3中断
{
	if(TIM_GetITStatus(TIM3, TIM_IT_Update) != RESET) //检查指定的TIM中断发生与否
	{
		TIM_ClearITPendingBit(TIM3, TIM_IT_Update);   //清除TIMx的中断待处理位
		
		Get_Motor_Speed(&leftSpeedNow,&rightSpeedNow);//计算电机速度
		
		Led_Flash(100);                               //程序闪烁灯
	}
}

