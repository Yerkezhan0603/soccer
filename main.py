import psycopg2
import sys

PG_HOST = "localhost"
PG_DB = "data visualization"
PG_USER = "postgres"
PG_PASS = "0000"

QUERIES_TO_RUN = [
    # basic check: first 10 matches
    ('First 10 matches', 'SELECT match_api_id, season, date, home_team_api_id, away_team_api_id, home_team_goal, away_team_goal FROM "Match" LIMIT 10;'),

    # aggregation: matches per season
    ('Matches per season', 'SELECT season, COUNT(*) AS matches_count FROM "Match" GROUP BY season ORDER BY matches_count DESC LIMIT 10;'),

    # join: avg home goals per league
    ('Avg home goals per league', 'SELECT l.name AS league, AVG(m.home_team_goal) AS avg_home_goals FROM "Match" m JOIN "League" l ON m.league_id = l.id GROUP BY l.name ORDER BY avg_home_goals DESC LIMIT 10;'),

    # analytical example: top scoring teams by total goals
    ('Top scoring teams', '''

SELECT 
    t.team_long_name,
    SUM(
        CASE WHEN m.home_team_api_id = t.team_api_id THEN m.home_team_goal ELSE 0 END +
        CASE WHEN m.away_team_api_id = t.team_api_id THEN m.away_team_goal ELSE 0 END
    ) AS total_goals
FROM "Team" t
LEFT JOIN "Match" m
    ON (m.home_team_api_id = t.team_api_id OR m.away_team_api_id = t.team_api_id)
GROUP BY t.team_long_name
ORDER BY total_goals DESC
LIMIT 20;
    ''')
]

def main():
    try:
        conn = psycopg2.connect(host=PG_HOST, dbname=PG_DB, user=PG_USER, password=PG_PASS)
    except Exception as e:
        print("Cannot connect to database:", e)
        sys.exit(1)

    cur = conn.cursor()
    for title, q in QUERIES_TO_RUN:
        print("\n===", title, "===\n")
        try:
            cur.execute(q)
            rows = cur.fetchall()
            # print header
            colnames = [desc[0] for desc in cur.description]
            print("\t".join(colnames))
            for r in rows:
                print("\t".join([str(x) if x is not None else 'NULL' for x in r]))
        except Exception as e:
            print("Query failed:", e)
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
