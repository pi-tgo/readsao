!/usr/bin/python

# Documentation of the SAO format: https://ulcar.uml.edu/~iag/SAO-4.3.htm

import sys
import struct
import datetime
from time import strptime
import numpy as np
import math
import matplotlib
import copy
# matplotlib.use('Agg')       # use the 'Agg' backend when $DISPLAY environment is not defined
import matplotlib.pyplot as plt
plt.rcParams["figure.figsize"] = (12, 8)

#filename = 'TR169_2020083143000.SAO'
#filename = 'TR169_2020064101500.SAO'			# for testing purposes

f = open(sys.argv[1], "rb")				# comment if you want to run the code inside python using >>> exec(open('readsao.py').read())
#f = open(filename, "rb")				# use this if filename is defined above 

#-----------------
# Data File Index 
#-----------------

num_elements = np.zeros(80)   # define array num_elements
data_index = f.read(40*3).decode("utf-8")
for i in range(40):
   num_elements[i] = int(data_index[i*3:i*3+3])

crdummy = f.read(2)

data_index = f.read(40*3).decode("utf-8")
for i in range(40):
   num_elements[i+40] = int(data_index[i*3:i*3+3])

# Print out the number of elements in each group
for i in range(80):
   if num_elements[i] != 0:
      print('GROUP ' + str(i+1) +': ' + str(int(num_elements[i])) + ' elements')

crdummy = f.read(2)

#--------------------------------
# GROUP 1: Geophysical Constants 
#--------------------------------

geophysical_constant = np.zeros(int(num_elements[0])) # define array geophysical_constants
for i in range(int(num_elements[0])):
   constant = f.read(7)
   geophysical_constant[i] = float(constant)

if int(num_elements[0]) != 0:
   crdummy = f.read(2)

#----------------------------------------------------
# GROUP 2: System Description and Operator's Message 
#----------------------------------------------------

for i in range(int(num_elements[1])):
   system_description_and_operator_message = str(f.read(120))

if int(num_elements[1]) != 0:
   crdummy = f.read(2)

#------------------------------------------
# GROUP 3: Time Stamp and Sounder Settings 
#------------------------------------------

# Assuming Digisonde Portable Sounder (DPS) System only (Table 4)
time_and_sounder_settings = f.read(int(num_elements[2]))

