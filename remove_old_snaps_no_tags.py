import boto3
import sys
from datetime import datetime, timedelta

ec2 = boto3.resource('ec2', region_name='us-east-1')

def lambda_handler(event, context):
    retention_days = 92
    delete_counter = 0
    error_counter = 0

    delete_date = datetime.utcnow() - timedelta(retention_days=retention_days)
    print "Today's date (UTC) is - " + str(datetime.utcnow())
    print "Deleting snapshots older than " + str(delete_date) + "(" + str(retention_days) + ") days"

    for snap in ec2.snapshots.filter(
    # SnapshotIds=[
    #     'string',
    # ],
    OwnerIds=[
        'self',
    ],
    # Filters=[
    #     {
    #         'Name': 'string',
    #         'Values': [
    #             'string',
    #         ]
    #     },
    # ],
    MaxResults=1000
    ):
        snap_date = snap.start_time.replace(tzinfo=None)
        #test_snap_id = 'snap-s0abc12d'
        snap_id = snap.id

        if delete_date > snap_date:
        #if snap_id != test_snap_id and delete_date > snap_date:
            try:
                snap.delete()
                print "Deleted snapshot " + snap.id + " from " + str(snap_date)
                delete_counter = delete_counter+1
            except Exception as e:
                print "Failed to delete snapshot"
                print e
                error_counter = error_counter+1
        # else:
        #     print "nothing to delete"
    print "Total snapshots deleted - " + str(delete_counter)
    print "Total errors - " + str(error_counter)
