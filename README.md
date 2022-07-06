# moon, a testnet3 tBTC faucet

![moon-faucet](https://moon-faucet.s3.amazonaws.com/moon-faucet.png)

1. Installation
2. Configuration
3. Bitcoinlib
4. Service Provider
5. RPC Server Connection
6. Database Setup
7. Environment
8. Redis
9. Running the Server


## Installation
Start by [cloning this repository](https://github.com/craigderington/moon.git) into your project directory.

```
ubuntu:~/projects$ git clone https://github.com/craigderington/moon.git
ubuntu:~/projects$ cd moon
ubuntu:~/projects/moon$ virtualenv venv --python=python3.9
ubuntu:~/projects/moon$ source venv/bin/activate
(venv)ubuntu:~/projects/moon$ pip install -r requirements.txt
... python project dependencies installed ...
```

## bitcoinlib
This faucet app utilizes [Bitcoinlib](http://bitcoinlib.readthedocs.io/) as the RPC client.  Several configuration changes are required to configure the module.


## Configuration
Browse into the Python virtual environment site-packages at /project-path/venv/lib/python3.9/sites-packags/bitcoinlib

Modify ```data/config.ini```

```
[locations]
default_databasefile=mysql://username:password@localhost:3306/bitcoinlib
```

Alternatively, you can use SQLite.  The bitcoinlib database is only used by the packages ```wallet``` features and is not dependent on the fronted faucet application.

Modify ```data/providers.json```

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
(venv)ubuntu:~/projects/moon$ curl --data-binary '{"jsonrpc": "1.0", "id": "crltext", "method":"getblockchaininfo", "params": []}' -H "Content-Type: text/plain" http://rpc-server-username:rpc-server-password@127.0.0.1:18332
... {json-server-response} ...
```

Since Bitcoin Core RPC Server only allows connections from the localhost, I recommend running the testnet server on a separate instance and configuring a SSH tunnel from the moon faucet web server to the BTC Testnet3 Server.

This can be accomplished by creating a tunnel to the testnet machine.

```
(venv)ubuntu:~/projects/moon$ ssh -L -fn localhost:18333:localhost:18332 ubuntu@host
```

When setting up this project using a SSH tunnel, make sure your RPC SERVER uses the correct port, in this case ```18333 (local)``` to ```18332 (remote)```


## Database Setup
The bitcoinlib database must be created before using MySQL as the data provider.  The schema will be created at run time, however, we need to create the database and create a user with permission to read/write to the database.

```
(venv)ubuntu:~/projects/moon$ mysql -u root -p
Enter password: 
Welcome to the MySQL monitor.
Server version: 5.7.38-0ubuntu0.18.04.1 (Ubuntu)

mysql> create database bitcoinlib;
mysql> create user "bitcoinlib"@"localhost" identified by "password";
mysql> grant all on bitcoinlib.* to "bitcoinlib"@"localhost" with grant option;
mysql> flush privileges;
```

## Environment
Create 2 files, ```.env``` and ```.flaskenv``` to store the apps environment variables. These vars must be configured prior to running the web server for the first time.

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
BITCOINLIB_DATABASE_PASSWORD=""
BITCOINLIB_RPC_SERVER_USERNAME=""
BITCOINLIB_RPC_SERVER_PASSWORD=""
```

### Redis
Make sure ```redis-server``` is running on the host and is accessible at...

```
redis://localhost:6379/0
```

Moon uses a redis in-memory cache to store and retrieve remote client IP addresses and user-agents to help fight against bots spamming the faucet request form and to limit client requests to once per hour.  

I'd rather not have to implement an unfriendly captcha solver. Even the best captcha can be beaten with the appropriate tools and software.

A bot detection redirect service may be required in the future.

## Running the Server

```
(venv)ubuntu:~/projects/moon$ flask run
```

For background tasks and messaging functionality, in a separate console, fire up the Celery worker to execute app tasks.

```
(venv)ubuntu:~/projects/moon$ venv/bin/celery worker -A celery_worker.celery -l info -n worker%h -c 2
```

#### TODO
- API's
- Bot detection 
- redis-cache
- python bloom filter (objects=10**8)
- Faucet wallet funding with tBTC
- Bitcoin RPC server command library (available commands)
- 