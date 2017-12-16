import argparse, logging, subprocess

def setup_logging(logging_file, logging_level):
    if logging_file == None:
        print "WARNING: Please pass a logging filename with --logging_file to enable logging."
    if logging_level == None:
        logging_level = "WARNING"

    if logging_level.upper() == "DEBUG":
        logging.basicConfig(filename=logging_file,level=logging.DEBUG)
    else:
        logging.basicConfig(filename=logging_file,level=logging.WARNING)
    

def get_empty_directories(working_directory):
    get_empty_directories = subprocess.Popen(['find', working_directory, '-type', 'd', '-empty'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    empty_files,error = get_empty_directories.communicate()
    return empty_files
    
def create_metadata_in_directories(directory_names):
    for line in directory_names.split("\n"):
        if line != "":
            file_name = line + "/.s3_index"
            logging.info("Creating file " + file_name)
            subprocess.Popen(['touch', file_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--s3_bucket')
    parser.add_argument('--working_directory')
    parser.add_argument('--logging_file')
    parser.add_argument('--logging_level')
    args = parser.parse_args()

    bucket = "s3://" + args.s3_bucket
    working_directory = args.working_directory
    logging_file = args.logging_file
    logging_level = args.logging_level
    
    setup_logging(logging_file, logging_level)

    while True:
        create_metadata_in_directories(get_empty_directories(working_directory))

        proc = subprocess.Popen(['aws', 's3', 'sync', '--delete', working_directory, bucket], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output,error = proc.communicate()


        if not output.strip() == "" or not error.strip() == "":
            logging.warning(error)
            logging.info(output)
    
if __name__ == "__main__": main()