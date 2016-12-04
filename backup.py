import boto3
import collections
import datetime

ec = boto3.client('ec2')

def lambda_handler(event, context):
    reservations = ec.describe_instances(
        Filters=[
		# any instance with the tag key backup and the value true should be selected
            {'Name': 'tag-key', 'Values': ['backup', 'Backup', 'BACKUP']},{'Name': 'tag-value', 'Values': ['True']}
        ]
    ).get(
        'Reservations', []
    )

    instances = sum(
        [
            [i for i in r['Instances']]
            for r in reservations
        ], [])

    to_tag = collections.defaultdict(list)

    for instance in instances:
        try:
            retention_days = [
                int(t.get('Value')) for t in instance['Tags']
                if t['Key'] == 'Retention'][0]
        except IndexError:
		# default retention days if key and value is not set
            retention_days = 28

        for dev in instance['BlockDeviceMappings']:
            if dev.get('Ebs', None) is None:
                continue
            vol_id = dev['Ebs']['VolumeId']
                vol_id, instance['InstanceId'])
            # give the snapshot a description to identify the source 
            SnapDescription="Automated Backup for "+instance['InstanceId']+" "+dev['DeviceName']

            snap = ec.create_snapshot(
                VolumeId=vol_id, Description=SnapDescription
            )

            to_tag[retention_days].append(snap['SnapshotId'])

            print "Snapshot %s of volume %s from instance %s for %d days" % (
                snap['SnapshotId'],
                vol_id,
                instance['InstanceId'],
                retention_days,
            )

    for retention_days in to_tag.keys():
        delete_date = datetime.date.today() + datetime.timedelta(days=retention_days)
        delete_fmt = delete_date.strftime('%Y-%m-%d')
        ec.create_tags(
            Resources=to_tag[retention_days],
			# add a tag marking when the snapshot should be deleted
            Tags=[
                {'Key': 'DeleteOn', 'Value': delete_fmt},
            ]
        )
