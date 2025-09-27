-- QUERY 1
SELECT * FROM "Match" LIMIT 10;

-- QUERY 2
SELECT match_api_id, season, date, home_team_api_id, away_team_api_id, home_team_goal, away_team_goal,
       (home_team_goal + away_team_goal) AS total_goals
FROM "Match"
WHERE season = '2014/2015' AND (home_team_goal + away_team_goal) > 3
ORDER BY date DESC
LIMIT 50;

-- QUERY 3
SELECT l.name AS league, AVG(m.home_team_goal) AS avg_home_goals
FROM "Match" m
JOIN "League" l ON m.league_id = l.id
GROUP BY l.name
ORDER BY avg_home_goals DESC
LIMIT 10;

-- QUERY 4
SELECT season, COUNT(*) AS matches_count
FROM "Match"
GROUP BY season
ORDER BY matches_count DESC;

-- QUERY 5
SELECT t.team_long_name,
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

-- QUERY 6
SELECT pa.date::date AS snapshot_date, AVG(pa.overall_rating)::numeric(8,2) AS avg_overall
FROM "Player_Attributes" pa
GROUP BY snapshot_date
ORDER BY snapshot_date DESC
LIMIT 20;

-- QUERY 7
SELECT t.team_long_name,
       SUM(
         CASE WHEN m.home_team_api_id = t.team_api_id THEN COALESCE(m.home_team_goal, 0) ELSE 0 END +
         CASE WHEN m.away_team_api_id = t.team_api_id THEN COALESCE(m.away_team_goal, 0) ELSE 0 END
       ) AS total_goals
FROM "Team" t
LEFT JOIN "Match" m ON (m.home_team_api_id = t.team_api_id OR m.away_team_api_id = t.team_api_id)
GROUP BY t.team_long_name
ORDER BY total_goals DESC
LIMIT 20;

-- QUERY 8
SELECT t.team_long_name,
       SUM((m.card IS NOT NULL)::int) as matches_with_cards,
       SUM(COALESCE(length(m.card) - length(replace(m.card, ';', '')) + 1, 0)) AS approx_card_count
FROM "Team" t
LEFT JOIN "Match" m ON (m.home_team_api_id = t.team_api_id OR m.away_team_api_id = t.team_api_id)
GROUP BY t.team_long_name
ORDER BY approx_card_count DESC
LIMIT 20;

-- QUERY 9
SELECT match_api_id, date, home_team_api_id, away_team_api_id,
       COALESCE(length(shoton) - length(replace(shoton, ';', '')) + 1, 0) AS shots_on_target_count
FROM "Match"
ORDER BY shots_on_target_count DESC
LIMIT 20;

-- QUERY 10
SELECT season, AVG(home_team_goal + away_team_goal) AS avg_goals
FROM "Match"
GROUP BY season
ORDER BY avg_goals DESC
LIMIT 10;