version_indicator = time_and_sounder_settings[0:2].decode("utf-8")  			# string (AA, FF or FE)
year = int(time_and_sounder_settings[2:6])						# int (1976-...)
day_of_year = int(time_and_sounder_settings[6:9])					# int (1-366)
month = int(time_and_sounder_settings[9:11])						# int (1-12)
day_of_month = int(time_and_sounder_settings[11:13])					# int (1-31)
hour = int(time_and_sounder_settings[13:15])						# int (0-23)
min = int(time_and_sounder_settings[15:17])						# int (0-59)
sec = int(time_and_sounder_settings[17:19])						# int (0-59)
receiver_station_id = time_and_sounder_settings[19:22].decode("utf-8")			# string (000-999) - three digits
transmitter_station_id = time_and_sounder_settings[22:25].decode("utf-8")		# string (000-999) - three digits
DPS_schedule = int(time_and_sounder_settings[25:26])					# int (1-6)
DPS_program = int(time_and_sounder_settings[26:27])					# int (1-7)
start_frequency = time_and_sounder_settings[27:32].decode("utf-8")			# string (01000-25000)
coarse_frequency = int(time_and_sounder_settings[32:36])				# int (1-2000)
stop_frequency = time_and_sounder_settings[36:41].decode("utf-8")			# string (01000-25000)
DPS_fine_frequency_step = time_and_sounder_settings[41:45].decode("utf-8")		# string (0000-9999)
multiplexing_disabled = int(time_and_sounder_settings[45:46])				# int (0,1) -> 0=enabled, 1=disabled
number_of_DPS_small_steps_in_a_scan = time_and_sounder_settings[46:47].decode("utf-8")	# string (1-F)
DPS_phase_code = time_and_sounder_settings[47:48].decode("utf-8")			# string (1-4, 9-C)
alternative_antenna_setup = int(time_and_sounder_settings[48:49])			# int (0,1) -> 0=standard, 1=alternative
DPS_antenna_options = time_and_sounder_settings[49:50].decode("utf-8")			# string (0 to F)
total_FFT_samples = int(time_and_sounder_settings[50:51])				# int (3-7)
DPS_radio_silent_mode = int(time_and_sounder_settings[51:52])				# int (0,1) -> 1=no transmission
pulse_repetition_rate = int(time_and_sounder_settings[52:55])				# int (0-999)
range_start = int(time_and_sounder_settings[55:59])					# int (0-9999)
DPS_range_increment = time_and_sounder_settings[59:60].decode("utf-8")			# string (2,5,A) - 2=2.5km, 5=5km, A=10km
number_of_ranges = int(time_and_sounder_settings[60:64])				# int (1-9999)
scan_delay = int(time_and_sounder_settings[64:68])					# int (0-1500) (15km units)
DPS_base_gain = time_and_sounder_settings[68:69].decode("utf-8")			# string (0-F, encoded)
DPS_frequency_search_enabled = int(time_and_sounder_settings[69:70])			# int (0,1)
DPS_operation_mode = int(time_and_sounder_settings[70:71])				# int (0-7), 0=vertical beam, 5=multi-beam
ARTIST_enabled = int(time_and_sounder_settings[71:72])					# int (0,1)
DPS_data_format = int(time_and_sounder_settings[72:73])					# int (0-6), 1=MMM, 4=RSF, 5=SBF
printer_selection = int(time_and_sounder_settings[73:74])				# int (0,1,2), 0=no printer, 1=b/w, 2=color
ionogram_thresholded_for_FTP_transfer = int(time_and_sounder_settings[74:76])		# int (0-20, encoded)
high_interference_condition = int(time_and_sounder_settings[76:77])			# int (0,1)

if int(num_elements[2]) != 0:
   crdummy = f.read(2)

#---------------------------------------------
# GROUP 4: Scaled Ionospheric Characteristics 
#---------------------------------------------

scaled_ionospheric_characteristics = np.zeros(int(num_elements[3]))
for i in range(int(num_elements[3])):
   if (i != 0) and ((i % 15) == 0):
      crdummy = f.read(2)
   scaled_ionospheric_characteristics[i] = f.read(8)

if int(num_elements[3]) != 0:
   crdummy = f.read(2)

#-------------------------
# GROUP 5: Analysis flags 
#-------------------------

analysis_flags = np.zeros(int(num_elements[4]))
for i in range(int(num_elements[4])):
   analysis_flags[i] = f.read(2)

if int(num_elements[4]) != 0:
   crdummy = f.read(2)

#------------------------------------
# GROUP 6: Doppler translation table 
#------------------------------------

doppler_translation_table = np.zeros(int(num_elements[5]))
for i in range(int(num_elements[5])):
   doppler_translation_table[i] = f.read(7)

if int(num_elements[5]) != 0:
   crdummy = f.read(2)

#------------------------------------------------------
# GROUP 7: O-Trace points - f2 layer - Virtual heights
#------------------------------------------------------

o_f2_virt_heights = np.zeros(int(num_elements[6]))
for i in range(int(num_elements[6])):
   if (i != 0) and ((i % 15) == 0):
      crdummy = f.read(2)
   o_f2_virt_heights[i] = f.read(8)

if int(num_elements[6]) != 0:
   crdummy = f.read(2)

#---------------------------------------------------
# GROUP 8: O-Trace points - f2 layer - True heights
#---------------------------------------------------

o_f2_true_heights = np.zeros(int(num_elements[7]))
for i in range(int(num_elements[7])):
   if (i != 0) and ((i % 15) == 0):
      crdummy = f.read(2)
   o_f2_true_heights[i] = f.read(8)

