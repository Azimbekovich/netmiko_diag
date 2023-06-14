import variables

def problems_report(output_handler_list, device_type, command_arg):
    if device_type == "fortinet":
        match command_arg:
            case 1:
                for device_dict in output_handler_list:
                    problem_sites = []
                    excluding_current_sites = []
                    problem_output = []
                    for device, bgp_failed in device_dict.items():
                        #Determine with which sites on the checked site there are no BGP sessions if you're using full mesh eBGP topology
                        for neighbor_ip, data in bgp_failed.items():
                            problem_sites.append(data[0])
                            problem_output.append(f"Site ID/code: {data[0]}\nAS number: {data[1]}\nRemote IP: {neighbor_ip}\nBGP state: {data[2]}\n")
                        problem_sites = sorted(list(set(problem_sites)))
                        #Create a list with sites, excluding the one being checked
                        for asnum, site in variables.sites_as.items():
                            if site in device:
                                site_device = site
                            elif "excluded site" in site: #If you need to exclude some site from checking
                                continue
                            else:
                                excluding_current_sites.append(site)
                                excluding_current_sites.sort()
                    if problem_sites == excluding_current_sites:
                        problem_output = "\n".join(problem_output)
                        problem_output = (f"On the device {device}, problems with setting up a BGP session:\n{problem_output}")
                        print(problem_output)