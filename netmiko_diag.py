#Python modules
import logging
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor
import netmiko
import paramiko
#Imported scripts
import passwork
import cli_commands
import output_handler

def netmiko_constant_diag(client_arg, device_type_arg, multiple_arg, devices_arg):
    #START THE PASSWORK INTEGRATION CODE
    client_choice = passwork.client_selector(passwork.folders, choice = client_arg)

    #Select a folder in the client directory.
    #The name of the device folder is stored in the choice_text variable
    children_method = "/children"
    json_data = passwork.folders_request(client_choice, children_method)
    child_choice, check_empty, choice_text = passwork.folders_list_func(json_data, choice = device_type_arg)

    #Choosing a host
    passwords_method = "/passwords"
    json_data = passwork.folders_request(child_choice, passwords_method)
    host_id, host_ip = passwork.host_selector(json_data, multiple_arg = multiple_arg, devices_arg = devices_arg)

    #Taking the password
    json_data = passwork.passwords_request(host_id, passwords_method)
    name, ip_addr, login, password, credentials_str = passwork.catch_credentials(host_id, host_ip, json_data)
    
    return choice_text, host_ip, name, ip_addr, login, password, credentials_str
    #END OF PASSWORK INTEGRATION CODE

#Function to determine device_type.
#Returns the device type, the number of the selected command for the output handler,
#command and port to connect
def device_type_choice(choice_text, command_arg = False, command_input_arg = False):
    match choice_text:
        case "FortiNet":
            device_type = "fortinet"
            cmd_choice, command, port = cli_commands.fortinet_cli(device_type, command_arg, command_input_arg)
        case "Cisco Wireless":
            device_type = "cisco_wlc"
            cmd_choice, command, port = cli_commands.cisco_wlc_cli(device_type, command_arg, command_input_arg)
    return device_type, cmd_choice, command, port

#This line specifies that paramiko log messages will be output
#only if they are WARNING or higher
logging.getLogger("paramiko").setLevel(logging.WARNING)

#Format of output of INFO messages by logging module
logging.basicConfig(
    format = '%(threadName)s %(name)s %(levelname)s: %(message)s',
    level=logging.INFO)

#Function for interacting with Netmiko using multithreading.
#Passing parameters for connection and passing commands.
#Takes a list of **args in multithreading mode.
def netmiko_multiple_command(device_dict):
    start_msg = '===> {} Connecting to IP {}, Hostname: {}, Login: {}'
    received_msg = '<=== {} Received data from IP {}, Hostname: {}, Login: {}'
    device_type = device_dict["device_type"]
    name = device_dict["name"]
    ip_addr = device_dict["ip_addr"]
    login = device_dict["login"]
    password = device_dict["password"]
    timeout = device_dict["timeout"]
    port = device_dict["port"]
    command = device_dict["command"]
    read_timeout_override = device_dict["read_timeout_override"]
    logging.info(start_msg.format(datetime.now().time(), ip_addr, name, login))

    try:
        with netmiko.ConnectHandler(
            device_type = device_type, host = ip_addr, username = login,
            password = password, timeout = timeout, port = port, read_timeout_override = read_timeout_override
        ) as ssh:
            ssh.enable()
            #If several commands are sent to the device at once
            if isinstance(command, list):
                out_list = []
                for cmd in command:
                    out = ssh.send_command(cmd)
                    out_list.append(out)
                #The output of several commands is combined into one through a line break
                out = "\n".join(out_list)
            #If one command is sent to the device
            else:
                out = ssh.send_command(command)
            logging.info(received_msg.format(datetime.now().time(), ip_addr, name, login))
        return out
    except netmiko.exceptions.NetmikoAuthenticationException as error:
        logging.warning(error)
    except ValueError as error:
        logging.warning(error)
    except netmiko.exceptions.NetmikoTimeoutException as error:
        logging.warning(error)

#Using multithreading when calling the netmiko_multiple_command function
def send_command_to_devices(args_list):
    data = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        out = executor.map(netmiko_multiple_command, args_list)
        for device, out in zip(args_list, out):
            data[device['ip_addr']] = out
    return data

