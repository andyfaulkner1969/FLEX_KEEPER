#!/usr/bin/env python3
import requests
import csv
import json
import logging
import yaml
from pathlib import Path
import os
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sys.tracebacklimit = 0

#  Fortinet FLEX VM utility tool.
#  This tool will allow you to manage your FLEX VMs in the 
#  Fortinet portal.  It allows you to get a list of VMs and 
#  be able to stop and even decomission.
#  
#  
""""
 ________         ____     _ __  ___           __              __
/_  __/ /  ___   / __/  __(_) / / _ )___ ____ / /____ ________/ /
 / / / _ \/ -_) / _/| |/ / / / / _  / _ `(_-</ __/ _ `/ __/ _  /
/_/ /_//_/\__/ /___/|___/_/_/ /____/\_,_/___/\__/\_,_/_/  \_,_/
afaulkner@fortinet.com 
"""
# Opening config file
with open('flex_keeper_config.yml', 'r') as file:
	config = yaml.safe_load(file)

# Getting support portal api user info
api_user = config['env_vars']['user']
api_pass = config['env_vars']['passwd']

client_idf = "flexvm"

log_dir = Path(config['debug_config']['debug_path'])
debug_path = Path(config['debug_config']['debug_path'])
debug_file = Path(debug_path,config['debug_config']['debug_file'] )

# Looking for log directory if not there create
if os.path.isdir(log_dir):
    pass
else:
	print("Missing logs directory...creating it now.")
	os.makedirs(log_dir)

# Setting up debug
def debug_setup():
	logging_flag = config['debug_config']['debug_log_flag']
	if config['debug_config']['debug_flag'] == "DEBUG":
		debug_flag = logging.DEBUG
	if config['debug_config']['debug_flag'] == "INFO":
		debug_flag = logging.INFO
	if config['debug_config']['debug_flag'] == "NOTSET":
		debug_flag = logging.NOTSET
	if logging_flag == "N":
		logging.basicConfig(level=debug_flag,format='%(asctime)s:%(levelname)s:%(message)s')
	if logging_flag == "Y":
		logging.basicConfig(filename=debug_file,level=debug_flag,format='%(asctime)s:%(levelname)s:%(message)s')
	logging.info("***** Start of FLEX KEEPER Script. *****")

print("   ")
print("Welcome to Fortinet FLEXVM keeper.")
print("    ")

def delete_temp_file():
	if os.path.isfile('vmslist.csv'):
		logging.info("Removing previous temp file")
		os.remove('vmslist.csv')
	else:
		pass

def write_to_csv(data):
	csvfile = open ('vmslist.csv','a',encoding='UTF8',newline='')
	writecsv = csv.writer(csvfile)
	writecsv.writerow(data)
	csvfile.close()

