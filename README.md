# fetch-project
ETL off a SQS Queue repository

## Introduction
This process is focused on retrieving data from the AWS SQS Queue service, transforming data, and finally writing data into the Postgres database.
The project includes steps for using docker to run all the components locally.
The ETL project was developed using python 3.10.1, and Visual Studio Code

## Objectives
1. read JSON data from AWS SQS Queue
2. hide personal identifiable information (PII). 'device_id' and 'ip' should be masked. (duplicate values should be identifiable easily after being masked)
3. write each record to a Postgres database. 

## Prerequisites 
- docker --> [docker](https://docs.docker.com/get-docker/)
- docker-compose
- awscli-local
- Postgres

## ETL process
Clone the repository, and test the ETL project

`git clone git@github.com:mgl-0589/fetch-project.git`


open a terminal, in Visual Studio Code and set up a local environment.
create a virtual environment and initialize it

`py -m venv .venv`


`.venv\Scripts\activate`


install modules

`pip install -r requirements.txt`


run docker-compose.yaml to initialize localstack and postgres pre-built images

`docker-compose up -d`


validate localstack and postgres images are running

`docker ps`


once the environment and images are running, the ETL pipeline can be executed

`py et.py`


if etl process runs successfully, the terminal will display a summary of records retrieved, messages with correct structure, and messages ignored because of incorrect structure
to validate the data inserted into postgres pre-built database, run this docker command

`docker exec -it fetch_project-postgres-1 sh`


validate access connecting to the postgres database pre-built, provide password

`psql -d [DATABASE] -U [USER] -p [PORT] -h localhost -W`

`SELECT * FROM [TABLE_NAME]`


Once is validated, close the docker images

`docker-compose down`

## References
Docker

(https://docs.docker.com/compose/gettingstarted/)

(https://docs.docker.com/engine/reference/commandline/exec/)

(https://www.linode.com/docs/guides/how-to-use-docker-compose/)

LocalStack

(https://hands-on.cloud/testing-python-aws-applications-using-localstack/)

(https://saturncloud.io/blog/how-to-get-all-messages-in-amazon-sqs-queue-using-boto-library-in-python/)

Base64

(https://www.geeksforgeeks.org/encoding-and-decoding-base64-strings-in-python/)

(https://stackabuse.com/encoding-and-decoding-base64-strings-in-python/)

JSON

(https://pynative.com/python-check-if-key-exists-in-json-and-iterate-the-json-array/)

requirements.txt

(https://note.nkmk.me/en/python-pip-install-requirements/)

string app_version into integer

(https://stackoverflow.com/questions/41516633/how-to-convert-version-number-to-integer-value)


