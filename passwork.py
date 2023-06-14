import requests
import re
import base64

#Passwork version 4 API
passwork_ip = ""
api_key = ""
url = f"https://{passwork_ip}/api/v4"

#Login and get a token
url_login = url + "/auth/login/" + api_key
r_login = requests.post(url_login, data = {"key": "value"})
token = r_login.json()["data"]["token"]
headers = {"Passwork-Auth": token}

#Taking the id of the Clients repository
url_get_vaults = url + "/vaults/list"
r_get_vaults = requests.get(url_get_vaults, headers = headers, data = {"key": "value"})
vault_clients = r_get_vaults.json()["data"][1]["id"]

#We take folders from the Clients storage (client directories)
url_get_folders = url + f"/vaults/{vault_clients}" + "/folders"
r_get_folders = requests.get(url_get_folders, headers = headers, data = {"key": "value"})
folders = r_get_folders.json()["data"]

#Input validation function for single selection
def check_input(choice, data_list):
    check = True
    while check:
       if not choice.isdigit():
           choice = input("="*40 + "\nNumber doesn't exist, please re-enter: ")
       elif int(choice) > (len(data_list) - 1):
           choice = input("="*40 + "\nNumber doesn't exist, please re-enter: ")
       elif int(choice) < 0:
           choice = input("="*40 + "\nNumber doesn't exist, please re-enter: ")
       else:
           check = False
           return choice

#Input validation feature for multiple selection
def check_input_multiple(m_pressed, choice, data_list):
    check = True
    #Returning when entered separated by commas
    choice_list = []    
    while check:
        if choice == "M":
            if m_pressed:
                check = False
                return choice
            #If M was pressed to enter multiple host selection,
            #then entering M again will call code under else
            else:
                choice = input("="*40 + "\nNumber doesn't exist, please re-enter: ")
                check = True
        elif choice == "END" and not m_pressed:
            check = False
            return choice
        #If hosts were entered separated by commas
        elif "," in choice:
            choice = set(choice.split(","))
            for item in choice:
                item = item.strip()
                if not item.isdigit():
                    choice = input("="*40 + f"\nNumber {item} does not exist in the list, please re-enter: ")
                elif int(item) > (len(data_list) - 1):
                    choice = input("="*40 + f"\nNumber {item} does not exist in the list, please re-enter: ")
                elif int(item) < 0:
                    choice = input("="*40 + f"\nNumber {item} does not exist in the list, please re-enter: ")
                else:
                    choice_list.append(item)
            if isinstance(choice, set):
                choice_list = sorted(list(set(choice_list)))
                check = False
                return choice_list
        #If single host input method is used
        elif "," not in choice and not choice_list:
            if not choice.isdigit() and not isinstance(choice, set):
                choice = input("="*40 + "\nNumber doesn't exist, please re-enter: ")
            elif int(choice) > (len(data_list) - 1) and not isinstance(choice, set):
                choice = input("="*40 + "\nNumber doesn't exist, please re-enter: ")
            elif int(choice) < 0 and not isinstance(choice, set):
                choice = input("="*40 + "\nNumber doesn't exist, please re-enter: ")      
            else:
                check = False
                return choice

#Client folder selector
def client_selector(json_data, choice = False):
    folders_dict = {}
    for folder in json_data:
        folders_dict[folder["name"]] = folder["id"]
    folders_list = list(folders_dict.keys())
    #To select in advance when the script is imported
    if choice:
        pass
    else:
        print("="*40 + "\nList of clients:")
        for folder in folders_list:
            print(str(folders_list.index(folder)) + " - " + folder)
        choice = input("="*40 + "\nEnter clients number: ")
        choice = check_input(choice, folders_list)
        print("="*40 + f"\nClient selection: {folders_list[int(choice)]}")
    client_choice = folders_dict[folders_list[int(choice)]]
    return client_choice

