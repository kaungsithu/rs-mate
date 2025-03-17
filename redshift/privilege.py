import redshift.sql_queries as sql
from redshift.database import Redshift
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class RedshiftPrivilege:
    schema_name: str
    schema_priv: str
    default_priv: str
    dpriv_owner_id: int
    dpriv_owner_name: str
    id: int
    id_name: str
    id_type: str
    schema_admin: bool
    dpriv_admin: bool

    def __str__(self):
        return f"{self.schema_name}\t{self.schema_priv}\t{self.default_priv}\t{self.dpriv_owner_id}\t{self.dpriv_owner_name}\t{self.id}\t{self.id_name}\t{self.id_type}\t{self.schema_admin}\t{self.dpriv_admin}"

class RedshiftPrivileges:
    def __init__(self, redshift: Redshift):
        self.redshift = redshift

    def get_schema_privileges(self) -> list[RedshiftPrivilege]:
        query = sql.GET_SCHEMA_PRIVILEGES
        results = self.redshift.query(query)
        return [RedshiftPrivilege(**row) for row in results]

    def get_user_privileges(self, user_id: int) -> list[RedshiftPrivilege]:
        query = sql.GET_USER_PRIVILEGES
        results = self.redshift.query(query, user_id)
        return [RedshiftPrivilege(**row) for row in results]

    def get_user_privileges_by_name(self, user_name: str) -> list[RedshiftPrivilege]:
        query = sql.GET_USER_PRIVILEGES_BY_NAME
        results = self.redshift.query(query, user_name)
        return [RedshiftPrivilege(**row) for row in results]

    def get_user_privileges_by_id(self, user_id: int) -> list[RedshiftPrivilege]:
        query = sql.GET_USER_PRIVILEGES_BY_ID
        results = self.redshift.query(query, user_id)
        return [RedshiftPrivilege(**row) for row in results]

    def get_user_privileges_by_schema(self, schema_name: str) -> list[RedshiftPrivilege]:
        query = sql.GET_USER_PRIVILEGES_BY_SCHEMA
        results = self.redshift.query(query, schema_name)
        return [RedshiftPrivilege(**row) for row in results]