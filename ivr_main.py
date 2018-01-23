import time
import serial
import signal
import subprocess
import sys

serial_port = '/dev/ttyACM3'

try:
	ser = serial.Serial(port=serial_port)
except serial.serialutil.SerialException: 
	print "\n[+] Could not open serial port on %s. Please recheck the connection.\n" %serial_port
	exit()

if ser.inWaiting() > 0:
    ser.flushInput()

ser.timeout=1
ser.baudrate=115200
ser.write_timeout=1


def print_banner():
	print "\n\t[*]------ IVR Security Assessment tool ------[*]\n"
	print "[+] Serial connection established on %s serial port" %serial_port



#Execution sink for AT commands
def execute(command):
	
	cmd = command + '\r'
	print ">> " + command
	try:
		ser.write(cmd)
	except serial.serialutil.SerialTimeoutException:
		pass
	finally:
		try:
			msg=ser.readlines()
		except serial.serialutil.SerialException:
			print "\n[+] Modem not ready. Try again!\n"
			exit()
		try:
			for response in msg:
				print response.strip()
			return response.strip()
		except UnboundLocalError:
			print "\n[+] Modem not ready. Try again!\n"
			exit()


#does not print output on the screen
def silent_execute(command):
	
	cmd = command + '\r'
	# print ">> " + command
	try:
		ser.write(cmd)
	except serial.serialutil.SerialTimeoutException:
		pass
	finally:
		try:
			msg=ser.readlines()
		except serial.serialutil.SerialException:
			print "\n[+] Modem not ready. Try again!\n"
			exit()
		# try:
		# 	for response in msg:
		# 		print response.strip()
		# 	return response.strip()
		# except UnboundLocalError:
		# 	print "\n[+] Modem not ready. Try again!\n"
		# 	exit()


#Execution sink for dtmf commands
def dtmf(no):
	
	num = str(no)
	for i in range(0,len(num)):
		cmd = 'AT+VTS=' + num[i] + '\r'
		print ">> " + cmd
		try:
			ser.write(cmd)
		except serial.serialutil.SerialTimeoutException:
			pass
		finally:
			msg=ser.readlines()
			for response in msg:
				print response.strip()
			if (response.find("CME ERROR: 3")!=-1):
				print "[+] WARNING: There is an error in sending this DTMF. Check the call connection again!"
				print "[+] ERROR: The Call has probably been disconnected!\n"
				return "CME ERROR: 3"
			elif (response.find("NO CARRIER")!=-1):
				print "[+] WARNING: There is an error in sending this DTMF. Check the call connection again!"
				print "[+] ERROR: The Call has probably been disconnected!\n"
				return "CME ERROR: 3"
			elif (response.find("OK")==-1):
				print "\n[+] WARNING: There is an error in sending this DTMF. \n"


#call a phone no
def call_no(no):
	result = execute(no)
	if (result.find("OK")==-1):
		print "\nWARNING: No proper response from Modem. Call cannot be connected!\n"
		exit()
	else:
		print "\n[+] Waiting for call to connect. . ."
		start_time = check_call_connected_or_not()
		return start_time



def hang_up():
	execute('ATH')
	print "\n[+] Call disconnected."

def silent_hang_up():
	silent_execute('ATH')


def check_call_connected_or_not():
	#AT+CLCC tells the call active status
	cmd = 'AT+CLCC' + '\r'
	while True:
		try:
			ser.write(cmd)
		except serial.serialutil.SerialTimeoutException:
			pass
		finally:
			msg=ser.readlines()
			for response in msg:
				#checks if the call is connected or not
				if (response.find("1,0,0,0,0,")!=-1):
					# print response.strip()
					start_time = time.time()
					print "\n[+] Call is connected\n"
					return start_time

				#if call does not get connected then automatically disconnect the call and exit the program
				elif (response.find("NO CARRIER")!=-1):
					print "[+] ERROR: Call Disconnected!\n"
					print "[+] Exiting.\n"
					sys.exit(0)
				
			




