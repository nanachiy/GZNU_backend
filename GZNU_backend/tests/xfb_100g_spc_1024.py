#! /usr/bin/python
# coding: utf-8
# Copyright (c) 2025 陈中旭
# License MIT
# Date: 2025.05.03
# Author: nanachiy(393744534@qq.com)
# Receive spectrums from FPGA block and plot, about 500MiB.

import socket,pylab,matplotlib,math,array,numpy
matplotlib.use('tkagg')
import struct
import time,datetime
import numpy as np


bw=1024
name=['AA','BB','CR','CI']

fftnum=1024
fftnum1=1024

def get_data():
    for k in range(10000):
        data, addr = sock.recvfrom(8256)

    return data


def plot_spectrum():
	

    matplotlib.pyplot.clf()
    beth = get_data()
    a = struct.unpack('>8256B', beth)  
    # print(len(beth))
    # print(a[0:12])
    count=struct.unpack('>2I',beth[0:8])
    print(count[1])
    matplotlib.pyplot.subplot(111)

    data_un=struct.unpack('8256B',beth)
    data_unb=struct.unpack('8256b',beth)
   
    num_acc= data_un[4]*0x1000000+data_un[5]*0x10000+data_un[6]*0x100+data_un[7]# big end 
    print('100gbe_get_acc_count %i\r\n'%num_acc),

    ffta=[]
    fftb=[]
    fftabr=[]
    fftabi=[]

    # ffta = np.array(data_un[])

    for i in range(fftnum):
        ffta.append(data_un[i+fftnum*0+8])
        fftb.append(data_un[i+fftnum*1+8])
        fftabr.append(data_unb[i+fftnum*2+8])
        fftabi.append(data_unb[i+fftnum*3+8])


    f=numpy.linspace(0,bw,fftnum)
    matplotlib.pyplot.clf() 
    matplotlib.pylab.subplot(411)   
    matplotlib.pylab.plot(f, ffta)
    #matplotlib.pylab.title('    fft_a')
    #matplotlib.pylab.ylim(0,100)
    matplotlib.pylab.grid()
    #matplotlib.pylab.xlabel('Channel')
    matplotlib.pylab.title('AA_ACC_NUM seq=%i'%(num_acc))
    
    #matplotlib.pylab.xlim(0,fftnum1)
    matplotlib.pylab.ylim(0,256)

    matplotlib.pylab.subplot(412)   
    matplotlib.pylab.plot(f,fftb)
    matplotlib.pylab.title('BB')    
    matplotlib.pylab.grid()  
    #matplotlib.pylab.xlim(0,fftnum1)
    matplotlib.pylab.ylim(0,256)

    matplotlib.pylab.subplot(413)   
    matplotlib.pylab.plot(f,fftabr)
    matplotlib.pylab.title('CR')    
    matplotlib.pylab.grid()  
    #matplotlib.pylab.xlim(0,fftnum1)

    matplotlib.pylab.subplot(414)   
    matplotlib.pylab.plot(f,fftabi)
    matplotlib.pylab.title('CI')    
    matplotlib.pylab.grid()  
    #matplotlib.pylab.xlim(0,fftnum1)

 
	

    fig.canvas.draw()	
    fig.canvas.manager.window.after(500,plot_spectrum)
    return True

if __name__ == '__main__':
        IP = '10.17.16.12' #bind on all IP addresses
        PORT = 17200
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((IP, PORT))
        if PORT != -1:
            print("100GbE port connect done!")
            fig = matplotlib.pyplot.figure()
            fig.canvas.manager.window.after(500,plot_spectrum)
            matplotlib.pyplot.show()