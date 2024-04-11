import boto3
import json
import os
import subprocess
import uuid

from botocore.client import ClientError

# Converts a video file to a GIF using ffmpeg.
def convert_video_to_gif(source_video_path, gif_output_path):
    # ffmpeg command for converting video to GIF with specified options.
    ffmpeg_command = [
        'ffmpeg', '-i', source_video_path, # Input file
        '-t', '2.5', # Duration of output GIF
        '-vf', 'fps=5,scale=200:-1', # Frame rate and scale
        gif_output_path # Output file path
    ]
    try:
        subprocess.run(ffmpeg_command, check=True)
        print("GIF conversion successful")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error converting video to GIF: {e}")
        return False

# Downloading file from S3 to local path.
def download_from_s3(bucket, key, download_path):
    s3_client = boto3.client('s3')
    try:
        s3_client.download_file(bucket, key, download_path)
        return True
    except ClientError as e:
        print(f"Error downloading video from S3: {e}")
        return False

# Uploading file from local file system to the specified S3 location.
def upload_to_s3(file_path, bucket, key):
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(file_path, bucket, key)
        print("Upload successful")
        return True
    except ClientError as e:
        print(f"Error uploading GIF to S3: {e}")
        return False

# Deletes local files to clean up the local file system.
def cleanup_local_files(*file_paths):
    for file_path in file_paths:
        try:
            os.remove(file_path)
            print(f"Deleted local file: {file_path}")
        except Exception as e:
            print(f"Error deleting local file {file_path}: {e}")

# Main entry point of lambda function
def lambda_handler(event, context):

    assetID = str(uuid.uuid4())
    sourceS3Bucket = event['Records'][0]['s3']['bucket']['name']
    sourceS3Key = event['Records'][0]['s3']['object']['key']
    sourceS3 = 's3://'+ sourceS3Bucket + '/' + sourceS3Key
    sourceS3Basename = os.path.splitext(os.path.basename(sourceS3))[0]
    destinationS3 = 's3://' + os.environ['DestinationBucket']
    destinationS3basename = os.path.splitext(os.path.basename(destinationS3))[0]
    mediaConvertRole = os.environ['MediaConvertRole']
    region = os.environ['AWS_DEFAULT_REGION']
    statusCode = 200
    body = {}
    
    # Use MediaConvert SDK UserMetadata to tag jobs with the assetID 
    # Events from MediaConvert will have the assetID in UserMedata
    jobMetadata = {'assetID': assetID}

    print (json.dumps(event))
    
    local_video_path = f"/tmp/{os.path.basename(sourceS3Key)}"
    local_gif_path = f"/tmp/{os.path.splitext(os.path.basename(sourceS3Key))[0]}.gif"
    gif_s3_key = f"{os.path.splitext(sourceS3Key)[0]}.gif"

    # Check and download video from S3.
    if not download_from_s3(sourceS3Bucket, sourceS3Key, local_video_path):
        return {'statusCode': 500, 'body': json.dumps('Failed to download video from S3')}

    # Convert the downloaded video to GIF.
    if not convert_video_to_gif(local_video_path, local_gif_path):
        return {'statusCode': 500, 'body': json.dumps('Failed to convert video to GIF')}

    # Upload the converted GIF to S3.
    if not upload_to_s3(local_gif_path, destinationS3, gif_s3_key):
        return {'statusCode': 500, 'body': json.dumps('Failed to upload GIF to S3')}
    
    # Local storage clean-up
    cleanup_local_files(local_video_path, local_gif_path)

    try:
        # Job settings are in the lambda zip file in the current working directory
        with open('main.json') as json_data:
            jobSettings = json.load(json_data)
            print(jobSettings)
        
        # get the account-specific mediaconvert endpoint for this region
        mc_client = boto3.client('mediaconvert', region_name=region)
        endpoints = mc_client.describe_endpoints()

        # add the account-specific endpoint to the client session 
        client = boto3.client('mediaconvert', region_name=region, endpoint_url=endpoints['Endpoints'][0]['Url'], verify=False)

        # Update the job settings with the source video from the S3 event and destination 
        # paths for converted videos
        jobSettings['Inputs'][0]['FileInput'] = sourceS3
        
        print("till here")
        

        print('jobSettings:')
        print(json.dumps(jobSettings))

        # Convert the video using AWS Elemental MediaConvert
        job = client.create_job(Role=mediaConvertRole, UserMetadata=jobMetadata, Settings=jobSettings)
        print (json.dumps(job, default=str))

    except Exception as e:
        print ('Exception: %s' % e)
        statusCode = 500
        raise

    finally:
        return {
            'statusCode': statusCode,
            'body': json.dumps(body),
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
        }
