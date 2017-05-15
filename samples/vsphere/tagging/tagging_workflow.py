#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) VMware, Inc. 2014, 2016. All Rights Reserved.
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

from com.vmware.cis.tagging_client import (
    Category, CategoryModel, Tag, TagAssociation)
from com.vmware.vapi.std_client import DynamicID

from samples.vsphere.common.sample_base import SampleBase
from samples.vsphere.common.vim.helpers.get_cluster_by_name import get_cluster_id


class TaggingWorkflow(SampleBase):
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
        SampleBase.__init__(self, self.__doc__)
        self.servicemanager = None

        self.category_svc = None
        self.tag_svc = None
        self.tag_association = None

        self.category_name = None
        self.category_desc = None
        self.tag_name = None
        self.tag_desc = None

        self.cluster_name = None
        self.cluster_moid = None
        self.category_id = None
        self.tag_id = None
        self.tag_attached = False
        self.dynamic_id = None

    def _options(self):
        self.argparser.add_argument('-clustername', '--clustername', help='Name of the cluster to be tagged')
        self.argparser.add_argument('-categoryname', '--categoryname', help='Name of the Category to be created')
        self.argparser.add_argument('-categorydesc', '--categorydesc', help='Description of the Category to be created')
        self.argparser.add_argument('-tagname', '--tagname', help='Name of the tag to be created')
        self.argparser.add_argument('-tagdesc', '--tagdesc', help='Description of the tag to be created')

    def _setup(self):
        if self.cluster_name is None:  # for testing
            self.cluster_name = self.args.clustername
        assert self.cluster_name is not None
        print('Cluster Name: {0}'.format(self.cluster_name))

        if self.category_name is None:
            self.category_name = self.args.categoryname
        assert self.category_name is not None
        print('Category Name: {0}'.format(self.category_name))

        if self.category_desc is None:
            self.category_desc = self.args.categorydesc
        assert self.category_desc is not None
        print('Category Description: {0}'.format(self.category_desc))

        if self.tag_name is None:
            self.tag_name = self.args.tagname
        assert self.tag_name is not None
        print('Tag Name: {0}'.format(self.tag_name))

        if self.tag_desc is None:
            self.tag_desc = self.args.tagdesc
        assert self.tag_desc is not None
        print('Tag Description: {0}'.format(self.tag_desc))

        if self.servicemanager is None:
            self.servicemanager = self.get_service_manager()

        # Sample is not failing if Clustername passed is not valid
        # Validating if Cluster Name passed is Valid
        print('finding the cluster {0}'.format(self.cluster_name))
        self.cluster_moid = get_cluster_id(service_manager=self.servicemanager, cluster_name=self.cluster_name)
        assert self.cluster_moid is not None
        print('Found cluster:{0} mo_id:{1}'.format(self.cluster_name, self.cluster_moid))

        self.category_svc = Category(self.servicemanager.stub_config)
        self.tag_svc = Tag(self.servicemanager.stub_config)
        self.tag_association = TagAssociation(self.servicemanager.stub_config)

    def _execute(self):
        print('List all the existing categories user has access to...')
        categories = self.category_svc.list()
        if len(categories) > 0:
            for category in categories:
                print('Found Category: {0}'.format(category))
        else:
            print('No Tag Category Found...')

        print('List all the existing tags user has access to...')
        tags = self.tag_svc.list()
        if len(tags) > 0:
            for tag in tags:
                print('Found Tag: {0}'.format(tag))
        else:
            print('No Tag Found...')

        print('creating a new tag category...')
        self.category_id = self.create_tag_category(self.category_name, self.category_desc,
                                                    CategoryModel.Cardinality.MULTIPLE)
        assert self.category_id is not None
        print('Tag category created; Id: {0}'.format(self.category_id))

        print("creating a new Tag...")
        self.tag_id = self.create_tag(self.tag_name, self.tag_desc, self.category_id)
        assert self.tag_id is not None
        print('Tag created; Id: {0}'.format(self.tag_id))

        print('updating the tag...')
        date_time = time.strftime('%d/%m/%Y %H:%M:%S')
        self.update_tag(self.tag_id, 'Server Tag updated at ' + date_time)
        print('Tag updated; Id: {0}'.format(self.tag_id))

        print('Tagging the cluster {0}...'.format(self.cluster_name))
        self.dynamic_id = DynamicID(type='ClusterComputeResource', id=self.cluster_moid)
        self.tag_association.attach(tag_id=self.tag_id, object_id=self.dynamic_id)
        for tag_id in self.tag_association.list_attached_tags(self.dynamic_id):
            if tag_id == self.tag_id:
                self.tag_attached = True
                break
        assert self.tag_attached
        print('Tagged cluster: {0}'.format(self.cluster_moid))

    def _cleanup(self):
        try:
            if self.tag_attached:
                self.tag_association.detach(self.tag_id, self.dynamic_id)
                print('Removed tag from cluster: {0}'.format(self.cluster_moid))

            if self.tag_id is not None:
                self.delete_tag(self.tag_id)
                print('Tag deleted; Id: {0}'.format(self.tag_id))

            if self.category_id is not None:
                self.delete_tag_category(self.category_id)
                print('Tag category deleted; Id: {0}'.format(self.category_id))
        except Exception as e:
            raise Exception(e)

    def create_tag_category(self, name, description, cardinality):
        """create a category. User who invokes this needs create category privilege."""
        create_spec = self.category_svc.CreateSpec()
        create_spec.name = name
        create_spec.description = description
        create_spec.cardinality = cardinality
        associableTypes = set()
        create_spec.associable_types = associableTypes
        return self.category_svc.create(create_spec)

    def delete_tag_category(self, category_id):
        """Deletes an existing tag category; User who invokes this API needs
        delete privilege on the tag category.
        """
        self.category_svc.delete(category_id)

    def create_tag(self, name, description, category_id):
        """Creates a Tag"""
        create_spec = self.tag_svc.CreateSpec()
        create_spec.name = name
        create_spec.description = description
        create_spec.category_id = category_id
        return self.tag_svc.create(create_spec)

    def update_tag(self, tag_id, description):
        """Update the description of an existing tag.
        User who invokes this API needs edit privilege on the tag.
        """
        update_spec = self.tag_svc.UpdateSpec()
        update_spec.setDescription = description
        self.tag_svc.update(tag_id, update_spec)

    def delete_tag(self, tag_id):
        """Delete an existing tag.
        User who invokes this API needs delete privilege on the tag."""
        self.tag_svc.delete(tag_id)


def main():
    tagging_workflow = TaggingWorkflow()
    tagging_workflow.main()


# Start program
if __name__ == '__main__':
    main()
