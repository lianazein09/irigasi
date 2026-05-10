import os

import psycopg


def ensure_sequence(cursor, table_name, column_name, sequence_name):
    cursor.execute(f"CREATE SEQUENCE IF NOT EXISTS {sequence_name};")
    cursor.execute(
        f"""
        ALTER TABLE {table_name}
        ALTER COLUMN {column_name}
        SET DEFAULT nextval('{sequence_name}');
        """
    )
    cursor.execute(
        f"""
        ALTER SEQUENCE {sequence_name}
        OWNED BY {table_name}.{column_name};
        """
    )
    cursor.execute(
        f"""
        SELECT setval(
            '{sequence_name}',
            GREATEST(COALESCE((SELECT MAX({column_name}) FROM {table_name}), 1), 1),
            true
        );
        """
    )


def main():
    conn = psycopg.connect(
        dbname=os.environ.get("DB_NAME", "tani_cerdas"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", ""),
        host=os.environ.get("DB_HOST", "127.0.0.1"),
        port=os.environ.get("DB_PORT", "5432"),
    )
    conn.autocommit = True

    try:
        with conn.cursor() as cursor:
            ensure_sequence(cursor, "users", "id_user", "users_id_user_seq")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
