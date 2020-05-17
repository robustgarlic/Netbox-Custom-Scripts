# Netbox-Custom-Scripts
Repository for various Netbox custom scripts, located in the organization tab.

'Assign_Prefix_and_IPv4_to_Tenant_and_VRF.py' simply assigns a child prefix from the selected parent prefix and then the first two usable host addresses to a VRF and Tenant, It also assigns the same in the Global VRF. It is assumed the Parent Prefix is Global or 'null'


'Assign_Prefix_to_Tenant_and_VRF.py' simply assigns a child prefix from the selected parent prefix to a VRF and Tenant, It also assigns the same in the Global VRF. It is assumed the Parent Prefix is Global or 'null'
'Official_Reference_Script.py' is jsut a reference script that is in the netbox custom script documents on their readthedocs.
