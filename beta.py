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
import protocol_config_apply_to_get_switching_value as protocol_switch
import protocol_config_apply_to_get_warning_value as protocol_warning
import protocol_config_apply_to_get_sysdata as protocol_sysdata
#import untitled1


#实例化cfg工具
object_cfg_tool = func.cfg_tool()
'''
-------------------------------------------------
串口定义为实例
-------------------------------------------------
'''
ser = serial.Serial()

'''
窗口部分 
'''

software =tk.Tk() 
software.geometry('700x540')  #窗口大小 

'''
创建框架
'''
frame_2 = tk.Frame(software,width=100,height = 100,borderwidth = 2,relief = 'sunken') #框架2,[Analog2_Data]						
frame_2.grid(row=0,column = 0)
frame_3 = tk.Frame(software,width=100,height = 100,borderwidth = 2,relief = 'sunken') #框架3，电池等信息[Analog2_Data]					
frame_3.grid(row=0,column = 1,sticky = 'N')
#数据显示label
func.common_label(frame_2,'ID',0,0,5,'raised')
func.common_label(frame_2,'名称',0,1,20,'raised')
func.common_label(frame_2,'A相',0,2,10,'raised')
func.common_label(frame_2,'B相',0,3,10,'raised')
func.common_label(frame_2,'C相',0,4,10,'raised')
func.common_label(frame_3,'ID',0,0,5,'raised')
func.common_label(frame_3,'名称',0,1,20,'raised')
func.common_label(frame_3,'值',0,2,10,'raised')


#线程传递变量定义，此部分值用于付给窗口用于把值显示出来。

receive_sysdata_str = ''
receive_switch_data_str = ''
receive_warning_data_str = ''
#菜单
'''
设置线程
'''
#系统设置窗口线程
def Setting_Sysdata_Window():
    sysdata_win = tk.Toplevel()
    sysdata_win.title('系统级参数设置')
    sysdata_win.geometry = ('600x800')
    func.common_label(sysdata_win,'参数名称',0,0,23,'raised')
    func.common_label(sysdata_win,'当前值',0,1,10,'raised')
    func.common_label(sysdata_win,'备注信息',0,2,75,'raised')
    ###第一列
    for i in range(int(object_cfg_tool.Pick_Option_In_Section('SYSData_Num',0,0))):
       Sysdata_name = object_cfg_tool.Pick_Option_In_Section('SYSData_List',i,1)
       func.common_label(sysdata_win,Sysdata_name,i+1,0,23,'groove')
    ###第三列
    for i in range(int(object_cfg_tool.Pick_Option_In_Section('SYSData_Num',0,0))):
       Sysdata_name = object_cfg_tool.Pick_Option_In_Section('SYSData_List',i,5)      ###！注意这个5可能会变
       func.common_label(sysdata_win,Sysdata_name,i+1,2,75,'groove')
    ###第二列button,路子1：线程 路子2textvariable
    def reflash_Sysdata():
        global receive_sysdata_str
        if receive_sysdata_str == '':
            sysdata_win.title('系统级参数设置-等待数据中')
            for i in range(int(object_cfg_tool.Pick_Option_In_Section('SYSData_Num',0,0))):
               func.common_label(sysdata_win,'\\',i+1,1,10,'groove')
        else:
           sysdata_win.title('开关量状态-已获取数据')
           sysdata_return_list = protocol_sysdata.analysis_protocol(receive_sysdata_str)
           for i in range(len(sysdata_return_list)):
               func.common_label_for_modify(sysdata_win,sysdata_return_list[i],i+1,1,10,'groove',object_cfg_tool.Pick_Option_In_Section('SYSData_List',i,1),i)
        
        reflash_switch_value = threading.Timer(1,reflash_Sysdata)
        reflash_switch_value.start()
    reflash_switch_value = threading.Timer(1,reflash_Sysdata)
    reflash_switch_value.start()
    

