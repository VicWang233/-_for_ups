# -*- coding: utf-8 -*-
"""
Created on Wed May  2 20:13:51 2018

@author: Administrator
"""

import func_def as func


def analysis_protocol(protocol_str):
    '''
    -------------------------------
    筛选数据部分
    -------------------------------
    '''
    #拆出起始位~
    protocol_Drop_startbit = protocol_str.split("~")[1]
    protocol_ver = func.data_split(protocol_str,'VER')   #版本
    protocol_adr = func.data_split(protocol_str,'ADR')    #设备号
    protocol_CID1 = func.data_split(protocol_str,'CID1')   #CID1
    protocol_CID2 = func.data_split(protocol_str,'CID2')   #CID2
    protocol_lchksum = func.data_split(protocol_str,'LCHKSUM')   #LENGTH的lchksum
    protocol_length = func.data_split(protocol_str,'LENGTH')    #LENGTH的LENID
    protocol_chksum = func.data_split(protocol_str,'CHKSUM')    #CHKSUM
    protocol_info = func.data_split(protocol_str,'DATA_INFO_for_switch')
    protocol_dataflag = func.data_split(protocol_str,'DATAFLAG')
    protocol_data_number = func.data_split(protocol_str,'DATA_NUM')
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

    protocol_switching_value_word1_dict = {                     #开关量状态字典
            '15':['','','','','','','','','','','','','','',''],
            '14':['断开状态','闭合状态'],
            '13':['断开状态(无效)','闭合状态(无效)'],
            '12':['断开状态','闭合状态'],
            '11':['断开状态(无效)','闭合状态(无效)'],
            '10':['发电机未接入(无效)','发电机接入(无效)'],
            '9':['主路逆变供电','电池逆变供电','联合逆变供电','整流电池均不供电'],
            '7':['关机','开机'],
            '6':['非充电状态','浮充','均充'],
            '4':['没有自检','自检中'],
            '3':['\\','\\','\\','\\'],
            '1':['均不供电','逆变供电','旁路供电'],
                                    }
 
    protocol_switching_value_word2_dict = {
            '8':['\\'],
            '7':['非ECO模式','ECO模式'],
            '6':['非智能并机模式(无效)','智能并机模式(无效)'],
            '5':['未接入(无效)','接入(无效)'],
            '4':['正常模式','维修模式','步进模式','自老化模式','隔离模式'],
            '1':['主路逆变供电(无效)','电池逆变供电(无效)','旁路供电(无效)','均不供电(无效)'],
                                            }
    
    '''
    -------------------------------
    处理数据部分
    -------------------------------
    '''
    #输出设备版本        
    #print("设备版本为：%s"%protocol_ver)
    #输出设备号
    #print("设备号：%s"%protocol_adr)
    #验证CID1是否等于2A
    if protocol_CID1 == '2A':
                #print("CID1:2AH正确")
                pass
    else:
                print("CID1:2AH错误",protocol_CID1)
                return 0
    #验证CID2对应的状态
    #CID2 = protocol_CID2_dict.get(protocol_CID2,'CID2传值错误')
    #print("CID2:",CID2)    
    #拆出length并验证  #字符，需要转十进制后加减在转2进制取反加1
    protocol_length2 = protocol_Drop_startbit[10]
    protocol_length3 = protocol_Drop_startbit[11]


    #-------------------------------------------------
    protocol_length2=func.str_to_int_ten(protocol_length2)  #字符A转换成对应16进制A再转成10进制的值2
    protocol_length3=func.str_to_int_ten(protocol_length3)
    protocol_length2_3_re =func.data_reverse((protocol_length2+protocol_length3)%16,4)  #求和后摸16取余不加1
       
    #print("LENID的校验码计算值（取反未加1）:%s"%protocol_length2_3_re)
       
    #lchksum的计算
    protocol_lchksum = func.str_to_int_ten(protocol_lchksum)
    #print("protocol_lchksum减1:",protocol_lchksum-1)
    str_to_bin = bin(((protocol_lchksum-1)))           #10进制转2进制字符串
    protocol_lchksum_final = str_to_bin.split('0b')[1]                  #去掉0b
    if len(protocol_lchksum_final)<4:                     #不够4位前面加0
        for i in range(4-len(protocol_lchksum_final)):
            protocol_lchksum_final='0'+protocol_lchksum_final  
            
    #print("lchksum的值-1：",protocol_lchksum_final)
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
    #验证LENID与info的长度是否匹配
