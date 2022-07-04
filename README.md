# moon, a testnet3 tBTC faucet

1. Installation
2. Configuration
3. Service Provider & RPC Server Connection
4. Database Setup
5. Environment
6. Running the Server



## Installation
Start by [cloning this repository](https://github.com/craigderington/moon.git) into your project directory.

```
ubuntu:$ git clone https://github.com/craigderington/moon.git
ubuntu:$ cd moon
ubuntu:~/projects/moon$ virtualenv venv --python=python3.9
ubuntu:~/projects/moon$ source venv/bin/activate
(venv)ubuntu:~/projects/moon$ pip install -r requirements.txt
... dependencies installed ...
```

## Configuration
Browse into the Python virtual environment site-packages at /project-path/venv/lib/python3.9/sites-packags/bitcoinlib

Modify data/config.ini

```
[locations]
default_databasefile=mysql://username:password@localhost:3306/bitcoinlib
```
and data/providers.json

```
{
  "bitcoinlib_test": {
    "provider": "bitcoinlibtest",
    "network": "bitcoinlib_test",
    "client_class": "BitcoinLibTestClient",
    "provider_coin_id": "",
    "url": "http://rpc-server-user:rpc-server-password@127.0.0.1:18332",
    "api_key": "",
    "priority": 10,
    "denominator": 100000000,
    "network_overrides": null
  }  
}
```

## Service Provider
Our connection to the Bitcoin Testnet3 RPC Server is dependent on a successful RPC Server setup on the host machine running Bitcoin Core 0.22+ testnet; with a properly configured wallet.  Please see Bitcoin Core documentation for setup instructions.

I recommend testing your RPC Server connection before running the web server for the first time.  In your console, run curl to make sure you can connect to the service.

```
(venv)ubuntu:~/projects/moon$ curl --data-binary '{"jsonrpc": "1.0", "id": "crltext", "method":"listtransactions", "params": []}' -H "Content-Type: text/plain" http://rpc-server-username:rpc-server-password@127.0.0.1:18332
... {json-response} ...
```

Since Bitcoin Core RPC Server only allows connections from the localhost, I recommend running the testnet server on one instance and configuring a SSH Tunnel on the machine running the moon faucet web server.

This can be accomplished by creating a tunnel to the testnet machine.

```
(venv)ubuntu:~/projects/moon$ ssh -L -fn localhost:18333:localhost:18332 ubuntu@host
```

When setting up this project using a SSH tunnel, make sure your RPC SERVER uses the correct port, in this case 18333 (local) to 18332 (remote)


## Database Setup
The bitcoinlib database must be created before using MySQL as the data provider.  The schema will be created at run time, however, we need to create he database and create a user with permission to read/write to the database.

```
(venv)ubuntu:~/projects/moon$ mysql -u root -p
Enter password: 
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 3
Server version: 5.7.38-0ubuntu0.18.04.1 (Ubuntu)

Copyright (c) 2000, 2022, Oracle and/or its affiliates.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> create database bitcoinlib;
OK
mysql> create user "bitcoinlib"@"localhost" identified by "password";
OK
mysql> grant all on bitcoinlib.* to "bitcoinlib"@"localhost" with grant option;
OK
mysql> flush privileges;
OK
```

## Environment
There are serveral environment variables that must be configured prior to running the web server for the first time.

```
# .flaskenv
FLASK_APP="manage.py"
FLASK_ENV="development"
```

```
# .env
FLASK_CONFIG=development
MAIL_USERNAME=""
MAIL_PASSWORD=""
MAIL_DEFAULT_SENDER="<sender@address>"
VALVE_DATABASE_PASSWORD=""
BITCOINLIB_DATABASE_PASSWORD=""
BITCOINLIB_RPC_SERVER_PASSWORD=""
```

## Running the Server

```
(venv)ubuntu:~/projects/moon$ flask run
```
