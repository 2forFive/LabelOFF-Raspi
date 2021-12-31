# uart_template_control
import serial
import time
import jm

uart2 = serial.Serial("/dev/ttyAMA0", 115200)
uart2.flushInput()
# 
# # initial txmsg, check ok
# uart2.write("11111111".encode("utf-8"))

def readOnce():
    while True:
        count = uart2.inWaiting()
        if count != 0:
            recv = uart2.read(count) 
            print("Recv some data is : ")
            print(recv)
            uart2.flushInput()
            break

# if __name__ == '__main__':
#     try:
#         readOnce()
#         a = 0
#         while True:
#             temp = input()
#             if temp:
#                 a = temp
#                 uart2.write(a.encode("utf-8"))
#                 readOnce()
#             
#     except KeyboardInterrupt:
#         print("stop")
# 
#     GPIO.cleanup()