if int(num_elements[7]) != 0:
   crdummy = f.read(2)

#-------------------------------------------------
# GROUP 9: O-Trace points - f2 layer - Amplitudes
#-------------------------------------------------

o_f2_amplitudes = np.zeros(int(num_elements[8]))
for i in range(int(num_elements[8])):
   if (i != 0) and ((i % 40) == 0):
      crdummy = f.read(2)
   o_f2_amplitudes[i] = f.read(3)

if int(num_elements[8]) != 0:
   crdummy = f.read(2)

#-------------------------------------------------------
# GROUP 10: O-Trace points - f2 layer - Doppler numbers
#-------------------------------------------------------

o_f2_doppler_numbers = np.zeros(int(num_elements[9]))
for i in range(int(num_elements[9])):
   if (i != 0) and ((i % 120) == 0):
      crdummy = f.read(2)
   o_f2_doppler_numbers[i] = f.read(1)

if int(num_elements[9]) != 0:
   crdummy = f.read(2)

#--------------------------------------------
# GROUP 11: O-Trace - f2 layer - Frequencies
#--------------------------------------------

o_f2_frequencies =  np.zeros(int(num_elements[10]))
for i in range(int(num_elements[10])):
   if (i != 0) and ((i % 15) == 0):
      crdummy = f.read(2)
   o_f2_frequencies[i] = f.read(8)

if int(num_elements[10]) != 0:
   crdummy = f.read(2)

#-------------------------------------------------------
# GROUP 12: O-Trace points - f1 layer - Virtual heights
#-------------------------------------------------------

o_f1_virt_heights = np.zeros(int(num_elements[11]))
for i in range(int(num_elements[11])):
   if (i != 0) and ((i % 15) == 0):
      crdummy = f.read(2)
   o_f1_virt_heights[i] = f.read(8)

if int(num_elements[11]) != 0:
   crdummy = f.read(2)

#----------------------------------------------------
# GROUP 13: O-Trace points - f1 layer - True heights
#----------------------------------------------------

o_f1_true_heights = np.zeros(int(num_elements[12]))
for i in range(int(num_elements[12])):
   if (i != 0) and ((i % 15) == 0):
      crdummy = f.read(2)
   o_f1_true_heights[i] = f.read(8)

if int(num_elements[12]) != 0:
   crdummy = f.read(2)

#--------------------------------------------------
# GROUP 14: O-Trace points - f1 layer - Amplitudes
#--------------------------------------------------

o_f1_amplitudes = np.zeros(int(num_elements[13]))
for i in range(int(num_elements[13])):
   if (i != 0) and ((i % 40) == 0):
      crdummy = f.read(2)
   o_f1_amplitudes[i] = f.read(3)

if int(num_elements[13]) != 0:
   crdummy = f.read(2)

#-------------------------------------------------------
# GROUP 15: O-Trace points - f1 layer - Doppler numbers
#-------------------------------------------------------

o_f1_doppler_numbers = np.zeros(int(num_elements[14]))
for i in range(int(num_elements[14])):
   if (i != 0) and ((i % 120) == 0):
      crdummy = f.read(2)
   o_f1_doppler_numbers[i] = f.read(1)

if int(num_elements[14]) != 0:
   crdummy = f.read(2)

#--------------------------------------------
# GROUP 16: O-Trace - f1 layer - Frequencies
#--------------------------------------------

o_f1_frequencies =  np.zeros(int(num_elements[15]))
for i in range(int(num_elements[15])):
   if (i != 0) and ((i % 15) == 0):
      crdummy = f.read(2)
   o_f1_frequencies[i] = f.read(8)

if int(num_elements[15]) != 0:
   crdummy = f.read(2)

#------------------------------------------------------
# GROUP 17: O-Trace points - E layer - Virtual heights
#------------------------------------------------------

o_e_virt_heights = np.zeros(int(num_elements[16]))
for i in range(int(num_elements[16])):
   if (i != 0) and ((i % 15) == 0):
      crdummy = f.read(2)
   o_e_virt_heights[i] = f.read(8)