'''
刷新开关量线程
'''
def Switching_Value_Window():         #开关量窗口及数值定义，为方便调用，定义于此。
   win = tk.Toplevel()
   win.title('开关量状态-正在获取数据')
   win.geometry('430x440')
   func.common_label(win,'开关量名称',0,0,30,'raised')
   func.common_label(win,'开关量状态',0,1,30,'raised')

   for i in range(int(object_cfg_tool.Pick_Option_In_Section('Switching_Value_Num',0,0))):
       Switching_Value_name = object_cfg_tool.Pick_Option_In_Section('Switching_Value_list',i,1)
       func.common_label(win,Switching_Value_name,i+1,0,30,'groove')

   def reflash_Switching_value():  #定时刷新开关量线程
       global receive_switch_data_str
       if receive_switch_data_str == '':
           win.title('开关量状态-正在获取数据')
           for i in range(int(object_cfg_tool.Pick_Option_In_Section('Switching_Value_Num',0,0))):
               func.common_label(win,'\\',i+1,1,30,'groove')

       else:
           win.title('开关量状态-已获取数据')
           switching_value_return_list = protocol_switch.analysis_protocol(receive_switch_data_str)
           for i in range(len(switching_value_return_list)):
               func.common_label(win,switching_value_return_list[i],i+1,1,30,'groove')
       #win.protocol('WM_DELETE_WINDOW',win.destroy())
       reflash_switch_value = threading.Timer(1,reflash_Switching_value)
       reflash_switch_value.start()
   reflash_switch_value = threading.Timer(1,reflash_Switching_value)
   reflash_switch_value.start()
'''
刷新告警量线程
'''       
def Warning_Value_Window():         #告警量窗口及数值定义，为方便调用，定义于此。
   #print('ssssssssssssssssssssreceive_warning_data_str',receive_warning_data_str)
   win_top = tk.Toplevel()
   win_top.title('告警量状态-正在获取数据')
   win_top.geometry('1180x420')
   list_for_menu = ['告警量part1名称','告警量part1状态','告警量part2名称','告警量part2状态',
                    '告警量part3名称','告警量part3状态','告警量part4名称','告警量part4状态',]
   for i in range(len(list_for_menu)):
       func.common_label(win_top,list_for_menu[i],0,i,20,'raised')   #加载告警banner
       
   warning_value_name_sections = ['Warning_Value_list_part1','Warning_Value_list_part2',
                                  'Warning_Value_list_part3','Warning_Value_list_part4'] 
   range_length = range(17)
   for i in range(0,4):                     #外部循环section
       for j in range_length:                #内部循环section的option并赋值
           warning_Value_name = object_cfg_tool.Pick_Option_In_Section(warning_value_name_sections[i],j,1)
           func.common_label(win_top,warning_Value_name,j+1,2*i,20,'groove')
   def reflash_Warning_value():  #定时刷新开关量线程
       global receive_warning_data_str
       if receive_warning_data_str == '':
           win_top.title('告警量状态-正在获取数据')
           for i in range(0,4):                     #外部循环section
               for j in range_length:                #内部循环section的option并赋值
                   func.common_label(win_top,'\\',j+1,2*i+1,20,'groove')
       else:
           win_top.title('告警量状态-已获取数据')
           warning_value_return_list = protocol_warning.analysis_protocol(receive_warning_data_str)
           #print('warning_value_return_list:',warning_value_return_list)
           warning_value_return_part1 = warning_value_return_list[:17]
           warning_value_return_part2 = warning_value_return_list[17:34]
           warning_value_return_part3 = warning_value_return_list[34:51]
           warning_value_return_part4 = warning_value_return_list[51:]
           warning_value_return_part_list = [warning_value_return_part1,warning_value_return_part2,
                                             warning_value_return_part3,warning_value_return_part4]
           

           for i in range(0,4):                     #外部循环section
               for j in range_length:                #内部循环section的option并赋值
                   func.common_label(win_top,warning_value_return_part_list[i][j],j+1,2*i+1,20,'groove')
        
       reflash_warning_value = threading.Timer(1,reflash_Warning_value)
       reflash_warning_value.start()
   reflash_warning_value = threading.Timer(1,reflash_Warning_value)
   reflash_warning_value.start()           
                   
                   
menu_main_button = tk.Menu(software)

menulist_file =  ['模拟量数据保存','故障点数据保存','历史记录数据保存','退出']
commandlist_file = [func.donothing,func.donothing,func.donothing,software.quit]
func.set_the_menu(menu_main_button,'文件','weight_file',menulist_file,commandlist_file)

menulist_config =  ['系统参数设置','整流参数设置','逆变参数设置','电池参数设置']
commandlist_config = [Setting_Sysdata_Window,func.donothing,func.donothing,func.donothing]
func.set_the_menu(menu_main_button,'设置','weight_config',menulist_config,commandlist_config)

menulist_advanced =  ['修改密码','修改电池曲线','序列号','调试诊断','软件升级']
commandlist_advanced = [func.donothing,func.donothing,func.donothing,func.donothing,func.donothing]
func.set_the_menu(menu_main_button,'高级操作','weight_advanced',menulist_advanced,commandlist_advanced)

