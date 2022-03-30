import pymysql
from .pool import POOL


class SQLHelper(object):

    @staticmethod
    def open():
        conn = POOL.connection()
        cursor = conn.cursor()
        return conn, cursor

    @staticmethod
    def close(conn, cursor):
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def feach_one(sql):
        conn, cursor = SQLHelper.open()

        cursor.execute(sql)

        object = cursor.fetchone()

        SQLHelper.close(conn, cursor)
        return object

    @staticmethod
    def insert1(sql):
        conn, cursor = SQLHelper.open()

        cursor.execute(sql)

        object = cursor.fetchone()

        SQLHelper.close(conn, cursor)
        return object

    @staticmethod
    def insert2(sql, args):
        conn, cursor = SQLHelper.open()

        cursor.execute(sql, args)

        object = cursor.fetchone()

        SQLHelper.close(conn, cursor)
        return object

    @staticmethod
    def delete(sql, args):
        conn, cursor = SQLHelper.open()

        cursor.execute(sql, args)

        object = cursor.fetchone()

        SQLHelper.close(conn, cursor)
        return object

    @staticmethod
    def update(sql, args):
        conn, cursor = SQLHelper.open()

        cursor.execute(sql, args)

        object = cursor.fetchone()

        SQLHelper.close(conn, cursor)
        return object