if int(num_elements[16]) != 0:
   crdummy = f.read(2)

#---------------------------------------------------
# GROUP 18: O-Trace points - E layer - True heights
#---------------------------------------------------

o_e_true_heights = np.zeros(int(num_elements[17]))
for i in range(int(num_elements[17])):
   if (i != 0) and ((i % 15) == 0):
      crdummy = f.read(2)
   o_e_true_heights[i] = f.read(8)

if int(num_elements[17]) != 0:
   crdummy = f.read(2)

#-------------------------------------------------
# GROUP 19: O-Trace points - E layer - Amplitudes
#-------------------------------------------------

o_e_amplitudes = np.zeros(int(num_elements[18]))
for i in range(int(num_elements[18])):
   if (i != 0) and ((i % 40) == 0):
      crdummy = f.read(2)
   o_e_amplitudes[i] = f.read(3)

if int(num_elements[18]) != 0:
   crdummy = f.read(2)

#------------------------------------------------------
# GROUP 20: O-Trace points - E layer - Doppler numbers
#------------------------------------------------------

o_e_doppler_numbers = np.zeros(int(num_elements[19]))
for i in range(int(num_elements[19])):
   if (i != 0) and ((i % 120) == 0):
      crdummy = f.read(2)
   o_e_doppler_numbers[i] = f.read(1)

if int(num_elements[19]) != 0:
   crdummy = f.read(2)

#--------------------------------------------------
# GROUP 21: O-Trace points - E layer - Frequencies
#--------------------------------------------------

o_e_frequencies =  np.zeros(int(num_elements[20]))
for i in range(int(num_elements[20])):
   if (i != 0) and ((i % 15) == 0):
      crdummy = f.read(2)
   o_e_frequencies[i] = f.read(8)

if int(num_elements[20]) != 0:
   crdummy = f.read(2)

#-------------------------------------------------------
# GROUP 22: X-Trace points - f2 layer - Virtual heights
#-------------------------------------------------------

x_f2_virt_heights = np.zeros(int(num_elements[21]))
for i in range(int(num_elements[21])):
   if (i != 0) and ((i % 15) == 0):
      crdummy = f.read(2)
   x_f2_virt_heights[i] = f.read(8)

if int(num_elements[21]) != 0:
   crdummy = f.read(2)

#--------------------------------------------------
# GROUP 23: X-Trace points - f2 layer - Amplitudes
#--------------------------------------------------

x_f2_amplitudes = np.zeros(int(num_elements[22]))
for i in range(int(num_elements[22])):
   if (i != 0) and ((i % 40) == 0):
      crdummy = f.read(2)
   x_f2_amplitudes[i] = f.read(3)

if int(num_elements[22]) != 0:
   crdummy = f.read(2)

#-------------------------------------------------------
# GROUP 24: X-Trace points - f2 layer - Doppler numbers
#-------------------------------------------------------

x_f2_doppler_numbers = np.zeros(int(num_elements[23]))
for i in range(int(num_elements[23])):
   if (i != 0) and ((i % 120) == 0):
      crdummy = f.read(2)
   x_f2_doppler_numbers[i] = f.read(1)

if int(num_elements[23]) != 0:
   crdummy = f.read(2)

#--------------------------------------------
# GROUP 25: X-Trace - f2 layer - Frequencies
#--------------------------------------------

x_f2_frequencies =  np.zeros(int(num_elements[24]))
for i in range(int(num_elements[24])):
   if (i != 0) and ((i % 15) == 0):
      crdummy = f.read(2)
   x_f2_frequencies[i] = f.read(8)

if int(num_elements[24]) != 0:
   crdummy = f.read(2)

#-------------------------------------------------------
# GROUP 26: X-Trace points - f1 layer - Virtual heights
#-------------------------------------------------------

