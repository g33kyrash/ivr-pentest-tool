from ivr_main import *
import time,sys,re
from xml.dom import minidom
from xml.dom.minidom import parse
import xml.dom.minidom
import xml.etree.cElementTree as ET
import datetime
import os.path
from tabulate import tabulate


#store the wait_time and dtmf as key,value pairs
data_dtmf = {}

filepath = 'ivr.xml'

#list will store the ongoing call details so that any function can access the ongoing call details.
global_call_values = []
	
def save_process():
	ch = ''
	if len(data_dtmf.keys()) > 0:
		print "\n[+] Disconnecting the Call if connected!"
		silent_hang_up()
		print "\nDo you want to save this call flow(y/n): "
		ch = sys.stdin.readline()
		ch = ch.strip('\n')
		if ch == 'y':
			desc = global_call_values[1]
			tel = global_call_values[2]
			save_recorded_flow(data_dtmf,desc,tel)
			#empty the data_dtmf dictionary and the call values list for the next call
			data_dtmf.clear()
			del global_call_values[:]
			ser.close()
			print "[+] Exiting the program.\n"
			sys.exit(0)

		elif ch == 'n':
			print "\n[+] Call flow not saved."
			data_dtmf.clear()
			del global_call_values[:]
			ser.close()
			print "[+] Exiting the program.\n"
			sys.exit(0)
	else:
		print "\n[+] Disconnecting the Call if connected!"
		silent_hang_up()
		ser.close()
		print "[+] Call flow not saved!\n"


def sig_handler(signum, frm):
	#give a random value to the previous raw_input so that the next raw_input works fine.
	# s = StringIO.StringIO("Ne048")
	# sys.stdin = s
	save_process()
	quit()

signal.signal(signal.SIGINT, sig_handler)


def record_new_call_flow():
	print "\nChecking modem Network connection"
	execute('AT')
	tel = raw_input("\nEnter the phone number to dial: ")
	cmd_no = 'ATD'+ tel +';'
	desc = raw_input("enter the description of the recording: ")
	print "\n[+] Calling the Phone number."

	#start time stores the time when the call gets recieved at the other end
	start_time = call_no(cmd_no)
	global_call_values.append(start_time)
	global_call_values.append(desc)
	global_call_values.append(tel)


#Enter dtmf while in the middle of a call
def enter_dtmf():
	start_time = float(global_call_values[0])
	try:
		input("Press enter to continue when the IVR is ready to accept the DTMF. . .")
	except SyntaxError:
	    pass

	dtmf_value = ''    
	def dtmf_value_func():
		pattern = "[^0-9#*]+"
		value = raw_input("Enter DTMF value: ")
		if re.findall(pattern, value):
			print "[+] Error: Only 0-9,* and # are allowed as DTMF values"
			return dtmf_value_func()
		elif value == '':
			print "[+] Error: Only 0-9,* and # are allowed as DTMF values"
			return dtmf_value_func()
		else:
			return value

	dtmf_value = dtmf_value_func()
	
	if len(data_dtmf) >= 1:
		previous_start_time= sum(data_dtmf.keys())
		elapsed_time = time.time() - start_time
		elapsed = elapsed_time - previous_start_time
		

	elif len(data_dtmf) == 0:
		elapsed = time.time() - start_time

	data_dtmf[elapsed] = dtmf_value
	return_code = dtmf(dtmf_value)
	if return_code == "CME ERROR: 3":
		choice = raw_input("Do you want to save this call flow(y/n): ")
		if choice == 'y':
			save_process()
			hang_up()
		elif choice == 'n':
			print "[+] Exiting the program\n"
			sys.exit(0)


def open_xml_db():
  # Open XML document using minidom parser and return all the calls
  # with open(filepath) as f:
  #    str = "<root>" + f.read() + "</root>"
  DOMTree = xml.dom.minidom.parse(filepath)
  root = DOMTree.documentElement

  calls = root.getElementsByTagName("call")
  return calls

