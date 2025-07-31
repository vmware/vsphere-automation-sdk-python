#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) VMware, Inc. 2019. All Rights Reserved.
* SPDX-License-Identifier: MIT
* *******************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
"""

from getpass import getpass
from pprint import pprint

from vmware.vapi.vsphere.client import create_vsphere_client
from com.vmware.vapi.std.errors_client import NotFound, InvalidArgument, AlreadyExists

from samples.vsphere.common import sample_cli
from samples.vsphere.common import sample_util
from samples.vsphere.common.ssl_helper import get_unverified_session


class LocalAccounts:

    def __init__(self):
        parser = sample_cli.build_arg_parser()
        args = sample_util.process_cli_args(parser.parse_args())
        session = get_unverified_session() if args.skipverification else None
        self.client = create_vsphere_client(server=args.server,
                                            username=args.username,
                                            password=args.password,
                                            session=session)
        self.local_accounts = self.client.appliance.LocalAccounts

    def run(self):
        """
        Running the workflow for Local accounts.
        It creates local account and updates its default security settings.
        Deletes the created local account at the end.
        """

        print("Listing available accounts")
        self.list_accounts()

        print("Create local account for yourself")
        local_user = self.create_local_account()

        print("Updating the local accounts security settings")
        self.update_local_account_security(local_user)

        print("Get information for specific account")
        self.get_account_info()

        print("Deleting the local account")
        self.delete_local_account(local_user)

    def get_account_info(self):
        try:
            username = input("username ::")
            pprint(self.local_accounts.get(username))
        except NotFound as e:
            print("Local Account mentioned is not found")

    def list_accounts(self):
        pprint(self.local_accounts.list())

    def create_local_account(self):
        account_created = False
        try:
            config = self.local_accounts.Config()
            print("The following are minimum details required to create local account")
            username = input("username of local account ::")
            config.password = getpass("password ::")
            print("Roles can be operator, admin, superAdmin.")
            config.roles = [input("role :: ")]
            config.full_name = input("Full name of user ::")

            self.local_accounts.create(username=username, config=config)
            print("Listing available accounts after creation of " + username)
            self.list_accounts()
            account_created = True
        except AlreadyExists as e:
            print("local account is already present")
        except InvalidArgument as e:
            print(str(e))
        return username if account_created else None

    def update_local_account_security(self, username):
        # update the account security settings with custom default
        config = self.local_accounts.UpdateConfig()
        config.days_after_password_expiration = 1
        config.inactive_after_password_expiration = True
        config.warn_days_before_password_expiration = 7
        self.list_accounts()
        try:
            if username is not None:
                self.local_accounts.update(username, config)
        except NotFound as e:
            print("Local Account mentioned is not found")

    def delete_local_account(self, username):
        if username is not None:
            self.local_accounts.delete(username=username)
            print("Listing available accounts after deletion of " + username)
            self.list_accounts()


def main():
    try:
        local_accounts = LocalAccounts()
        local_accounts.run()
    except Exception:
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
