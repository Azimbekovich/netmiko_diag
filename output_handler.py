import re
import variables

def handler(device_type, device, cmd_choice, out, command_arg = False):
    #Command output from devices
    if command_arg:
        pass
    else:
        print("="*40 + f"\nOutput from the device {device}:\n" + "="*40 + f"\n{out}")

    #Output handler for FortiGate devices
    if device_type == "fortinet":
        output_handler_dict = {}
        match cmd_choice:
            #Output handler for "diag sys sdwan service" command
            case 0:
                pass
            #Output handler for "get router info bgp summary" command if you're using full mesh eBGP topology
            case 1:
                if out is not None:
                    bgp_regex = r"([0-9]+(\.[0-9]+)+)\W+4\W+(\S+)(\W+\S+){5} (\S+|\W+never)\W+(\S+)"
                    out_to_process = out.split("\n")
                    i = 0
                    bgp_failed = {}
                    output_handler_out = []
                    for string in out_to_process:
                        i += 1
                        if "local AS number" in string:
                            local_as = string[-4:]
                        elif i > 8 and string:
                            m_bgp = re.search(bgp_regex, string)
                            if m_bgp:
                                neighbor_ip = m_bgp.group(1)
                                remote_as = m_bgp.group(3)
                                bgp_uptime = m_bgp.group(5).lstrip()
                                bgp_state = m_bgp.group(6)
                                #variables stored in variables.py
                                site_id = variables.sites_as[remote_as]
                                if bgp_uptime == "never":
                                    bgp_failed[neighbor_ip] = [site_id, remote_as, bgp_state]
                    output_handler_dict[device] = bgp_failed
                    for key, value in bgp_failed.items():
                        output_handler_out.append(f"Site ID/code: {value[0]}\nAS number: {value[1]}\nRemote IP: {key}\nBGP state: {value[2]}\n")
                    output_handler_out = "\n".join(output_handler_out)
                    if not command_arg:
                        #If netmiko_constant_diag is not used, returns the output of the command handler
                        print("="*40 + f"\nОтсутствует BGP сессия {device}\n" + "="*40 + f"\n{output_handler_out}")
            #Output handler for command "exec telnet telnetmyip.com"
            case 2:
                pass
            #Output handler for command "exec ping-options interface", "exec ping 8.8.8.8"
            case 3:
                pass
        #Returns a dictionary in the dictionary to be processed by the problems_report script if netmiko_constant_diag is used
        if command_arg:
            return output_handler_dict

    #Output handler for Cisco WLC devices
    elif device_type == "cisco_wlc":
        match cmd_choice:
            #Output handler for "show ap summary" command. Shows which IP points from the DHCP pool.
            #If you're using static IPs for APs this could be handy to monitor which access points have rebooted and need to be assigned static IPs
            case 0:
                if out is not None:
                    print("=" * 40 + "\nWhich access points have IP from DHCP pool\n" + "=" * 40)
                    ap_name_regex = r"^\S+"
                    ip_regex = r" ([0-9]+(\.[0-9]+)+)"
                    out_to_process = out.split("\n")
                    i = 0
                    for string in out_to_process:
                        i += 1
                        if i > 8 and string:
                            m_ap_name = re.search(ap_name_regex, string)
                            if m_ap_name:
                                ap_name = m_ap_name.group()
                            m_ip = re.search(ip_regex, string)
                            if m_ip.group():
                                ip = m_ip.group(1)
                                dhcp_ip = ip.split(".")
                                #Assign your own DHCP pool start and end IPs
                                if int(dhcp_ip[3]) in range(2, 30):
                                    print(f"Hostname: {ap_name} IP: {ip} from DHCP pool!!!")
                                else:
                                    print(f"Hostname: {ap_name} IP: {ip}")
                        else:
                            continue
                else:
                    pass