#print all the recorded call details
def view_recorded_call_flows():

  if os.path.isfile(filepath) == False:
  	print "\n[+] Error: No call flows saved yet.\n"
  	start_menu()

  print "\n[+] Recorded call flows are: \n"
  calls = open_xml_db()
  total_data = []
  k=1
  for call in calls:
     call_id = call.getAttribute("id")
     description = call.getAttribute("description")
     tel = call.getAttribute("tel")
     date_time = call.getElementsByTagName('save_time')[0]
     save_time = date_time.childNodes[0].data
     flow = call.getElementsByTagName("flow")[0]
     flow_id = flow.getAttribute("id")
     flow_desc = flow.getAttribute("description")
     actions = flow.getElementsByTagName("action")

     list_data = []
     list_data.extend([k,tel, description, call_id, save_time])
     total_data.append(list_data)
     k+=1

  print tabulate(total_data, tablefmt="fancy_grid", numalign="left", headers=["Serial","Tel", "Description", "Call Id", "Saved time"])


#delete a node with a particular call id and rewrite the whole xml document
def remove_recorded_call():

	call_id_entered = raw_input("\nEnter the call Id You want to delete (or press Enter to go back): ")
    #go to start menu if pressed enter
	if call_id_entered == '':
		start_menu()

	DOMTree = xml.dom.minidom.parse(filepath)
	root = DOMTree.documentElement

	calls = root.getElementsByTagName("call")
	flag = 0
	
	for call in calls:
		call_id = call.getAttribute("id")
		if call_id_entered == call_id:
			DOMTree.documentElement.removeChild(call)
			flag = 1
			break
		

	if flag == 0:
		print "\nCall Id not found in the database! Try again"
		remove_recorded_call()

	s = root.toxml()

	#remove more than 3 newlines with double newlines.
	xmlstr = re.sub(r'\n{3,}', '\n\n', s)
	xmlstr = "<?xml version='1.0' ?>\n" + xmlstr
	with open(filepath, "w") as f:
	    f.write(xmlstr)

	print "\n[+] Call flow successfully deleted from database with call index: %s\n" %call_id_entered
  	start_menu()

#get the last call index from the xml db to maintain call id no. in a increasing way
def get_last_call_index_fromDb():
  calls = open_xml_db()
  call = calls[-1]
  last_call_index = call.getAttribute("id")
  return last_call_index


#save the recorded call flow when cntrl+c is pressed
def save_recorded_flow(data_dtmf,desc,tel):

	#when the script runs for the first time, the index would start from 100
	if os.path.isfile(filepath):
		call_index = str(int(get_last_call_index_fromDb()) + 1)
	else:
		call_index = "100"
	i = datetime.datetime.now()
	date_time = str(i).split(".")[0]

	call = ET.Element("call", id=call_index, description=desc, tel=tel)
	save_time = ET.SubElement(call, "save_time").text = date_time
	flow = ET.SubElement(call, "flow", id="foo", description="bar")

	k=0
	for wait_time,dtmf_value in data_dtmf.items():
		ET.SubElement(flow, "action", seq=str(k), type="Wait").text = str(wait_time)
		ET.SubElement(flow, "action", seq=str(k), type="Dtmf").text = str(dtmf_value)
		k+=1

	xmlstr = minidom.parseString(ET.tostring(call)).toprettyxml(indent="   ")
	xmlstr = xmlstr.replace('<?xml version="1.0" ?>', '')


	#if xml file exists, read all the contents, add a node in the Document tree and overwrite the file to save it.
	if os.path.isfile(filepath):
	  DOMTree = xml.dom.minidom.parse(filepath)
	  root = DOMTree.documentElement
	  calls = root.getElementsByTagName("call")
	  
	  #read all the previous saved call flow records and append that with new one
	  calls_str = ''
	  for call in calls:
	    calls_str+="\n"+call.toxml()+"\n"

	  calls_str = calls_str + xmlstr
	  xmlstr1 = "<?xml version='1.0' ?>\n<root>\n" + calls_str + "\n\n</root>" 
	  with open(filepath, "w") as f:
	    f.write(xmlstr1)    

	#if xml file does not exist create one with the root tag
	elif os.path.isfile(filepath) == False:
	  xmlstr1 = "<?xml version='1.0' ?>\n<root>\n" + xmlstr + "\n\n</root>" 
	  with open(filepath, "w") as f:
	    f.write(xmlstr1)    

  
	print "\n[+] Call flow successfully saved in database with call index: %s\n" %call_index
  


