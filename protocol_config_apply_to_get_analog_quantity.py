# -*- coding: utf-8 -*-
"""
Created on Mon Apr  9 21:32:16 2018

@author: VicWang
"""
'''
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
'''
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
    protocol_info = func.data_split(protocol_str,'DATA_INFO')
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
                print("CID1:2AH正确")
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
       
    print("LENID的校验码计算值（取反未加1）:%s"%protocol_length2_3_re)
       
    #lchksum的计算
    protocol_lchksum = func.str_to_int_ten(protocol_lchksum)
    #print("protocol_lchksum减1:",protocol_lchksum-1)
    str_to_bin = bin(((protocol_lchksum-1)))           #10进制转2进制字符串
    protocol_lchksum_final = str_to_bin.split('0b')[1]                  #去掉0b
    if len(protocol_lchksum_final)<4:                     #不够4位前面加0
        for i in range(4-len(protocol_lchksum_final)):
            protocol_lchksum_final='0'+protocol_lchksum_final  
            
    print("lchksum的值-1：",protocol_lchksum_final)
    if protocol_lchksum_final == protocol_length2_3_re:    #比较lchksum的值与后三位计算出来的值是否相等
        print("LCHKSUM校验值正确")
    elif protocol_Drop_startbit[8]==protocol_Drop_startbit[9]==protocol_Drop_startbit[10]==protocol_Drop_startbit[11]=='0':
        print("LCHKSUM校验值正确，info为0")   #如果length为0000
    elif ((protocol_Drop_startbit[10]+protocol_Drop_startbit[11])=='6A' and protocol_Drop_startbit[8]=='0') :
        print("LCHKSUM校验值正确，LENID等于6A")    #6A时且lchksum = '0'时
    else:
        print("LCHKSUM校验值错误")
        return 0
    #验证LENID与info的长度是否匹配
    

    ############################拆出datainfo#############################
    '''
    以上内容为通用设置，以下内容根据DATAINFO的构成编写
    只含有DATAF的类型如下：
    '''

    #dataflag
    #protocol_dataflag = ord(protocol_dataflag)
    #print("protocol_dataflag",protocol_dataflag)

          
    #print("DATAINFO:",protocol_info)
    if protocol_info == None:
        pass
    elif len(protocol_info)%8 != 0:         #判断info长度
        print("DATAINFO长度有误")
        return 0
    elif len(protocol_info)%8 == 0:          #如果是8的倍数，则分割开始计算数值
        print("info长度",len(protocol_info))
        protocol_info_list = []
        for i in range(0,len(protocol_info),8):
            protocol_info_list.append(protocol_info[i:i+8])
        #print(protocol_info_list)
        protocol_dataf_list = []
        for i in range(0,len(protocol_info_list)):
            protocol_dataf_list.append(func.calc_float((protocol_info_list[i])))
            #print("第%d个数为："%(i+1),func.calc_float((protocol_info_list[i])))
    else:
        print("DATAINFO长度为None")


####################拆出chksum并验证######################
   
    get_chksum = func.get_chksum(protocol_Drop_startbit[0:len(protocol_Drop_startbit)-4])
    print("get_chksum",get_chksum)
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





