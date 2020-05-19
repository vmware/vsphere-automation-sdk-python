import argparse
import requests

from vmware.vapi.vmc.client import create_vmc_client

parser = argparse.ArgumentParser()
parser.add_argument(
        '--refresh_token',
        required=True,
        help='VMware Cloud API refresh token')

parser.add_argument(
        '--org_id',
        required=True,
        help='Organization identifier.')

parser.add_argument(
        '--sddc_id',
        required=True,
        help='Sddc Identifier.')

args = parser.parse_args()
refresh_token = args.refresh_token
org_id = args.org_id
sddc_id = args.sddc_id

client = create_vmc_client(refresh_token)
site_recovery_activation_task = client.draas.SiteRecovery.get(org_id, sddc_id)
print(site_recovery_activation_task)
