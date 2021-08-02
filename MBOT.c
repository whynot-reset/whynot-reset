#include "sys.h"

//====================�Լ������ͷ�ļ�===============================
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
�����ܣ�ֱ�����ٵ�����ٶȱջ����Ʋ��ԣ���ͬʱ������·������������ֱ�����ٵ��
===================================================================*/
int leftSpeedNow  =0;
int rightSpeedNow =0;

int leftSpeeSet   = 300;//mm/s
int rightSpeedSet = 300;//mm/s

int main(void)
{ 

	GPIO_PinRemapConfig(GPIO_Remap_SWJ_Disable,ENABLE);
	GPIO_PinRemapConfig(GPIO_Remap_SWJ_JTAGDisable,ENABLE);//����JTAG ���� SWD
	
	MY_NVIC_PriorityGroupConfig(2);	//=====�����жϷ���
	
	delay_init();	    	        //=====��ʱ������ʼ��
	LED_Init();                     //=====LED��ʼ��    �����	
	
	usart3_init(9600);              //=====����3��ʼ��  ���� ���͵�����Ϣ

	Encoder_Init_TIM2();            //=====��ʼ��������1�ӿ�
	Encoder_Init_TIM4();            //=====��ʼ��������2�ӿ�
	
	Motor_Init(7199,0);             //=====��ʼ��PWM 10KHZ������������� �����ʼ���������ӿ�
	
	TIM3_Int_Init(50-1,7200-1);     //=====��ʱ����ʼ�� 5msһ���ж�

	PID_Init();						//=====PID������ʼ��
	
	//�ջ��ٶȿ���
	while(1)
	{
		//���ٶ��趨ֵ�����޸��ٶȣ��͸���leftSpeeSet��rightSpeedSet������ֵ
		pid_Task_Letf.speedSet  = leftSpeeSet;
		pid_Task_Right.speedSet = rightSpeedSet;
		
		//�����ٶ�ʵʱֵ
		pid_Task_Letf.speedNow  = leftSpeedNow;
		pid_Task_Right.speedNow = rightSpeedNow;
		
		//ִ��PID���ƺ���
		Pid_Ctrl(&motorLeft,&motorRight);
		
		//����PID�����PWM���ݽ�������PWM
		Set_Pwm(motorLeft,motorRight);
		
		//��ӡ�ٶ�
		printf("%d,%d\r\n",leftSpeedNow,rightSpeedNow);
		delay_ms(2);
	} 
}

//5ms ��ʱ���жϷ����� --> �����ٶ�ʵʱֵ�����иó���֮ǰ��ȷ���Լ��Ѿ��ܻ�����٣�����������ɿ�֮ǰ������ٵ�����

void TIM3_IRQHandler(void)                            //TIM3�ж�
{
	if(TIM_GetITStatus(TIM3, TIM_IT_Update) != RESET) //���ָ����TIM�жϷ������
	{
		TIM_ClearITPendingBit(TIM3, TIM_IT_Update);   //���TIMx���жϴ�����λ
		
		Get_Motor_Speed(&leftSpeedNow,&rightSpeedNow);//�������ٶ�
		
		Led_Flash(100);                               //������˸��
	}
}

