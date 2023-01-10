from sys import exit
import serial
from optparse import OptionParser
import time

#TODO
# - defining ports
# - write log file
# - adjust read bytes in read_emg() function

FORCE_EMG_RATIO = 10
SAMPLE_TIME = 0.001   


parser = OptionParser()
parser.add_option("-o", "--output-file", dest="filename",
                  help="write output to CSV, and log", metavar="FILE")
parser.add_option("-p", "--serial-port1", dest="port1",
                  help="device serial port")
parser.add_option("-n", "--num-samples", dest="num_samp",
                  help="number of samples to collect", default=0, type='int')


(options, args) = parser.parse_args()

filename = options.filename
filename_emg1 = filename + '_emg1'
filename_emg2 = filename + '_emg2'
filename_emg3 = filename + '_emg3'
num_samp = options.num_samp


if options.filename == None:
    print('No output file name added')
    exit()

port1 = options.port1
if options.port1 == None:
    print('No serial port 1 added')
    exit()


# def write_log_file(filename):
    
#     filename_emg = filename + '_emg'
    
#     log_file = open(filename+".log","a+")
    
#     log_file.write('python_serial_reader_v80Hz.py\n')
#     start_time = time.time()
#     log_file.write('start at: %s\n'% (time.asctime( time.localtime(start_time))))
#     print('start at: %s\n'% (time.asctime(time.localtime(start_time))))
#     log_file.write('force output filename: %s\n'% (filename))
#     print('force output filename: %s\n'% (filename))
#     log_file.write('emg output filename: %s\n'% (filename_emg))
#     print('emg output filename: %s\n'% (filename_emg))
#     log_file.write('serial port1: %s\n'% (port1))
#     print('serial port1: %s\n'% (port1))
#     log_file.write('number of force samples to collect: %d\n'% (num_samp))
#     print('number of force samples to collect: %d\n'% (num_samp))
#     log_file.write('number of emg samples: %d\n'% (num_samp*FORCE_EMG_RATIO))
#     log_file.write('time of acquisition (s): ~%d\n'% (num_samp*SAMPLE_TIME))
#     log_file.write('unit of force: kg\nunit of emg (values 0-255): - ')
#     log_file.close()

# write_log_file(filename)

# out_file = open(filename+".csv","w+", buffering=1)
# out_file_emg = open(filename_emg+".csv","w+", buffering=1)

#initializing empty lists for data to save
emg_values1 = [None for y in range(num_samp)]
emg_values2 = [None for y in range(num_samp)]
emg_values3 = [None for y in range(num_samp)]



def read_emg(serialPort):
    return(ord(serialPort.read(1))) #serialPort.read(numberOfBytes) - here we can manipulate number of bytes read by script

ser = serial.Serial(port1, 115200, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, timeout=1000)
time.sleep(3) #wait for esp32 and sensor to reset



print("Starting now...\n")
ser.reset_input_buffer()
# we need to define how we will know from which sensor we are acquiring data
for i in range(0, num_samp):
    emg_values1[i]=read_emg(ser)
    emg_values2[i]=read_emg(ser)
    emg_values3[i]=read_emg(ser)
    #print("EMG: ", emg_values[i*10 +j])
       
time.sleep(SAMPLE_TIME) #wait for data to acumulate in buffer

ser.close()

print("End of acquisition\n") 

out_file1 = open(filename_emg1+".csv","w+", buffering=1)
out_file2 = open(filename_emg2+".csv","w+", buffering=1)
out_file3 = open(filename_emg3+".csv","w+", buffering=1)

# for indx, val in enumerate(emg_values1):
#     f_val= float(val)
#     if f_val<0:
#         f_val=0
#     #if f_val>15:
#     #    f_val=(float(force_values[indx-1])+float(force_values[indx+1]))/2
#     out_file.write('{:.2f},\n'.format(f_val))

for val in emg_values1:
    out_file1.write(str(val)+',\n')
for val in emg_values2:
    out_file2.write(str(val)+',\n')
for val in emg_values3:
    out_file3.write(str(val)+',\n')

out_file1.close()
out_file2.close()
out_file3.close()

#-------------------------------
#wykresiki.py
#we check how our data looks like. We are reading from file because we want to see what values are saved.

import pandas as pd


emg1 = pd.read_csv(filename_emg1 + '.csv')
emg2 = pd.read_csv(filename_emg2 + '.csv')
emg3 = pd.read_csv(filename_emg3 + '.csv')

import matplotlib.pyplot as plt

plt.figure(1)
plt.plot(emg1)
plt.title(filename_emg1)
plt.ylabel("wartosc sygnalu [-]")
plt.xlabel("Nr probki")
plt.show()

plt.figure(2)
plt.plot(emg2)
plt.title(filename_emg2)
plt.ylabel("wartosc sygnalu [-]")
plt.xlabel("Nr probki")
plt.show()

plt.figure(3)
plt.plot(emg3)
plt.title(filename_emg3)
plt.ylabel("wartosc sygnalu [-]")
plt.xlabel("Nr probki")
plt.show()