menulist_help =  ['关于']
commandlist_help = [func.donothing]
func.set_the_menu(menu_main_button,'帮助','weight_help',menulist_help,commandlist_help)

menulist_Switching_and_Warning =  ['开关量状态','报警量状态']
commandlist_Switching_and_Warning = [Switching_Value_Window,Warning_Value_Window]
func.set_the_menu(menu_main_button,'开关与报警','weight_help',menulist_Switching_and_Warning,commandlist_Switching_and_Warning)

software.config(menu =menu_main_button)

'''
数据显示label
'''


#cfg调用类转为对象

#设定Analog1_data面板ID名称值等
for i in range(0,int(object_cfg_tool.Pick_Option_In_Section('Analog1_Num',0,0))):
    func.common_label(frame_2,i,i+1,0,5,'groove')    #ID
    name_left = object_cfg_tool.Pick_Option_In_Section('Analog1_Data',i,1)
    func.common_label(frame_2,name_left,i+1,1,20,'groove')    #名称
#设定Analog2_data面板ID名称值等
for i in range(0,int(object_cfg_tool.Pick_Option_In_Section('Analog2_Num',0,0))):
    func.common_label(frame_3,i,i+1,0,5,'groove')    #ID
    name_right = object_cfg_tool.Pick_Option_In_Section('Analog2_Data',i,1)
    func.common_label(frame_3,name_right,i+1,1,20,'groove')   #名称

#B、C两相数据设定为'\'
for i in range(0,int(object_cfg_tool.Pick_Option_In_Section('Analog1_Num',0,0))):
    if i == 6 or i == 16 or i == 20:
        func.common_label(frame_2,'',i+1,3,10,'groove')
        func.common_label(frame_2,'',i+1,4,10,'groove')
    else:
        func.common_label(frame_2,'\\',i+1,3,10,'groove')
        func.common_label(frame_2,'\\',i+1,4,10,'groove') 


