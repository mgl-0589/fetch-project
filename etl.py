
import configparser
import psycopg2
import localstack_client.session
import json
from datetime import datetime
import base64
from sql_queries import user_logins_create_table, user_logins_insert_data

# # importing credential from .config file
config = configparser.ConfigParser()
config.read('creds.cfg')


def receive_sqs_messages():
    """
    function to connect with localstack to receive user_login data
    """
    
    # # create sqs client object
    sqs = localstack_client.session.client("sqs")

    # # get the queue URL
    queue_url = sqs.get_queue_url(QueueName=config['SQS']['QUEUE_NAME'])['QueueUrl']

    # # retrieve all messages from the queue
    messages = []
    while True:
        response = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=50)
        if 'Messages' not in response:
            break
        messages += response['Messages']

    return messages


def data_transformations(messages):
    """
    function to:
        mask personal identifiable information (pii) [device_id, ip]
        transform string app_version into integer data type
    """

    # # defining empty list to store messages transformed
    list_messages_transformed = []

    # # defining variables to count messages processed
    bad_messages_count = 0
    good_messages_count = 0

    # # extract the body messages
    for message in messages:
        message_body = json.loads(message['Body']) 

        # # validating if message has correct structure
        if 'device_id' not in message_body or 'ip' not in message_body or 'app_version' not in message_body:
            # # increasing bad message counter, and skipping it
            bad_messages_count += 1
            continue

        else:
            # # encoding the device_id
            device_id_to_bytes = message_body['device_id'].encode('ascii')
            device_id_bytes_encoded = base64.b64encode(device_id_to_bytes)
            device_id_decoded = device_id_bytes_encoded.decode('ascii')

            # # encoding the ip
            ip_to_bytes = message_body['ip'].encode('ascii')
            ip_bytes_encoded = base64.b64encode(ip_to_bytes)
            ip_decoded = ip_bytes_encoded.decode('ascii')

            # # transforming app_version into integer data type
            app_version = message_body['app_version']

            # # identifying app_vresion string with less characters to stablish a base adding zeros if needed
            if app_version.count('.') < 2 and len(app_version.split('.')[1]) < 2 and not app_version.startswith('0'):
                # # removing '.' character and converting into integer data type
                app_version_int = int(app_version.replace('.', '') + '0')

            else:
                # # removing '.' character and convert into integer data type    
                app_version_int = int(app_version.replace('.', ''))

            # # replacing the values transformed
            message_body['device_id'] = device_id_decoded
            message_body['ip'] = ip_decoded
            message_body['app_version'] = app_version_int

            # # increasing messages processed
            good_messages_count += 1

            # # counting total of messages
            total_messages = good_messages_count + bad_messages_count

            # # appendign message content into the list
            list_messages_transformed.append(message_body)

    # # displaying count of messages
    print(f'\nTotal messages retreived: {total_messages} \n\n\tMessages correct: {good_messages_count} \n\tMessages incorrect: {bad_messages_count}\n\n')

    return list_messages_transformed


def create_user_logins(cur, conn):
    """
    function to create the table if not exists
    """

    # # executing 'create table' query 
    cur.execute(user_logins_create_table)
    conn.commit()

    return f'Table user_logins is ready!' 


def insert_users_data(messages_transformed, cur, conn):
    """
    function to insert messages into users_login table
    """

    # # looping the executing 'insert into' query
    for message in messages_transformed:
        messages_values = (message['user_id'], message['device_type'], message['ip'], message['device_id'], message['locale'], message['app_version'], datetime.now().strftime('%Y-%m-%d'))
        cur.execute(user_logins_insert_data, messages_values)
    conn.commit()
    
    return f'User logins data inserted!'


# # function to execute etl process
def main():
    """
    Principal function to run the etl process 
    """

    # # create connexion with postgres DB
    conn = psycopg2.connect(
        host=config['POSTGRES']['HOSTNAME'], 
        dbname=config['POSTGRES']['DB_NAME'], 
        user=config['POSTGRES']['DB_NAME'], 
        password=config['POSTGRES']['DB_PASSWORD'], 
        port=config['POSTGRES']['DB_PORT']
        )
    cur = conn.cursor()

    # # retrieving sqs messages
    messages = receive_sqs_messages()
    
    # # transforming ip, device_id, and app_version data
    messages_transformed = data_transformations(messages)
    
    # # creating table if not exists
    create_user_logins(cur, conn)

    # # inserting data into table user_logins
    insert_users_data(messages_transformed, cur, conn)

    # # closing postgres connection
    conn.close()


if __name__ == "__main__":
    main()
    