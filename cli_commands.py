#Input validation function. A number must be entered from the list
def check_input(choice, data_list):
    check = True
    while check:
       if not choice.isdigit():
           choice = input("="*40 + "\nThe number doesn't exist, please re-enter: ")
       elif int(choice) > (len(data_list) - 1):
           choice = input("="*40 + "\nThe number doesn't exist, please re-enter: ")
       elif int(choice) < 0:
           choice = input("="*40 + "\nThe number doesn't exist, please re-enter: ")
       else:
           check = False
           return choice


def fortinet_cli(device_type, command_arg = False, command_input_arg = False):
    #Command selection
    port = "" #Enter SSH port
    commands_dict = {
        0: "diag sys sdwan service", 1: "get router info bgp summary", 2: "exec telnet telnetmyip.com",
        3: ["exec ping-options interface", "exec ping 8.8.8.8"]
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
        case 0:
            if command_input_arg:
                sdwan_service = command_input_arg[choice]
            else:
                sdwan_service = input("Enter SD-WAN service number: ")
            command = commands_dict[choice] + " " + sdwan_service
        #Requires additional input
        case 3:
            if command_input_arg:
                interface = command_input_arg[choice]
            else:
                interface = input("Enter the name of the outgoing interface: ")
            cmd_copy = commands_dict[choice][0]
            commands_dict[choice].pop(0)
            commands_dict[choice].insert(0, f"{cmd_copy} {interface}")
            command = commands_dict[choice]
        case 1 | 2:    
            command = commands_dict[choice]
    return choice, command, port

def cisco_wlc_cli(device_type, command_arg = False, command_input_arg = False):
    #Command selection
    port = "" #Enter SSH port
    commands_dict = {
        0: "show ap summary"
    }
    if command_arg:
        choice = int(command_arg)
    else:
        print("="*40 + "\n" + "Command list:")
        for i in commands_dict:
            print(str(i) + " - " + commands_dict[i])
        print("="*40)
        commands_list = list(commands_dict.keys())
        choice = input("Choose a command from the list: ")
        choice = int(check_input(str(choice), commands_list))
    match choice:
        case 0:
            command = commands_dict[choice]
    return choice, command, port