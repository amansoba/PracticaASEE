"""Run existing backend suites inside running Compose services, on separate test DBs.

Installs dev dependencies inside disposable containers; never uses the demo DB.
"""
import argparse
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SERVICES = ("auth", "catalog", "event", "commerce", "provider")
WORKER = r'''
import os
from pathlib import Path
import subprocess
import sys
import psycopg
from psycopg import sql
from dotenv import set_key

service = sys.argv[1]
database = {'auth':'auth','catalog':'catalog','event':'events','commerce':'commerce','provider':'providers'}[service]
test_name = f'subsonic_{database}_test'
assert test_name.endswith('_test')
with psycopg.connect(host=os.environ['DB_HOST'], port=os.environ['DB_PORT'],
                     user=os.environ['DB_USER'], password=os.environ['DB_PASSWORD'],
                     dbname='postgres', autocommit=True) as db:
    if not db.execute('SELECT 1 FROM pg_database WHERE datname=%s', (test_name,)).fetchone():
        db.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(test_name)))
config = {key: os.environ[key] for key in ('DB_HOST','DB_PORT','DB_USER','DB_PASSWORD')}
config['DB_NAME'] = test_name
config['AUTH_SERVICE_URL'] = 'http://auth:8000'
config['EVENT_SERVICE_URL'] = 'http://event:8000'
config['CATALOG_SERVICE_URL'] = 'http://catalog:8000'
for key, value in config.items():
    set_key('.env.test', key, value)
subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements-dev.txt'], check=True)
subprocess.run([sys.executable, '-m', 'pytest', 'tests', '-q', '-p', 'no:cacheprovider'], check=True)
'''


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default="subsonic")
    parser.add_argument("--service", choices=SERVICES)
    args = parser.parse_args()
    for service in (args.service,) if args.service else SERVICES:
        print(f"Testing {service} with the image's installed dependencies", flush=True)
        subprocess.run(["docker", "compose", "-p", args.project, "exec", "-T", service,
                        "python", "-", service], cwd=ROOT, input=WORKER, text=True, check=True)
