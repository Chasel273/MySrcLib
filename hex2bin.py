# -*- coding:utf-8 -*-
 
import os
import sys
from struct import *

#声明变量：
#低位地址
Low_addr  = 0
#保存长度用于比较
Last_Size = 0
#保存地址用于比较
Last_Addr = 0
#高位地址
High_Addr = 0
#扩展线性地址标志位
Expand_Flag  = 0



#hex to hex
def Hex_Hex(srchexfile,desthexfile,destlenth):
	#创建源Hex对象
	Fin = open(srchexfile)
	#创建或写入目标Hex文件,使用‘w’来提醒python用写入的方式打开
	Fout = open(desthexfile,'w')
	#playload缓存
	Data = ''
	#符号
	Sign = ':'
	#XOR
	XOR = 0x0000
	#文件的长度倍数
	Times = 0
	#第几次循环
	LoopTimes = 0
	#目标长度
	DestLen = int(destlenth,16)
	#剔除XOR
	RemoveXOR = 0
	#Hex文件解析
	for HexStr in Fin.readlines():
		#处理数据，去除空格\n\r\t
		HexStr = HexStr.strip()
		#读取源文件长度，存作Size变量
		Size = int(HexStr[1:3],16)
		#判断数据类型:00：数据记录
		if int(HexStr[7:9],16) == 0:
			if DestLen == Size :
				#不需要转换
				Fout.write(HexStr + '\n')
				continue
			#短转长：
			elif DestLen > Size :
				if DestLen/Size == 2:
					Times = 2
				elif DestLen/Size == 4:
					Times = 4
				else:
					Times = 1
				#读取playload
				for h in range(0, Size):
					Data += HexStr[(9+h*2):(9+h*2+2)]
				#第一条数据的地址作为合并后的地址
				if LoopTimes == 0:
					Addr = int(HexStr[3:7],16)
				LoopTimes += 1
				if LoopTimes >= Times:
					#从读取出来的playload中再求和
					for i in range(0,int(len(Data)/2)):
						XOR += int(Data[(i*2):(i*2+2 )],16)
					#playload合并后开始写入文件
					Fout.write(Sign)
					Fout.write('%02X' % int(len(Data)/2))
					DataHead = str('%04X' % Addr)
					DataHead += HexStr[7:9]
					Fout.write(DataHead)
					Fout.write(Data)
					#XOR
					XOR += int(len(Data)/2) + (Addr >>8) + (Addr & 0xff)
					XOR = (~(XOR % 0x100)+ 0x01) & 0xff
					Fout.write('%02X\n' % XOR)
					#Reset
					Data = ''
					XOR = 0x0000
					LoopTimes = 0
			#长转短：
			elif DestLen < Size :
				if Size/DestLen == 2:
					Times = 2
				elif Size/DestLen == 4:
					Times = 4
				elif DestLen - (Size % DestLen) == 1 :
					#剩余长度不足标志位
					RemoveXOR = 1
				#读取地址
				Addr = int(HexStr[3:7],16)
				#下一次循环开始地址补偿
				LenOffset = 0
				for i in range(0,Times):
					#读取playload
					for h in range(0, DestLen):
						Data += HexStr[(9+h*2+LenOffset):(9+h*2+2+LenOffset)]
					#跳出这次循环
					if Data == '':
						continue
					#剔除XOR
					if (RemoveXOR == 1 or len(Data)/2 < DestLen) and i != 0:
						Data = Data[0:-2]
						RemoveXOR = 0
					#从读取出来的playload中再求和
					for j in range(0,int(len(Data)/2)):
						XOR += int(Data[(j*2):(j*2+2)],16)
					#playload合并后开始写入文件
					Fout.write(Sign)
					Fout.write('%02X' % int(len(Data)/2))
					DataHead = str('%04X' % Addr)
					DataHead += HexStr[7:9]
					Fout.write(DataHead)
					Fout.write(Data)
					XOR += int(len(Data)/2) + (Addr >>8) + (Addr & 0xff)
					XOR = (~(XOR % 0x100)+ 0x01) & 0xff
					Fout.write('%02X\n' % XOR)
					#数据递增
					Addr += DestLen
					LenOffset += DestLen*2
					#Reset
					XOR = 0x0000
					Data = ''
		#判断数据类型:01：文件结束记录
		elif int(HexStr[7:9],16) == 1:
			#不需要转换
			Fout.write(HexStr + '\n')
		#判断数据类型:02：扩展段地址记录
		elif int(HexStr[7:9],16) == 2:
			#不需要转换
			Fout.write(HexStr + '\n')
		#判断数据类型:03：开始段地址记录
		elif int(HexStr[7:9],16) == 3:
			#不需要转换
			Fout.write(HexStr + '\n')
		#判断数据类型:04:扩展线性地址记录
		elif int(HexStr[7:9],16) == 4:
			#不需要转换
			Fout.write(HexStr + '\n')
		#判断数据类型:05:开始线性地址记录
		elif int(HexStr[7:9],16) == 5:
			#不需要转换
			Fout.write(HexStr + '\n')
	#done
	Fin.close()
	Fout.close()


