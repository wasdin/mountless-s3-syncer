# mountless-s3-syncer
The purpose of this project is to be able to use an S3 bucket as a constantly synchronized folder without mounting it as a file system. This has the key advantage of allowing you to use an S3 bucket for consistent storage in a Docker container without needing kernel level permissions (such as running a Docker container as priveleged), as do most tools like [S3FS](https://github.com/s3fs-fuse/s3fs-fuse). Furthermore, it can be used to allow a simple, persistent storage option for applications running in Fargate and other Docker orchestration methods that do not allow interaction with a host OS. 

It is currently very limited, but it proves a possible use case. It does not handle object permissions, so it is not recommended to be used on most applications at this stage. It has also only been tested on *nix systems (macOS and Linux).

## Setting up access to your S3 bucket
All commands to S3 are run using the AWS CLI. See [this article](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html) for details on setting up the AWS CLI.

The user you authenticate with will need access to your S3 bucket, including read and write.

## Running locally
Pre-requisites: Python 2.7, awscli (recommended installation via `pip install awscli`)

Example run command:
`python s3_syncer.py --s3_bucket mybucketname --working_directory /data --logging_file errors.log --logging_level INFO &`

Explanation of inputs:
* **s3_bucket**: The name of your S3 bucket to keep in sync. If your full bucket name is _s3://mybucketname_ pass in _mybucketname_
* **working_directory**: The directory to keep up-to-date from S3
* **logging_file**: The file to output logging data to. If not specified, no logging will occur. It is recommended to at least have this available for initial setup, as logging will go here if it cannot connect to S3 or if there are permission errors. It is not recommended to have this in the same directory as your working directory, as the file could be constantly written to.
* **logging_level**: Options are DEBUG and INFO. INFO logging is default and will only provide errors that prevent from working correctly. DEBUG must be passed and will give all information, including every file that is updated.
* **&** is provided to run as a service. It will provide a process ID that can be stopped when you are done running the s3_syncer.


## Running in a Docker Container
The original intention of this project was to be run in a Docker container. A simple Dockerfile is included in this project to get you started. Here is how to use it:

First, build the Docker container:
`docker build -t mountless-s3-syncer .`

Now, run the Docker container. Pass in the S3 bucket as an environment variable: 
`docker run -d -e s3_bucket=mybucketname mountless-s3-syncer`

The Docker container will keep the folder `/data` internally in sync with the passed in S3 bucket's contents. It will log errors to `/errors.log`

## What's happening underneath
This project is simply leveraging the AWS CLI to use the `aws s3 sync` command continuously. Note that a POST or GET from S3 is only initated when there is a change to a file, a file is deleted, or a file is removed.

### How folders are handled
S3 does not distinguish between folders/directories and files, but filesystems have folders. One limitation of this is that by default, an empty folder cannot be created in S3. To get around this, the s3_syncer will create a blank, hidden (in *nix, not in S3) file called `.s3_index` in any detected empty directories.
