#!/media/hero/Intel6/anaconda3/bin/python

"""
FFT with datas in files, return fits fomat data.
Email: 393744534@qq.com
Author: Chen Zhongxu
"""

import numpy as np
from numpy.fft import rfft
from astropy.io import fits
import os
import struct
import queue
import fits_config
import time
import multiprocessing

import time

# config: file
data_queue = multiprocessing.Queue(maxsize=250000*10)
spec_queue = multiprocessing.Queue(maxsize=250000*10)

file_A_order = 0
file_B_order = 0
file_A_pointer = 0
file_B_pointer = 0
path_fits = 'spectrum_fits_2/'
pkt_per_sec = 250000
shutdown_flag = False
fits_example = 'test_data_32bits.fits'

# config: data structure
PACKET_SIZE = 8256
N_fft = 4096
N_acc = 10
N_time = 1024
N_raw = 128
factor_norm = 2.8/7000
offset = 2**13

# config: FFT
fre_sample = 1024.0 # MHz
fs = fre_sample/N_fft
delta = np.sqrt(0.1)/1000


def get_filelist_sorted(file_path):
    """

    """
    filelist = os.listdir(file_path)
    filelist.sort(key = lambda x: int(x.split('_')[2]))
    return filelist


def open_files(file_A_list, file_B_list):
    """

    """
    global file_A_order, file_B_order, file_A_pointer, file_B_pointer, shutdown_flag
    if file_A_order < len(file_A_list) and file_B_order < len(file_B_list):
        end_pointer = open(file_A_list[file_A_order], 'rb').seek(0, 2)

        file_A = open(file_A_list[file_A_order], 'rb')
        file_A.seek(file_A_pointer, 0)

        file_B = open(file_B_list[file_B_order], 'rb')
        file_B.seek(file_B_pointer, 0)

        return file_A, file_B, end_pointer
    else:
        shutdown_flag = True
        return (None, )*3


def get_dataarray(file_A, file_B, end_pointer):
    """
    
    """
    global file_A_order, file_B_order, file_A_pointer, file_B_pointer
    
    while True:
        time_1 = time.perf_counter()
        if data_queue.full():
            continue

        # determine if files are at the end
        if file_A.tell() >= end_pointer or file_B.tell() >= end_pointer:
            if file_A.tell() >= end_pointer:
                file_A_order += 1
                file_A_pointer = 0
            
            
            if file_B.tell() >= end_pointer:
                file_B_order += 1
                file_B_pointer = 0

            file_A.close()
            file_B.close()
            
            break
        
        # read from files, compare vdif headers
        pkt_A = file_A.read(PACKET_SIZE)
        pkt_B = file_B.read(PACKET_SIZE)

        header_A = struct.unpack('<8L', pkt_A[0:32])
        sec_ref_ep_A = header_A[0] & (2**30-1)
        data_frame_A = header_A[1] & (2**24-1)
        
        header_B = struct.unpack('<8L', pkt_B[0:32])
        sec_ref_ep_B = header_B[0] & (2**30-1)
        data_frame_B = header_B[1] & (2**24-1)

        if sec_ref_ep_A == sec_ref_ep_B and data_frame_A == data_frame_B:
            # print('Good')
            data_queue.put(np.array(struct.unpack('<4096H', pkt_A[64:]), dtype='uint16'))
            data_queue.put(np.array(struct.unpack('<4096H', pkt_B[64:]), dtype='uint16'))
            # if i == 0:
            #     time_2 = time.perf_counter()
            #     print(f'一次时间读取数据并比较时间戳的时间:{time_2 - time_1}秒')
            #     i=1
            
        elif sec_ref_ep_A > sec_ref_ep_B:
            file_A.seek(-PACKET_SIZE, 1)
        elif sec_ref_ep_A < sec_ref_ep_B:
            file_B.seek(-PACKET_SIZE, 1)
        elif data_frame_A > data_frame_B:
            file_A.seek(-PACKET_SIZE, 1)
        elif data_frame_A < data_frame_B:
            file_B.seek(-PACKET_SIZE, 1)
        

def get_dataarray_pthread():
    """
    """
    while True:
        file_A, file_B, end_pointer = open_files(file_A_list, file_B_list)

        if shutdown_flag:
            break
        get_dataarray(file_A, file_B, end_pointer)


