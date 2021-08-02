/******************** (C) COPYRIGHT 2008 STMicroelectronics ********************
* File Name          : main.c
* Author             : MCD Application Team
* Version            : V2.0.1
* Date               : 06/13/2008
* Description        : Main program body
********************************************************************************
* THE PRESENT FIRMWARE WHICH IS FOR GUIDANCE ONLY AIMS AT PROVIDING CUSTOMERS
* WITH CODING INFORMATION REGARDING THEIR PRODUCTS IN ORDER FOR THEM TO SAVE TIME.
* AS A RESULT, STMICROELECTRONICS SHALL NOT BE HELD LIABLE FOR ANY DIRECT,
* INDIRECT OR CONSEQUENTIAL DAMAGES WITH RESPECT TO ANY CLAIMS ARISING FROM THE
* CONTENT OF SUCH FIRMWARE AND/OR THE USE MADE BY CUSTOMERS OF THE CODING
* INFORMATION CONTAINED HEREIN IN CONNECTION WITH THEIR PRODUCTS.
*******************************************************************************/

/* Includes ------------------------------------------------------------------*/
#include "System_init.h"
#include "Adjust.h "
/* Private typedef -----------------------------------------------------------*/
/* Private define ------------------------------------------------------------*/
/* Private macro -------------------------------------------------------------*/
/* Private variables ---------------------------------------------------------*/
extern vu16 ADCConvertedValue;
extern unsigned char Flag_1mS;
extern unsigned char Flag_100mS;
extern unsigned char Flag_1S;
extern int U_Set;
extern u16 CCR1_Val;
/* Private function prototypes -----------------------------------------------*/
/*******************************************************************************
* Function Name  : main
* Description    : Main program
* Input          : None
* Output         : None
* Return         : None
*******************************************************************************/
int main(void)
{
unsigned char N=0;
float Pv;
#ifdef DEBUG
  debug();
#endif
  System_Configuration();
  printf("This is an example of PID!\n\r");
  while (1)
  { 
  switch (N){
	  case 0:
	  		if(Flag_1mS==1)
					{
						if(U_Set-ADCConvertedValue>=10||U_Set-ADCConvertedValue<=-10)
							{
								Pv=Vol(U_Set,ADCConvertedValue);
								CCR1_Val=CCR1_Val+Pv/2.04;
								if(CCR1_Val>=999)
									CCR1_Val=999;
								else if(CCR1_Val<=1)
									CCR1_Val=1;

			TIM3->CCR1=CCR1_Val;
							}
							Flag_1mS=0;
					}
			break;
	  case 1:
	  	  	if(Flag_100mS==1)
						{
							printf("%d,",ADCConvertedValue);printf("%d   ",CCR1_Val);
							Flag_100mS=0;
						}
			break;
	  case 2:
	  	  	if(Flag_1S==1)
						{
			//printf("The feedback is %d\n\r",ADCConvertedValue);
							//printf("The feedback is %d\n\r",ADDConvertedValue);
							Flag_1S=0;

							Flag_100mS=0;
						}
			break;
	  default : break;
	}
	
  N++;
  if(N==3)
		{
   N=0;
		}
  }
}
/******************* (C) COPYRIGHT 2008 STMicroelectronics *****END OF FILE****/
