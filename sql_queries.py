import configparser

# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

user_logins_create_table = ("""
                            CREATE TABLE IF NOT EXISTS users_login (
                              user_id varchar(128),
                              device_type varchar(32),
                              masked_ip varchar(256),
                              masked_device_id varchar(256),
                              locale varchar(32),
                              app_version integer,
                              create_date date
                            );
                            """)

user_logins_insert_data = ("""
                        INSERT INTO user_logins (user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date)
                        VALUES (%s, %s, %s, %s, %s, %s, %s);
                      """)