#!/bin/bash

# ip list
ip_0=10.17.16.11
ip_1=10.17.16.12

# port list
port_0=17200
port_1=17201
port_2=17202
port_3=17203

# receive config
n_write=75000

# run Receive

taskset -c 0-7 ./ReceiveAndSave_main ${n_write} /media/hero/Intel5/data_test/test_0_ ${ip_1} ${port_0}&
taskset -c 8-15 ./ReceiveAndSave_main ${n_write} /media/hero/Intel7/data_test/test_1_ ${ip_1} ${port_1}&
wait