def search_vms_list():
	print(" ")
	global token, program_ser
	choices = ["Display list of VMS",
	    "Search for VMS by Hostname",
	    "Search for VMS by Serial Number", 
	    "Regenerate VMS file list",
		"Quit (or q)"]
	direction_choice = {}
	for index, value in enumerate(choices, 1):
		print( "{}. {}".format(index,value))
		direction_choice.update({index:value})

	choice = input("Choose if you dare : ")
	if choice == "q":
		exit()
	if not choice.isdigit():
		print("****** Not a choice ******")
		search_vms_list()
		pass
	if choice.isdigit():
		choice = int(choice)
	if int(choice) in direction_choice:
		index_spot = choice - 1
		x = choices[index_spot]
	if x == "Display list of VMS":
		with open('vmslist.csv', mode ='r')as file:
			csvFile = csv.reader(file)
			print("    ")
			print(f'{"Name": <{20}}{"Serial Number": <{20}}{"Status": <{10}}{"Token Status": <{15}}')
			print("__________________________________________________________________")
			for lines in csvFile:
				print(f'{lines[0]: <{20}}{lines[1]: <{20}}{lines[2]: <{10}}{lines[3]: <{15}}')
			search_vms_list()
	if x == "Search for VMS by Hostname":
			hostname = input("Enter the exact hostname: ")
			with open('vmslist.csv', mode ='r')as file:
				csvFile = csv.reader(file)
				print("    ")
				print(f'{"Name": <{20}}{"Serial Number": <{20}}{"Status": <{10}}{"Token Status": <{15}}')
				print("__________________________________________________________________")
				for lines in csvFile:
					if lines[0] == hostname:
						print(f'{lines[0]: <{20}}{lines[1]: <{20}}{lines[2]: <{10}}{lines[3]: <{15}}')
						if lines[2] == "ACTIVE":
							choice = input(f"Host {lines[0]} with serial number {lines[1]} is ACTIVE, would you like to STOP it? (y/n)")
							if choice.lower() == "y":
								print("Let's go do that")
								stop_active_vms(token,lines[1])
							if choice.lower() == "n":
								print("Doing nothing....skiping...")
								search_vms_list()
							else:
								exit()
						if lines[2] == "STOPPED":
							choice = input(f"Host {lines[0]} with serial number {lines[1]} is STOPPED, would you like to Decomission it? (y/n)")
							if choice.lower() == "y":
								print("Let's go do that....")
								decom_assest(lines[1])
							if choice.lower() == "n":
								print("Doing nothing....skiping...")
								search_vms_list()
							else:
								exit()
						if lines[2] == "PENDING":
							choice = input(f"Host {lines[0]} with serial number {lines[1]} is PENDING, would you like to STOP it? (y/n)")
							if choice.lower() == "y":
								print("Let's go do that")
							if choice.lower() == "n":
								print("Doing nothing......")
								search_vms_list()
							else:
								exit()
					else:
						pass
			print("************************")
			print("Can't find host in list.")
			print("You might want to check your spelling or regenerate the file.")
			search_vms_list()
	if x == "Search for VMS by Serial Number":
			sernumber = input("Enter the exact serial number: ")
			with open('vmslist.csv', mode ='r')as file:
				csvFile = csv.reader(file)
				print("    ")
				print(f'{"Name": <{20}}{"Serial Number": <{20}}{"Status": <{10}}{"Token Status": <{15}}')
				print("__________________________________________________________________")
				for lines in csvFile:
					if lines[1] == sernumber:
						print(f'{lines[0]: <{20}}{lines[1]: <{20}}{lines[2]: <{10}}{lines[3]: <{15}}')
						if lines[2] == "ACTIVE":
							choice = input(f"Host {lines[0]} with serial number {lines[1]} is ACTIVE, would you like to STOP it? (y/n)")
							if choice.lower() == "y":
								print("Let's go do that")
								stop_active_vms(token,lines[1])
							if choice.lower() == "n":
								print("Doing nothing....skiping...")
								search_vms_list()
							else:
								exit()
						if lines[2] == "STOPPED":
							choice = input(f"Host {lines[0]} with serial number {lines[1]} is STOPPED, would you like to Decomission it? (y/n)")
							if choice.lower() == "y":
								print("Let's go do that....")
								decom_assest(lines[1])
							if choice.lower() == "n":
								print("Doing nothing....skiping...")
								search_vms_list()
							else:
								exit()
						if lines[2] == "PENDING":
							choice = input(f"Host {lines[0]} with serial number {lines[1]} is PENDING, would you like to STOP it? (y/n)")
							if choice.lower() == "y":
								print("Let's go do that")
							if choice.lower() == "n":
								print("Doing nothing......")
								search_vms_list()
							else:
								exit()
					else:
						pass
			print("************************")
			print("Can't find serial number in list.")
			print("You might want to check your spelling or regenerate the file.")
			search_vms_list()
	if x == "Regenerate VMS file list":
		delete_temp_file()
		get_flex_config_list(token,program_ser)
		search_vms_list()
	if x == "Quit":
		exit()
		
def gettoken(user, password, client_id):
	logging.info("Getting bearer token from server. ")
	url = "https://customerapiauth.fortinet.com/api/v1/oauth/token/"
	jsondata = {"username":user,
							"password":password,
							"client_id":client_id,
							"grant_type":"password"}
						
	apiheaders =  {"Content-Type":"application/json"}
	
	#get auth token from IAM
	try:
		result = requests.post(url, data=json.dumps(jsondata), headers=apiheaders, timeout=10)
		logging.debug(result)
		token = result.json()['access_token']
		logging.debug("Token from server: " + str(token))
		return token
	# except requests.exceptions.HTTPError as errh:
	# 	logging.info("Http Error:",errh)
	# except requests.exceptions.ConnectionError as errc:
	# 	logging.info("Error Connecting:",errc)
	# except requests.exceptions.Timeout as errt:
	# 	logging.info("Timeout Error:",errt)
	# except requests.exceptions.RequestException as err:
	# 	logging.info("OOps: Something Else",err)
	except (urllib3.exceptions.ReadTimeoutError,
		    requests.ConnectionError,urllib3.connection.ConnectionError,
			urllib3.exceptions.MaxRetryError,urllib3.exceptions.ConnectTimeoutError,
			urllib3.exceptions.TimeoutError,socket.error,socket.timeout) as e:
			print("HERE IS THE ERROR: ", e)

def get_program_id(token):
	logging.info("Getting program ID. ")
	apiheaders =  {"Content-Type":"application/json","Authorization":"Bearer "+token}
	url = "https://support.fortinet.com/ES/api/flexvm/v1/programs/list"
	result = requests.post(url, headers=apiheaders,timeout=10)
	parsed_json = json.loads(result.text)
	program_ser = parsed_json['programs'][0]['serialNumber']
	logging.info("Program ID: " + program_ser)
	return program_ser

