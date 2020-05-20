# Netbox-Custom-Scripts
Repository for various Netbox custom scripts, located in the organization tab.

This script uses pynetbox, because it allows us to call the API to assign next available prefixes and/or IPAddresses. Currently, at least I don't think, we can do that locally usually django queries, if so please let me know.

Install pynetbox with pip3 install pynetbox, then install custom scripts into the /opt/netbox/netbox/scripts folder.

'Assign_Prefix_and_IPv4_to_Tenant_and_VRF.py' simply assigns a child prefix from the selected parent prefix and then the first two usable host addresses to a VRF and Tenant, It also assigns the same in the Global VRF. It is assumed the Parent Prefix is Global or 'null'


'Assign_Prefix_to_Tenant_and_VRF.py' simply assigns a child prefix from the selected parent prefix to a VRF and Tenant, It also assigns the same in the Global VRF. It is assumed the Parent Prefix is Global or 'null'
'Official_Reference_Script.py' is jsut a reference script that is in the netbox custom script documents on their readthedocs.
