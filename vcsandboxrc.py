import sys
from lxml import etree
import logging
import argparse
import datetime

import anticrlf
from veracode_api_py import VeracodeAPI as vapi

log = logging.getLogger(__name__)

def setup_logger():
    handler = logging.FileHandler('vcsandboxrc.log', encoding='utf8')
    handler.setFormatter(anticrlf.LogFormatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'))
    logger = logging.getLogger(__name__)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

def creds_expire_days_warning():
    creds = vapi().get_creds()
    exp = datetime.datetime.strptime(creds['expiration_ts'], "%Y-%m-%dT%H:%M:%S.%f%z")
    delta = exp - datetime.datetime.now().astimezone() #we get a datetime with timezone...
    if (delta.days < 7):
        print('These API credentials expire {}'.format(creds['expiration_ts']))

def process_app(the_app_id):
    log.info("Getting sandbox info for application {}".format(the_app_id))
    data2 = vapi().get_sandbox_list(the_app_id)

    if len(data2)==0:
        return 0

    sandbox_list = etree.fromstring(data2)
    sandbox_count = len(sandbox_list)

    if sandbox_count==1:
        count_noun = "sandbox"
    else:
        count_noun = "sandboxes"

    log.info("app_id {} has {} {}".format(the_app_id,sandbox_count,count_noun))

    if sandbox_count==0:
        return 0

    iteration = 0
    for sandbox in sandbox_list:
        sandbox_name = sandbox.get('sandbox_name')
        auto_recreate = sandbox.get('auto_recreate')
        expires = sandbox.get('expires')
        sandbox_id = sandbox.get('sandbox_id')

        if expires == None:
            continue #can't set auto_recreate on a non-expiring sandbox
        if auto_recreate == 'true':
            continue #don't set auto_recreate again
        
        log.info("Updating auto_recreate for sandbox {}, sandbox id {}".format(sandbox_name,sandbox_id))
        updated = vapi().update_sandbox(sandbox_id,"autorecreate",True)
        if updated==None:
            return 0    #something went wrong

        updated_xml = etree.fromstring(updated)
        log.info('==>Sandbox {} auto_recreate = {}'.format(sandbox_name,updated_xml.get('auto_recreate')))

        iteration += 1

    return iteration

def main():
    parser = argparse.ArgumentParser(
        description='This script sets any expiring sandboxes in the scope to auto-recreate. It can operate on one application '
                    'or all applications in the account.')
    parser.add_argument('-a', '--app_id', required=True, help='App ID to update. Ignored if --all is specified.')
    parser.add_argument('-l', '--all', action='store_true', help='Set to TRUE to update all applications.')
    args = parser.parse_args()

    target_app = args.app_id
    all_apps = args.all 

    # CHECK FOR CREDENTIALS EXPIRATION
    creds_expire_days_warning()
    
    if all_apps:

        data = vapi().get_apps()

        print('Evaluating {} applications for update'.format(len(data)))
        for app in data:
            iterations = process_app(app["id"])
            if iterations > 0:
                print("==>Updated {} sandboxes".format(iterations))
    else:
        print("Evaluating application id {} for update".format(target_app))
        iterations = process_app(target_app)
        print("==>Updated {} sandboxes".format(iterations))
        
if __name__ == '__main__':
    setup_logger()
    main()