x_f1_virt_heights = np.zeros(int(num_elements[25]))
for i in range(int(num_elements[25])):
   if (i != 0) and ((i % 15) == 0):
      crdummy = f.read(2)
   x_f1_virt_heights[i] = f.read(8)

if int(num_elements[25]) != 0:
   crdummy = f.read(2)

#--------------------------------------------------
# GROUP 27: X-Trace points - f1 layer - dmplitutes
#--------------------------------------------------

x_f1_amplitudes = np.zeros(int(num_elements[26]))
for i in range(int(num_elements[26])):
   if (i != 0) and ((i % 40) == 0):
      crdummy = f.read(2)
   x_f1_amplitudes[i] = f.read(3)

if int(num_elements[26]) != 0:
   crdummy = f.read(2)

#-------------------------------------------------------
# GROUP 28: X-Trace points - f1 layer - Doppler numbers
#-------------------------------------------------------

x_f1_doppler_numbers = np.zeros(int(num_elements[27]))
for i in range(int(num_elements[27])):
   if (i != 0) and ((i % 120) == 0):
      crdummy = f.read(2)
   x_f1_doppler_numbers[i] = f.read(1)

if int(num_elements[27]) != 0:
   crdummy = f.read(2)

#---------------------------------------------------
# GROUP 29: X-Trace points - f1 layer - Frequencies
#---------------------------------------------------

x_f1_frequencies =  np.zeros(int(num_elements[28]))
for i in range(int(num_elements[28])):
   if (i != 0) and ((i % 15) == 0):
      crdummy = f.read(2)
   x_f1_frequencies[i] = f.read(8)

if int(num_elements[28]) != 0:
   crdummy = f.read(2)

#------------------------------------------------------
# GROUP 30: X-Trace points - E layer - Virtual heights
#------------------------------------------------------

x_e_virt_heights = np.zeros(int(num_elements[29]))
for i in range(int(num_elements[29])):
   if (i != 0) and ((i % 15) == 0):
      crdummy = f.read(2)
   x_e_virt_heights[i] = f.read(8)

if int(num_elements[29]) != 0:
   crdummy = f.read(2)

#-------------------------------------------------
# GROUP 31: X-Trace points - E layer - Amplitudes
#-------------------------------------------------

x_e_amplitudes = np.zeros(int(num_elements[30]))
for i in range(int(num_elements[30])):
   if (i != 0) and ((i % 40) == 0):
      crdummy = f.read(2)
   x_e_amplitudes[i] = f.read(3)

if int(num_elements[30]) != 0:
   crdummy = f.read(2)

#------------------------------------------------------
# GROUP 32: X-Trace points - E layer - Doppler numbers
#------------------------------------------------------

x_e_doppler_numbers = np.zeros(int(num_elements[31]))
for i in range(int(num_elements[31])):
   if (i != 0) and ((i % 120) == 0):
      crdummy = f.read(2)
   x_e_doppler_numbers[i] = f.read(1)

if int(num_elements[31]) != 0:
   crdummy = f.read(2)

#--------------------------------------------------
# GROUP 33: X-Trace points - E layer - Frequencies
#--------------------------------------------------

x_e_frequencies =  np.zeros(int(num_elements[32]))
for i in range(int(num_elements[32])):
   if (i != 0) and ((i % 15) == 0):
      crdummy = f.read(2)
   x_e_frequencies[i] = f.read(8)

if int(num_elements[32]) != 0:
   crdummy = f.read(2)

#-----------------------------------------
# GROUP 34: Median amplitudes of F echoes
#-----------------------------------------

median_amplitudes_f_echoes = np.zeros(int(num_elements[33]))
for i in range(int(num_elements[33])):
   if (i != 0) and ((i % 40) == 0):
      crdummy = f.read(2)
   median_amplitudes_f_echoes[i] = f.read(3)   

if int(num_elements[33]) != 0:
   crdummy = f.read(2)

#-----------------------------------------
# GROUP 35: Median amplitudes of E echoes
#-----------------------------------------