#Function for interacting with Netmiko without using multithreading.
#Passing parameters for connection and passing commands.
#Accepts **kwargs
def netmiko_single_command(device_type, name, ip_addr, login, password, timeout, port, command, read_timeout_override):
    print("="*40 + f"\nConnecting to IP {ip_addr}\nHostname: {name}\nLogin: {login}")
    try:
        with netmiko.ConnectHandler(
            device_type = device_type, host = ip_addr, username = login,
            password = password, timeout = timeout, port = port, read_timeout_override = read_timeout_override
        ) as ssh:
            ssh.enable()
            #If several commands are sent to the device at once
            if isinstance(command, list):
                out_list = []
                for cmd in command:
                    out = ssh.send_command(cmd)
                    out_list.append(out)
                out = "\n".join(out_list)
            else:
                out = ssh.send_command(command)
            return out
    except netmiko.exceptions.NetmikoAuthenticationException as error:
        print(error)
    except ValueError as error:
        print(error)
    except netmiko.exceptions.NetmikoTimeoutException as error:
        logging.warning(error)

#When the script is called, the code below is executed:
if __name__ == "__main__":
    #BEGINNING OF PASSWORK INTEGRATION CODE
    client_choice = passwork.client_selector(passwork.folders, choice = 2) #Enter the client number or remove choice to select the client manually while the script is running

    #Select a folder in the client directory.
    #The name of the device folder is stored in the choice_text variable
    children_method = "/children"
    json_data = passwork.folders_request(client_choice, children_method)
    child_choice, check_empty, choice_text = passwork.folders_list_func(json_data)

    #Choose a host
    passwords_method = "/passwords"
    json_data = passwork.folders_request(child_choice, passwords_method)
    host_id, host_ip = passwork.host_selector(json_data)

    #Get the password
    json_data = passwork.passwords_request(host_id, passwords_method)
    name, ip_addr, login, password, credentials_str = passwork.catch_credentials(host_id, host_ip, json_data)
    #END OF PASSWORK INTEGRATION CODE

    #To calculate the total running time of the script
    start_time_total = datetime.now()
    #After the output of the command, you will be prompted to run the command from the list on the same hardware,
    #select other devices from the same directory, select another directory and devices,
    #end the script
    repeat_command = True #As long as this variable is True, the script works
    while repeat_command:
        #To calculate the execution time of commands
        start_time = datetime.now()
        #Select device_type and display available commands
        try:
            #If there was a return to the directory selection
            new_device_type, new_cmd_choice, new_command, new_port
        except NameError:
            device_type, cmd_choice, command, port = device_type_choice(choice_text)
        else:
            #Then we use new connection data and a new command
            device_type, cmd_choice, command, port = new_device_type, new_cmd_choice, new_command, new_port
        
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
        if isinstance(ip_addr, list):            
            out_dict = send_command_to_devices(args_list)
            for device in args_list:
                out_device = device["name"]
                out_command = out_dict[device["ip_addr"]]
                output_handler.handler(device_type, out_device, cmd_choice, out_command)
        else:
            out = netmiko_single_command(**kwargs)
            output_handler.handler(device_type, kwargs["name"], cmd_choice, out)              
        print("="*40 + f"\nCommand execution time: {datetime.now() - start_time}")
        
        #Menu after running the script
        print("="*40 + "\nChoose an action:")
        repeat_command_list = ["Run command on same hardware",
                                "Return from device list", "Return to previous directory",
                                "Finish script"]
        for i in repeat_command_list:
            print(str(repeat_command_list.index(i)) + " - " + i)
        input_repeat_command = input("Answer choice: ")
        input_repeat_command = passwork.check_input(input_repeat_command, repeat_command_list)
        if int(input_repeat_command) == 0:
            #Repeat the new command on the same device
            repeat_command = True
        elif int(input_repeat_command) == 1:
            #Select another device from the same directory
            #Choose a host
            json_data = passwork.folders_request(child_choice, passwords_method)
            host_id, host_ip = passwork.host_selector(json_data)
            #Get the password
            json_data = passwork.passwords_request(host_id, passwords_method)
            name, ip_addr, login, password, credentials_str = passwork.catch_credentials(host_id, host_ip, json_data)
            repeat_command = True
        elif int(input_repeat_command) == 2:
            #Select another directory and another device
            #Choose a directory
            json_data = passwork.folders_request(client_choice, children_method)
            child_choice, check_empty, choice_text = passwork.folders_list_func(json_data)
            #Choose a host
            json_data = passwork.folders_request(child_choice, passwords_method)
            host_id, host_ip = passwork.host_selector(json_data)
            #Get the password
            json_data = passwork.passwords_request(host_id, passwords_method)
            name, ip_addr, login, password, credentials_str = passwork.catch_credentials(host_id, host_ip, json_data)
            #Fetch new connection data and select a command
            new_device_type, new_cmd_choice, new_command, new_port = device_type_choice(choice_text)
            repeat_command = True
        else:
            #Completion of the script
            print("="*40 + f"\nTotal script running time: {datetime.now() - start_time_total}")
            print("="*40 + "\nCompletion of the script")
            repeat_command = False