FROM alpine:3.5
MAINTAINER Jake Wasdin <jake@wasdin.net>

RUN apk add --no-cache python py-pip
RUN pip install awscli
RUN mkdir /data
ADD s3_syncer.py .

ENTRYPOINT python s3_syncer.py --s3_bucket $s3_bucket --working_directory /data --logging_file /errors.log