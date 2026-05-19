import os

import pymysql


def main():
    engine_name = os.environ.get("DB_ENGINE", "mysql").strip().lower()
    if engine_name != "mysql":
        return

    db_name = os.environ["DB_NAME"]
    db_user = os.environ["DB_USER"]
    db_password = os.environ["DB_PASSWORD"]
    db_host = os.environ.get("DB_HOST", "127.0.0.1")
    db_port = int(os.environ.get("DB_PORT", "3306"))
    admin_user = os.environ.get("DB_ADMIN_USER", "root")
    admin_password = os.environ.get(
        "DB_ADMIN_PASSWORD",
        os.environ.get("DB_ROOT_PASSWORD", ""),
    )

    connection = pymysql.connect(
        host=db_host,
        port=db_port,
        user=admin_user,
        password=admin_password,
        autocommit=True,
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci"
            )
            cursor.execute(
                "CREATE USER IF NOT EXISTS %s@'%%' IDENTIFIED BY %s",
                (db_user, db_password),
            )
            cursor.execute(
                "ALTER USER %s@'%%' IDENTIFIED BY %s",
                (db_user, db_password),
            )
            cursor.execute(
                f"GRANT ALL PRIVILEGES ON `{db_name}`.* TO %s@'%%'",
                (db_user,),
            )
            cursor.execute("FLUSH PRIVILEGES")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
