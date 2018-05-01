# -*- coding: utf-8 -*-
"""
Created on Thu Apr 19 21:09:58 2018

@author: VicWang
"""
import tkinter as tk
#import configparser
import serial.tools.list_ports as list_ports
import serial
import time
from configparser import ConfigParser   #取configparser模块中的ConfigParser类
'''
-------------------------------------------------------------------------------
cfg文件调用类函数定义
-------------------------------------------------------------------------------
'''
###########指定section和option的序号调出参数名###########（未在工程中使用）
#section_you_choose=你选择的section，option_i_you_choose=你选择的section下的列表序号。
#返回选定option的参数值

#用于处理CFG文件的类
class cfg_tool(ConfigParser):           #继承父类
    def __init__(self):                 #初始化，定义需要搞的cfg文件名，
        self.conf = ConfigParser(allow_no_value=True)    #定义加载cfg文件的对象
        self.conf.read('ToolsDebugChs.cfg')                          #读cfg文件
        self.sections = self.conf.sections()
        
    def Pick_Section_number(self,section_num_you_choose):
        for i in range(len(self.sections)):                          #循环找出对应的section
            if self.sections[i] == section_num_you_choose:
                return int(self.conf.options(self.sections[i])[0])
        
    '''
    section_you_choose:你选择的section，格式为字符串
    option_i_you_choose:你选择的option行，格式为int
    
    '''
    #参数1：self，参数2：所选的section，参数3：section中所选的option，参数4：option中所选的元素 
    def Pick_Option_In_Section(self,section_you_choose,option_row_you_choose,option_list_i):
                options = self.conf.options(section_you_choose)       #options数组
                for i in range(len(options)):                   #对应的行
                    if i == option_row_you_choose:
                            if options[i].split('\t')[1] == 'a':
                                return ''
                            else:
                                return options[i].split('\t')[option_list_i]
            
            
            
            #修改cfg的值，此功能目前不可用，待完善。
    def Change_Value_In_CFG(self,section_you_choose,option_row_you_choose,option_list_i,new_option_value):
        self.openfile = open('ToolsDebugChs.cfg','w')
        #self.conf.set(section_you_choose,option_i_you_choose,new_option_value)
        #self.Pick_Option_In_Section(self,section_you_choose,option_row_you_choose,option_list_i) = new_option_value
        self.conf.write(self.openfile) 
        print("%s的值%s改为%s"%(section_you_choose,option_row_you_choose,new_option_value))