median_amplitudes_e_echoes = np.zeros(int(num_elements[34]))
for i in range(int(num_elements[34])):
   if (i != 0) and ((i % 40) == 0):
      crdummy = f.read(2)
   median_amplitudes_e_echoes[i] = f.read(3)   

if int(num_elements[34]) != 0:
   crdummy = f.read(2)

#------------------------------------------
# GROUP 36: Median amplitudes of ES echoes
#------------------------------------------

median_amplitudes_es_echoes = np.zeros(int(num_elements[35]))
for i in range(int(num_elements[35])):
   if (i != 0) and ((i % 40) == 0):
      crdummy = f.read(2)
   median_amplitudes_es_echoes[i] = f.read(3)   

if int(num_elements[35]) != 0:
   crdummy = f.read(2)

#------------------------------------------------------------
# GROUP 37: True heights coefficients f2 layer Umlcar method
#------------------------------------------------------------

true_heights_coeff_f2_layer = np.zeros(int(num_elements[36]))
for i in range(int(num_elements[36])):
   if (i != 0) and ((i % 11) == 0):
      crdummy = f.read(2)
   true_heights_coeff_f2_layer[i] = f.read(11)

if int(num_elements[36]) != 0:
   crdummy = f.read(2)

#------------------------------------------------------------
# GROUP 38: True heights coefficients f1 layer Umlcar method
#------------------------------------------------------------

true_heights_coeff_f1_layer = np.zeros(int(num_elements[37]))
for i in range(int(num_elements[37])):
   if (i != 0) and ((i % 11) == 0):
      crdummy = f.read(2)
   true_heights_coeff_f1_layer[i] = f.read(11)

if int(num_elements[37]) != 0:
   crdummy = f.read(2)

#-----------------------------------------------------------
# GROUP 39: True heights coefficients E layer Umlcar method
#-----------------------------------------------------------

true_heights_coeff_e_layer = np.zeros(int(num_elements[38]))
for i in range(int(num_elements[38])):
   if (i != 0) and ((i % 11) == 0):
      crdummy = f.read(2)
   true_heights_coeff_e_layer[i] = f.read(11)

if int(num_elements[38]) != 0:
   crdummy = f.read(2)

#----------------------------------------------------------
# GROUP 40: Quazi-Parabolic segments fitted to the profile
#----------------------------------------------------------

quazi_parabolic_segments = np.zeros(int(num_elements[39]))
for i in range(int(num_elements[39])):
   if (i != 0) and ((i % 6) == 0):
      crdummy = f.read(2)
   quazi_parabolic_segments[i] = f.read(20)

if int(num_elements[39]) != 0:
   crdummy = f.read(2)

#--------------------------------------
# GROUP 41: Edit flags characteristics 
#--------------------------------------

edit_flags = np.zeros(int(num_elements[40]))
for i in range(int(num_elements[40])):
   if (i != 0) and ((i % 120) == 0):
      crdummy = f.read(2)
   edit_flags[i] = f.read(1)

if int(num_elements[40]) != 0:
   crdummy = f.read(2)

#------------------------------
# GROUP 42: Valley description
#------------------------------

valley_description = np.zeros(int(num_elements[41]))
for i in range(int(num_elements[41])):
   if (i != 0) and ((i % 11) == 0):
      crdummy = f.read(2)
   valley_description[i] = f.read(11)

if int(num_elements[41]) != 0:
   crdummy = f.read(2)

#-------------------------------------------------------
# GROUP 43: O-Trace points - Es layer - Virtual heights
#-------------------------------------------------------

o_es_virt_heights = np.zeros(int(num_elements[42]))
for i in range(int(num_elements[42])):
   if (i != 0) and ((i % 15) == 0):
      crdummy = f.read(2)
   o_es_virt_heights[i] = f.read(8)

if int(num_elements[42]) != 0:
   crdummy = f.read(2)

#--------------------------------------------------
# GROUP 44: O-Trace points - Es layer - Amplitudes
#--------------------------------------------------

