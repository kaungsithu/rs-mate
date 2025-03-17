import dataclasses
from os import name
from sqlite3 import connect
from urllib.parse import quote_plus
from uu import encode
from fasthtml.common import *
import redshift_connector
import sqlalchemy as sa 
from sqlalchemy.engine.url import URL
from sqlalchemy import orm as sa_orm 
from sqlalchemy_redshift.dialect import TIMESTAMPTZ, TIMETZ
import pandas as pd
import json
from cryptography.fernet import Fernet

app, rt = fast_app()
fernet = Fernet(Fernet.generate_key())

connect_redir = RedirectResponse('/connect', status_code=303)
db_info = []

@rt('/')
def get():
    return connect

@rt('/connect')
def get():
    frm = Form(action='/connect', method='post')(
        Input(id='host', placeholder='Database Host'),
        Input(id='port', placeholder='Database Port', hx_vals=['5439']),
        Input(id='name', placeholder='Database Name'),
        Input(id='user', placeholder='Username'),
        Input(id='pwd', type='password', placeholder='Password'),
        Button('Connect'))

    return Titled("Connect Redshift", frm)

@dataclass
class DBInfo: host:str; port:int; name:str; user:str; pwd:str

@rt('/connect')
def post(session, db:DBInfo):
    if not (db.host and db.port and db.name and db.user and db.pwd):
        return connect_redir
    # test connection 
    df = run_sql('select usename from pg_user_info limit 1', db)
    card = Card(A('Manage Users', href='/users', cls='btn btn-primary'))
    if not df.empty:
        store_db_info(db, session)
        return Titled('Connected'), card, P(session['dbinfo'])
    else:
        return Titled('Connection failed...'), P(db)

@rt('/users')
def get(session):
    db = load_db_info(session)
    df = run_sql('select * from pg_user_info', db)
    return Card(NotStr(df.to_html()))

def store_db_info(db:DBInfo, session):
    session['dbinfo'] = fernet.encrypt(json.dumps(dataclasses.asdict(db)).encode()).decode()

def load_db_info(session):
    return DBInfo(**json.loads(fernet.decrypt(session['dbinfo'].encode()).decode()))
    
def get_db_engine(db:DBInfo):
    url = URL.create(
        drivername='redshift+redshift_connector',
        host=db.host,
        port=db.port,
        username=db.user,
        password=db.pwd,
        database=db.name
    )
    engine = sa.create_engine(url)
    return engine

def run_sql(sql:str, db:DBInfo):
    conn = redshift_connector.connect(
        host=db.host, port=db.port, database=db.name, user=db.user, password=db.pwd
    )
    cursor = conn.cursor()
    cursor.execute(sql)
    df = cursor.fetch_dataframe()
    return df

def test_db_conn(engine):
    df = pd.read_sql_query("SELECT usename FROM pg_user_info;", engine)
    print(df)
    return not df.empty
    # return not pd.read_sql_query("SELECT 1 FROM pg_user_info;", engine).empty

if __name__ == "__main__":
    try: serve()
    except KeyboardInterrupt: pass
    finally:
        sys.exit(0)
