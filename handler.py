from __future__ import print_function

import base64
import json
import os
import requests
import time


__version__ = '0.1.0'


def _remove_containers(host, headers):
    url = host['links']['instances']
    res = requests.get(url, headers=headers)
    res_data = res.json()
    if res_data['data'] and len(res_data['data']) > 0:
        for container in res_data['data']:
            url = container['links']['self'] + '/?action=stop'
            res = requests.post(url, headers=headers, data={
                "remove": True,
                "timeout": 0
            })


def _delete_host(host, headers):
    # First deactivate the host
    url = host['links']['self']
    res = requests.post(url + '/?action=deactivate', headers=headers)

    # Wait for host to be inactive
    res = requests.get(url, headers=headers)
    res_data = res.json()
    state = res_data['state']
    count = 0
    while state != 'inactive' and count < 60:
        res = requests.get(url, headers=headers)
        count += 1
        time.sleep(0.5)

    # Now remove the host
    res = requests.post(url + '/?action=remove', headers=headers)


def lambda_handler(event, context):
    print("Starting ...")
    host = os.getenv('RANCHER_URL')
    access_key = os.getenv('RANCHER_ACCESS_KEY', None)
    secret_key = os.getenv('RANCHER_SECRET_KEY', None)
    message = json.loads(event['Records'][0]['Sns']['Message'])
    project_id = message['rancher_project_id']
    instance_id = message['instance_id']
    base_url = '{0}/v1/projects/{1}'.format(host, project_id)

    if message['event'] != 'AWS_EC2_INSTANCE_TERMINATED':
        return
    if access_key is None or secret_key is None:
        print("ERROR: Invalid Rancher keys")
        return

    api_token = base64.b64encode("{0}:{1}".format(access_key, secret_key))
    headers = {
        'Authorization': 'Basic {0}'.format(api_token)
    }
    # Load the hosts from rancher and find the one whose label
    # spotinst.instanceId matches the instance_id from the message
    res = requests.get(base_url + "/hosts", headers=headers)
    res_data = res.json()
    label = 'spotinst.instanceId'
    if res_data['data'] and len(res_data['data']) > 0:
        for host in res_data['data']:
            if label in host['labels'] and host['labels'][label] == instance_id:
                print('Removing containers from host {0}'.format(host['id']))
                _remove_containers(host, headers)

                print ('Removing host {0}'.format(host['id']))
                _delete_host(host, headers)
                break

    print("done")

#
# if __name__ == "__main__":
#     event = {
#         'Records': [
#             {
#                 'Sns': {
#                     'Message': {
#                         'rancher_project_id': '1a5',
#                         'instance_id': '123',
#                         'event': 'AWS_EC2_INSTANCE_TERMINATE'
#                     }
#                 }
#             }
#         ]
#     }
#
#     lambda_handler(event, None)
