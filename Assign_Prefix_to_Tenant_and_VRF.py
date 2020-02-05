
#########################################################################################################
####      This Python Script to provision a Child Prefix and assign it to a Tenant and VRF.          ####
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

class NewPrefixAssignment(Script):

    class Meta:
        name = "Assign Prefix to Existing Tenant and VRF"
        description = "Assign only a Prefix to a Tenant and specific VRF, reserves in Global VRF as well."
        field_order = ['tenant_name', 'tenant_address', 'prefix_assignment', 'prefix_length', 'vrf_assignment']

    tenant_name = ObjectVar(
        description="Name of tenant, Create the Tenant First if they do not already Exist.",
        queryset = Tenant.objects.all()
    )
    tenant_address = StringVar(
        description="Address of Tenant"         #could be a generic decription, any string works
    )
    prefix_assignment = ObjectVar(
        description="Select Parent Prefix to be assigned.",
        queryset = Prefix.objects.filter(
            id='43219' #172.28.77.0/24
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
        nb = pynetbox.api(url='http://localhost:80', token='generate token here')
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
            description = '{}-{}-'.format(tenant.name, input_addr) # descripton based on Tenant and Tenant Address Field
        )

        # Creates the New Prefix and Reserves them in both Global and specfically assigned VRF #
        # Gathers objects from User Selected Parent Prefix #
        get_prefix = nb.ipam.prefixes.get(prefix=input_pfx)

        # Created next available prefix based on get from selected prefix in Global #
        new_prefix = get_prefix.available_prefixes.create(pfx_dict)
        get_crtd_gbl_pfx = nb.ipam.prefixes.get(prefix=new_prefix["prefix"])


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

        output =  (
        "Successfully Assigned Newly Created Prefix: {} to the following:, \n"
        "Tenant: {}, \n"
        "VRF:{}, \n"
        "Description: {}, \n".format(input_pfx, tenant.name,  input_vrf.name, get_crtd_gbl_pfx.description,
        ))


        return (output)
