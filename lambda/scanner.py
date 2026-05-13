import boto3
from botocore.exceptions import ClientError

ALL_REGIONS = boto3.session.Session().get_available_regions('ec2')

def scan_all_regions():
    report = {}
    # for region in ALL_REGIONS:
    for region in ['us-east-1', 'eu-central-1']:  # limit to a few regions for testing
        data = scan_region(region)
        if data:  # only include regions with something
            report[region] = data
    return report

def scan_region(region: str) -> dict:
    result = {}

    # EC2
    try:
        ec2 = boto3.client('ec2', region_name=region)
        instances = ec2.describe_instances()['Reservations']
        running = sum(1 for r in instances for i in r['Instances'] if i['State']['Name'] == 'running')
        stopped = sum(1 for r in instances for i in r['Instances'] if i['State']['Name'] == 'stopped')
        if running + stopped > 0:
            result['ec2'] = {'running': running, 'stopped': stopped}
    except ClientError:
        pass

    return result

