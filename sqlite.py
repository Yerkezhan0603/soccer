import sqlite3
import psycopg2

# Настройки
SQLITE_FILE = r"C:\Users\Erasyl\Downloads\archive\database.sqlite"
PG_HOST = "localhost"
PG_DB = "data visualization"
PG_USER = "postgres"
PG_PASS = "0000"

# Подключение к SQLite
sqlite_conn = sqlite3.connect(SQLITE_FILE)
sqlite_cur = sqlite_conn.cursor()

# Подключение к PostgreSQL
pg_conn = psycopg2.connect(
    host=PG_HOST,
    dbname=PG_DB,
    user=PG_USER,
    password=PG_PASS
)
pg_conn.autocommit = True  # включаем автокоммит
pg_cur = pg_conn.cursor()

# Получаем список таблиц из SQLite
sqlite_cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = sqlite_cur.fetchall()

for table_name_tuple in tables:
    table_name = table_name_tuple[0]
    print(f"\n📦 Перенос таблицы: {table_name}")

    # Получаем схему таблицы из SQLite
    sqlite_cur.execute(f"PRAGMA table_info({table_name});")
    columns_info = sqlite_cur.fetchall()
    columns = [col[1] for col in columns_info]  # имена колонок

    # Создаем таблицу в PostgreSQL (если нет)
    col_defs = []
    for col in columns_info:
        col_name, col_type = col[1], col[2]

        # Простое сопоставление типов
        if "INT" in col_type.upper():
            pg_type = "INTEGER"
        elif "CHAR" in col_type.upper() or "CLOB" in col_type.upper() or "TEXT" in col_type.upper():
            pg_type = "TEXT"
        elif "REAL" in col_type.upper() or "FLOA" in col_type.upper() or "DOUB" in col_type.upper():
            pg_type = "REAL"
        elif "DATE" in col_type.upper():
            pg_type = "TIMESTAMP"
        else:
            pg_type = "TEXT"

        col_defs.append(f"\"{col_name}\" {pg_type}")

    create_sql = f"CREATE TABLE IF NOT EXISTS \"{table_name}\" ({', '.join(col_defs)});"
    pg_cur.execute(create_sql)

    # Очистка таблицы перед вставкой
    pg_cur.execute(f'TRUNCATE TABLE "{table_name}" RESTART IDENTITY CASCADE;')

    # Перенос данных
    sqlite_cur.execute(f"SELECT * FROM {table_name};")
    rows = sqlite_cur.fetchall()
    if rows:
        placeholders = ", ".join(["%s"] * len(columns))
        col_names = ", ".join([f'"{c}"' for c in columns])
        insert_sql = f'INSERT INTO "{table_name}" ({col_names}) VALUES ({placeholders})'

        for row in rows:
            try:
                pg_cur.execute(insert_sql, row)
            except Exception as e:
                print(f"⚠ Ошибка вставки в {table_name}: {e}\n  Строка: {row}")
                pg_conn.rollback()  # сброс транзакции, чтобы не зависнуть

print("\n✅ Перенос завершён.")

# Закрываем соединения
sqlite_conn.close()
pg_cur.close()
pg_conn.close()