'''
-------------------------------------------------------------------------------
通信类函数定义
-------------------------------------------------------------------------------
'''
#函数功能：split函数各位，并返回需求位。
#protocol_str:可选字符串
#protocol_option可选参数：VER版本，ADR设备，CID1，CID2，DATA_NUM数据个数。
#函数功能，拆分协议响应，返回所选option的值
def data_split(protocol_str,protocol_option):
    protocol = ''
    protocol = protocol_str
    #起始位判断
    if protocol[0] =='~':
        #print("起始位为:%s"%protocol[0])
        pass
    else:
        print("起始位错误:",protocol[0])
        return 0

    protocol_Drop_startbit = protocol.split("~")[1]   #split掉“~”
    protocol_ver = ''   #版本
    protocol_adr = ''    #设备号
    protocol_CID1 = ''   #CID1
    protocol_CID2 = ''   #CID2
    protocol_lchksum = ''   #LENGTH的lchksum
    protocol_length = ''    #LENGTH的LENID
    protocol_chksum = ''    #CHKSUM
    protocol_info = ''
    protocol_dataflag = ''
    protocol_data_number = ''
    protocol_CID2_dict = {
                          '00':'状态正常',
                          '01':'VER错',
                          '02':'CHKSUM错',
                          '03':'LCHKSUM',
                          '04':'CID2无效',
                          '05':'命令格式错',
                          '06':'无效数据',
                          '80':'无效权限',
                          '81':'操作失败',
                          '82':'存储芯片故障'
                          }

    for i in range(len(protocol_Drop_startbit)):
        if i<2:
            protocol_ver+=protocol_Drop_startbit[i]    #挑出版本
            if i == 1 and protocol_option == 'VER':
                return protocol_ver
        elif 2<=i<=3:
            protocol_adr+=protocol_Drop_startbit[i]    #挑出设备号，目前写死了默认只有两位
            if i == 3 and protocol_option == 'ADR':
                return protocol_adr
        elif 4<=i<=5:
            protocol_CID1+=protocol_Drop_startbit[i]    #挑出CID1
            if i == 5 and protocol_option == 'CID1':
                return protocol_CID1
        elif 6<=i<=7:
            protocol_CID2+=protocol_Drop_startbit[i]    #挑出CID2
            if i == 7 and protocol_option == 'CID2':
                return protocol_CID2
        elif i==8:
            protocol_lchksum+=protocol_Drop_startbit[i]  #LCHKSUM
            if i == 8 and protocol_option == 'LCHKSUM':
                return protocol_lchksum
        elif 9<=i<=11:
            protocol_length+=protocol_Drop_startbit[i]   #挑出length
            if i == 11 and protocol_option == 'LENGTH':
                return protocol_length
        elif len(protocol_Drop_startbit) == 16:
            protocol_chksum+=protocol_Drop_startbit[i]#如果长度为16，即无info时
            if protocol_option == 'CHKSUM':
                return protocol_chksum
        elif len(protocol_Drop_startbit) > 16:            #长度大于16，抽出info和chksum
            if 12<=i<=13:
                protocol_dataflag+=protocol_Drop_startbit[i]
                if i == 13 and protocol_option == 'DATAFLAG':
                    return protocol_dataflag
            elif 14<=i<=15:           #12和13位为datainfo前两位表示datainfo数据的长度
                protocol_data_number+=protocol_Drop_startbit[i]    #
                if i == 15 and protocol_option == 'DATA_NUM':
                    return protocol_data_number
            elif 16<=i<=len(protocol_Drop_startbit)-4-1:   #
                protocol_info+=protocol_Drop_startbit[i]
                if i == len(protocol_Drop_startbit)-4-1 and protocol_option == 'DATA_INFO':
                    return protocol_info
            elif  len(protocol_Drop_startbit)-4<=i<=len(protocol_Drop_startbit)-1:
                protocol_chksum+=protocol_Drop_startbit[i]
                if i == len(protocol_Drop_startbit)-1 and protocol_option == 'CHKSUM':
                    return protocol_chksum
        elif protocol_option == 'CID2_DICT':
            return protocol_CID2_dict
                
        
#################轮询COM口函数#########################
#返回设备com号，通过发送指令来判断COM口是否有响应。
def figure_out_available_com(command):
    ser = serial.Serial()
    port_list = list(list_ports.comports())
    com_list = []
    for i in range(0,len(port_list)):
        com_list.append(str(port_list[i]).split(' ')[0])
    while True:                                   #循环判断哪个com口时通的
            for i in range(0,len(com_list)):

                ser.port = com_list[i]
                ser.baudrate =9600
                try:                              #尝试开串口，监听异常
                    ser.open()                    
                    ser.write(command.encode())        #的写一串发送代码
                    time.sleep(1)                   #睡1秒
                    if ser.inWaiting()>0:           #如果串口有返回数据
                        return com_list[i]                       #返回com号，结束
                    elif ser.inWaiting()== 0:       #如果串口无返回数据，继续循环
                                    print("%s未返回"%com_list[i])   #输出无返回
                                    ser.close()
                except(OSError,serial.SerialException):     #如果触发串口占用异常
                                    print("%s占用或串口不可用"%com_list[i])
'''
-------------------------------------------------------------------------------
UI类函数定义
-------------------------------------------------------------------------------
'''
#################通用label函数#########################
#window=label所在框架，name=label名称，text_1=label显示的文本,row_1=label所在行,column_1=label所在列
#width_1=label的宽度,relief_1=label 的风格（可选参数'sunken','groove',
def common_label(window,name,text_1,row_1,column_1,width_1,relief_1):
    name = tk.Label(window,text=text_1,relief = relief_1,width = width_1,height=1)
    name.grid(row=row_1,column=column_1,sticky = 'W'+'N')   #sticky=西北
    

#通讯异常状态下所有数据全部置0
def set_analog_quantity_to_zero(frame_2,frame_3):
    object_cfg_tool = cfg_tool()
    for i in range(0,object_cfg_tool.Pick_Section_number('Analog1_Num')):
            if i == 6 or i == 16 or i == 20:
                common_label(frame_2,i,'',i+1,2,15,'groove')
            else:
                common_label(frame_2,i,0,i+1,2,15,'groove') 
        #Analog2_data中的数据置0        
    for i in range(0,object_cfg_tool.Pick_Section_number('Analog2_Num')):
            if i == 6 or i == 13:
                common_label(frame_3,i,'',i+1,2,15,'groove')
            else:
                common_label(frame_3,i,0,i+1,2,15,'groove')
                
