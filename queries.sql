-- Basic checks
-- 1) Show first 10 rows of Match
SELECT * FROM "Match" LIMIT 10;

-- 2) Filtering + sorting: matches in 2014 season with more than 3 total goals, newest first
SELECT match_api_id, season, date, home_team_api_id, away_team_api_id, home_team_goal, away_team_goal,
       (home_team_goal + away_team_goal) AS total_goals
FROM "Match"
WHERE season = '2014/2015' AND (home_team_goal + away_team_goal) > 3
ORDER BY date DESC
LIMIT 50;

-- 3) Aggregation example: average home goals per league (top 10)
SELECT l.name AS league, AVG(m.home_team_goal) AS avg_home_goals
FROM "Match" m
JOIN "League" l ON m.league_id = l.id
GROUP BY l.name
ORDER BY avg_home_goals DESC
LIMIT 10;

-- 4) COUNT example: number of matches per season (descending)
SELECT season, COUNT(*) AS matches_count
FROM "Match"
GROUP BY season
ORDER BY matches_count DESC;

-- 5) JOIN example: top scoring teams (total goals scored as home + away)
SELECT t.team_long_name,
       SUM(COALESCE(m.home_team_goal,0) FILTER (WHERE m.home_team_api_id = t.team_api_id) +
           COALESCE(m.away_team_goal,0) FILTER (WHERE m.away_team_api_id = t.team_api_id)) AS total_goals
FROM "Team" t
LEFT JOIN "Match" m ON (m.home_team_api_id = t.team_api_id OR m.away_team_api_id = t.team_api_id)
GROUP BY t.team_long_name
ORDER BY total_goals DESC
LIMIT 20;

-- Analytical topics (10 queries)
-- Topic 1: Average player overall_rating per season (use Player_Attributes)
SELECT pa.date::date AS snapshot_date, AVG(pa.overall_rating)::numeric(8,2) AS avg_overall
FROM "Player_Attributes" pa
GROUP BY snapshot_date
ORDER BY snapshot_date DESC
LIMIT 20;

-- Topic 2: Top 10 players by potential (latest snapshot)
WITH latest AS (
  SELECT player_api_id, MAX(date) AS maxdate
  FROM "Player_Attributes"
  GROUP BY player_api_id
)
SELECT p.player_name, pa.potential, pa.overall_rating
FROM "Player_Attributes" pa
JOIN latest l ON pa.player_api_id = l.player_api_id AND pa.date = l.maxdate
JOIN "Player" p ON p.player_api_id = pa.player_api_id
ORDER BY pa.potential DESC
LIMIT 10;

-- Topic 3: Teams with highest average possession (home matches)
SELECT t.team_long_name, AVG((regexp_replace(m.possession, '%',''))::numeric) AS avg_possession
FROM "Match" m
JOIN "Team" t ON m.home_team_api_id = t.team_api_id
WHERE m.possession IS NOT NULL AND m.possession <> ''
GROUP BY t.team_long_name
ORDER BY avg_possession DESC
LIMIT 15;

-- Topic 4: Number of home wins vs away wins per league (season 2014/2015)
SELECT l.name,
       SUM(CASE WHEN m.home_team_goal > m.away_team_goal THEN 1 ELSE 0 END) AS home_wins,
       SUM(CASE WHEN m.away_team_goal > m.home_team_goal THEN 1 ELSE 0 END) AS away_wins,
       SUM(CASE WHEN m.home_team_goal = m.away_team_goal THEN 1 ELSE 0 END) AS draws
FROM "Match" m
JOIN "League" l ON m.league_id = l.id
WHERE season = '2014/2015'
GROUP BY l.name
ORDER BY home_wins DESC
LIMIT 20;

-- Topic 5: Average market odds (B365H, B365D, B365A) per league (as a proxy for home advantage)
SELECT l.name,
       AVG(m."B365H") AS avg_B365H,
       AVG(m."B365D") AS avg_B365D,
       AVG(m."B365A") AS avg_B365A
FROM "Match" m
JOIN "League" l ON m.league_id = l.id
GROUP BY l.name
ORDER BY avg_B365H NULLS LAST
LIMIT 15;

-- Topic 6: Players who appeared most frequently in matches (count of appearances as home or away player)
SELECT p.player_name, COUNT(*) AS appearances
FROM "Match" m
JOIN "Player" p ON p.player_api_id IN (
  m.home_player_1, m.home_player_2, m.home_player_3, m.home_player_4, m.home_player_5,
  m.home_player_6, m.home_player_7, m.home_player_8, m.home_player_9, m.home_player_10, m.home_player_11,
  m.away_player_1, m.away_player_2, m.away_player_3, m.away_player_4, m.away_player_5,
  m.away_player_6, m.away_player_7, m.away_player_8, m.away_player_9, m.away_player_10, m.away_player_11
)
GROUP BY p.player_name
ORDER BY appearances DESC
LIMIT 20;

-- Topic 7: Correlation-ish: do teams with higher buildUpPlaySpeed concede fewer goals? (avg by team)
SELECT t.team_long_name,
       AVG(ta.buildUpPlaySpeed::numeric) AS avg_build_up_speed,
       AVG(CASE WHEN m.home_team_api_id = t.team_api_id THEN m.away_team_goal
                WHEN m.away_team_api_id = t.team_api_id THEN m.home_team_goal END) AS avg_conceded
FROM "Team" t
LEFT JOIN "Team_Attributes" ta ON ta.team_api_id = t.team_api_id
LEFT JOIN "Match" m ON (m.home_team_api_id = t.team_api_id OR m.away_team_api_id = t.team_api_id)
GROUP BY t.team_long_name
ORDER BY avg_build_up_speed DESC
LIMIT 20;

-- Topic 8: Count of cards per team (home + away)
SELECT t.team_long_name,
       SUM((m.card IS NOT NULL)::int) as matches_with_cards,
       SUM(COALESCE((length(m.card) - length(replace(m.card, ';','')) + 1),0)) AS approx_card_count
FROM "Team" t
LEFT JOIN "Match" m ON (m.home_team_api_id = t.team_api_id OR m.away_team_api_id = t.team_api_id)
GROUP BY t.team_long_name
ORDER BY approx_card_count DESC
LIMIT 20;

-- Topic 9: Top 10 matches with highest total shots on target (use shoton column which may have ; separated)
SELECT match_api_id, date, home_team_api_id, away_team_api_id,
       COALESCE((length(shoton) - length(replace(shoton, ';','')) + 1),0) AS shots_on_target_count
FROM "Match"
ORDER BY shots_on_target_count DESC
LIMIT 20;

-- Topic 10: Seasons with highest average total goals per match
SELECT season, AVG(home_team_goal + away_team_goal) AS avg_goals
FROM "Match"
GROUP BY season
ORDER BY avg_goals DESC
LIMIT 10;
