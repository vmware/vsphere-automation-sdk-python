#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) VMware, Inc. 2023. All Rights Reserved.
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
__vcenter_version__ = '8.0u1+'

import urllib.request
import concurrent.futures
import asyncio
import requests
import logging
import sys
import ssl
from vmware.vapi.vsphere.client import create_vsphere_client
from com.vmware.vcenter.authorization_client import PrivilegeChecks
from pyVim.connect import SmartConnect
from pyVmomi import vim, VmomiSupport

from samples.vsphere.common import sample_cli
from samples.vsphere.common import sample_util
from samples.vsphere.common.ssl_helper import get_unverified_session
from six.moves import http_client, urllib
from os import path
from time import sleep

"""
Creates a virtual machine from an ovf template
and then retrieves the minimal set of privileges
required for the performed workflow

The vm create workflow can be swapped
for any other desired vCenter workflow
like e.g. network/host configuration,
vCenter upgrade etc.

Sample Prerequisites:
    - Existing vCenter environment with at least 1 host
    - The user executing the script should have at least Sessions.CollectPrivilegeChecks
    to invoke the PrivilegeChecks API.
    However VM creation and other workflows will require different set of privileges.
    The script is intended to be executed by an administrator or another privileged user.
"""

parser = sample_cli.build_arg_parser()

parser.add_argument("--host_moId",
                    help="Host's moId on which to deploy vm",
                    required=True)
parser.add_argument("--ovf_url",
                    help="Url to the ovf from which to create vm",
                    required=True)
parser.add_argument('--vm_name',
                    default='Sample_Default_VM_for_Simple_Testbed',
                    help='Name of the testing vm')
parser.add_argument("--dc_moId",
                    help="Datacenter's moId under which to create vm.")
parser.add_argument("--ds_moId",
                    help="Datastore's moId which to use for vm storage")
parser.add_argument("--rp_moId",
                    help="Resource pool's moId")
parser.add_argument("--opId",
                    help="opId which to use for vc invocations in order to track used privileges",
                    default="create-vm-opId")


class OpId:

    def __init__(self, opId):
        self.opId = opId

    def __enter__(self, name=None):
        reqCtx = VmomiSupport.GetRequestContext()
        self.prevId = reqCtx[
            'operationID'] if 'operationID' in reqCtx else None
        reqCtx["operationID"] = self.opId
        return self

    def __exit__(self, *args):
        reqCtx = VmomiSupport.GetRequestContext()
        if self.prevId is not None:
            reqCtx['operationID'] = self.prevId
        else:
            del reqCtx['operationID']