#####################后台数据处理线程模块##################
response_data_str = ''           #定义接收到的数据字符串
Device_VER = ''
Device_ADR = ''
Device_CID2 = ''
def send_massage():
    global receive_switch_data_str,receive_warning_data_str,receive_sysdata_str
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
            try:
                if ser.inWaiting() == 0:
                    time.sleep(0.1)
                    
                    
                    ##############设置量获取############
                    res = object_cfg_tool.get_value_IN_CFG('Config_for_Sysdata','temporary_variable','command')[0]
                    Sysdata_0 = object_cfg_tool.get_value_IN_CFG('Config_for_Sysdata','temporary_variable','command')[1]
                    print(res)
                    print(Sysdata_0)
                    '''
                    massage为命令，命令组成为4f获取的设备号和设备地址+中间部分+计算出的校验和
                    '''
                    massage_4F = '~21012A4F0000FD8F\r'      #获取协议版本号协议
                    ############模拟量chksum############
                    chksum_for_41 = func.get_chksum(Device_VER+Device_ADR+'2A410000')
                    chksum_for_90 = func.get_chksum(Device_VER+Device_ADR+'2A900000')
                    chksum_for_81 = func.get_chksum(Device_VER+Device_ADR+'2A810000')
                    chksum_for_82 = func.get_chksum(Device_VER+Device_ADR+'2A820000')
                    chksum_for_83 = func.get_chksum(Device_VER+Device_ADR+'2A830000')
                    chksum_for_43 = func.get_chksum(Device_VER+Device_ADR+'2A430000')
                    chksum_for_44 = func.get_chksum(Device_VER+Device_ADR+'2A440000')
                    chksum_for_80 = func.get_chksum(Device_VER+Device_ADR+'2A800000')
                    ############设置量chksum############
                    chksum_for_97 = func.get_chksum(Device_VER+Device_ADR+'2A97600A'+Sysdata_0+res)
                    ############模拟量完整命令############
                    massage_41 = '~'+Device_VER+Device_ADR+'2A410000'+chksum_for_41+'\r'      #获取标准模拟量数据指令
                    massage_90 = '~'+Device_VER+Device_ADR+'2A900000'+chksum_for_90+'\r'      #获取调试量数据
                    massage_81 = '~'+Device_VER+Device_ADR+'2A810000'+chksum_for_81+'\r'      #获取自定义模拟量数据1
                    massage_82 = '~'+Device_VER+Device_ADR+'2A820000'+chksum_for_82+'\r'      #获取自定义模拟量数据2
                    massage_83 = '~'+Device_VER+Device_ADR+'2A830000'+chksum_for_83+'\r'      #获取自定义模拟量数据3
                    massage_43 = '~'+Device_VER+Device_ADR+'2A430000'+chksum_for_43+'\r'      #获取开关量
                    massage_44 = '~'+Device_VER+Device_ADR+'2A440000'+chksum_for_44+'\r'      #获取告警量
                    massage_80 = '~'+Device_VER+Device_ADR+'2A800000'+chksum_for_80+'\r'      #获取系统设置当前值
                    ##########设置量完整命令##############
                    
                    if res == '1' or Sysdata_0 == '1':
                        massage_97 = '0'
                    else:
                        massage_97 = '~'+Device_VER+Device_ADR+'2A97600A'+Sysdata_0+res+chksum_for_97+'\r'
                        print("massage_97",massage_97)
                    if Device_CID2 == '':
                        ser.write(massage_4F.encode())
                        Device_CID2 = '4F'
                    elif Device_CID2 == '4F':
                        ser.write(massage_41.encode())
                        Device_CID2 = '41'
                    elif Device_CID2 == '41':
                        ser.write(massage_90.encode())
                        Device_CID2 = '90'
                    elif Device_CID2 == '90':
                        ser.write(massage_81.encode())
                        Device_CID2 = '81'
                    elif Device_CID2 == '81':
                        ser.write(massage_82.encode())
                        Device_CID2 = '82'
                    elif Device_CID2 == '82':
                        ser.write(massage_83.encode())
                        Device_CID2 = '83'
                    elif Device_CID2 == '83':
                        ser.write(massage_43.encode())
                        Device_CID2 = '43'
                    elif Device_CID2 == '43':
                        ser.write(massage_44.encode())
                        Device_CID2 = '44'
                    elif Device_CID2 == '44':
                        if massage_97 == '0':
                            Device_CID2 = '97'
                        else:
                            ser.write(massage_97.encode())
                            Device_CID2 = '97'
                    elif Device_CID2 == '97':
                        ser.write(massage_80.encode())
                        Device_CID2 = '80'
                    elif Device_CID2 == '80':
                        ser.write(massage_41.encode())
                        Device_CID2 = '41'
                    
                    
                
                
                while ser.inWaiting()>0:                 #串口等待数据的数量  
                    #global response_data_str
                    data = ''
                    try:                                     #尝试读取串口数据 ，如果 串口数据 有 格式 错误 则break
                        data += ser.read(1).decode()         #将等待数据持续写入data中bytes转str
                        response_data_str+= data
                        
                    except:
                        break
                    
                    if data =='\r':                      #判断是否为回车
                        #print("response_data_str",response_data_str)
                        #Device_LENGTH = func.data_split(response_data_str,'LENGTH')
                        #print("Device_LENGTH",Device_LENGTH)
                        #print("massage_41",chksum_for_41)
                        Device_VER = func.data_split(response_data_str,'VER')   #抽出响应中的VER
                        Device_ADR = func.data_split(response_data_str,'ADR')   #抽出响应中的ADR
                        Device_RTN = func.data_split(response_data_str,'CID2')  #抽出响应中的CID2
                        #Device_DATA_NUM = func.data_split(response_data_str,'DATA_NUM') #抽出响应的DATA数量，也就是判断标准 
                        Device_DATAFLAG = func.data_split(response_data_str,'DATAFLAG')
                        #print("Device_DATA_NUM",Device_DATA_NUM)
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
                            
                            response_data_str = response_data_str.split('\r')[0]#去掉结束位
                            '''
                            开关量于告警量空间
                            '''
                            if Device_CID2 == '43':                                                                             
                                receive_switch_data_str = response_data_str
                                break
                            elif Device_CID2 == '44':
                                receive_warning_data_str = response_data_str
                                break
                            elif Device_CID2 == '80':
                                receive_sysdata_str = response_data_str
                                break
                           #########设置量空间############
                            elif Device_CID2 == '97':
                                if Device_RTN == '00':
                                    print("设置成功")
                                else: 
                                    print("设置失败码：",Device_RTN)
                            ########################################    
                            else:
                                protocol_list = protocol.analysis_protocol(response_data_str)
                                #print('protocol_list：',protocol_list)
                            #下列字典的键值对用于放入label面板中，通过set_analog_quantity_to_label函数实现
                            #key:名称  value1:所在框架 value2：响应解析值 value3:所在面板的位置（行）

                            if  Device_CID2 == '41':
                                
                                
                                common_label_dict_for_41 = {'输入线电压':[frame_2,protocol_list[0],1],
                                                            '输出相电压':[frame_2,protocol_list[3],6],
                                                            '输出电流':[frame_2,protocol_list[6],7],
                                                            '电池电压':[frame_3,protocol_list[9],1],
                                                            '输出频率':[frame_2,protocol_list[10],13],
                                                            '电池容量':[frame_3,protocol_list[11],7],
                                                            '电池温度':[frame_3,protocol_list[12],5]
                                                            }
                                
                                func.set_analog_quantity_to_label(common_label_dict_for_41)
                                
                            elif Device_CID2 == '90':
                                '自定义模拟量数据1'
                                common_label_dict_for_90 = {'6p整流器相电流':[frame_2,protocol_list[15],17],
                                                            '逆变相电压':[frame_2,protocol_list[0],18],
                                                            '逆变相电流':[frame_2,protocol_list[3],19],
                                                            '电感电流':[frame_2,protocol_list[28],20],
                                                            '输出电容电流':[frame_2,protocol_list[25],21],
                                                            '母线电压':[frame_3,protocol_list[6],3],
                                                            'DSP调试变量1':[frame_3,protocol_list[7],9],
                                                            'DSP调试变量2':[frame_3,protocol_list[8],10],
                                                            'DSP调试变量3':[frame_3,protocol_list[9],11],
                                                            'DSP调试变量4':[frame_3,protocol_list[10],12],
                                                            'UPS序列号':[frame_3,protocol_list[35],18]
                                                            }
                                func.set_analog_quantity_to_label(common_label_dict_for_90)
                                
                            elif Device_CID2 == '81':
                                '自定义模拟量数据1'
                                common_label_dict_for_81 = {'输入相电流':[frame_2,protocol_list[0],2],
                                                            '输入频率':[frame_2,protocol_list[3],3],
                                                            #'旁路线电压':[frame_2,protocol_list[4],4],
                                                            '旁路相电压':[frame_2,protocol_list[7],6],
                                                            '旁路频率':[frame_2,protocol_list[10],5],
                                                            '输出有功功率':[frame_2,protocol_list[14],8],
                                                            '输出功率因数':[frame_2,protocol_list[20],10],
                                                            '负载':[frame_2,protocol_list[23],11],
                                                            '峰值比':[frame_2,protocol_list[26],12],
                                                            '输出视在功率':[frame_2,protocol_list[17],22]
                                                            }
                                func.set_analog_quantity_to_label(common_label_dict_for_81)
                                
                            elif Device_CID2 == '82':
                                if Device_DATAFLAG == 'A3':
                                    '自定义模拟量数据2' 
                                    common_label_dict_for_82 = {'系统输出有功功率':[frame_2,protocol_list[0],14],
                                                                '系统输出无功功率':[frame_2,protocol_list[3],15],
                                                                '系统输出视在功率':[frame_3,protocol_list[6],16],
                                                                '电池电流':[frame_3,protocol_list[10],2],
                                                                '后备时间':[frame_3,protocol_list[9],6]
                                                                }

                                    func.set_analog_quantity_to_label(common_label_dict_for_82)

                                elif Device_CID2 == '83':
                                    '自定义模拟量数据3'
                                    common_label_dict_for_83 = {'输出有功功率':[frame_2,protocol_list[3],12],
                                                                '电池老化系数':[frame_3,protocol_list[1],8],
                                                                '总输入功率因数':[frame_3,protocol_list[2],15],
                                                                '环境温度':[frame_3,protocol_list[0],16],
                                                                'IGBT模块温度':[frame_3,protocol_list[9],17],
                                                                '充电电压':[frame_3,protocol_list[11],4]
                                                                }
                                    func.set_analog_quantity_to_label(common_label_dict_for_83)
                                                        
                            else:
                                print("Device_CID2无对应:",Device_CID2)
                            software.title('串口助手-通讯正常')

                            ser.flushInput()
                         
                        
                        
                if ser.inWaiting() == 0:      #串口中待处理的数据为0后，把响应字符串清0
                    #print("response_data_str的值为",response_data_str)
                    response_data_str = '' 
            except(OSError,serial.SerialException):
                #print("串口有问题")
                ser.close()
                software.title('串口助手-通讯异常')
                func.set_analog_quantity_to_zero(frame_2,frame_3)
                receive_switch_data_str = ''      #拔出串口开关量手动置空
                receive_warning_data_str = ''
                receive_sysdata_str = ''
    global send_massage_timer
    send_massage_timer = threading.Timer(0.4,send_massage) 
    send_massage_timer.start()
send_massage_timer = threading.Timer(0.4,send_massage) 
send_massage_timer.start()






software.mainloop()








