"""
* *******************************************************
* Copyright VMware, Inc. 2018. All Rights Reserved.
* SPDX-License-Identifier: MIT
* *******************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
"""

__author__ = 'VMware, Inc.'

# To create a policy of a different type, import the CreateSpec of the
# corresponding capability.
from com.vmware.vcenter.compute.policies.capabilities.vm_host_affinity_client \
     import CreateSpec
from com.vmware.vapi.std_client import DynamicID
from com.vmware.vcenter.vm_client import Power
from com.vmware.vcenter_client import Host
from samples.vsphere.common import sample_cli
from samples.vsphere.common import sample_util
from samples.vsphere.common.ssl_helper import get_unverified_session
from samples.vsphere.vcenter.helper.vm_helper import get_vm
from vmware.vapi.vsphere.client import create_vsphere_client


def attach_tag(client, inv_obj, inv_type, tag):
    dyn_id = DynamicID(type=inv_type, id=inv_obj)
    try:
        client.tagging.TagAssociation.attach(tag.id, dyn_id)
    except Exception as e:
        print("Check that the tag is associable to {}".format(inv_type))
        raise e


class ComputePolicyWorkflow(object):
    """
    Demonstrates usage of the compute policy APIs to create a policy of
    VM-Host affinity capability and checks the compliance status of the policy
    for a particular virtual machine after the virtual machine is powered on.
    """
    def __init__(self):
        self.policy_id = None
        self.vm_id = None
        self.vm_info = None

        # Create argument parser for standard inputs:
        # server, username, password, cleanup and skipverification.
        parser = sample_cli.build_arg_parser()

        parser.add_argument('-n', '--name', required=True,
                            help='Name of the policy')
        parser.add_argument('-d', '--description', required=False,
                            help='Description for the policy',
                            default='Sample policy description')
        parser.add_argument('-vn', '--vmname', required=True,
                            help='Name of the virtual machine')
        parser.add_argument('-hn', '--hostname', required=True,
                            help='Name of the host')
        parser.add_argument('-vt', '--vmtag', required=True,
                            help='Tag name to attach to the virtual machine')
        parser.add_argument('-ht', '--hosttag', required=True,
                            help='Tag name to attach to the host')

        # Parse the arguments.
        args = sample_util.process_cli_args(parser.parse_args())
        self.vm_name = args.vmname
        self.vm_tag_name = args.vmtag
        self.host_name = args.hostname
        self.host_tag_name = args.hosttag
        self.policy_name = args.name
        self.policy_desc = args.description
        self.cleardata = args.cleardata

        # Skip server cert verification if needed.
        # This is not recommended in production code.
        session = get_unverified_session() if args.skipverification else None

        # Connect to vSphere client.
        self.client = create_vsphere_client(server=args.server,
                                            username=args.username,
                                            password=args.password,
                                            session=session)

    def run(self):
        # Get the virtual machine and power it off.
        self.vm_id = get_vm(self.client, self.vm_name)
        self.vm_info = self.client.vcenter.VM.get(self.vm_id)
        if not self.vm_info:
            raise ValueError("Virtual machine {} not found".format(
                self.vm_name))
        else:
            if self.vm_info.power_state == Power.State.POWERED_ON:
                self.client.vcenter.vm.Power.stop(self.vm_id)
            elif self.vm_info.power_state == Power.State.SUSPENDED:
                self.client.vcenter.vm.Power.start(self.vm_id)
                self.client.vcenter.vm.Power.stop(self.vm_id)

        # Get the tags.
        tags = self.client.tagging.Tag.list()
        for tag in tags:
            info = self.client.tagging.Tag.get(tag)
            if info.name == self.vm_tag_name:
                vm_tag = info
            if info.name == self.host_tag_name:
                host_tag = info

        if not vm_tag or not host_tag:
            raise ValueError("Provided tag(s) not found")

        # Tag the virtual machine and the host.
        attach_tag(self.client, self.vm_id, "VirtualMachine", vm_tag)

        filter_spec = Host.FilterSpec(names=set([self.host_name]))
        all_hosts = self.client.vcenter.Host.list(filter_spec)
        if not len(all_hosts) > 0:
            raise ValueError("Provided host not found")
        host_id = all_hosts[0].host

        attach_tag(self.client, host_id, "HostSystem", host_tag)

        # Create a vm-host affinity policy.
        create_spec = CreateSpec(vm_tag=vm_tag.id, host_tag=host_tag.id,
                                 name=self.policy_name,
                                 description=self.policy_desc)
        print("Creating a VM-Host affinity policy")
        try:
            self.policy_id = self.client.vcenter.compute.\
                             Policies.create(create_spec)
        except Exception as e:
            print("Policy creation failed")
            raise e
        print("Policy created with id: {}".format(self.policy_id))

        # Power-on the virtual machine.
        print("Powering on {}".format(self.vm_name))
        self.client.vcenter.vm.Power.start(self.vm_id)
        self.vm_info = self.client.vcenter.VM.get(self.vm_id)
        assert self.vm_info.power_state == Power.State.POWERED_ON

        # Check the compliance status of the policy on this virtual machine.
        status = self.client.vcenter.vm.compute.Policies.get(self.vm_id,
                                                             self.policy_id)
        print("The compliance status of policy {} for virtual machine "
              "{} is {}".format(self.policy_id, self.vm_id, status.status))

    def cleanup(self):
        '''
        Delete the policy and power off the virtual machine.
        '''
        if self.policy_id is not None:
            print("Deleting the policy {}".format(self.policy_id))
            self.client.vcenter.compute.Policies.delete(self.policy_id)

        if self.vm_info.power_state == Power.State.POWERED_ON:
            print("Powering off {}".format(self.vm_name))
            self.client.vcenter.vm.Power.stop(self.vm_id)


def main():
    cp_workflow = ComputePolicyWorkflow()
    cp_workflow.run()
    if cp_workflow.cleardata:
        cp_workflow.cleanup()


if __name__ == '__main__':
    main()
