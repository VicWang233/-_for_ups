# -*- coding: utf-8 -*-
"""
Created on Thu Apr 19 21:09:58 2018

@author: VicWang


s.strip()     #开头和结尾
s.lstrip()   #开头
s.rstrip()  #结尾

#import binascii
#------------------------------------------------------
#各种转换
a = 0x0A  #表示16进制数
b = 10    #表示10进制数
print(hex(b)) #10转16                输出0xa
print(a)  #输出10进制数             输出10
print((b'a')) #转换为bytes供串口传输   输出b'a'
print(chr(49))   #10进制整形转换成对应ASCII字符 输出1
print(chr(0x31))  #16进制整形转换成对应ASCII字符 输出1
print(hex(ord('1')))    #ASCII转16进制，输出0x31
print((ord('1')))     #ASCII转10进制，输出49
print(int('1010',2))   #2进制转10进制
print(bin(10))        #十进制转2进制
#-------------------------------------------------------

"""
import tkinter as tk
#import configparser
from tkinter import simpledialog
import serial.tools.list_ports as list_ports
import serial
import time
from configparser import ConfigParser   #取configparser模块中的ConfigParser类
#import protocol_config_apply_to_get_switching_value as protocol_switch
#import threading
import ctypes

'''
-------------------------------------------------------------------------------
cfg文件调用类函数定义
-------------------------------------------------------------------------------
'''
###########指定section和option的序号调出参数名###########
#section_you_choose=你选择的section，option_i_you_choose=你选择的section下的列表序号。
#返回选定option的参数值

#用于处理CFG文件的类
class cfg_tool(ConfigParser):           #继承父类
    def __init__(self):                 #初始化，定义需要搞的cfg文件名，
        self.conf = ConfigParser(allow_no_value=True,strict = False)    #定义加载cfg文件的对象
        self.conf.read('ToolsDebugChs.cfg')                          #读cfg文件
        self.sections = self.conf.sections()
      
    def Pick_Section_number(self,section_num_you_choose):
        #section = self.conf.keys
        for i in range(len(self.sections)):                          #循环找出对应的section
            if self.sections[i] == section_num_you_choose:
                return int(self.conf.options(self.sections[i])[0])
        
    '''
    section_you_choose:你选择的section，格式为字符串
    option_i_you_choose:你选择的option行，格式为int
    
    '''
    def Pick_Option_In_Section(self,section_you_choose,option_row_you_choose,option_list_i,*args):
                options = self.conf.items(section_you_choose)
                option = list(options[option_row_you_choose])[0].split('\t')[option_list_i]
                if option == 'a':
                                return ''
                else:
                    if type(args) == type('1'):
                        option = args
                        print(option)
                    else:
                        return option
            
            
            
#######修改[Config_for_Sysdata]下的两个值，一个是修改值的float值，一个是命令#######
    def Change_Value_In_CFG(self,section_you_choose,option1_you_choose,option2_you_choose,new_option_value1,new_option_value2):
        self.openfile = open('ToolsDebugChs.cfg','w')
        self.conf.set(section_you_choose,option1_you_choose,new_option_value1)
        self.conf.set(section_you_choose,option2_you_choose,new_option_value2)
        self.conf.write(self.openfile)
        self.openfile.close()
        print("%s的值%s改为%s"%(section_you_choose,option1_you_choose,new_option_value1))
        #return self.conf.get(section_you_choose,option_row_you_choose)
        #####专门获取系统[Config_for_Sysdata]中的传入值，付给return_value,再把Config_for_Sysdata中的值清空####
    def get_value_IN_CFG(self,section_you_choose,option1_you_choose,option2_you_choose):
        self.return_list = []
        self.return_list.append(self.conf.get(section_you_choose,option1_you_choose))
        self.return_list.append(self.conf.get(section_you_choose,option2_you_choose))
        #self.Change_Value_In_CFG(section_you_choose,option1_you_choose,option2_you_choose,'1','1')
        return self.return_list
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
                if i == 13 and (protocol_option == 'DATAFLAG' or  protocol_option == 'DATA_NUM_for_Sysdata'):
                    return protocol_dataflag
            elif 14<=i<=len(protocol_Drop_startbit)-4-1 and (protocol_option == 'DATA_INFO_for_switch' or protocol_option == 'DATA_INFO_for_Sysdata'):
                protocol_info+=protocol_Drop_startbit[i]
                if i == len(protocol_Drop_startbit)-4-1:
                    return protocol_info
            elif 14<=i<=15 and protocol_option == 'DATA_NUM':           #12和13位为datainfo前两位表示datainfo数据的长度
                protocol_data_number+=protocol_Drop_startbit[i]    #
                if i == 15:
                    return protocol_data_number
            elif 16<=i<=len(protocol_Drop_startbit)-4-1 and protocol_option == 'DATA_INFO':   #
                protocol_info+=protocol_Drop_startbit[i]
                if i == len(protocol_Drop_startbit)-4-1:
                    return protocol_info
            elif  len(protocol_Drop_startbit)-4<=i<=len(protocol_Drop_startbit)-1 and protocol_option == 'CHKSUM':
                protocol_chksum+=protocol_Drop_startbit[i]
                if i == len(protocol_Drop_startbit)-1:
                    return protocol_chksum
        elif protocol_option == 'CID2_DICT':
            return protocol_CID2_dict


