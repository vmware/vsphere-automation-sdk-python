#!/usr/bin/env python
"""
* *******************************************************
* Copyright (c) VMware, Inc. 2014, 2016, 2018 All Rights Reserved.
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
__copyright__ = 'Copyright 2014, 2016 VMware, Inc. All rights reserved.'
__vcenter_version__ = '6.0+'

import time
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim, vmodl

from com.vmware.cis.tagging_client import (Category, CategoryModel, Tag,
                                           TagAssociation)
from com.vmware.vcenter_client import Cluster
from com.vmware.vapi.std_client import DynamicID

from vmware.vapi.vsphere.client import create_vsphere_client

from samples.vsphere.common import vapiconnect
from samples.vsphere.common.vim.helpers import vim_utils
from samples.vsphere.common import sample_cli
from samples.vsphere.common import sample_util
from samples.vsphere.common.ssl_helper import get_unverified_session
from samples.vsphere.common.ssl_helper import get_unverified_context
from samples.vsphere.common.vim.helpers.get_cluster_by_name import get_cluster_id


class TaggingWorkflow:
    """
    Demonstrates tagging CRUD operations
    Step 1: Create a Tag category.
    Step 2: Create a Tag under the category.
    Step 3: Retrieve the managed object id of an existing cluster from its name.
    Step 4: Assign the tag to the cluster.
    Additional steps when clearData flag is set to TRUE:
    Step 5: Detach the tag from the cluster.
    Step 6: Delete the tag.
    Step 7: Delete the tag category.
    Note: the sample needs an existing cluster
    """

    def __init__(self):

        parser = sample_cli.build_arg_parser()

        parser.add_argument(
            '--clustername',
            action='store',
            required=True,
            help='Name of the cluster to be tagged')

        parser.add_argument(
            '--categoryname',
            action='store',
            required=True,
            help='Name of the Category to be created')

        parser.add_argument(
            '--categorydesc',
            action='store',
            default='Sample category description',
            help='Description of the Category to be created')

        parser.add_argument(
            '--tagname',
            action='store',
            required=True,
            help='Name of the tag to be created')

        parser.add_argument(
            '--tagdesc',
            action='store',
            default='Sample tag description',
            help='Description of the tag to be created')

        args = sample_util.process_cli_args(parser.parse_args())
        self.cleardata = args.cleardata
        self.cluster_name = args.clustername
        self.category_name = args.categoryname
        self.category_desc = args.categorydesc
        self.tag_name = args.tagname
        self.tag_desc = args.tagdesc
        self.skip_verification = args.skipverification

        session = get_unverified_session() if args.skipverification else None

        # Connect to vSphere client
        self.client = create_vsphere_client(
            server=args.server,
            username=args.username,
            password=args.password,
            session=session)

        # For vSphere 6.0 users, use pyVmomi to get the cluster ID
        context = get_unverified_context() if self.skip_verification else None
        si = SmartConnect(
            host=args.server,
            user=args.username,
            pwd=args.password,
            sslContext=context)

        cluster_obj = vim_utils.get_obj(
            content=si.RetrieveContent(),
            vimtype=[vim.ClusterComputeResource],
            name=args.clustername)

        if cluster_obj:
            self.cluster_moid = cluster_obj._GetMoId()
            print('Found cluster:{} mo_id:{}'.format(self.cluster_name,
                                                     self.cluster_moid))
        else:
            raise ValueError('Cluster with name "{}" not found'.format(
                self.cluster_name))

        # Note: for vSphere 6.5+ users, use vSphere Automation APIs to get the cluster ID
        # filter_spec = Cluster.FilterSpec(names=set([self.cluster_name]))
        # cluster_summaries = self.client.vcenter.Cluster.list(filter_spec)
        # if len(cluster_summaries) > 0:
        #     self.cluster_moid = cluster_summaries[0].cluster

    def run(self):
        print('List all the existing categories user has access to...')
        categories = self.client.tagging.Category.list()
        if len(categories) > 0:
            for category in categories:
                print('Found Category: {0}'.format(category))
        else:
            print('No Tag Category Found...')

        print('List all the existing tags user has access to...')
        tags = self.client.tagging.Tag.list()
        if len(tags) > 0:
            for tag in tags:
                print('Found Tag: {0}'.format(tag))
        else:
            print('No Tag Found...')

        print('creating a new tag category...')
        self.category_id = self.create_tag_category(
            self.category_name, self.category_desc,
            CategoryModel.Cardinality.MULTIPLE)
        assert self.category_id is not None
        print('Tag category created; Id: {0}'.format(self.category_id))

        print("Get category name and description...")
        category_ids = self.client.tagging.Category.list()
        for category_id in category_ids:
            category_model = self.client.tagging.Category.get(category_id)
            print("Category ID '{}', name '{}', description '{}'".format(
                category_model.id, category_model.name, category_model.description
            ))

        print("creating a new Tag...")
        self.tag_id = self.create_tag(self.tag_name, self.tag_desc,
                                      self.category_id)
        assert self.tag_id is not None
        print('Tag created; Id: {0}'.format(self.tag_id))

        print("Get tag name and description...")
        tag_ids = self.client.tagging.Tag.list()
        for tag_id in tag_ids:
            tag_model = self.client.tagging.Tag.get(tag_id)
            print("Tag ID '{}', name '{}', description '{}'".format(
                tag_model.id, tag_model.name, tag_model.description
            ))

        print('updating the tag...')
        date_time = time.strftime('%d/%m/%Y %H:%M:%S')
        self.update_tag(self.tag_id, 'Server Tag updated at ' + date_time)
        print('Tag updated; Id: {0}'.format(self.tag_id))

        print('Tagging the cluster {0}...'.format(self.cluster_name))
        self.dynamic_id = DynamicID(
            type='ClusterComputeResource', id=self.cluster_moid)
        self.client.tagging.TagAssociation.attach(
            tag_id=self.tag_id, object_id=self.dynamic_id)
        for tag_id in self.client.tagging.TagAssociation.list_attached_tags(
                self.dynamic_id):
            if tag_id == self.tag_id:
                self.tag_attached = True
                break
        assert self.tag_attached
        print('Tagged cluster: {0}'.format(self.cluster_moid))

    def cleanup(self):
        if self.cleardata:
            if self.tag_attached:
                self.client.tagging.TagAssociation.detach(
                    self.tag_id, self.dynamic_id)
                print('Removed tag from cluster: {0}'.format(
                    self.cluster_moid))

            if self.tag_id is not None:
                self.delete_tag(self.tag_id)
                print('Tag deleted; Id: {0}'.format(self.tag_id))

            if self.category_id is not None:
                self.delete_tag_category(self.category_id)
                print('Tag category deleted; Id: {0}'.format(self.category_id))

    def create_tag_category(self, name, description, cardinality):
        """create a category. User who invokes this needs create category privilege."""
        create_spec = self.client.tagging.Category.CreateSpec()
        create_spec.name = name
        create_spec.description = description
        create_spec.cardinality = cardinality
        associableTypes = set()
        create_spec.associable_types = associableTypes
        return self.client.tagging.Category.create(create_spec)

    def delete_tag_category(self, category_id):
        """Deletes an existing tag category; User who invokes this API needs
        delete privilege on the tag category.
        """
        self.client.tagging.Category.delete(category_id)

    def create_tag(self, name, description, category_id):
        """Creates a Tag"""
        create_spec = self.client.tagging.Tag.CreateSpec()
        create_spec.name = name
        create_spec.description = description
        create_spec.category_id = category_id
        return self.client.tagging.Tag.create(create_spec)

    def update_tag(self, tag_id, description):
        """Update the description of an existing tag.
        User who invokes this API needs edit privilege on the tag.
        """
        update_spec = self.client.tagging.Tag.UpdateSpec()
        update_spec.setDescription = description
        self.client.tagging.Tag.update(tag_id, update_spec)

    def delete_tag(self, tag_id):
        """Delete an existing tag.
        User who invokes this API needs delete privilege on the tag."""
        self.client.tagging.Tag.delete(tag_id)


def main():
    tagging_workflow = TaggingWorkflow()
    tagging_workflow.run()
    tagging_workflow.cleanup()


if __name__ == '__main__':
    main()
