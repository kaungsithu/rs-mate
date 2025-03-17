from ast import Tuple
from dataclasses import dataclass, asdict, field
from cryptography.fernet import Fernet
import redshift_connector
import json
import os
from typing import Optional

# TODO: Add proper logging mechnism instead of prints

redshift_connector.paramstyle = 'pyformat'


@dataclass
class Redshift: 
    host: Optional[str] = None
    port: Optional[int] = 5439
    name: str = 'dev'
    user: Optional[str] = None
    pwd: Optional[str] = None
    _password: bytes = field(default=b'', repr=False)

    @property
    def password(self) -> bytes:
        return Redshift.get_fernet().decrypt(self._password).decode()
    
    @password.setter
    def password(self, val: str) -> None:
        self._password = Redshift.get_fernet().encrypt(val.encode())

    def __post_init__(self):
        if self.pwd:
            self.password = self.pwd
            self.pwd = None


    @staticmethod
    def get_fernet() -> Fernet:
        env_key = 'RSMATE_FERNET_KEY'
        # get fernet object with key from env var. key created if none 
        if env_key in os.environ:
            key = bytes.fromhex(os.environ.get(env_key))
        else:
            key = Fernet.generate_key()
            os.environ[env_key] = key.hex()
        return Fernet(key)

    def store_db_info(self, session):
        session['dbinfo'] = Redshift.get_fernet().encrypt(json.dumps(asdict(self)).encode()).decode()

    def load_db_info(self, session):
        try:
            return Redshift(**json.loads(Redshift.get_fernet().decrypt(session.get('dbinfo').encode()).decode()))
        except Exception as e:
            print(e)
            return None

    def run_sql(self, query: str, args=None, fetch=True) -> Tuple | int | None:
        try:
            with redshift_connector.connect(
                host=self.host, port=self.port, database=self.name, user=self.user, password=self.password
            ) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, args=args)

                    if fetch:
                        results = cursor.fetchall()
                        return results
                    else:
                        conn.commit()
                        return cursor.rowcount
        except Exception as e:
            print(f"Database error: {e}")
            return None 

    def execute_query(self, query: str, args=None) -> Tuple | None:
        try:
            return self.run_sql(query, args, fetch=True)
        except Exception as e:
            print(e)
            return None 

    def execute_cmd(self, query: str, args=None) -> bool:
        try:
            return self.run_sql(query, args, fetch=False) == -1
        except Exception as e:
            print(e)
            return False

    def test_conn(self) -> bool:
        'Test connection by selecting 1. Returns True if successful.'
        return self.execute_query('SELECT 1') is not None