#hex to bin
def hex_bin(hexfile,binfile):
	#创建源Hex对象
	Fin = open(hexfile)
	#创建或写入目标Hex文件,使用‘w’来提醒python用写入的方式打开
	Fout = open(binfile,'wb')

	#Hex文件解析
	for HexStr in Fin.readlines():
		#处理数据，去除空格\n\r\t
		HexStr = HexStr.strip()
		#读取源文件长度，存作Size变量
		Size = int(HexStr[1:3],16)
		#判断数据类型:00：数据记录
		if int(HexStr[7:9],16) == 0:
			#处理数据
			for h in range(0, Size):
				#将playload切片成一个个字节，打包成byte
				Result = int(HexStr[(9+h*2):(9+h*2+2)],16)
				#写入文件
				Fout.write(pack('B',Result))
		#判断数据类型:01：文件结束记录
		elif int(HexStr[7:9],16) == 1:
			#直接剔除
			continue
		#判断数据类型:02：扩展段地址记录
		elif int(HexStr[7:9],16) == 2:
			#直接剔除
			continue
		#判断数据类型:03：开始段地址记录
		elif int(HexStr[7:9],16) == 3:
			#直接剔除
			continue
		#判断数据类型:04:扩展线性地址记录
		elif int(HexStr[7:9],16) == 4:
			#直接剔除
			continue
		#判断数据类型:05:开始线性地址记录
		elif int(HexStr[7:9],16) == 5:
			#直接剔除
			continue
				
	Fin.close()
	Fout.close()

# bin to hex
def bin_hex(binfile,hexfile,hexlenth,startaddr):
	Fbin = open(binfile,'rb')
	Fhex = open(hexfile,'w')
	Addr = int(startaddr,16)

	#扩展线性地址
	Expand_Addr = 0x0000
	while 1:
		#read data based on lenth
		Bindata = Fbin.read(int(hexlenth,16))
		#done
		if len(Bindata) == 0:
			break
		#扩展线性段地址
		if Addr > 0xFFFF:
			Fhex.write(':02000004')
			Expand_Addr += 1
			Expand_XOR = 0x02 + 0x04 + (Expand_Addr >> 8) + (Expand_Addr & 0xff)
			Expand_XOR = (~(Expand_XOR % 0x100) + 0x01) & 0xff
			Fhex.write(str('%04X' % Expand_Addr))
			Fhex.write(str('%02X' % Expand_XOR) + '\n')
			Addr = 0x0000
		#XOR
		XOR = len(Bindata) + (Addr >>8) + (Addr & 0xff)
		#创建模板，依次写入00类型数据记录
		DataHead = ':'
		DataHead += str('%02X' % len(Bindata))
		DataHead += str('%04X' % Addr)
		DataHead += '00'
		Fhex.write(DataHead)
		Addr += int(hexlenth,16)

		for i in range(0,len(Bindata)):
			Fhex.write('%02X' % Bindata[i])
			XOR += Bindata[i]
		#XOR
		XOR = (~(XOR % 0x100)+ 0x01) & 0xff
		Fhex.write('%02X\n' % XOR)
		if len(Bindata) < int(hexlenth,16):
			break
	#开始线性地址
	#if Expand_Addr != 0x0000:
		#Fhex.write(':04000005')
		
		#StartXOR = 0x04 + 0x05 
		#StartXOR = (~(StartXOR % 0x100) + 0x01) & 0xff
		#Fhex.write(str('%02X' % StartXOR) + '\n')
	#done
	Fhex.write(':00000001FF')
	Fbin.close()
	Fhex.close()

	
#命令行交互
def usage():
	print ('Hex to Bin:')
	print (' python hex2bin.py -b [Hexfile.hex] [Binfile.bin]')
	print ('Bin to Hex:')
	print (' python hex2bin.py -h [Binfile.bin] [Hexfile.hex] [Hexfile lenth] [Start addr]')
	print ('Hex to Hex for other lenth:')
	print (' python hex2bin.py -c [SrcHex.hex]  [DestHex.hex] [DestHex lenth]')
	exit(0)
if len(sys.argv) < 4 or len(sys.argv) > 6:
	usage()
elif sys.argv[1] == '-b' and len(sys.argv) == 4:
	hex_bin(sys.argv[2],sys.argv[3])
elif sys.argv[1] == '-h' and len(sys.argv) == 6:
	bin_hex(sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5])
elif sys.argv[1] == '-c' and len(sys.argv) == 5:
	Hex_Hex(sys.argv[2],sys.argv[3],sys.argv[4])
else:
	usage()
