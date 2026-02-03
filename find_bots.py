import duckdb

consistent_placement_users_query = f"""
WITH gaps AS (
    SELECT user_int_id,
    timestamp, timestamp - LAG(timestamp)
    OVER ( PARTITION BY user_int_id ORDER BY timestamp ) AS time_gap,
    FROM read_parquet('../asgn3/r_place.parquet')
),

    filtered AS ( SELECT * FROM gaps WHERE time_gap IS NOT NULL )

    SELECT 
        user_int_id,
        stddev_samp(EXTRACT(EPOCH FROM time_gap)) AS std_seconds_between,
        avg(EXTRACT(EPOCH FROM time_gap)) AS avg_seconds_between,
        COUNT(*) AS placements
    FROM filtered GROUP BY user_int_id HAVING COUNT(*) >= 20 -- avoid small samples
    AND avg_seconds_between > 305
    ORDER BY std_seconds_between ASC
    LIMIT 10; 
"""




result = duckdb.sql(consistent_placement_users_query).fetchall()

print("Users with most consistent placement intervals:\n")
for row in result:
    print(f"User ID: {row[0]}, Std Dev: {row[1]}, Avg: {row[2]}, Count: {row[3]}")


random_placement_users_query = f"""
WITH gaps AS (
    SELECT user_int_id,
    timestamp, timestamp - LAG(timestamp)
    OVER ( PARTITION BY user_int_id ORDER BY timestamp ) AS time_gap,
    FROM read_parquet('../asgn3/r_place.parquet')
),
    filtered AS ( SELECT * FROM gaps WHERE time_gap IS NOT NULL )

    SELECT 
        user_int_id,
        stddev_samp(EXTRACT(EPOCH FROM time_gap)) AS std_seconds_between,
        avg(EXTRACT(EPOCH FROM time_gap)) AS avg_seconds_between,
        COUNT(*) AS placements
    FROM filtered GROUP BY user_int_id HAVING COUNT(*) >= 20 -- avoid small samples
    AND avg_seconds_between > 305
    ORDER BY RANDOM()
    LIMIT 10; 
"""

result = duckdb.sql(random_placement_users_query).fetchall()

print("Random set of users with placement intervals:\n")
for row in result:
    print(f"User ID: {row[0]}, Std Dev: {row[1]}, Avg: {row[2]}, Count: {row[3]}")