o_es_amplitudes = np.zeros(int(num_elements[43]))
for i in range(int(num_elements[43])):
   if (i != 0) and ((i % 40) == 0):
      crdummy = f.read(2)
   o_es_amplitudes[i] = f.read(3)

if int(num_elements[43]) != 0:
   crdummy = f.read(2)

#-------------------------------------------------------
# GROUP 45: O-Trace points - Es layer - Doppler numbers
#-------------------------------------------------------

o_es_doppler_numbers = np.zeros(int(num_elements[44]))
for i in range(int(num_elements[44])):
   if (i != 0) and ((i % 120) == 0):
      crdummy = f.read(2)
   o_es_doppler_numbers[i] = f.read(1)

if int(num_elements[44]) != 0:
   crdummy = f.read(2)

#---------------------------------------------------
# GROUP 46: O-Trace points - Es layer - Frequencies
#---------------------------------------------------

o_es_frequencies =  np.zeros(int(num_elements[45]))
for i in range(int(num_elements[45])):
   if (i != 0) and ((i % 15) == 0):
      crdummy = f.read(2)
   o_es_frequencies[i] = f.read(8)

if int(num_elements[45]) != 0:
   crdummy = f.read(2)

#--------------------------------------------------------------
# GROUP 47: O-Trace points - E Auroral layer - Virtual heights
#--------------------------------------------------------------

o_ea_virt_heights = np.zeros(int(num_elements[46]))
for i in range(int(num_elements[46])):
   if (i != 0) and ((i % 15) == 0):
      crdummy = f.read(2)
   o_ea_virt_heights[i] = f.read(8)

if int(num_elements[46]) != 0:
   crdummy = f.read(2)

#--------------------------------------------------
# GROUP 48: O-Trace points - Es layer - Amplitudes
#--------------------------------------------------

o_ea_amplitudes = np.zeros(int(num_elements[47]))
for i in range(int(num_elements[47])):
   if (i != 0) and ((i % 40) == 0):
      crdummy = f.read(2)
   o_ea_amplitudes[i] = f.read(3)

if int(num_elements[47]) != 0:
   crdummy = f.read(2)

#-------------------------------------------------------
# GROUP 49: O-Trace points - Es layer - Doppler numbers
#-------------------------------------------------------

o_ea_doppler_numbers = np.zeros(int(num_elements[48]))
for i in range(int(num_elements[48])):
   if (i != 0) and ((i % 120) == 0):
      crdummy = f.read(2)
   o_ea_doppler_numbers[i] = f.read(1)

if int(num_elements[48]) != 0:
   crdummy = f.read(2)

#---------------------------------------------------
# GROUP 50: O-Trace points - Es layer - Frequencies
#---------------------------------------------------

o_ea_frequencies =  np.zeros(int(num_elements[49]))
for i in range(int(num_elements[49])):
   if (i != 0) and ((i % 15) == 0):
      crdummy = f.read(2)
   o_ea_frequencies[i] = f.read(8)

if int(num_elements[49]) != 0:
   crdummy = f.read(2)

#--------------------------------
# GROUP 51: True height profiles
#--------------------------------

true_heights = np.zeros(int(num_elements[50]))
for i in range(int(num_elements[50])):
   if (i != 0) and ((i % 15) == 0):
      crdummy = f.read(2)
   true_heights[i] = f.read(8)

if int(num_elements[50]) != 0:
   crdummy = f.read(2)

#------------------------------
# GROUP 52: Plasma Frequencies
#------------------------------

plasma_frequencies = np.zeros(int(num_elements[51]))
for i in range(int(num_elements[51])):
   if (i != 0) and ((i % 15) == 0):
      crdummy = f.read(2)
   plasma_frequencies[i] = f.read(8)

if int(num_elements[51]) != 0:
   crdummy = f.read(2)

#------------------------------
# GROUP 53: Electron densities
#------------------------------

