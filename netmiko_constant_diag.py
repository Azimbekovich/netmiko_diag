#Python modules
from sys import argv
from time import sleep
import re
#Imported scripts
from netmiko_diag import *
from problems_report import problems_report

#Arguments passed when calling the script:
#Clients choice
client_arg = argv[1]
#Select device type (based on directory)
device_type_arg = argv[2]
#Run on one or more devices.
#To run on one S to run on multiple M
multiple_arg = argv[3]
#Device/devices (separated by commas without spaces)
devices_arg = argv[4]
#Command/commands number
command_arg = argv[5]
#For commands requiring additional input
command_input_arg = argv[6]
#Delay before new iteration
delay_arg = argv[7]

print(command_input_arg)

if __name__ == "__main__":
    #To run with multiple commands
    if "," in command_arg:
        command_list = list(set(command_arg.split(",")))
        commant_iter = 0
    else:
        command_list = False
    #To pass additional parameters to commands requiring additional input
    command_input_arg_regex = r"(\d+):(\S+)"
    command_input_arg_dict = {}
    if ":" in command_input_arg and "#" not in command_input_arg:
        m_command_input_arg = re.search(command_input_arg_regex, command_input_arg)
        command_input_arg_dict[int(m_command_input_arg.group(1))] = m_command_input_arg.group(2)
        command_input_arg = command_input_arg_dict
    elif ":" and "#" in command_input_arg:
        command_input_arg_list = command_input_arg.split("#")
        for cmd in command_input_arg_list:
            m_command_input_arg = re.search(command_input_arg_regex, cmd)
            command_input_arg_dict[int(m_command_input_arg.group(1))] = m_command_input_arg.group(2)
        command_input_arg = command_input_arg_dict
    elif command_input_arg == "N":
        command_input_arg = False

    #Using a function to accept arguments
    choice_text, host_ip, name, ip_addr, login, password, credentials_str = netmiko_constant_diag(client_arg, device_type_arg, multiple_arg, devices_arg)
    #To calculate the total running time of the script
    start_time_total = datetime.now()
    #Script will run until manually stopped
    repeat_command = True #As long as this variable is True, the script works
    while repeat_command:
        if command_list:
            command_arg = command_list[commant_iter]
        #To calculate the execution time of commands
        start_time = datetime.now()
        #Select device_type and display available commands
        device_type, cmd_choice, command, port = device_type_choice(choice_text, command_arg, command_input_arg)
        
        #Filling in parameters for connecting to devices in multithreaded mode
        if isinstance(ip_addr, list):
            args_list = []
            i = 0
            if i <= len(ip_addr):
                for each_ip in ip_addr:
                    each_name, each_ip, each_login, each_password = name[i], ip_addr[i], login[i], password[i]
                    args = {
                    "device_type": device_type, "name": each_name, "ip_addr": each_ip,
                    "login": each_login, "password": each_password, "timeout": 5,
                    "port": port, "command": command, "read_timeout_override": 300
                    }
                    args_list.append(args)
                    i += 1
        
        #Filling in parameters for connecting to devices in single mode
        else:
            kwargs = {
            "device_type": device_type, "name": name, "ip_addr": ip_addr,
            "login": login, "password": password, "timeout": 5,
            "port": port, "command": command, "read_timeout_override": 300
            }
        
        #Connect to devices, send command and receive output
        #In multithreaded mode
        if isinstance(ip_addr, list):            
            out_dict = send_command_to_devices(args_list)
            output_handler_list = []
            for device in args_list:
                out_device = device["name"]
                out_command = out_dict[device["ip_addr"]]
                output_handler_dict = output_handler.handler(device_type, out_device, cmd_choice, out_command, command_arg)
                output_handler_list.append(output_handler_dict)
            problems_report(output_handler_list, device_type, int(command_arg))
        #In single mode
        else:
            out = netmiko_single_command(**kwargs)
            output_handler_list = []
            output_handler_dict = output_handler.handler(device_type, kwargs["name"], cmd_choice, out, command_arg)
            output_handler_list.append(output_handler_dict)
            problems_report(output_handler_list, device_type, int(command_arg))
        print("="*40 + f"\nCommand execution time: {datetime.now() - start_time}")
        
        #To change commands on startup with multiple commands and return to the first one when the list ends
        if command_list:
            if command_list[commant_iter] != command_list[-1]:
                commant_iter += 1
                print(command_list[commant_iter])
            else:
                commant_iter = 0
                print(command_list[commant_iter])
        
        #Delay before next iteration
        sleep(int(delay_arg))