def get_flex_config_list(token,program_ser):
	config_list_name = []
	config_list_id = []
	logging.info("Getting flex config IDs. ")
	apiheaders =  {"Content-Type":"application/json","Authorization":"Bearer "+token}
	data = {
		"programSerialNumber": program_ser
		}
	url = "https://support.fortinet.com/ES/api/flexvm/v1/configs/list"

	#try:
	result = requests.post(url, headers=apiheaders, json=data,timeout=10)
	parsed_json = json.loads(result.text)
	logging.debug("RAW json return")
	logging.debug(parsed_json)
	config_count = len(parsed_json['configs'])
	count = 0
	while count < config_count:
		config_id = parsed_json['configs'][count]['id']
		config_list_id.append(config_id)
		config_name = parsed_json['configs'][count]['name']
		config_list_name.append(config_name)
		count = count + 1
	logging.info("Getting config_ids.")
	count_up = 0
	config_id_choice = {}
	print("")
	print(" ***** FLEX KEEPER *****")
	print("")
	for index, value in enumerate(config_list_name, 1):
		print( "{}. Name: {}".format(index,value) + " - Config_ID # "
			+ str(config_list_id[count_up]))
		x = config_list_id[count_up]
		config_id_choice.update({index:x})
		count_up = count_up + 1
	print("    ")
	print("Choose which config_id you want to list the VMs.")
	choice = input("Enter the number choice of config_id: ")
	if choice == "q":
		exit()
	if not choice.isdigit():
		print("****** Not a choice ******")
		get_flex_config_list(token,program_ser)
		pass
	if choice.isdigit():
		choice = int(choice)
		get_flex_vm_list(token,config_id_choice[choice])

def get_flex_vm_list(token,config_id):
	logging.info("Creating FLEX VMS CSV file...")
	global active_vms,stopped_vms
	apiheaders =  {"Content-Type":"application/json","Authorization":"Bearer "+token}
	data = {
		"ConfigId": config_id
		}
	url = "https://support.fortinet.com/ES/api/flexvm/v1/vms/list"
	result = requests.post(url, headers=apiheaders, json=data,timeout=15)
	parsed_json = json.loads(result.text)
	count_up = len(parsed_json['vms'])
	count = 0
	while count < count_up:
		ser_num = parsed_json['vms'][count]['serialNumber']
		status = parsed_json['vms'][count]['status']
		token_status = parsed_json['vms'][count]['tokenStatus']
		desc = parsed_json['vms'][count]['description']
		x = desc.split(':') # have to split because site adds FLexVM to description
		y = x[1] # getting only the host name
		z = y[1:]# Have to strip off the blank space at the start of the name
		vms_data = [z,ser_num,status,token_status]
		write_to_csv(vms_data) # writing to CSV file
		count = count + 1

def stop_active_vms(token,ser_number):
	global active_vms,stopped_vms
	apiheaders =  {"Content-Type":"application/json","Authorization":"Bearer "+token}
	data = {
		"serialNumber": ser_number
	}
	logging.debug("String sent to portal: " + ser_number)
	url = "https://support.fortinet.com/ES/api/flexvm/v1/vms/stop"
	result = requests.post(url, headers=apiheaders, json=data,timeout=10)
	parsed_json = json.loads(result.text)
	logging.debug(parsed_json)
	if parsed_json['message'] == "Request processed successfully.":
		print("Stopped VM: " + ser_number)
	else:
		print("Something went wrong check DEBUG")
	choice = input("Would you like to continue? (y/n) :")
	if choice.lower() == "y":
		delete_temp_file()
		get_flex_config_list(token,program_ser)
		search_vms_list()
	if choice.lower() == "n":
		print("Okay, we are done here..Goodbye")
		exit()
	else:
		print("I have no idea what you want...Goodbye")
		exit()

def decom_assest(ser_number):
	client_ida = "assetmanagement"
	global token, program_ser
	tokena = gettoken(api_user, api_pass, client_ida)
	apiheaders =  {"Content-Type":"application/json","Authorization":"Bearer "+tokena}
	data = {
		"serialNumbers": [ser_number]
		}
	logging.debug("Serial number in json string is .." + ser_number)
	url = "https://support.fortinet.com/ES/api/registration/v3/products/decommission/"
	result = requests.post(url, headers=apiheaders, json=data,timeout=10)
	#result = result.json()
	parsed_json = json.loads(result.text)
	logging.debug(parsed_json)
	if parsed_json['message'] == "Success":
		print("   ")
		print("Serial number " + ser_number + " has been decomissiond.")
	else:
		print("Something went wrong, look at debug")
	choice = input("Would you like to continue? (y/n) :")
	if choice.lower() == "y":
		delete_temp_file()
		get_flex_config_list(token,program_ser)
		search_vms_list()
	if choice.lower() == "n":
		print("Okay, we are done here..Goodbye")
		exit()
	else:
		print("I have no idea what you want...Goodbye")
		exit()

debug_setup()
delete_temp_file()
client_id = "flexvm"
token = gettoken(api_user, api_pass, client_id)	
program_ser = get_program_id(token)
config_id = get_flex_config_list(token,program_ser)
search_vms_list()

	
	

	