#数据验证函数，验证CID1和lchksum以及chksum是否正确，全部正确返回1，否则返回0
#command：命令
def data_verify(command):
    protocol_Drop_startbit = command.split("~")[1]
    protocol_CID1 = data_split(command,'CID1')   #CID1
    protocol_lchksum = data_split(command,'LCHKSUM')   #LENGTH的lchksum
    protocol_chksum = data_split(command,'CHKSUM')
    ####################2A验证##########################
    if protocol_CID1 == '2A':
                pass
    else:
                print("CID1:2AH错误",protocol_CID1)
                return 0
    protocol_length1 = protocol_Drop_startbit[9]
    protocol_length2 = protocol_Drop_startbit[10]
    protocol_length3 = protocol_Drop_startbit[11]


    #-------------------------------------------------
    protocol_length1=str_to_int_ten(protocol_length1) 
    protocol_length2=str_to_int_ten(protocol_length2)  #字符A转换成对应16进制A再转成10进制的值2
    protocol_length3=str_to_int_ten(protocol_length3)
    protocol_length2_3_re =data_reverse((protocol_length1+protocol_length2+protocol_length3)%16,4)  #求和后摸16取余不加1
       
       
    ############lchksum验证###############
    protocol_lchksum = str_to_int_ten(protocol_lchksum)
    #print("protocol_lchksum减1:",protocol_lchksum-1)
    str_to_bin = bin(((protocol_lchksum-1)))           #10进制转2进制字符串
    protocol_lchksum_final = str_to_bin.split('0b')[1]                  #去掉0b
    if len(protocol_lchksum_final)<4:                     #不够4位前面加0
        for i in range(4-len(protocol_lchksum_final)):
            protocol_lchksum_final='0'+protocol_lchksum_final  
            
    #print("protocol_lchksum_final：",protocol_lchksum_final)
    #print('protocol_length2_3_re',protocol_length2_3_re)
    if protocol_lchksum_final == protocol_length2_3_re:    #比较lchksum的值与后三位计算出来的值是否相等
        #print("LCHKSUM校验值正确")
        pass
    elif protocol_Drop_startbit[8]==protocol_Drop_startbit[9]==protocol_Drop_startbit[10]==protocol_Drop_startbit[11]=='0':
        #print("LCHKSUM校验值正确，info为0")   #如果length为0000
        pass
    elif ((protocol_Drop_startbit[10]+protocol_Drop_startbit[11])=='6A' and protocol_Drop_startbit[8]=='0') :
        #print("LCHKSUM校验值正确，LENID等于6A")    #6A时且lchksum = '0'时
        pass
    else:
        print("LCHKSUM校验值错误")
        return 0
    ############chksum验证###############
    get_chksum_1 = get_chksum(protocol_Drop_startbit[0:len(protocol_Drop_startbit)-4])
    #print("get_chksum",get_chksum_1)
    #print("protocol_chksum",protocol_chksum)
    #最终判断计算值与协议校验值-1是否相等
    if get_chksum_1 == protocol_chksum:
        #print("CHKSUM校验码正确")
        pass
    else:
        print("CHKSUM校验码错误")
        return 0

    return 1               
        
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
object_cfg_tool = cfg_tool()
#################通用label函数#########################
#window=label所在框架，name=label名称，text_1=label显示的文本,row_1=label所在行,column_1=label所在列
#width_1=label的宽度,relief_1=label 的风格（可选参数'sunken','groove',
def common_label(window,text_1,row_1,column_1,width_1,relief_1):
    tk.Label(window,text=text_1,relief = relief_1,width = width_1,height=1,anchor = 'w').grid(row=row_1,column=column_1,sticky = 'W'+'N')
#暂时用不上    
def common_label_for_textvariable(window,text_1,row_1,column_1,width_1,relief_1):
    tk.Label(window,textvariable=text_1,relief = relief_1,width = width_1,height=1,anchor = 'w').grid(row=row_1,column=column_1,sticky = 'W'+'N')
