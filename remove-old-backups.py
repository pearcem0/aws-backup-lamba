import boto3
import re
import datetime

ec = boto3.client('ec2')
iam = boto3.client('iam')

def lambda_handler(event, context):
    account_ids = list()
    try:
        iam.get_user()
    except Exception as e:
        # use the exception message to get the account ID the function executes under
        account_ids.append(re.search(r'(arn:aws:sts::)([0-9]+)', str(e)).groups()[1])

    delete_on = datetime.date.today().strftime('%Y-%m-%d')
    filters = [
	# find all snapshots tagged as DeleteOn = Today
        {'Name': 'tag-key', 'Values': ['DeleteOn']},
        {'Name': 'tag-value', 'Values': [delete_on]},
    ]
    snapshot_response = ec.describe_snapshots(OwnerIds=account_ids, Filters=filters)


    for snap in snapshot_response['Snapshots']:
        print "Removing snapshot %s" % snap['SnapshotId']
        ec.delete_snapshot(SnapshotId=snap['SnapshotId'])
