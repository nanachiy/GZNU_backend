#!/media/hero/Intel6/anaconda3/bin/python

"""
Calculate loss rates of files. 
Email: 393744534@qq.com
Author: Chen Zhongxu
"""

from astropy.io import fits
import subprocess
import struct
import time
import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib
matplotlib.use('tkagg')
import matplotlib.pyplot as plt

# result = subprocess.run(['./2-ReadAndPrint /media/hero/Intel5/data_test/test_0_28'], capture_output=True, text=True)
# print(result.stdout)

# def get_filelist_sorted(file_path):
#     """

#     """
#     filelist = os.listdir(file_path)
#     filelist.sort(key = lambda x: int(x.split('_')[2]))
#     return filelist

# file_A_path = '/media/hero/Intel5/data_test/'
# file_B_path = '/media/hero/Intel7/data_test/'

# file_A_list = get_filelist_sorted(file_A_path)
# file_B_list = get_filelist_sorted(file_B_path)

# file_A_list = [file_A_path + file for file in file_A_list]
# file_B_list = [file_B_path + file for file in file_B_list]

# coun = 0
# for file in file_B_list:
#     print(file)
#     os.system('./2-ReadAndPrint ' + file)

# data = pd.read_csv('usage.csv')
# data_array = np.array(data)

# loss_rate = np.zeros(30)
# cpu = data_array[:, 1]
# mem_percent = data_array[:, 2]
# rss = data_array[:, 4]

# plt.figure()
# plt.bar(np.arange(0, 30), loss_rate, label='Polarization 1')
# plt.bar(np.arange(0, 30), loss_rate, label='Polarization 2')
# plt.xlabel('File Number')
# plt.ylabel('Loss Rate (%)')
# plt.legend()
# plt.title('Loss Rates of Files')


# plt.figure()
# plt.plot(cpu)
# plt.xlabel('Time (second)')
# plt.ylabel('CPU usage (%)')
# plt.title('CPU usage of the Program')


# plt.figure()
# plt.plot(mem_percent, 'r-', label='Memory usage percent(%)')
# plt.plot(rss/1000, 'g--', label='Physical memory(MB)')
# plt.xlabel('Time (second)')
# plt.legend()
# plt.title('Memory Usage')

# # 创建图表和第一个Y轴
# fig, ax1 = plt.subplots()
# ax1.plot(mem_percent, 'b--', label='Memory usage percent(%)')
# ax1.set_xlabel('Time (second)')
# ax1.set_ylabel('Memory usage percent(%)', color='b')
# ax1.tick_params(axis='y', labelcolor='b')
# plt.ylim((0, 10))

# # 创建第二个Y轴
# ax2 = ax1.twinx()
# ax2.plot(rss/1000, 'g-', label='Physical memory(MB)')
# ax2.set_ylabel('Physical memory(MB)', color='g')
# ax2.tick_params(axis='y', labelcolor='g')

# # 添加图例
# fig.legend(loc='upper left', bbox_to_anchor=(0.1, 1), bbox_transform=ax1.transAxes)

# plt.title('Memory Usage')
# plt.tight_layout()

# plt.show()

# load fits file of FAST
path = "spectrum_fits_3/spectrum_power_result_0"
hdu_list = fits.open(path, cache=True)

data = hdu_list[1].data['DATA']

pic = np.abs(data[1,:,:,:,0])

xx = hdu_list[1].data['DAT_FREQ']

# fre = hdu_list[1].data['']

df1 = pd.DataFrame(pic[:, 0, :], index=np.arange(1024), columns=xx[0, :])
df2 = pd.DataFrame(pic[:, 1, :], index=np.arange(1024), columns=xx[0, :])
df3 = pd.DataFrame(pic[:, 2, :], index=np.arange(1024), columns=xx[0, :])
df4 = pd.DataFrame(pic[:, 3, :], index=np.arange(1024), columns=xx[0, :])

# plt.subplot(2,2,1)

# ax = sns.heatmap(df1)

# plt.xlabel('Frequence(MHz)')
# plt.ylabel('Time Channel')
# plt.title('AA(dB)')
# ax.set_xticks([])

# plt.subplot(2,2,2)

# ax = sns.heatmap(df2)

# plt.xlabel('Frequence(MHz)')
# plt.ylabel('Time Channel')
# plt.title('BB(dB)')
# ax.set_xticks([])

# plt.subplot(2,2,3)

# ax = sns.heatmap(df3)

# plt.xlabel('Frequence(MHz)')
# plt.ylabel('Time Channel')
# plt.title('CR(dB)')

# plt.subplot(2,2,4)

# ax = sns.heatmap(df4)

# plt.xlabel('Frequence(MHz)')
# plt.ylabel('Time Channel')
# plt.title('CI(dB)')

plt.subplot(2,2,1)

plt.semilogy(xx[0, :-1], np.mean(pic[:, 0, :], axis=0)[:-1])

# plt.xlabel('Frequence(MHz)')
plt.ylabel('Power')
plt.title('AA')

plt.subplot(2,2,2)

plt.semilogy(xx[0, :-1], np.mean(pic[:, 1, :], axis=0)[:-1])

# plt.xlabel('Frequence(MHz)')
plt.ylabel('Power')
plt.title('BB')

plt.subplot(2,2,3)

plt.semilogy(xx[0, :-1], np.mean(pic[:, 2, :], axis=0)[:-1])

plt.xlabel('Frequence(MHz)')
plt.ylabel('Power')
plt.title('CR')

plt.subplot(2,2,4)

plt.semilogy(xx[0, :], np.mean(pic[:, 3, :], axis=0))

plt.xlabel('Frequence(MHz)')
plt.ylabel('Power')
plt.title('CI')

plt.show()