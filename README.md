#### Valve, a Testnet3 Bitcoin Faucet

```
Create a virtualenv and install the requirements (pip install requirements/dev.txt)

Run the database migrations (python manage.py db upgrade)

Open a second terminal window and start a local Redis server (if you are on Linux or Mac, execute run-redis.sh to install and launch a private copy).

Open a third terminal window. Set two environment variables MAIL_USERNAME and MAIL_PASSWORD to a valid Gmail account credentials (these will be used to send emails through Gmail's SMTP server). Then start a Celery worker: venv/bin/celery worker -A celery_worker.celery --loglevel=info.

Configure environment.

Configure Bitcoind service provider.

Start App on your first terminal window: venv/bin/python manage.py runserver.

Go to http://localhost:5880/ and register an account to see how the Celery background emails work!<!--  -->


```
