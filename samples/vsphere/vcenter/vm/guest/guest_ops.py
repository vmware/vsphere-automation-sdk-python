#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) VMware, Inc. 2020. All Rights Reserved.
* SPDX-License-Identifier: MIT
* *******************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
"""

__author__ = 'VMware Inc.'
__vcenter_version__ = 'VCenter 7.0 U2'

import os
import ssl
import time

from com.vmware.vcenter.vm.guest.filesystem_client import Transfers
from com.vmware.vcenter.vm.guest_client import Credentials
from com.vmware.vcenter.vm.guest_client import Processes
from com.vmware.vcenter_client import VM
from samples.vsphere.common import sample_cli
from samples.vsphere.common import sample_util
from samples.vsphere.common.ssl_helper import get_unverified_session
from vmware.vapi.vsphere.client import create_vsphere_client

try:
    # Python 3
    from urllib.parse import urlparse
    import http.client as httpclient
except ImportError:
    # Python 2
    from urlparse import urlparse
    import httplib as httpclient


class GuestOps(object):
    """
    Demonstrate the vAPI Guest Operations.

    Show the basic procedure to start a program or process on a Linux
    guest VM and collect any output:
        - create a temporary directory and temporary files for the process
          stdout and stderr.
        - upload a script to the guest.
        - execute the script and collect the output.

    Prerequisites:
        - vCenter
        - ESX host
        - running guest 'Photon-3.2-64-EFI-Open-VM-Tools-for-GuestOps-SDK'
          with open-vm-tools installed and running.  The testbed created by
          samples/vsphere/vcenter/setup/main.py does not contain a guest
          with a runnable Linux or Windows OS.
    """

    # Create the Process.CreateSpec for initiating processes in the guest
    def _process_create_spec(self, path, args=None, dir=None, env={}):
        return Processes.CreateSpec(path=path,
                                    arguments=args,
                                    working_directory=dir,
                                    environment_variables=env)

    # Create the Transfer.CreateSpec for the file transfer to/from the guest
    def _create_transfer_spec(self,
                              path,
                              attributes=None):
        return Transfers.CreateSpec(attributes=attributes,
                                    path=path)

    # Create a FileAttributeCreateSpec for a generic (non-OS specific) guest
    def _fileAttributeCreateSpec_Plain(self,
                                       size,
                                       overwrite=None,
                                       last_modified=None,
                                       last_accessed=None):
        return Transfers.FileCreationAttributes(size,
                                                overwrite=overwrite,
                                                last_modified=last_modified,
                                                last_accessed=last_accessed)

    # Create a FileAttributeCreateSpec for a linux (Posix) guest
    def _fileAttributeCreateSpec_Linux(self,
                                       size,
                                       overwrite=None,
                                       last_modified=None,
                                       last_accessed=None,
                                       owner_id=None,
                                       group_id=None,
                                       permissions=None):
        posix = Transfers.PosixFileAttributesCreateSpec(owner_id=owner_id,
                                                        group_id=group_id,
                                                        permissions=permissions)
        return Transfers.FileCreationAttributes(size,
                                                overwrite=overwrite,
                                                last_modified=last_modified,
                                                last_accessed=last_accessed,
                                                posix=posix)

    def _download(self,
                  url,
                  expectedLen=None):
        urloptions = urlparse(url)
        # Skip server cert verification.
        # This is not recommended in production code.
        conn = httpclient.HTTPSConnection(urloptions.netloc,
                                          context=ssl._create_unverified_context())

        conn.request("GET", urloptions.path + "?" + urloptions.query)
        res = conn.getresponse()
        if res.status != 200:
            print("GET request failed with errorcode : %s" % res.status)
            raise HTTPError(res.status, res.reason)
        body = res.read().decode()

        return body

    def _upload(self, url, body):
        urloptions = urlparse(url)
        conn = httpclient.HTTPSConnection(urloptions.netloc,
                                          context=ssl._create_unverified_context())

        headers = {"Content-Length": len(body)}
        # Skip server cert verification.
        # This is not recommended in production code.
        conn.request("PUT", urloptions.path + "?" + urloptions.query,
                     body,
                     headers)
        res = conn.getresponse()
        if res.status != 200:
            print("PUT request failed with errorcode : %s" % res.status)
            raise HTTPError(res.status, res.reason)

        return res

    def __init__(self):
        # Create argument parser for standard inputs:
        # server, username, password, cleanup and skipverification
        parser = sample_cli.build_arg_parser()

        # Add your custom input arguments
        parser.add_argument('--vm_name',
                            action='store',
                            help='Name of the testing vm')
        parser.add_argument('--root_user',
                            action='store',
                            help='Administrator account user name')
        parser.add_argument('--root_passwd',
                            action='store',
                            help='Administrator account password')

        args = sample_util.process_cli_args(parser.parse_args())
        self.vm_name = args.vm_name
        self.root_user = args.root_user
        self.root_passwd = args.root_passwd

        self.cleardata = args.cleardata

        # Skip server cert verification if needed.
        # This is not recommended in production code.
        session = get_unverified_session() if args.skipverification else None

        # Connect to vSphere client
        self.client = create_vsphere_client(server=args.server,
                                            username=args.username,
                                            password=args.password,
                                            session=session)

    def run(self):
        # Using vAPI to find VM.
        filter_spec = VM.FilterSpec(names=set([self.vm_name]))
        vms = self.client.vcenter.VM.list(filter_spec)
        if len(vms) != 1:
            raise Exception('Could not locate the required VM with name ' +
                            self.vm_name + '. Please create the vm first.')
        if vms[0].power_state != 'POWERED_ON':
            raise Exception('VM is not powered on: ' + vms[0].power_state)
        vm_id = vms[0].vm

        # Check that vmtools svc (non-interactive user) is running.
        info = self.client.vcenter.vm.guest.Operations.get(vm_id)
        if info.guest_operations_ready is not True:
            raise Exception('VMware Tools/open-vm-tools is not running as required.')

        # Establish the user credentials that will be needed for all Guest Ops
        # APIs.
        creds = Credentials(interactive_session=False,
                            user_name=self.root_user,
                            password=self.root_passwd,
                            type=Credentials.Type.USERNAME_PASSWORD)

        # Step 2 - Create a temporary directory from which to run the command
        #          and capture any output
        tempDir = self.client.vcenter.vm.guest.filesystem.Directories.create_temporary(
                    vm_id, creds, '', '', parent_path=None)

        # Step 3 - Create temproary files to reveive stdout and stderr
        #          as needed.
        stdout = self.client.vcenter.vm.guest.filesystem.Files.create_temporary(
                   vm_id, creds, '', '.stdout', parent_path=tempDir)
        stderr = self.client.vcenter.vm.guest.filesystem.Files.create_temporary(
                   vm_id, creds, '', '.stderr', parent_path=tempDir)

        # Step 4 - (Optional)  copy in the script to be run.
        #          While optional, using this step to demo tranfer of a
        #          file to a guest.
        scriptPath = self.client.vcenter.vm.guest.filesystem.Files.create_temporary(
                       vm_id, creds, '', '.sh', tempDir)

        # Create script contents and transfer to the guest.
        # TODO: Need generic pick up of script content
        baseFN = os.path.basename(scriptPath)
        script = ('#! /bin/bash\n'
                  '#    ' +
                  baseFN + '\n'
                  '\n'
                  'sleep 5    # Adding a little length to the process.\n'
                  'ps -ef\n'
                  'echo\n'
                  'rpm -qa | sort\n'
                  '\n')
        print(script)
        attr = self._fileAttributeCreateSpec_Linux(size=len(script),
                                                   overwrite=True,
                                                   permissions='0755')
        spec = self._create_transfer_spec(path=scriptPath,
                                          attributes=attr)
        toURL = self.client.vcenter.vm.guest.filesystem.Transfers.create(vm_id,
                                                                         creds,
                                                                         spec)
        res = self._upload(toURL, script)

        # Check that the uploaded file size is correct.
        info = self.client.vcenter.vm.guest.filesystem.Files.get(vm_id,
                                                                 creds,
                                                                 scriptPath)
        if info.size != len(script):
            raise Exception('Uploaded file size not as epected.')

        # Step 5 - Start the program on the guest, capturing stdout and stderr
        # in the separate temp files obtained earlier.
        options = (" > " + stdout + " 2> " + stderr)

        spec = self._process_create_spec(scriptPath,
                                         args=options,
                                         dir=tempDir)
        pid = self.client.vcenter.vm.guest.Processes.create(vm_id, creds, spec)
        print('process created with pid: %s\n' % pid)

        # Step 6
        # Need a loop to wait for the process to finish to handle longer
        # running processes.
        while True:
            time.sleep(1.0)
            try:
                # List the single process for pid.
                result = self.client.vcenter.vm.guest.Processes.get(vm_id,
                                                                    creds,
                                                                    pid)
                if result.exit_code is not None:
                    print('Command: ' + result.command)
                    print('Exit code: %s\n' % result.exit_code)
                    break
                if result.finished is None:
                    print('Process with pid %s is still running.' % pid)
                    continue
            except Exception as e:
                raise e

        # Step 7 Copy out the results (stdout).
        spec = self._create_transfer_spec(path=stdout)
        # create the download URL
        fromURL = self.client.vcenter.vm.guest.filesystem.Transfers.create(vm_id,
                                                                           creds,
                                                                           spec)
        body = self._download(fromURL, expectedLen=info.size)
        print("-----------  stdout  ------------------")
        print(body)
        print("---------------------------------------")

        # Optionally the contents of "stderr" could be downloaded.

        # And finally, clean up the temporary files and directories on the
        # Linux guest.  Deleting the temporary diretory and its contents.
        self.client.vcenter.vm.guest.filesystem.Directories.delete(vm_id,
                                                                   creds,
                                                                   tempDir,
                                                                   recursive=True)


def main():
    sample = GuestOps()
    sample.run()


if __name__ == '__main__':
    main()