#Function for generating GET requests for the Folders methods: Get children and Get passwords
def folders_request(folder_id, method, url = url, headers = headers):
    url_get_folders = url + "/folders/" + folder_id + method
    r_get_folders = requests.get(url_get_folders, headers = headers, data = {"key": "value"})
    json_data = r_get_folders.json()["data"]
    return json_data

#Function for selecting a directory and subdirectory with hosts
def folders_list_func(json_data, choice = False):
    children_folders_dict = {}
    for child in json_data:
        children_folders_dict[child["name"]] = [child["id"], child["foldersAmount"]]
    children_folders_list = list(children_folders_dict.keys())
    if choice:
        pass
    else:
        print("="*40 + "\nFolder list:")
        for child in children_folders_list:
            print(str(children_folders_list.index(child)) + " - " + child)
        choice = input("="*40 + "\nEnter parent directory number: ")
        choice = check_input(choice, children_folders_list)
        print("="*40 + f"\nHosts selection: {children_folders_list[int(choice)]}")
    choice_text = children_folders_list[int(choice)]
    child_choice = children_folders_dict[children_folders_list[int(choice)]][0]
    check_empty = children_folders_dict[children_folders_list[int(choice)]][1]
    return child_choice, check_empty, choice_text

#Function to select host/hosts
def host_selector(json_data, multiple_arg = False, devices_arg = False):
    hostname_dict = {}
    for host in json_data:
        hostname_dict[host["name"]] = [host["id"], host["login"], host["url"]]
    hostname_list = list(hostname_dict.keys())
    if not multiple_arg and not devices_arg:
        print("="*40 + "\nDevice List:")
        for host in hostname_list:
            print(str(hostname_list.index(host)) + " - " + host)
        print("M - Multiple device selection")
        choice = input("="*40 + "\nEnter device number or M to select multiple devices: ")
    check = True
    while check:
        #Single host selection for netmiko_constant_diag
        if multiple_arg and multiple_arg == "S" and devices_arg and devices_arg.isdigit():
            choice = devices_arg
            host_id = hostname_dict[hostname_list[int(choice)]][0]
            host_url = hostname_dict[hostname_list[int(choice)]][2]
            m = re.search(r"([0-9]+(\.[0-9]+)+)", host_url)
            host_ip = m.group()
            check = False
            return host_id, host_ip            
        elif not multiple_arg and not devices_arg and choice.isdigit():
            #Single host selection
            choice = check_input(choice, hostname_list)
            print("="*40)
            host_id = hostname_dict[hostname_list[int(choice)]][0]
            host_url = hostname_dict[hostname_list[int(choice)]][2]
            m = re.search(r"([0-9]+(\.[0-9]+)+)", host_url)
            host_ip = m.group()
            check = False
            return host_id, host_ip
        #Multiple host selection for netmiko_constant_diag
        elif multiple_arg and multiple_arg == "M" and devices_arg and "," in devices_arg:
            multiple_host = []
            multiple_ip = []
            choice = list(set(devices_arg.split(",")))
            for item in choice:
                multiple_host.append(hostname_dict[hostname_list[int(item)]][0])
                m = re.search(r"([0-9]+(\.[0-9]+)+)", hostname_dict[hostname_list[int(item)]][2])
                host_ip = m.group()
                multiple_ip.append(host_ip)
            end_multiple = False
            check = False
            return multiple_host, multiple_ip
        #Selecting multiple hosts
        elif choice == "M":
            m_pressed = True
            choice = check_input_multiple(m_pressed, choice, hostname_list)
            end_multiple = True
            #Lists returned on completion of a function
            multiple_host = []
            multiple_ip = []
            while end_multiple == True:
                m_pressed = False
                choice = input("="*40 + "\nEnter numbers separated by commas and press Enter\nor enter one at a time, type END to complete: ")
                choice = check_input_multiple(m_pressed, choice, hostname_list)
                #Entering hosts separated by commas
                if isinstance(choice, list):
                    for item in choice:
                        multiple_host.append(hostname_dict[hostname_list[int(item)]][0])
                        m = re.search(r"([0-9]+(\.[0-9]+)+)", hostname_dict[hostname_list[int(item)]][2])
                        host_ip = m.group()
                        multiple_ip.append(host_ip)
                    end_multiple = False
                    check = False
                #Enter one host at a time and END to complete
                elif choice.isdigit():
                    multiple_host.append(hostname_dict[hostname_list[int(choice)]][0])
                    multiple_host = list(set(multiple_host))
                    m = re.search(r"([0-9]+(\.[0-9]+)+)", hostname_dict[hostname_list[int(choice)]][2])
                    host_ip = m.group()
                    multiple_ip.append(host_ip)
                    multiple_ip = list(set(multiple_ip))
                elif choice == "END" and multiple_host and multiple_ip:
                    end_multiple = False
                    check = False
                else:
                    end_multiple = True
            return multiple_host, multiple_ip
        else:
            check = True
            choice = input("="*40 + "\nEnter device number or M to select multiple devices: ")


