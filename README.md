# netmiko_diag

# Tool is in beta!
Network diagnostics tool with Passwork integration

All code was tested on Python 3.11.0

## Requirements
1) This tool uses Passwork version 4 as the source of credentials to connect to hardware.
You must make sure that you are using version 4 of Passwork at the link https://IP_or_domain_name_of_Passwork/api/v4
Also you need to have an API key.

2) Make sure that directory structure in your Passwork arranged in this way:
```
--Organization vault
----Folder with devices credentials
--------Device
```
3) Make sure that Login and Password for each device stored in main Login and Password fields, not in additionals.
   Also you need to have URL or IP for each device in URL field. These fields described above are used for catching credentials.

## Setting-up
1) Passwork integration:
You need to fill variables below in passwork.py with your own values:
```
#URL or IP of Passwork in your local network
passwork_ip = ""
#API key that available after authorization
api_key = ""
```
2) Adding own device types: 
Function device_type_choice in netmiko_diag.py script is used to define device type for Netmiko
You need to match name of folder with devices credentials with actual device type that Netmiko supports (link with supported devices below)
https://github.com/ktbyers/netmiko/blob/develop/PLATFORMS.md
   
For now this tool supports only fortinet and cisco_wlc device types, but you can add your own like this
```
#Function that matches folder with devices credentials with actual device type
def device_type_choice(choice_text, command_arg = False, command_input_arg = False):
    match choice_text:
        #Start of added code
        case "Cisco FTD":
            device_type = "cisco_ftd"
            cmd_choice, command, port = cli_commands.cisco_ftd_cli(device_type, command_arg, command_input_arg)
        #End of added code
```
Then you need to add function with CLI commands in cli_commands.py and fill it with commands that you need like this:
```
def cisco_ftd_cli(device_type, command_arg = False, command_input_arg = False):
    #Command selection
    port = "" #Enter SSH port
    #Commands that you need
    commands_dict = {
        0: "show run", 1: "show int ip br",
        #To execute several commands at the same time, you need to write them to the list
        2: ["ping 8.8.8.8", "ping 8.8.4.4"]
    }
    if command_arg:
        choice = int(command_arg)
    else:
        print("="*40 + "\n" + "Command list:")
        for i in commands_dict:
            if isinstance(commands_dict[i], list):
                command_list = "\n".join(commands_dict[i])
                print(str(i) + " - " + command_list)
            else:
                print(str(i) + " - " + commands_dict[i])
        print("="*40)
        commands_list = list(commands_dict.keys())
        choice = input("Choose a command from the list: ")
        choice = int(check_input(str(choice), commands_list))
    match choice:
        #Requires additional input
        case 0 | 1 | 2:    
            command = commands_dict[choice]
    return choice, command, port
```
3) Don't forget to enter port that will be used for SSH connection in cli_commands.py in each function

## Using netmiko_diag tool
1) If you want to only fetch credentials you need run passwork.py script
2) If you want to run commands on device/devices you need run netmiko_diag.py
3) If you need constant commands sending on your device/devices you need run netmiko_constant_diag (you can stop the script only manually) with arguments like in this example:
```
python netmiko_constant_diag.py 1 2 S 0 1 N 10
1 - Clients vault (choose your own)
2 - Folder with devices credentials
S - Single device selection
0 - Device
1 - Command
N - Commands doesn't require additional input
10 - Delay time in seconds between iterations of command running
```
Or like in this example:
```
python netmiko_constant_diag.py 1 2 M 0,1,2,3 0,1 N 10
Arguments description:
1 - Clients vault (choose your own)
2 - Folder with devices credentials
M - Multiple device selection
0,1,2,3 - Devices separated by comma
0,1 - Commands separated by comma
N - Commands doesn't require additional input
10 - Delay time in seconds between iterations of commands running
```
