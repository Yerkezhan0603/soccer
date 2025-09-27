import psycopg2
import re

# Конфигурация подключения к PostgreSQL
PG_HOST = "localhost"
PG_DB = "data visualization"
PG_USER = "postgres"
PG_PASS = "0000"

def read_sql_queries(filename):
    """Считывает SQL-запросы из файла с метками -- QUERY N"""
    queries = {}
    current_label = None
    current_sql = []

    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line_strip = line.strip()

            # Если это комментарий с меткой (-- QUERY N)
            if line_strip.startswith("-- QUERY"):
                # если был предыдущий запрос, сохраняем его
                if current_label and current_sql:
                    queries[current_label] = " ".join(current_sql).strip()
                    current_sql = []

                # новая метка
                current_label = line_strip.replace("--", "").strip()
            
            # Если это обычная строка SQL
            elif line_strip:
                current_sql.append(line_strip)

        # сохраняем последний запрос
        if current_label and current_sql:
            queries[current_label] = " ".join(current_sql).strip()

    return queries

def main():
    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            dbname=PG_DB,
            user=PG_USER,
            password=PG_PASS
        )
        print("✅ Connected to database successfully!")
    except Exception as e:
        print("❌ Unable to connect to database:", e)
        return

    # Читаем запросы
    queries = read_sql_queries('queries.sql')
    print(f"📌 Found {len(queries)} queries in queries.sql")

    cur = conn.cursor()

    for label, q in queries.items():
        print(f"\n=== {label} ===\n")
        try:
            cur.execute(q)

            if cur.description:  # если есть результат
                rows = cur.fetchall()
                colnames = [desc[0] for desc in cur.description]

                print("\t".join(colnames))
                for r in rows:
                    print("\t".join([str(x) if x is not None else 'NULL' for x in r]))
            else:
                print("Query executed successfully, no results to fetch.")

        except Exception as e:
            print(f"⚠️ Error executing {label}: {e}")

    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