#Function for generating GET requests Passwords: Get
def passwords_request(host_id, method, url = url, headers = headers):
    if isinstance(host_id, list):
        multiple_json_data = []
        for each_id in host_id:
            url_get_passwords = url + method + "/" + each_id
            r_get_passwords = requests.get(url_get_passwords, headers = headers, data = {"key": "value"})
            json_data = r_get_passwords.json()["data"]
            multiple_json_data.append(json_data)
        return multiple_json_data
    else:
        url_get_passwords = url + method + "/" + host_id
        r_get_passwords = requests.get(url_get_passwords, headers = headers, data = {"key": "value"})
        json_data = r_get_passwords.json()["data"]
        return json_data

#Function for collecting credentials
def catch_credentials(host_id, host_ip, json_data):
    #With multiple choice
    if isinstance(json_data, list) and host_id:
        multiple_name = []
        multiple_ip_addr = []
        multiple_login = []
        multiple_password = []
        multiple_result_str = []
        for data in json_data:
            name = data["name"]
            m = re.search(r"([0-9]+(\.[0-9]+)+)", data["url"])
            host_ip = m.group()
            ip_addr = host_ip
            login = data["login"]
            password = base64.b64decode(data["cryptedPassword"]).decode("utf-8")
            result_str = (
                f"Device name: {name}\n"
                f"IP address: {host_ip}\n"
                f"Login: {login}\n"
                f"Password: {password}"
            )
            multiple_name.append(name)
            multiple_ip_addr.append(ip_addr)
            multiple_login.append(login)
            multiple_password.append(password)
            multiple_result_str.append(result_str)
        return multiple_name, multiple_ip_addr, multiple_login, multiple_password, multiple_result_str
    #With a single choice
    elif host_id:
        name = json_data["name"]
        ip_addr = host_ip
        login = json_data["login"]
        password = base64.b64decode(json_data["cryptedPassword"]).decode("utf-8")
        result_str = (
            f"Device name: {name}\n"
            f"IP address: {host_ip}\n"
            f"Login: {login}\n"
            f"Password: {password}"
        )
        return name, ip_addr, login, password, result_str

if __name__ == "__main__":
    #Select the client directory by number from the list
    client_choice = client_selector(folders)

    #Choose a catalog with hosts
    children_method = "/children"
    json_data = folders_request(client_choice, children_method)
    child_choice, check_empty, choice_text = folders_list_func(json_data)

    #Select subdirectory with devices
    while check_empty:
        json_data = folders_request(child_choice, children_method)
        child_choice, check_empty = folders_list_func(json_data)
        print(child_choice)

    #Choosing a device
    passwords_method = "/passwords"
    json_data = folders_request(child_choice, passwords_method)
    host_id, host_ip = host_selector(json_data)

    #Taking the Password
    json_data = passwords_request(host_id, passwords_method)
    name, ip_addr, login, password, credentials_str = catch_credentials(host_id, host_ip, json_data)
    if isinstance(credentials_str, list):
        for each_cred in credentials_str:
            print("="*40 + f"\n{each_cred}")
    else:
        print(credentials_str)