#-----------------------------

    protocol_dataf_list = []
    if protocol_info == None:
        pass
    elif len(protocol_info) != 8:         #判断info长度
        print("DATAINFO长度有误")
        return 0
    else:
        word1 = protocol_info[:4]
        #print('word1',word1)
        word2 = protocol_info[4:]
        word1_to_bin  = bin(int(word1,16)).lstrip('0b')    #2进制word1
        word2_to_bin  = bin(int(word2,16)).lstrip('0b')    #2进制word2
        if len(word1_to_bin)<16:                     #不够16位前面加0
            for i in range(16-len(word1_to_bin)):
                word1_to_bin='0'+word1_to_bin
        if len(word2_to_bin)<16:                     #不够16位前面加0
            for i in range(16-len(word2_to_bin)):
                word2_to_bin='0'+word2_to_bin
        #word1_to_bin = word1_to_bin[::-1]            #搞反了，反转
        #word2_to_bin = word2_to_bin[::-1]  
        #print('word1_to_bin',word1_to_bin)
        #print('word2_to_bin',word2_to_bin)
        word1_list = []
        word2_list = []
        for i in range(len(word1_to_bin)):               #把datainfo分割成数组，方便与前面的字典组合来选择数据
            if i == 7 or i == 10 or i == 13 or i == 15:
                word1_list.append(word1_to_bin[i-1:i+1])
            elif i==6 or i == 9 or i == 12 or i ==14:
                continue
            else:
                word1_list.append(word1_to_bin[i])        
        for i in range(len(word2_to_bin)):                        
            if i == 11 or i == 12 or i == 14 or 1<=i<=7:   #此处应要反向遍历。详细见文档标记
                continue
            elif i == 15 or i == 13:
                word2_list.append(word2_to_bin[i-1:i+1])
            elif i == 0:
                word2_list.append(str(0))   #写死
            else:
                word2_list.append(word2_to_bin[i])
                
        #print(word1_list)
        #print(word2_list)
       
        for i in range(len(protocol_switching_value_word2_dict)):        #通过字典把word作为key，开关量的状态作为value进行配对。
            dict_key = list(protocol_switching_value_word2_dict.keys())[i]
            dict_value = protocol_switching_value_word2_dict.get(dict_key)
            index_for_value = int(word2_list[i],2)
            protocol_dataf_list.append(dict_value[index_for_value])
        for i in range(len(protocol_switching_value_word1_dict)):
            dict_key = list(protocol_switching_value_word1_dict.keys())[i]
            dict_value = protocol_switching_value_word1_dict.get(dict_key)
            index_for_value = int(word1_list[i],2)
            protocol_dataf_list.append(dict_value[index_for_value])
        
        protocol_dataf_list = protocol_dataf_list[::-1]

        #print(protocol_dataf_list)




#
    get_chksum = func.get_chksum(protocol_Drop_startbit[0:len(protocol_Drop_startbit)-4])
    #print("get_chksum",get_chksum)
    #最终判断计算值与协议校验值-1是否相等
    if get_chksum == protocol_chksum:
        print("CHKSUM校验码正确")
    else:
        print("CHKSUM校验码错误")  

    try:
        return protocol_dataf_list
    except:
        pass
    
    #拆出结束位OR（回车）
    
    
#pro = input("请输入指令：")

#pro_1 = pro  #使用encode来模拟串口传来的bytes数据

#analysis_protocol(pro_1)
   
    
    
    
    
    
    
    
    
    
    
    