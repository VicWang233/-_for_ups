# -*- coding: utf-8 -*-
"""
coding by VicWang

This is a temporary script file.
"""
import time
import serial
import tkinter as tk
import threading
#from tkinter import ttk
#import serial.tools.list_ports as list_ports
import protocol_config_apply_to_get_analog_quantity as protocol
import func_def as func
#import untitled1

'''
-------------------------------------------------
串口定义
-------------------------------------------------
'''
ser = serial.Serial()

'''
窗口部分 
'''

software =tk.Tk() 
software.geometry('1000x720')  #窗口大小 

'''
创建框架
'''
#框架frame1：顶部菜单框架。frame2：左侧数据框架 frame3右侧数据框架。
frame_1 = tk.Frame(software,width=200,height=30,borderwidth = 2,relief ='groove') #框架1，内含第一行4个构件
frame_1.grid(row=0,column=0)
frame_2 = tk.Frame(software,width=100,height = 100,borderwidth = 2,relief = 'sunken') #框架2,28个数字
frame_2.grid(row=1,column = 0)
frame_3 = tk.Frame(software,width=100,height = 100,borderwidth = 2,relief = 'sunken') #框架3，电池等信息
frame_3.grid(row=1,column = 1,sticky = 'N')

func.common_label(frame_2,'label_inFrame_index_left','ID',0,0,5,'raised')
func.common_label(frame_2,'label_inFrame_name_left','名称',0,1,30,'raised')
func.common_label(frame_2,'label_inFrame_A','A相',0,2,15,'raised')
func.common_label(frame_2,'label_inFrame_B','B相',0,3,15,'raised')
func.common_label(frame_2,'label_inFrame_C','C相',0,4,15,'raised')
func.common_label(frame_3,'label_inFrame_index_right','ID',0,0,5,'raised')
func.common_label(frame_3,'label_inFrame_name_right','名称',0,1,30,'raised')
func.common_label(frame_3,'label_inFrame_value_right','值',0,2,15,'raised')


'''
数据显示label
'''


#cfg调用类转为对象
object_cfg_tool = func.cfg_tool()
#设定Analog1_data面板ID名称值等
for i in range(0,object_cfg_tool.Pick_Section_number('Analog1_Num')):
    func.common_label(frame_2,i,str(i),i+1,0,5,'groove')    #ID
    name_left = object_cfg_tool.Pick_Option_In_Section('Analog1_Data',i,1)
    func.common_label(frame_2,name_left,name_left,i+1,1,30,'groove')    #名称
#设定Analog2_data面板ID名称值等
for i in range(0,object_cfg_tool.Pick_Section_number('Analog2_Num')):
    func.common_label(frame_3,i,str(i),i+1,0,5,'groove')    #ID
    name_right = object_cfg_tool.Pick_Option_In_Section('Analog2_Data',i,1)
    func.common_label(frame_3,name_right,name_right,i+1,1,30,'groove')   #名称

#B、C两相数据设定为'\'
for i in range(0,object_cfg_tool.Pick_Section_number('Analog1_Num')):
    if i == 6 or i == 16 or i == 20:
        func.common_label(frame_2,i,'',i+1,3,15,'groove')
        func.common_label(frame_2,i,'',i+1,4,15,'groove')
    else:
        func.common_label(frame_2,i,'\\',i+1,3,15,'groove')
        func.common_label(frame_2,i,'\\',i+1,4,15,'groove') 


