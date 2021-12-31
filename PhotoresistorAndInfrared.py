import vlc
import time
import smbus
import GUI2
import serial #通信

#通信的初始化
uart2 = serial.Serial(port = "/dev/ttyAMA1", baudrate = 115200)
uart2.flushInput()

bus = smbus.SMBus(1) ## 开启总线
address = 0x48 ## address  ---> 器件的地址(硬件地址 由器件决定)
A0 = 0x40      ##  A0    ----> 器件某个端口的地址（数据存储的寄存器）
A1 = 0x41
A2 = 0x42
A3 = 0x43


check = 0
#光敏电阻:0=没有检测到瓶子 1:有瓶子有标签 2:有瓶子没有标签
#红外对射:3:有东西经过

#0为程序停止，1为程序开始
sta = 0
Nun = 0


def readOnce():
    while True:
        count = uart2.inWaiting()
        if count != 0:
            recv = uart2.read(count) 
            print("Recv some data is : ")
            print(recv)
            uart2.flushInput()
            break

def loop1():#光敏电阻的循环
    global check
    global sta
    global Num
    part = 0#现输入值所在范围
    Time = 0#重复次数
    T=7#目标次数
    starttime = time.time()
    while True:
        bus.write_byte(address,A0)  ## 告诉树莓派 你想获取那个器件的那个端口的数据
        value0 =bus.read_byte(address) ## 获得数据
        print(value0)
        print(sta)

        time.sleep(0.5)
        if(value0 <= 100 and sta == 1):#没有瓶子
#             print("in")
            check = 0
            Time=0
            part=0
            if(time.time()-starttime >= 40):
                break
        elif(value0 <= 100 and sta == 0):
#             print("in")
            if(part == 0):
                Time = Time + 1
            else:
                Time=1
                part=0
            if(Time == T-2):
                check = 0
                Time=0
                part=0
                print(check)
                break
        
        elif(value0 > 125):#有瓶子有标签
            if(part == 1):
                Time = Time + 1
            else:
                Time=1
                part=1
            if(Time == T):
                check = 1
                Time=0
                part=0
                print(check)
                break

        elif(value0>100 and value0 <= 125):#有瓶子没标签
            if(part == 2):
                Time = Time + 1
            else:
                Time=1
                part=2
            if(Time == T):
                check = 2
                Time=0
                part=0
#            print("有瓶子没有标签")
                break
#        print(value1)
#0：没有检测到瓶子（<=90)
#1：有瓶子有标签(=>160)
#2：有瓶子没有标签(100<X<=110)


def loop2():#红外线的循环
    global check
    global sta
    global Num

    bus.write_byte(address,A1)  ## 告诉树莓派 你想获取那个器件的那个端口的数据
    X =bus.read_byte(address) ## 获得数据
    bus.write_byte(address,A2)
    Y =bus.read_byte(address)
    bus.write_byte(address,A3)
    Z =bus.read_byte(address)
    
    starttime = time.time()
    

    time1 = 0
    time2 = 0
    time3 = 0
    Time = 80
    
    while True:
        if(time.time()-starttime >= 10):#一段时间检测不到东西
            check  = 4
            break
            
        bus.write_byte(address,A1)
        print(bus.read_byte(address))
        if(X == bus.read_byte(address)):#和第一次的X为同一个数值就time++
            time1 = time1 + 1
        elif(X != bus.read_byte(address)):#当X和当时读进来的值不同就重新开始循环
            time1 = 0
            X = bus.read_byte(address)
###########
        bus.write_byte(address,A2)
        if(Y == bus.read_byte(address)):
            time2 = time2 + 1
        elif(Y != bus.read_byte(address)):
            time2 = 0
            Y = bus.read_byte(address)
############
        bus.write_byte(address,A3)
        if(Z == bus.read_byte(address)):
            time3 = time3 + 1
        elif(Z != bus.read_byte(address)):
            time3 = 0
            Z = bus.read_byte(address)
