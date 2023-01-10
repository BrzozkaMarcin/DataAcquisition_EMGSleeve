from sys import exit
import serial
from optparse import OptionParser
import time
import struct

def get_slave_state(connection):
    connection.write(('whatState' + EOM).encode('ascii'))
    state = connection.read_until(EOM)
    return state.decode('ascii')

def read_emg(connection):
    # return ord(connection.read(3))
    # data = connection.read_until() 
    data = connection.read(4) #until the first sample this waits very long. Now its set by connection timeout but maybe think about smth else
    # print(int.from_bytes(data[:-2], byteorder="little", signed=False))
    return int.from_bytes(data[:-2], byteorder="little", signed=False)

def save_to_file(filename, emg1, emg2, emg3):
    out_file = open(filename + ".csv","w+", buffering=1)
    out_file.write("EMG1, EMG2, EMG3\r\n")
    for i in range(len(emg1)):
        out_file.write(str(emg1[i]) + ',')
        out_file.write(str(emg2[i]) + ',')
        out_file.write(str(emg3[i])+'\r\n')
    out_file.close()
parser = OptionParser()
parser.add_option("-o", "--output-file", dest="filename",
                  help="write output to CSV, and log", metavar="FILE")
parser.add_option("-p", "--serial-port1", dest="COM_port",
                  help="device serial port")
parser.add_option("-n", "--num-samples", dest="num_samp",
                  help="number of samples to collect", type='int')
parser.add_option("-s", '--sensors', dest = "sensors",
                help = "Choose which number of sensors: 0x01 = sensor1, 0x02 = sensor2, 0x04 = sensor3. Ex.: 3 = sensor1+sensor2. Default is 7 - all 3 sensors", 
                default = 0x07, type = "int")


(options, args) = parser.parse_args()

if options.filename == None:
    print('No output file name added. Aborting.')
    exit()

if options.COM_port == None:
    print('No serial port added. Aborting.')
    exit()

if options.num_samp <=0 or options.num_samp == None:
    print('Invalid number of samples to collect. Aborting.')
    exit()


states = {'Init': 1, 'Idle' : 2, 'Read' : 3}
EOM = '#'

#Header will send essential info like state (enum/dict), measurement format, sampling frequency etc to the slave to perform measurement.
#Then if info is received (maybe need feedback) sending in data is started.
header = ("number_of_samples" + EOM + str(options.num_samp) + EOM).encode('ascii')

#need to choose character as end of message (EOM) /n for now


#initializing empty lists for data to save
emg_values1 = [None for y in range(options.num_samp)]
emg_values2 = [None for y in range(options.num_samp)]
emg_values3 = [None for y in range(options.num_samp)]


connection = serial.Serial(options.COM_port, 115200, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, timeout=options.num_samp/1000 + 3)
time.sleep(2)
connection.reset_input_buffer()
connection.reset_output_buffer()

connection.write(("Read" + EOM + str(options.num_samp) + EOM).encode('ascii')) 
start_time = time.time()
for i in range(0, options.num_samp):
    emg_values1[i] = read_emg(connection)
    emg_values2[i] = read_emg(connection)
    emg_values3[i] = read_emg(connection)

collecting_time = time.time()
connection.reset_output_buffer()
connection.close()
print("Acquisition time: ", time.time() - start_time)
print("Collecting time: ", collecting_time - start_time)

save_to_file(options.filename, emg_values1, emg_values2, emg_values3)


import pandas as pd


emg1 = pd.read_csv(options.filename + '.csv')
print("Received and saved values:")
print(emg1)
# import matplotlib.pyplot as plt

# plt.figure(1)
# plt.plot(emg1)
# plt.title(filename_emg1)
# plt.ylabel("wartosc sygnalu [-]")
# plt.xlabel("Nr probki")
# plt.show()

# plt.figure(2)
# plt.plot(emg2)
# plt.title(filename_emg2)
# plt.ylabel("wartosc sygnalu [-]")
# plt.xlabel("Nr probki")
# plt.show()

# plt.figure(3)
# plt.plot(emg3)
# plt.title(filename_emg3)
# plt.ylabel("wartosc sygnalu [-]")
# plt.xlabel("Nr probki")
# plt.show()

# else :
#     print("Error occured, slave not in Idle mode")
    