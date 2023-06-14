# Instruction in development...

# netmiko_diag
Network diagnostics tool with Passwork integration

All code was tested on Python 3.11.0

## Setting-up
1) This tool uses Passwork version 4 as the source of credentials to connect to hardware.
   You must make sure that you are using version 4 of Passwork at the link https://IP_or_domain_name_of_Passwork/api/v4 and you have an API key.
2) Make sure that directory structure in your Passwork arranged in this way:
```
--Organization vault
----Folder with devices credentials
--------Device
```
   Then make sure that Login and Password for each device stored in main Login and Password fields, not in additionals.
   Also you need to have URL or IP for each device in URL field. These fields described above are used for catching credentials.
3) You need to enter values in variables below that located in passwork.py script:
```
passwork_ip = ""
api_key = ""
```
4) Function device_type_choice in netmiko_diag.py script is used to define device type for Netmiko
   You need to match name of folder with devices credentials with actual device type that Netmiko supports
   https://github.com/ktbyers/netmiko/blob/develop/PLATFORMS.md
   
   For now this tool supports only fortinet and cisco_wlc device types, but you cat add your own like this
```
def device_type_choice(choice_text, command_arg = False, command_input_arg = False):
    match choice_text:
        #Start of added code
        case "Cisco FTD":
            device_type = "cisco_ftd"
            cmd_choice, command, port = cli_commands.cisco_ftd_cli(device_type, command_arg, command_input_arg)
        #End of added code
```
Then you need to add function with CLI commands in cli_commands.py like this:
```
def cisco_ftd_cli(device_type, command_arg = False, command_input_arg = False):
    #Command selection
    port = "" #Enter SSH port
    commands_dict = {
        0: "show run", 1: "show int ip br"
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
        case 0 | 1:    
            command = commands_dict[choice]
    return choice, command, port
```
5) 
