
# AWS Lambda Video Processing Function 🎥➡️🎞️

## Overview
This AWS Lambda function is designed to automate the process of converting videos stored in Amazon S3 into GIFs. It listens for new video uploads to an S3 bucket, converts the uploaded video into a GIF format using `ffmpeg`, and then uploads the resulting GIF back to a specified S3 bucket. This document explains the function's components, their purposes, and how they work together.

## How It Works 🛠️
When a video file is uploaded to the designated S3 input bucket, an event triggers this Lambda function. The function then performs the following steps:

### 1. Download Video from S3 📥
The `download_from_s3` function is called with the S3 bucket name and the key (path) of the newly uploaded video file. It uses the AWS SDK (`boto3`) to download the video file to the Lambda environment's temporary storage (`/tmp` directory).

### 2. Convert Video to GIF 🔄
With the video file now locally available, the `convert_video_to_gif` function uses the `ffmpeg` tool to convert the video into a GIF. It specifies parameters such as the frame rate and scale to control the GIF's quality and size.

### 3. Upload GIF to S3 📤
After conversion, the `upload_to_s3` function uploads the GIF to a specified output S3 bucket. It ensures that the GIF is stored correctly and is accessible for future use.

### 4. Clean Up Local Storage 🧹
Finally, the `cleanup_local_files` function deletes the temporary video and GIF files from the Lambda environment to free up space for future invocations.

## Functions Explained

- `download_from_s3`: Connects to S3 and downloads the video file triggering the event.
- `convert_video_to_gif`: Executes the `ffmpeg` command to convert the video to a GIF.
- `upload_to_s3`: Uploads the converted GIF back to an S3 bucket.
- `cleanup_local_files`: Removes temporary files to prevent the Lambda environment from running out of space.
  

### `download_from_s3(bucket, key, download_path)`
Downloads a file from S3 to the Lambda's local storage.
- `bucket`: Name of the S3 bucket.
- `key`: Key (path) of the file in the bucket.
- `download_path`: Local path to save the file.

### `convert_video_to_gif(source_video_path, gif_output_path)`
Converts a video file to a GIF using `ffmpeg`.
- `source_video_path`: Local path of the source video file.
- `gif_output_path`: Local path where the GIF should be saved.

### `upload_to_s3(file_path, bucket, key)`
Uploads a file from the Lambda's local storage to an S3 bucket.
- `file_path`: Local path of the file to upload.
- `bucket`: Destination S3 bucket name.
- `key`: Destination key (path) in the bucket.

### `cleanup_local_files(*file_paths)`
Deletes files from the Lambda's local storage.
- `*file_paths`: Paths of the files to be deleted.

### `lambda_handler(event, context)`
The main function that AWS Lambda calls when the function is triggered.
- `event`: Contains data about the triggering event.
- `context`: Contains runtime information about the function call.

## Performance and Considerations 🚀
- **Temporary Storage**: The Lambda function uses the `/tmp` directory for temporary storage, which has a limit of 512 MB. Ensure your video and GIF files fit within this constraint.
- **Execution Time**: Lambda functions have a maximum execution time limit (15 minutes). Video-to-GIF conversion should be optimized to complete within this time frame.
- **`ffmpeg` Installation**: The Lambda execution environment must have `ffmpeg` installed. This can be achieved by including `ffmpeg` in the deployment package or using a Lambda layer.

## Conclusion 🎬
This Lambda function simplifies the process of converting videos to GIFs on AWS, automating what would otherwise be a manual and time-consuming task. It showcases the power of AWS services working together to achieve seamless media processing workflows.

---

Hope this guide helps you understand the Video to GIF Converter Lambda Function! 🌟