############      
        if(time1 == Time|time2 == Time|time3 == Time):#同一个数值有十次就break
            time1 = 0
            time2 = 0
            time3 = 0
            check=3
            break
    print("red out")
    
#瓶子是否掉落,如果循环跳出，说明瓶子掉落
def loop3():
    Time = 0
    T = 5
    while True:
        time.sleep(1)
        bus.write_byte(address,A0)
        value = bus.read_byte(address)
        print(value)
        if(value <= 105):#没有瓶子
            Time= Time + 1
        else:
            Time = 0
        if(Time == 5):
            break

def loop():
    global check
    global sta
    global Num
    Num = 0
    ####
    uart2.write("#W1000".encode("utf-8"))#点击开始，发送信息
    readOnce()
    time.sleep(1.5)
    while True:
        uart2.write("#F1001".encode("utf-8"))#开始接收瓶子
        readOnce()
        #光敏电阻阶段
        loop1()
        #check=0一定时间无瓶子递入 check=1瓶子有标签 check=2瓶子无标签
        
        if(check == 0 & Num == 0):#回到UI开始界面,全部参数初始化,发送一个信息
            uart2.write("#F0000".encode("utf-8"))
            readOnce()
            destroy()
            GUI2.a = 0
            break
            ######!
        elif(check == 0 & Num != 0):#结束界面,重置所有参数,发送一个信息
            uart2.write("#F0000".encode("utf-8"))
            readOnce()
            destroy()
            GUI2.a = 0
            break
            #####!
        elif(check == 1):#有瓶子有标签, 切割步骤，发送信息
            uart2.write("#F1002".encode("utf-8"))
            readOnce()
            Num= Num + 1
            #########
            #红外线阶段
            time.sleep(4)
            while True:
                loop6()
                if(check == 3):#有东西经过，把瓶子送走
                    uart2.write("#F1004".encode("utf-8"))
                    readOnce()
                    break
                elif(check == 4):
                    break
#                 elif(check == 4):#没东西经过
#                     loop1()
#                     if (check == 2):#标签已脱落，但没有掉落——发送消息,瓶子送走
#                         uart2.write("#F1004".encode("utf-8"))
#                         readOnce()
#                         check = 0
#                         break
#                    elif(check == 1):#回到红外检测循环
                        
        elif(check == 2):#有瓶子无标签, 瓶子送走
            uart2.write("#F1004".encode("utf-8"))
            readOnce()
            Num= Num+1
            print(check)
        if(check == 4):
            GUI2.a=0
            destroy()
            break
        #瓶子是否掉落,如果循环跳出，说明瓶子掉落
        loop3()
        print(Num)
        uart2.write("#F0000".encode("utf-8"))
        readOnce()
        if(sta == 0 ):
            uart2.write("#E9999".encode("utf-8"))
            readOnce()
            destroy()
            break

def loop4():
    while True:
        bus.write_byte(address,A3)
        Z =bus.read_byte(address)
        print(Z)

def loop5():
    global check
    Time = 0
    T = 5
    starttime = time.time()
    while True:
        if(time.time()-starttime >= 20):#一段时间检测不到东西
            check  = 4
            #break
        bus.write_byte(address,A1)
        value = bus.read_byte(address)
        print(value)
        if(value>=70):
            Time = Time + 1
        if(Time >= T ):
            check = 3
            #break
            print("red out")
            
def loop6():
    global check
    Time = 0
    T = 10
    bus.write_byte(address,A0)
    while True:
        time.sleep(0.5)
        value = bus.read_byte(address)
        print(value)
        if(value>100 and value <= 125):
            Time= Time+1
        if(Time>=T):
            check = 3
            break
            print("red out")
        if(GUI2.a == 0):
            check = 4
            break
        
    
def destroy():
    global check
    global sta
    global Num
    
    check = 0
    Num = 0
    sta=0