electron_density = np.zeros(int(num_elements[52]))
for i in range(int(num_elements[52])):
   if (i != 0) and ((i % 15) == 0):
      crdummy = f.read(2)
   electron_density[i] = f.read(8)

if int(num_elements[52]) != 0:
   crdummy = f.read(2)

#-----------------------------------
# GROUP 54: URSI Qualifying letters
#-----------------------------------

#------------------------------------
# GROUP 55: URSI Descriptive letters
#------------------------------------

#------------------------------------------------
# GROUP 56: URSI Edit flags - traces and profile
#------------------------------------------------

#-------------------------------------------------------------------------------------------
# GROUP 57: Auroral E_Layer Profile Data - True heights coefficients Ea Layer Umclar method
#-------------------------------------------------------------------------------------------

#-------------------------------------------------------
# GROUP 58: Auroral E_Layer Profile Data - True Heights
#-------------------------------------------------------

#-------------------------------------------------------------
# GROUP 59: Auroral E_Layer Profile Data - Plasma Frequencies
#-------------------------------------------------------------

#-------------------------------------------------------------
# GROUP 60: Auroral E_Layer Profile Data - Electron Densities
#-------------------------------------------------------------

f.close()

# plotting

#title = 'Ionogram - ' + ascii_datetime[1:21] + ' UTC'
title = 'Ionosonde TOS ' + str(datetime.datetime(year, month, day_of_month, hour, min, sec))

fig, ax = plt.subplots()
#plt.scatter(o_f2_frequencies, o_f2_virt_heights, s=1, c="blue", label='O-F2')
#plt.scatter(o_f1_frequencies, o_f1_virt_heights, s=1, c="green", label='O-F1')
#plt.scatter(o_e_frequencies, o_e_virt_heights, s=1, c="red", label='O-E')
#plt.scatter(x_f2_frequencies, x_f2_virt_heights, s=1, c="cyan", label='X-F2')
#plt.scatter(x_f1_frequencies, x_f1_virt_heights, s=1, c="magenta", label='X-F1')
#plt.scatter(x_e_frequencies, x_e_virt_heights, s=1, c="yellow", label='X-E')
#plt.scatter(o_es_frequencies, o_es_virt_heights, s=1, c="black", label='O-Es')
#plt.scatter(o_ea_frequencies, o_ea_virt_heights, s=1, c="#005030", label='O-E Aur')
plt.plot(o_f2_frequencies, o_f2_virt_heights, c="blue", label='O-Trace Points - F2 Layer')
plt.plot(o_f1_frequencies, o_f1_virt_heights, c="green", label='O-Trace Points - F1 Layer')
plt.plot(o_e_frequencies, o_e_virt_heights, c="red", label='O-Trace Points - E Layer')
plt.plot(x_f2_frequencies, x_f2_virt_heights, c="cyan", label='X-Trace Points - F2 Layer')
plt.plot(x_f1_frequencies, x_f1_virt_heights, c="magenta", label='X-Trace Points - F1 Layer')
plt.plot(x_e_frequencies, x_e_virt_heights, c="yellow", label='X-Trace Points - E Layer')
plt.plot(o_es_frequencies, o_es_virt_heights, c="black", label='O-Trace Points - Es Layer')
plt.plot(o_ea_frequencies, o_ea_virt_heights, c="#005030", label='O-Trace Points - E Auroral Layer')
plt.plot(plasma_frequencies, true_heights, label='True')

plt.legend(loc='upper right')
ax.grid(True, which='both')

ax.set_xlim(1,16)                  # set X limits (min and max frequency in MHz)
ax.set_ylim(80,640)                 # set Y limits (min and max height in km)
ax.set_title(title) 
ax.set_xlabel('Frequency (Mhz)') 
ax.set_ylabel('Virtual height (km)') 

# toggle output to file, comment/uncomment these lines 
# if you don't want output to file: usage: python readsao.py inputfile

savefilename = sys.argv[2]
fig.savefig(savefilename)

# toggle output to screen, comment/uncomment the next line (note you can have both!)
plt.show()
