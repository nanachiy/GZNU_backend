#!/media/hero/Intel6/anaconda3/bin/python

"""
FFT with datas in files, return fits fomat data.
Email: 393744534@qq.com
Author: Chen Zhongxu
"""

import numpy as np
from astropy.io import fits
import os
import struct
import fits_config
import time
import multiprocessing
import time
import socket
import struct

# config: files
data_queue = multiprocessing.Queue()
shutdown_flag = False
IP = '10.17.16.12' #bind on all IP addresses
PORT = 17200
example_path = 'fits_example_8bit_2048MHz_2048FFT.fits'
path_fits = 'spectrum_fits_3/'

# config: fits file
N_raw = 128
N_fft = 2048
N_time = 1024
N_fre_channel = N_fft//2
N_acc = 10
i_file = 0
spec_shape = str(N_fft//2) + 'B'
spec_shape_2 = str(N_fft//2) + 'b'
len_header = 8
specrtrum_power_result = np.empty((N_raw, N_time, 4, N_fre_channel, 1), dtype='uint8')
n_spec_per_fits = 128*N_time*N_acc//2
n_spec = n_spec_per_fits*1


def get_data():
    global shutdown_flag
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((IP, PORT))

    for i in range(n_spec):
        data, _ = sock.recvfrom(8256)
        data_queue.put(data)
    
    shutdown_flag = True


def fits_writer():
    hdu_list =  fits.open(example_path)
    hdu_list[1].data['DATA'] = specrtrum_power_result
    hdu_list.writeto(path_fits + f'spectrum_power_result_{i_file}', overwrite=True)
    hdu_list.close()


def write_file():
    global i_file
    spectrum_acc = np.empty((N_acc, 4, N_fre_channel), dtype='uint8')
    i_acc = 0
    i_raw = 0
    i_time = 0

    while not data_queue.empty() or not shutdown_flag:
        if data_queue.empty():
            continue

        pkt = data_queue.get()
        spectrum_acc[i_acc % N_acc, 0, :] = struct.unpack(spec_shape, pkt[len_header: len_header+N_fre_channel])
        spectrum_acc[i_acc % N_acc, 1, :] = struct.unpack(spec_shape, pkt[len_header+N_fre_channel: len_header+N_fre_channel*2])
        spectrum_acc[i_acc % N_acc, 2, :] = np.abs(struct.unpack(spec_shape_2, pkt[len_header+N_fre_channel*2: len_header+N_fre_channel*3])).astype('uint8')
        spectrum_acc[i_acc % N_acc, 3, :] = np.abs(struct.unpack(spec_shape_2, pkt[len_header+N_fre_channel*3: len_header+N_fre_channel*4])).astype('uint8')
        i_acc += 1
        # print(f"[write_file] i_acc = {i_acc}")
        spectrum_acc[i_acc % N_acc, 0, :] = struct.unpack(spec_shape, pkt[len_header+N_fre_channel*4: len_header+N_fre_channel*5])
        spectrum_acc[i_acc % N_acc, 1, :] = struct.unpack(spec_shape, pkt[len_header+N_fre_channel*5: len_header+N_fre_channel*6])
        spectrum_acc[i_acc % N_acc, 2, :] = np.abs(struct.unpack(spec_shape_2, pkt[len_header+N_fre_channel*6: len_header+N_fre_channel*7])).astype('uint8')
        spectrum_acc[i_acc % N_acc, 3, :] = np.abs(struct.unpack(spec_shape_2, pkt[len_header+N_fre_channel*7: len_header+N_fre_channel*8])).astype('uint8')
        i_acc += 1
        # print(f"[write_file] i_acc = {i_acc}")
    
        if i_acc % N_acc == 0:
            specrtrum_power_result[i_raw % N_raw, i_time % N_time, :, :, 0] = np.mean(spectrum_acc, axis=0)
            # print(f"[write_file] i_time = {i_time}")
            i_time += 1

            if i_time % N_time == 0:
                print(f"[write_file] i_raw = {i_raw}")
                i_raw += 1

                if i_raw % N_raw == 0:
                    fits_writer()
                    print(f"[write_file] i_file = {i_file}")
                    i_file +=  1

if __name__ == '__main__':
    time_1 = time.perf_counter()

    data_getter = multiprocessing.Process(target=get_data)
    file_writer =  multiprocessing.Process(target=write_file)

    file_writer.start()
    data_getter.start()

    data_getter.join()
    file_writer.join()

    time_2 = time.perf_counter()
    print(f'[Main] Time use:{time_2 - time_1} seconds')