#####################后台数据处理线程模块##################
response_data_str = ''           #定义接收到的数据字符串
Device_VER = ''
Device_ADR = ''
Device_CID2 = ''
def send_massage(): 
    if ser.isOpen()== False:                                
        software.title('串口助手-通讯异常')
        func.set_analog_quantity_to_zero(frame_2,frame_3)
        com_available = func.figure_out_available_com('~21012A4F0000FD8F\r')
        ser.port = com_available
        ser.baudrate = 9600
        ser.timeout = 1
        ser.open()
        global Device_VER,Device_ADR,Device_CID2,response_data_str           #使用全局变量，可调用后面的Device
        
    elif ser.isOpen()== True:
            try:                                        #此异常处理 用于检测是否串口被突然拔出
                ser.inWaiting()
            except(OSError,serial.SerialException):
                print("串口有问题")
                ser.close()
                software.title('串口助手-通讯异常')
                func.set_analog_quantity_to_zero(frame_2,frame_3)
            else:
                if ser.inWaiting() == 0:
                    time.sleep(0.5)
    
                    '''
                    massage为命令，命令组成为4f获取的设备号和设备地址+中间部分+计算出的校验和
                    '''
                    massage_4F = '~21012A4F0000FD8F\r'      #获取协议版本号协议
                    chksum_for_41 = func.get_chksum(Device_VER+Device_ADR+'2A410000')
                    chksum_for_81 = func.get_chksum(Device_VER+Device_ADR+'2A810000')
                    chksum_for_82 = func.get_chksum(Device_VER+Device_ADR+'2A820000')
                    chksum_for_83 = func.get_chksum(Device_VER+Device_ADR+'2A830000')
                    massage_41 = '~'+Device_VER+Device_ADR+'2A410000'+chksum_for_41+'\r'      #获取标准模拟量数据指令
                    massage_81 = '~'+Device_VER+Device_ADR+'2A810000'+chksum_for_81+'\r'      #获取自定义模拟量数据1
                    massage_82 = '~'+Device_VER+Device_ADR+'2A820000'+chksum_for_82+'\r'      #获取自定义模拟量数据2
                    massage_83 = '~'+Device_VER+Device_ADR+'2A830000'+chksum_for_83+'\r'      #获取自定义模拟量数据3
                    if Device_CID2 == '':
                        ser.write(massage_4F.encode())
                        Device_CID2 = func.data_split(massage_4F,'CID2')
                    elif Device_CID2 == '4F':
                        ser.write(massage_41.encode())
                        Device_CID2 = func.data_split(massage_41,'CID2')
                    elif Device_CID2 == '41':
                        ser.write(massage_81.encode())
                        Device_CID2 = func.data_split(massage_81,'CID2')
                    elif Device_CID2 == '81':
                        ser.write(massage_82.encode())
                        Device_CID2 = func.data_split(massage_82,'CID2')
                    elif Device_CID2 == '82':
                        ser.write(massage_83.encode())
                        Device_CID2 = func.data_split(massage_83,'CID2')
                    elif Device_CID2 == '83':
                        ser.write(massage_41.encode())
                        Device_CID2 = func.data_split(massage_41,'CID2')
                    
                    
                
                
                while ser.inWaiting()>0:                 #串口等待数据的数量  
                    #global response_data_str
                    data = ''
                    try:                                     #尝试读取串口数据 ，如果 串口数据 有 格式 错误 则break
                        data += ser.read(1).decode()         #将等待数据持续写入data中bytes转str
                        response_data_str+= data
                        
                    except:
                        break
                    
                    if data =='\r':                      #判断是否为回车
                        print("response_data_str",response_data_str)
                        Device_LENGTH = func.data_split(response_data_str,'LENGTH')
                        print("Device_LENGTH",Device_LENGTH)
                        #print("massage_41",chksum_for_41)
                        Device_VER = func.data_split(response_data_str,'VER')   #抽出响应中的VER
                        Device_ADR = func.data_split(response_data_str,'ADR')   #抽出响应中的ADR
                        Device_RTN = func.data_split(response_data_str,'CID2')  #抽出响应中的CID2
                        Device_DATA_NUM = func.data_split(response_data_str,'DATA_NUM') #抽出响应的DATA数量，也就是判断标准 
                        Device_DATAFLAG = func.data_split(response_data_str,'DATAFLAG')
                        print("Device_DATA_NUM",Device_DATA_NUM)
                        #print("Device_Ver",Device_Ver)
                        if Device_RTN != '00':
                            software.title('串口助手-通讯异常')
                            CID2_DICT = func.data_split(response_data_str,'CID2_DICT')
                            CID2_VALUE = CID2_DICT.get(Device_RTN,'RTN传值错误')
                            print("返回值RTN为%s:"%CID2_VALUE)
                            #print('RTN不为00')
                            Device_CID2 = ''#CID2重新置空，方便发送请求指令
                            
                        else:          #RTN为00，数据正常，判断长度来选择分配数值
                            print('当前请求CID2',Device_CID2)
                            
                            response_data_str = response_data_str.split('\r')[0]                #去掉结束位                    
                            protocol_list = protocol.analysis_protocol(response_data_str)
                            print('protocol_list：',protocol_list)
                            #下列字典的键值对用于放入label面板中，通过set_analog_quantity_to_label函数实现
                            #key:名称  value1:所在框架 value2：响应解析值 value3:所在面板的位置（行）

                            if  Device_CID2 == '41':
                                '''标准模拟量数据，使用字典实现循环。'''
                                common_label_dict_for_41 = {'输入线电压':[frame_2,protocol_list[0],1],
                                                            '输出相电压':[frame_2,protocol_list[3],9],
                                                            '输出电流':[frame_2,protocol_list[6],10],
                                                            '电池电压':[frame_3,protocol_list[9],1],
                                                            '输出频率':[frame_2,protocol_list[10],16],
                                                            '电池容量':[frame_3,protocol_list[11],5],
                                                            '电池温度':[frame_3,protocol_list[12],3]
                                                            }
                                
                                func.set_analog_quantity_to_label(common_label_dict_for_41)
                            elif Device_CID2 == '81':
                                '自定义模拟量数据1'
                                common_label_dict_for_81 = {'输入相电流':[frame_2,protocol_list[0],2],
                                                            '输入频率':[frame_2,protocol_list[3],3],
                                                            '旁路线电压':[frame_2,protocol_list[4],4],
                                                            '旁路相电压':[frame_2,protocol_list[7],5],
                                                            '旁路频率':[frame_2,protocol_list[10],6],
                                                            '输出有功功率':[frame_2,protocol_list[14],11],
                                                            '输出功率因数':[frame_2,protocol_list[20],13],
                                                            '负载':[frame_2,protocol_list[23],14],
                                                            '峰值比':[frame_2,protocol_list[26],15],
                                                            '输出视在功率':[frame_2,protocol_list[17],29]
                                                            }
                                func.set_analog_quantity_to_label(common_label_dict_for_81)
                                
                            elif Device_CID2 == '82':
                                if Device_DATAFLAG == 'A3':
                                    '自定义模拟量数据2' 
                                    common_label_dict_for_82 = {'系统输出有功功率':[frame_2,protocol_list[0],18],
                                                                '系统输出无功功率':[frame_2,protocol_list[3],19],
                                                                '系统输出视在功率':[frame_3,protocol_list[6],20],
                                                                '电池电流':[frame_3,protocol_list[10],2],
                                                                '后备时间':[frame_3,protocol_list[9],4]
                                                                }

                                    func.set_analog_quantity_to_label(common_label_dict_for_82)

                                elif Device_CID2 == '83':
                                    '自定义模拟量数据3'
                                    common_label_dict_for_83 = {'输出有功功率':[frame_2,protocol_list[3],12],
                                                                '电池老化系数':[frame_2,protocol_list[1],6],
                                                                '总输入功率因数':[frame_3,protocol_list[2],15],
                                                                '环境温度':[frame_3,protocol_list[0],19],
                                                                'IGBT模块温度':[frame_3,protocol_list[9],20]
                                                                }
                                    func.set_analog_quantity_to_label(common_label_dict_for_83)
                                    '''
                                    func.common_label(frame_2,'输出有功功率',protocol_list[3],12,2,15,'groove')
                                    func.common_label(frame_3,'电池老化系数',protocol_list[1],6,2,15,'groove')
                                    func.common_label(frame_3,'总输入功率因数',protocol_list[2],15,2,15,'groove')
                                    func.common_label(frame_3,'环境温度',protocol_list[0],19,2,15,'groove')
                                    func.common_label(frame_3,'IGBT模块温度',protocol_list[9],20,2,15,'groove')
                                    '''
                                else:
                                    print("DATA_NUM数据有错误")
                            elif Device_DATA_NUM == '90':
                                print('DATA_NUM为90')
                            else:
                                print("DATA_NUM数据有错误")
                            software.title('串口助手-通讯正常')
    
                            ser.flushInput()
                        
                        
                        
                if ser.inWaiting() == 0:      #串口中待处理的数据为0后，把响应字符串清0
                    print("response_data_str的值为",response_data_str)
                    response_data_str = ''    
    global send_massage_timer
    send_massage_timer = threading.Timer(1,send_massage) 
    send_massage_timer.start()
send_massage_timer = threading.Timer(1,send_massage) 
send_massage_timer.start()

software.mainloop()