#get dtmf and wait time values from db for a particular call
def get_wait_dtmf_values(id):
  k=0
  calls = open_xml_db()
  
  for call in calls:
    call_id = call.getAttribute("id")
    if call_id == id:
      k=1
      description = call.getAttribute("description")
      tel = call.getAttribute("tel")
      date_time = call.getElementsByTagName('save_time')[0]
      save_time = date_time.childNodes[0].data
      flow = call.getElementsByTagName("flow")[0]
      actions = flow.getElementsByTagName("action")
      dtmf = []
      wait = []
      wait_dtmf = []
      for action in actions:
        type = action.getAttribute("type")
        if type == "Wait":
          wait.append(action.childNodes[0].data)
        elif type == "Dtmf":
          dtmf.append(action.childNodes[0].data)
      
      wait_dtmf.append(tel)
      wait_dtmf.append(description)
      wait_dtmf.extend([wait,dtmf])
      return wait_dtmf

  if (k==0):
    print "\nCall Id not found in the database! Try again"
    call_replay()


def call_replay():
  id = raw_input("\nEnter the call Id you want to replay (or press Enter to go back): ")
  #go to start menu if pressed enter
  if id == '':
  	start_menu()
  
  wait_dtmf = get_wait_dtmf_values(id)
  tel = str(wait_dtmf[0])
  desc = str(wait_dtmf[1])
  wait_values = wait_dtmf[2]
  dtmf_values = wait_dtmf[3]

  print "Replaying call for. . . \n\n[+] Tel: %s \n[+] Call description: %s \n[+] Call Id: %s\n\n"%(tel,desc,id)
  cmd_no = 'ATD'+ tel +';'
  start_time = call_no(cmd_no)
  for i in range(0,len(wait_values)):
	print "\nwaiting for %s seconds. . " %str(wait_values[i])
	time.sleep(float(wait_values[i]))
	print "Sending %s as DTMF tone. . \n" %str(dtmf_values[i])
	dtmf_tone = (dtmf_values[i])
	return_code = dtmf(dtmf_tone)
	if return_code == "CME ERROR: 3":
		i = raw_input("Do you want to go to the start menu(y/n): ")
		if i=='y':
			silent_hang_up()
			start_menu()
		elif i=='n':
			print "\n[+] Exiting\n"
			ser.close()
			sys.exit(0)

  print "\n[+] Recorded Call flow ends here."
  silent_hang_up()
  print "[+] Disconnected the call.\n"
  start_menu()


def start_menu():

  flag =0

  if (flag == 0):
	  print "\n------- IVR Menu --------"	
	  print "\n1. Record a new call flow."
	  print "2. View and replay recorded call flows."
	  print "3. Remove recorded call flow."
	  print "4. Exit."

  choice = raw_input("\nEnter your choice: ")
  
  if choice == '1': 
    record_new_call_flow()
    while True:
      enter_dtmf()

  elif choice == '2':
    view_recorded_call_flows()
    call_replay()

  elif choice == '3':
  	view_recorded_call_flows()
	remove_recorded_call()
	ser.close()
	quit()
  
  elif choice == '4':
	print "[+] Exiting the program\n"
	ser.close()
	quit()

  else:
	print "\n[+] Wrong Choice entered! Try again\n"
	flag = 1
	s = StringIO.StringIO('3')
	sys.stdin = s
	start_menu()

if __name__ == '__main__':
	print_banner()
	start_menu()