class OvfDeployer:
    def __init__(self, args):
        self.logger = logging.getLogger("ovf-deploy")
        self.logger.addHandler(logging.StreamHandler(sys.stdout))
        self.logger.setLevel(logging.DEBUG)
        self.context = ssl._create_unverified_context() if args.skipverification else None
        self.si = SmartConnect(host=args.server,
                               user=args.username,
                               pwd=args.password,
                               sslContext=self.context)
        self.base_url = path.dirname(args.ovf_url)
        self.ovf_content = self.get_ovf_content(args.ovf_url)
        self.container_view = None
        self.host = vim.HostSystem(args.host_moId, self.si._stub)
        self.datacenter = self.get_datacenter(args)
        self.datastore = self.get_datastore(args)
        self.resource_pool = self.get_resource_pool(args)
        self.vm_name = args.vm_name
        # Set config options
        self.set_vpxd_option(self.si, "config.vpxd.privCheck.bufferSize",
                             "5000000")
        self.set_vpxd_option(self.si, "config.vpxd.privCheck.cleanupInterval",
                             "1000")

    def __del__(self):
        # Unset config options
        self.set_vpxd_option(self.si, "config.vpxd.privCheck.bufferSize", "0")
        self.set_vpxd_option(self.si, "config.vpxd.privCheck.cleanupInterval",
                             "0")

    async def deploy(self):
        import_spec = self.create_import_spec()
        lease = self.import_vapp(import_spec)
        await self.upload_files(lease, import_spec.fileItem)
        lease.Progress(100)
        lease.Complete()

    def set_vpxd_option(self, si, key, val):
        optionVal = vim.option.OptionValue()
        optionVal.key = key
        optionVal.value = val
        optionVals = [optionVal]
        om = si.content.setting
        om.UpdateValues(optionVals)

    def get_ovf_content(self, ovf_url):
        return urllib.request.urlopen(ovf_url).read()

    def create_import_spec(self):
        importSpecParams = vim.OvfManager.CreateImportSpecParams(
            ipAllocationPolicy='dhcpPolicy',
            ipProtocol='IPv4',
            diskProvisioning='thin',
            entityName=self.vm_name)
        spec = self.si.content.ovfManager.CreateImportSpec(
            ovfDescriptor=self.ovf_content.decode(),
            resourcePool=self.resource_pool,
            datastore=self.datastore,
            cisp=importSpecParams)
        return spec

    def import_vapp(self, import_spec):
        lease = self.resource_pool.ImportVApp(import_spec.importSpec,
                                              self.datacenter.vmFolder,
                                              self.host)
        while lease.state == vim.HttpNfcLease.State.initializing:
            sleep(1)

        assert lease.state == vim.HttpNfcLease.State.ready
        return lease

    async def upload_files(self, lease, file_items):
        upload_map = {}
        for device_url in lease.info.deviceUrl:
            upload_map[device_url.importKey] = [device_url.key, device_url.url]

        loop = asyncio.get_event_loop()
        upload_tasks = []
        with concurrent.futures.ThreadPoolExecutor() as pool:
            for file_item in file_items:
                _, dst_url = upload_map[file_item.deviceId]
                upload_tasks.append(
                    loop.run_in_executor(pool, self.upload_file,
                                         *[file_item, dst_url]))
            await asyncio.wait(upload_tasks, return_when=asyncio.ALL_COMPLETED,
                               timeout=2 * 60 * 60)

    def upload_file(self, file_item, dst_url):
        src_url = "{}/{}".format(self.base_url, file_item.path)
        src_req = requests.get(src_url, verify=False, stream=True)
        assert src_req.ok
        parsed_url = urllib.parse.urlparse(dst_url)
        dst_req = http_client.HTTPSConnection(self.host.name,
                                              context=self.context)
        request_type = "PUT" if file_item.create else "POST"
        dst_req.putrequest(request_type, parsed_url.path)
        dst_req.putheader('Content-Length', file_item.size)
        dst_req.endheaders()
        chunk = min(64 * 1024, file_item.size)
        for content_chunk in src_req.iter_content(chunk_size=chunk):
            dst_req.send(content_chunk)
        dst_req.close()
        src_req.close()

    async def _wait_for_task(self, task):
        state = task.info.state
        error = task.info.error
        while state not in (
                vim.TaskInfo.State.success, vim.TaskInfo.State.error):
            if state not in ['running', 'success']:
                self.logger.debug(
                    'task state is not expected:\n %s' % task.info)
            await asyncio.sleep(3)
            self.logger.info('%s progress=%s' % (task, task.info.progress))
        if state != vim.TaskInfo.State.success:
            self.logger.debug(task.info)
            raise error
        self.logger.info('%s' % task.info)

    def _get_container_view(self):
        if self.container_view is not None:
            return self.container_view
        self.container_view = self.si.RetrieveContent().viewManager.CreateContainerView(
            self.host, recursive=False)
        return self.container_view

    def get_datacenter(self, args):
        if args.dc_moId:
            return vim.Datacenter(args.dc_moId, self.si._stub)
        container_view = self._get_container_view()
        return self.get_parent(container_view.container, vim.Datacenter)

    def get_resource_pool(self, args):
        if args.rp_moId:
            return vim.ResourcePool(args.rpId, self.si._stub)
        container_view = self._get_container_view()
        compute_resource = self.get_parent(container_view.container,
                                           vim.ComputeResource) or \
                           self.get_parent(container_view.container,
                                           vim.ClusterComputeResource)
        return compute_resource.resourcePool

    def get_datastore(self, args):
        if args.ds_moId:
            return vim.Datastore(args.ds_moId, self.si._stub)
        container_view = self._get_container_view()
        return container_view.container.datastore[0]

    def get_parent(self, container, parent_type):
        parent = container.parent
        while type(parent) is not parent_type:
            if not hasattr(parent, "parent"):
                return None
            parent = parent.parent
        return parent


args = sample_util.process_cli_args(parser.parse_args())
deployer = OvfDeployer(args)
with OpId(args.opId) as opId:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait([deployer.deploy()]))

session = get_unverified_session() if args.skipverification else None
client = create_vsphere_client(server=args.server,
                               username=args.username,
                               password=args.password,
                               session=session)
user, domain = args.username.split("@")
principal = PrivilegeChecks.Principal(name=user, domain=domain)
filterSpec = PrivilegeChecks.FilterSpec(op_ids={args.opId},
                                        principals=[principal])
iterationSpec = PrivilegeChecks.IterationSpec(size=50)
checks = PrivilegeChecks(client._stub_config).list(filter=filterSpec,
                                                   iteration=iterationSpec)

for item in checks.items:
    print(
        f"Object: {item.object.type}:{item.object.id},"
        f" Privilege: {item.privilege},"
        f" Principal: {item.principal.name}@{item.principal.domain}")
del deployer
