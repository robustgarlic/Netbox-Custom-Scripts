#super simple script to add a service to a vm, selecting any IP address.

from ipam.choices import IPAddressStatusChoices
from ipam.models import IPAddress
from virtualization.models import Cluster, VirtualMachine
from ipam.models import Service
from utilities.forms import APISelect
from extras.scripts import *


class AddService(Script):
    class Meta:
        name = "Add Service"
        description = "Easily add services to a device or VM"
        field_order = ['server_name', 'service_name', 'service_ip','service_port',
                       'service_desc']
        commit_default = False

    server_name = ObjectVar(
        description="Select Virtual Machine: ",
        queryset = VirtualMachine.objects.all()
    )
    service_name = StringVar(label='Service Name')
    service_ip = ObjectVar(
        label="Select IP Address below: ",
        queryset = IPAddress.objects.all(),
            widget=APISelect(
                api_url='/api/ipam/ip-addresses/',
                display_field='address'
        ),
    )
    service_port = StringVar(label="Service port")
    service_desc = StringVar(label="Description")




    def run(self, data, commit):
        vm = VirtualMachine.objects.get(name=data["server_name"])
        addr = data['service_ip']
        newservice = Service(
            device=None,
            virtual_machine=vm,
            name=data["service_name"],
            port=data["service_port"],
            protocol="tcp",
            description=data["service_desc"]
        )

        newservice.save()
        newservice.ipaddresses.add(addr)
        output = (vm,newservice,addr)

        return (output)
