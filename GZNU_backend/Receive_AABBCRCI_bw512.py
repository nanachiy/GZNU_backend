#!/media/hero/Intel6/anaconda3/bin/python

"""
FFT with datas in files, return fits fomat data.
Email: 393744534@qq.com
Author: Chen Zhongxu
"""

import numpy as np
from astropy.io import fits
from astropy.time import Time
import struct
import fits_config
import time
import multiprocessing
import time
import socket
import struct
import datetime
import math

# config: files
data_queue = multiprocessing.Queue()
spec_queue = multiprocessing.Queue()
shutdown_flag = False
IP = '10.17.16.12' #bind on all IP addresses
PORT = 17200
example_path = 'fits_example_8bit_1024MHz_1024FFT.fits'
path_fits = '20250518_B0833-45_fits/'

# config: fits file
# rate_sam = 2048
N_raw = 128
N_fft = 1024
N_time = 1024
N_fre_channel = N_fft//2
bw = 512
N_acc = 64
i_file = 0
spec_shape = str(N_fft) + 'B'
spec_shape_2 = str(N_fft) + 'b'
len_header = 8
specrtrum_power_result = np.empty((N_raw, N_time, 4, N_fre_channel, 1), dtype='uint8')
n_spec_per_fits = N_raw*N_time//2
n_spec = n_spec_per_fits*200

# config: time
date = datetime.datetime.now()
i_mjd = Time.now().mjd
s_mjd = i_mjd*24*3600
stt_imjd = math.floor(i_mjd)
stt_smjd = math.floor(s_mjd)
stt_offs = s_mjd - stt_smjd
fits_time = 64*1024*128*10**(-6)

def get_data():
    global shutdown_flag
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((IP, PORT))

    for i in range(n_spec):
        pkt, _ = sock.recvfrom(8256)
        # data = struct.unpack('2048B2048b2048B2048b', pkt[len_header: len_header + N_fft*8])
        # if i == 0:
        #     frame_start = struct.unpack('>I', pkt[4:8])[0]

        data_queue.put(pkt[len_header: len_header + N_fft*8])
    
    # frame_end = struct.unpack('>I', pkt[4:8])[0]
    # print(f'[get data] loss rate: {(n_spec-(frame_end-frame_start+1))/n_spec}')

    sock.close()
    shutdown_flag = True
    print(f'[get_data] Processing is finished')


def fits_writer():
    hdu_list = fits.open(example_path)
    hdu_list[1].data['DATA'] = specrtrum_power_result

    delta = fits_time*i_file
    date_now = str(date+datetime.timedelta(seconds=delta)).replace(' ', 'T')[0:20]
    i_mjd_now = i_mjd + delta/24/3600
    s_mjd_now = (i_mjd_now - math.floor(i_mjd_now))*24*3600
    stt_imjd_now = math.floor(i_mjd_now)
    stt_smjd_now = math.floor(s_mjd_now)
    stt_offs = s_mjd_now - stt_smjd_now

    hdu_list[0].header['DATE-OBS'] = date_now
    hdu_list[0].header['STT_IMJD'] = stt_imjd_now
    hdu_list[0].header['STT_SMJD'] = stt_smjd_now
    hdu_list[0].header['STT_OFFS'] = stt_offs

    hdu_list.writeto(path_fits + f'AABBCRCI_{i_file:0>4}.fits', overwrite=True)
    hdu_list.close()


def write_file():
    global i_file, shutdown_flag
    # spectrum_acc = np.empty((N_acc, 4, N_fre_channel), dtype='uint8')
    i_raw = 0
    i_time = 0

    # time_3 = time.perf_counter()
    while not data_queue.empty() or not shutdown_flag:
        # time_3 = time.perf_counter()
        data = struct.unpack('8192B', data_queue.get())

        specrtrum_power_result[i_raw % N_raw, i_time % N_time, 0, :, 0] = data[1023:511:-1]
        specrtrum_power_result[i_raw % N_raw, i_time % N_time, 1, :, 0] = data[2047:1535:-1]
        specrtrum_power_result[i_raw % N_raw, i_time % N_time, 2, :, 0] = data[3071:2559:-1]
        specrtrum_power_result[i_raw % N_raw, i_time % N_time, 3, :, 0] = data[4095:3583:-1]
        specrtrum_power_result[i_raw % N_raw, (i_time+1) % N_time, 0, :, 0] = data[5119:4607:-1]
        specrtrum_power_result[i_raw % N_raw, (i_time+1) % N_time, 1, :, 0] = data[6143:5631:-1]
        specrtrum_power_result[i_raw % N_raw, (i_time+1) % N_time, 2, :, 0] = data[7167:6655:-1]
        specrtrum_power_result[i_raw % N_raw, (i_time+1) % N_time, 3, :, 0] = data[8191:7679:-1]

        i_time += 2

        if i_time % N_time == 0:
            # print(f"[write_file] i_raw = {i_raw}")
            i_raw += 1

            if i_raw % N_raw == 0:
                # time_3 = time.perf_counter()
                fits_writer()
                print(f"[write_file] i_file = {i_file}")
                i_file +=  1
                # time_4 = time.perf_counter()
                # print(f'[Main] Time use:{time_4 - time_3} seconds')


def init_fits():
    hdu_list = fits.open(example_path)
    hdu_list[0].header['DATE'] = fits_config.date
    hdu_list[0].header['OBSERVER'] = fits_config.observer
    hdu_list[0].header['PROJID'] = fits_config.projid
    # hdu_list[0].header['DATE-OBS'] = fits_config.date_obs
    hdu_list[0].header['SRC_NAME'] = fits_config.src_name
    hdu_list[0].header['RA'] = fits_config.ra
    hdu_list[0].header['DEC'] = fits_config.dec
    # hdu_list[0].header['STT_IMJD'] = fits_config.stt_imjd
    # hdu_list[0].header['STT_sMJD'] = fits_config.stt_smjd
    # hdu_list[0].header['STT_OFFS'] = fits_config.stt_offs
    hdu_list.writeto(example_path, overwrite=True)
    hdu_list.close()


if __name__ == '__main__':
    time_1 = time.perf_counter()

    init_fits()

    data_getter = multiprocessing.Process(target=get_data)
    file_writer =  multiprocessing.Process(target=write_file)

    file_writer.start()
    data_getter.start()

    data_getter.join()
    file_writer.join()

    time_2 = time.perf_counter()
    print(f'[Main] Time use:{time_2 - time_1} seconds')
