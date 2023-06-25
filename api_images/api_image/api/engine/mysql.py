import pymysql
from pymysql import err
import pandas as pd
from sqlalchemy import create_engine


class EngineMySql:
    def __init__(self, host, user, password, db,autocommit=True):
        self.host = host
        self.user = user
        self.password = password
        self.db = db
        self.autocommit = autocommit

    def engine_with_url(self):
        return create_engine(f'mysql+pymysql://{self.user}:{self.password}@{self.host}/{self.db}')

    def run_query(self, query, dql=True):
        try:
            con = self.__get_engine()
            with con.cursor() as cursor:
                cursor.execute(query)
                if dql:
                    data = cursor.fetchall()
                    return pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])
        except Exception as ex:
            print(f'Error: {ex}')
        finally:
            con.close()

    def __get_engine(self):
        try:
            con = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                autocommit=self.autocommit,
                database=self.db,
            )
            return con
        except err.OperationalError as error:
            raise err.OperationalError(f"An error occurred during the database connection: {error}")