#dialogname表示修改值弹窗的名称，i表示cfg文件当中的行。
def common_label_for_modify(window,text_1,row_1,column_1,width_1,relief_1,dialogname,i):
    def print_float(self):
       res = simpledialog.askfloat(dialogname,"修改值")
       res = float_2_hex_2_com(res)
       object_cfg_tool.Change_Value_In_CFG('Config_for_Sysdata','SYSData_List','temporary_variable',res,object_cfg_tool.Pick_Option_In_Section('SYSData_List',i,0))
       #print(object_cfg_tool.get_value_IN_CFG('Config_for_Sysdata','temporary_variable'))
       #return res

    name = tk.Label(window,text=text_1,relief = relief_1,width = width_1,height=1,anchor = 'w')
    name.bind('<Double-Button-1>',print_float)
    name.grid(row=row_1,column=column_1,sticky = 'W'+'N')
    
def close_window(root):
    ans = tk.messagebox.askokcancel(title = '退出',message = '是否退出')
    if ans:
        root.destory()
    else:
        return
#################通用设置BUTTON函数#########################    

    
#通讯异常状态下所有数据全部置0
def set_analog_quantity_to_zero(frame_2,frame_3):
    
    for i in range(0,object_cfg_tool.Pick_Section_number('Analog1_Num')):
            if i == 6 or i == 16 or i == 20:
                common_label(frame_2,'',i+1,2,10,'groove')
            else:
                common_label(frame_2,0,i+1,2,10,'groove') 
        #Analog2_data中的数据置0        
    for i in range(0,object_cfg_tool.Pick_Section_number('Analog2_Num')):
            if i == 6 or i == 13:
                common_label(frame_3,'',i+1,2,10,'groove')
            else:
                common_label(frame_3,0,i+1,2,10,'groove')
                
#模拟量名称及数据加载到面板
def set_analog_quantity_to_label(common_label_dict):
    for i in range(len(common_label_dict)):
        label_key = list(common_label_dict.keys())[i]
        label_value = common_label_dict.get(label_key)
        common_label(label_value[0],label_value[1],label_value[2],2,10,'groove')
#创建下拉菜单列表
#frame:所在框   name:菜单名   menulist = 下拉菜单列表  commandlist = 下拉菜单对应的命令列表
def set_the_menu(frame,label_name,weight_name,menulist,commandlist):
    #menu_main_button = tk.Menu(frame)
    weight_name = tk.Menu(frame,tearoff = 0)
    frame.add_cascade(label = label_name,menu = weight_name)
    for i in range(len(menulist)):
        weight_name.add_command(label = menulist[i],command = commandlist[i])
    #frame.config(menu =menu_main_button)
#预留，用于后续控制扩展

def Setting_the_Value():
   def print_float(parent_1):
       res = simpledialog.askfloat("需要修改的数据名","修改值",parent = parent_1)
       #parent.wait_window()
       print("ressssssssssssssssss:",res)
   filewin = tk.Toplevel()
   button = tk.Button(filewin, text="Do nothing button",relief = 'groove',command = lambda: print_float(filewin))
   button.pack()

def donothing():

   filewin = tk.Toplevel()
   button = tk.Button(filewin, text="Do nothing button",relief = 'groove')
   button.pack()



'''
-------------------------------------------------------------------------------
函数处理类函数定义
-------------------------------------------------------------------------------
'''
##################单精度float值转16进制计算函数######################
#例：输入2，输出00000040(hex:40000000)
def float_2_hex_2_com(s):
    fp = ctypes.pointer(ctypes.c_float(s))
    cp = ctypes.cast(fp,ctypes.POINTER(ctypes.c_longlong))
    hex_value = str(hex(cp.contents.value)).lstrip('0x')
    hex_value = hex_value[::-1]                 #--------
    hex_new_value = ''
    for i in range(0,7,2):            #把串口显示值转换为float值
        hex_new_value+=hex_value[i+1]
        hex_new_value+=hex_value[i]
    return hex_new_value
#################数值取反函数#########################
#data为十进制数字，bit为2进制位数。
def data_reverse(data,bit):                                     #
        clear_bin_list = list(bin(data).split('0b')[1])      #10进制转2进制字符串,把字符串转换成数组
        
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
    sum_chksum_bin = data_reverse(sum_chksum%65535,16)     #默认长度为16位
    sum_chksum_bin = int(sum_chksum_bin,2)
    return hex(sum_chksum_bin+1).lstrip('0x').upper()       #取反+1转16进制去掉'0x'换算成大写，返回校验和

'''
def set_the_value_from_simpledialog_to_outside(send_value,receive_value):
    receive_value = send_value
'''    
'''
-------------------------------------------------------------------------------
线程类函数定义
-------------------------------------------------------------------------------
''' 
    
   

    
    
    
    
    
    
    
    
    
    
    
    
    
    