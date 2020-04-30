
#########################################################################################################
####      This Python Script to provision Child Prefix and First and Second Usable Host Addresses.   ####
####        It is assumed that the Tenant and the VRF are created prior to running this script.      ####
#### Python script based on pynetbox https://readthedocs.org/projects/pynetbox/downloads/pdf/latest/ ####
#### This Script is intended to be placed in the /opt/netbox/netbox/scripts directory of netbox and  ####
#### ran from the custom scripts tab. Please read official documents located at:                     ####
####          https://netbox.readthedocs.io/en/stable/additional-features/custom-scripts/            ####
#########################################################################################################

###import pynetbox and Django models###
#import pprint

import pynetbox
from netaddr import *
from ipam.constants import *
from ipam.models import IPAddress, Prefix, VRF
from tenancy.models import Tenant, TenantGroup
from extras.scripts import *




### Start of Object querying for fields###

class NewPrefixandIPAssignment(Script):

    class Meta:
        name = "Assign Prefix and IP Addresses to Existing Tenant"
        description = "Assign Prefix and IP Addresses to Existing Tenant, Ideal for PtPs."
        field_order = ['tenant_name', 'tenant_address', 'prefix_assignment', 'prefix_length', 'vrf_assignment']

    tenant_name = ObjectVar(
        description="Name of tenant, Create the Tenant First if they do not already Exist.",
        queryset = Tenant.objects.all()
    )
    tenant_address = StringVar(
        description="Address of Tenant"
    )
    prefix_assignment = ObjectVar(
        description="Select Parent Prefix to be assigned.",
        queryset = Prefix.objects.all(
            widget=APISelect(
                api_url='/api/ipam/aggregates/',
                display_field='prefix',
            ) 
        )
    )
    prefix_length = IntegerVar(
        description = "Select size of prefix desired.",
        min_value = 24,
        max_value = 32
    )
    vrf_assignment = ObjectVar(
        description="Assign a vrf to the prefix and IP addresses, Create the VRF First if it does not already exist",
        queryset = VRF.objects.all()
    )
#### program function####
    def run(self, data):

        # pynetbox variables
        nb = pynetbox.api(url='http://localhost:80', token='generate a new token here')
        # defining variables based on user input from Class #
        tenant = data['tenant_name']
        input_vrf = data['vrf_assignment']
        input_addr = data['tenant_address']
        input_pfx = data['prefix_assignment']
        input_cidr = data['prefix_length']
        # Dictionary for Prefix  #
        pfx_dict = dict(
            prefix_length = input_cidr,                                 # assigns Child Prefix CIDR
            tenant = tenant.id,                                         # assigns Tenant based on ID
            description = '{}-{}-P2P'.format(tenant.name, input_addr) # descripton based on Tenant and Tenant Address Field
        )
        # Dictionary for IP Assignment #
        addr_dict = dict(
            prefix_length = input_cidr,                                  # assigns IP CIDR, same as prefix
            tenant= tenant.id,                                          # assigns Tenant Based on ID
            description= "{}-{}-P2P".format(tenant.name, input_addr)  # descripton based on Tenant and Tenant Address Field
        )
        # Creates the New Prefix and Global IPs #
        # Gathers objects from User Selected  Parent Prefix #
        get_prefix = nb.ipam.prefixes.get(prefix=input_pfx)

        # Created next available prefix based on get from selected prefix in Global #
        new_prefix = get_prefix.available_prefixes.create(pfx_dict)
        get_crtd_gbl_pfx = nb.ipam.prefixes.get(prefix=new_prefix["prefix"])


         # Creates Two Consecutive Host IP assignments in Global #
        for i in range(2):
            new_ipaddr = get_crtd_gbl_pfx.available_ips.create(addr_dict)

        # Updates created VRF because VRFS cannot be assigned explicitly in the above creation, the inherit the parent prefixes #
        update_pfx = nb.ipam.prefixes.get(prefix=new_prefix['prefix'])
        update_pfx.update({
            "vrf": input_vrf.id,
        })
        update_success = update_pfx.save()

        # Recreates Global Prefix #
        glbl_prefix = get_prefix.available_prefixes.create(pfx_dict)


        # Log Success and show created prefix#
        self.log_success("Prefix '{}' created with VRF '{}' and Tenant '{}'.".format(update_pfx, input_vrf.name, tenant.name,))


        # Start of IP assignment for VRF #

        # Creates Two Consecutive Host IP assignments for specific VRF#
        # Pulls original prefix after its been updated #
        for i in range(2):
            new_ipaddr = get_crtd_gbl_pfx.available_ips.create(addr_dict)

        self.log_success("Created and Assigned IP Addresses '{}' and '{}', for Tenant: '{}'.".format(update_pfx, new_ipaddr['address'], tenant.name,))

        ## Output Format ##
        output =  (
        "Successfully Assigned Newly Created Prefix: {} to the following:, \n"
        "Tenant: {}, \n"
        "VRF:{}, \n"
        "Description: {}, \n"
        "Successfully Assigned and Created IP Addresses: {} and {}, \n".format(input_pfx, tenant.name,  input_vrf.name, get_crtd_gbl_pfx.description, update_pfx, new_ipaddr['address'],
        ))


        return (output)