#模拟量名称及数据加载到面板
def set_analog_quantity_to_label(common_label_dict):
    for i in range(len(common_label_dict)):
        label_key = list(common_label_dict.keys())[i]
        label_value = common_label_dict.get(label_key)
        common_label(label_value[0],label_key,label_value[1],label_value[2],2,15,'groove')
'''
-------------------------------------------------------------------------------
函数处理类函数定义
-------------------------------------------------------------------------------
'''
#################数值取反函数#########################
#data为十进制数字，bit为2进制位数。
def data_reverse(data,bit):
        str_to_bin = bin(((data)))           #10进制转2进制字符串
        clear_bin = str_to_bin.split('0b')[1]  #去掉2进制字符串前面的0b
        clear_bin_list = list(clear_bin)      #把字符串转换成数组
        
        if len(clear_bin_list)<bit:                #如果位数小于指定位数，前面补0
            for i in range(bit-len(clear_bin_list)):
                clear_bin_list.insert(i,'0')
        
        clear_bin_str = ''                          #定义取反后的二进制字符串
        for i in range(len(clear_bin_list)):         #取反
            if clear_bin_list[i] == '0':
                clear_bin_list[i] = '1'
            else:
                clear_bin_list[i] = '0'
            clear_bin_str+=clear_bin_list[i]
        return clear_bin_str

##############单个字符转十进制数值函数###############
#字符串A转换成对应数字10进制,即'A'→10    
def str_to_int_ten(data):

            for i in range(10):
                if data == str(i):
                    data = int(data)
                    return int(str(data),16)
            if data == 'A':
                return 10    
            elif data == 'B':
                return 11
            elif data == 'C':
                return 12
            elif data == 'D':
                return 13
            elif data == 'E':
                return 14
            elif data == 'F':
                return 15   
            
#################十六进制单精度float值转浮点数函数#############

def calc_float(data):     
        if len(data)%8 != 0 :
            print("info长度有错误,不是8的倍数")
            return 0
        elif len(data)%8 ==0:
            data = data[::-1]                 #--------
            data_new = ''
            for i in range(0,7,2):            #把串口显示值转换为float值
                data_new+=data[i+1]
                data_new+=data[i]              #--------
        data_new_list = []
        for i in range(8):                     #把float转换成10进制数字列表，把列表元素处理成2进制构成字符串
            data_new_list.append(str_to_int_ten(data_new[i]))
            data_new_list[i] = bin(data_new_list[i]).split("0b")[1]
            if len(data_new_list[i])<2:
                data_new_list[i] ='000'+data_new_list[i]
            elif len(data_new_list[i])<3:
                data_new_list[i] ='00'+data_new_list[i]
            elif len(data_new_list[i])<4:
                data_new_list[i] ='0'+data_new_list[i]
        data_new_str = ''.join(data_new_list)   #D31-D0，列表转字符串
        data_new_str_E = int(data_new_str[1:9],2)      #计算公式的E值
        data_new_str_M = int(data_new_str[9:32],2)     #计算公式的M值
        float_data = round(float((1+data_new_str_M*(pow(2,-23)))*pow(2,data_new_str_E-127)),2) #公式
        if data_new_list[0] =='1':
            float_data = 0-float_data
        return float_data     

###############校验和生成函数########################
#函数功能：获取chksum
#data_str_exclude_chksum：不包括~以及chksum的中间部分
def get_chksum(data_str_exclude_chksum):
    sum_chksum = 0   #存储所有字符的十进制和（除去CHKSUM）
    for i in range(0,len(data_str_exclude_chksum)):
        sum_chksum+=int(ord(data_str_exclude_chksum[i]))
    sum_chksum_bin = bin(sum_chksum)
    sum_chksum_bin=sum_chksum_bin.split('0b')[1]
    sum_chksum_bin = data_reverse(sum_chksum%65535,16)     #默认长度为16位
    sum_chksum_bin = int(sum_chksum_bin,2)
    sum_chksum=data_reverse(sum_chksum,4)

    return hex(sum_chksum_bin+1).lstrip('0x').upper()       #取反+1转16进制去掉'0x'换算成大写，返回校验和
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    