def gen_fft():
    # j = 0
    while not shutdown_flag or not data_queue.empty():
        if not data_queue.empty():
            time_3 = time.perf_counter()
            spec_queue.put(rfft(data_queue.get())[1:])
            spec_queue.put(rfft(data_queue.get())[1:])
            time_4 = time.perf_counter()
            # if j == 0:
            #     print(f'AB两路完成fft的时间：{time_4 - time_3}')
            #     j = 1
        # else:
        #     print(f'Data queue empty{count}')
        #     count += 1



def fft_acc():
    """

    """
    # k = 0
    # print(1)
    i_spectrum = 0
    i_time = 0
    i_raw = 0
    i_file = 0
    
    spectrum_acc_A = np.empty((N_acc, N_fft//2), dtype='complex64')
    spectrum_acc_B = np.empty((N_acc, N_fft//2), dtype='complex64')

    specrtrum_power_result = np.empty((N_raw, N_time, 4, N_fft//2, 1))

    # print(2)
    while not shutdown_flag or not spec_queue.empty():
        time_5 = time.perf_counter()
        if spec_queue.empty():
            # print('empty')
            continue

        # data_array_A =  data_queue.get()
        # data_array_B =  data_queue.get()

        # print(3)

        spectrum_acc_A[i_spectrum % N_acc, :] = spec_queue.get()
        spectrum_acc_B[i_spectrum % N_acc, :] = spec_queue.get()
        i_spectrum += 1


        if i_spectrum % N_acc == 0:
            specrtrum_power_single = cross_correlation(np.mean(spectrum_acc_A, axis=0), np.mean(spectrum_acc_B, axis=0))
            specrtrum_power_result[i_raw % N_raw, i_time % N_time, :, :, 0] = specrtrum_power_single
            i_time += 1
            # print(f"[fft_acc] Time = {i_time}")
            if i_time % N_time == 0:
                i_raw += 1
                print(f"[fft_acc] Row = {i_raw}")
                time_6 = time.perf_counter()
                # if k == 0:
                #     print(f'进行一次取平均并写入raw的时间：{time_6 - time_5}')
                #     k = 1
                if i_raw %  N_raw ==0:
                    write_into_fits(i_file, specrtrum_power_result)
                    print(f"[fft_acc] Fits file {i_file} is finished.")
                    i_file += 1


def cross_correlation(spec_A, spec_B):
    matrix = []
    matrix.append(np.abs(spec_A)**2)
    matrix.append(np.abs(spec_B)**2)
    matrix.append(np.multiply(spec_A, spec_B.conjugate()).real)
    matrix.append(np.multiply(spec_A, spec_B.conjugate()).imag)

    return np.stack(matrix, axis = 1).transpose()


def write_into_fits(i_file, specrtrum_power_result):
    """

    """
    hdu_list = fits.open(fits_example)
    hdu_list[1].data['DATA'] = specrtrum_power_result.astype('float32')
    hdu_list.writeto(path_fits + f'spectrum_power_result_{i_file}', overwrite=True)
    hdu_list.close()


def init_fits():
    hdu_list = fits.open(fits_example)
    hdu_list[0].header['DATE'] = fits_config.date
    hdu_list[0].header['OBSERVER'] = fits_config.observer
    hdu_list[0].header['PROJID'] = fits_config.projid
    hdu_list[0].header['DATE-OBS'] = fits_config.date_obs
    hdu_list[0].header['SRC_NAME'] = fits_config.src_name
    hdu_list[0].header['RA'] = fits_config.ra
    hdu_list[0].header['DEC'] = fits_config.dec
    hdu_list[0].header['STT_IMJD'] = fits_config.stt_imjd
    hdu_list[0].header['STT_sMJD'] = fits_config.stt_smjd
    hdu_list[0].header['STT_OFFS'] = fits_config.stt_offs
    hdu_list.writeto(fits_example, overwrite=True)
    hdu_list.close()

if __name__ == "__main__":
    init_fits()

    file_A_path = '/media/hero/Intel5/data_test/'
    file_B_path = '/media/hero/Intel7/data_test/'

    file_A_list = get_filelist_sorted(file_A_path)
    file_B_list = get_filelist_sorted(file_B_path)

    file_A_list = [file_A_path + file for file in file_A_list]
    file_B_list = [file_B_path + file for file in file_B_list]

    spec_writer = multiprocessing.Process(target=fft_acc)
    data_getter = multiprocessing.Process(target=get_dataarray_pthread)
    fft_gener = multiprocessing.Process(target=gen_fft)
    
    spec_writer.start()
    fft_gener.start()
    data_getter.start()


    data_getter.join()
    fft_gener.join()
    spec_writer.join()
