import duckdb
import pandas
import matplotlib.pyplot as plt

RADIUS = 30

# get fast placement users
query_fast_placement_users = """
    SELECT user_int_id, COUNT(*) AS fast_actions
    FROM (
    SELECT user_int_id,
            timestamp,
            timestamp - LAG(timestamp) OVER (PARTITION BY user_int_id ORDER BY timestamp) AS diff
    FROM read_parquet('../asgn3/r_place.parquet')
    )
    WHERE diff < INTERVAL '4.9 minutes'
    GROUP BY user_int_id
    ORDER BY fast_actions DESC
    LIMIT 20
    """

result = duckdb.sql(query_fast_placement_users).fetchall()

fast_placement_users = [row[0] for row in result]

for user in fast_placement_users:

    # get pixels by user, near median of their placements
    fast_placements_query = f"""
    WITH user_points AS (
        SELECT x, y, timestamp, pixel_color
        FROM read_parquet('../asgn3/r_place.parquet')
        WHERE user_int_id = {user}
    ),
    med AS (
        SELECT median(x) AS med_x, median(y) AS med_y FROM user_points
    )
    SELECT p.*
    FROM user_points p, med
    WHERE abs(p.x - med.med_x) <= {RADIUS}
    AND abs(p.y - med.med_y) <= {RADIUS}
    ORDER BY p.timestamp DESC;
    """

    df = duckdb.sql(fast_placements_query).df()


    # plot rapid pixels
    x_range = df.x.max() - df.x.min() + 1
    y_range = df.y.max() - df.y.min() + 1
    size = (6*36/x_range)**2 

    plt.figure(figsize=(6,6))
    plt.scatter(df.x, df.y, c=df.pixel_color, s=size, marker="s")
    plt.gca().invert_yaxis()
    plt.axis("equal")
    plt.axis("off")
    plt.show()
