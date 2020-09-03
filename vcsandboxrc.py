import sys
from lxml import etree
import logging
import argparse
import datetime

from veracode_api_py import VeracodeAPI as vapi

def creds_expire_days_warning():
    creds = vapi().get_creds()
    exp = datetime.datetime.strptime(creds['expiration_ts'], "%Y-%m-%dT%H:%M:%S.%f%z")
    delta = exp - datetime.datetime.now().astimezone() #we get a datetime with timezone...
    if (delta.days < 7):
        print('These API credentials expire ', creds['expiration_ts'])

def process_app(the_app_id):
    data2 = vapi().get_sandbox_list(the_app_id)

    if len(data2)==0:
        return 0

    sandbox_list = etree.fromstring(data2)
    sandbox_count = len(sandbox_list)

    if sandbox_count==0:
        return 0
    elif sandbox_count==1:
        count_noun = "sandbox"
    else:
        count_noun = "sandboxes"

    print("app_id",sandbox_list.get('app_id'),"has",sandbox_count,count_noun)
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
        
        print("Updating auto_recreate for sandbox ",sandbox_name,", sandbox id", sandbox_id)
        updated = vapi().update_sandbox(sandbox_id,"autorecreate",True)
        if updated==None:
            return 0    #something went wrong

        updated_xml = etree.fromstring(updated)
        print('==>Sandbox',sandbox_name,'auto_recreate = ', updated_xml.get('auto_recreate'))

        iteration += 1

    return iteration

def main():
    parser = argparse.ArgumentParser(
        description='This script sets any expiring sandboxes in the scope to auto-recreate. It can operate on one application '
                    'or all applications in the account.')
    parser.add_argument('-a', '--app_id', required=True, help='App ID to update. Ignored if --all is specified.')
    parser.add_argument('-l', '--all', required=True, help='Set to TRUE to update all applications.')
    args = parser.parse_args()

    target_app = args.app_id
    all_apps = args.all 

    logging.basicConfig(filename='Vcsandboxrc.log',
                        format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S%p',
                        level=logging.INFO)

    # CHECK FOR CREDENTIALS EXPIRATION
    creds_expire_days_warning()
    
    if all_apps == "true":

        data = vapi().get_apps()

        for app in data:
            iterations = process_app(app["id"])
            if iterations > 0:
                print("==>Updated",iterations,"sandboxes")
    else:
        iterations = process_app(target_app)
        if iterations > 0:
            print("==>Updated",iterations,"sandboxes")

if __name__ == '__main__':
    main()