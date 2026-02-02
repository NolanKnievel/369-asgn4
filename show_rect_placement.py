import duckdb
import matplotlib.pyplot as plt
import pandas
import random

# border pad to give us more context around censored rect
BORDER_PAD = 25


# note my parquet truncates the rect placements, so we read from the csv
query_rect_coordinates = f"""
SELECT coordinate, timestamp
FROM read_csv('../asgn1/2022_place_canvas_history.csv')
WHERE LENGTH(coordinate) - LENGTH(REPLACE(coordinate, ',', '')) > 1
AND ABS(
    (CAST(SPLIT_PART(coordinate, ',', 2) AS INT) - CAST(SPLIT_PART(coordinate, ',', 1) AS INT)) *
    (CAST(SPLIT_PART(coordinate, ',', 4) AS INT) - CAST(SPLIT_PART(coordinate, ',', 3) AS INT))
) > 100
"""

result = duckdb.sql(query_rect_coordinates).fetchall()

num = random.randint(0, len(result) - 1)

example_rect_coordinates = result[num][0].split(',')
example_rect_timestamp = result[num][1]


rect_x1 = int(example_rect_coordinates[0])
rect_y1 = int(example_rect_coordinates[1])
rect_x2 = int(example_rect_coordinates[2])
rect_y2 = int(example_rect_coordinates[3])


query_before_rect = f"""
    SELECT x, y, pixel_color, timestamp
    FROM (
        SELECT
            x,
            y,
            pixel_color,
            timestamp,
            ROW_NUMBER() OVER (
                PARTITION BY x, y
                ORDER BY timestamp DESC
            ) AS rn
        FROM read_parquet('../asgn3/r_place.parquet')
        WHERE x BETWEEN {rect_x1 - BORDER_PAD} AND {rect_x2 + BORDER_PAD}
        AND y BETWEEN {rect_y1 - BORDER_PAD} AND {rect_y2 + BORDER_PAD}
        AND timestamp <= '{example_rect_timestamp}'
    )
    WHERE rn = 1;

"""


df = duckdb.sql(query_before_rect).df()

# Estimate pixel size
x_range = df.x.max() - df.x.min() + 1
y_range = df.y.max() - df.y.min() + 1
size = (6*72/x_range)**2  # 6 inches * 72 dpi / width in pixels

plt.figure(figsize=(6,6))
plt.scatter(df.x, df.y, c=df.pixel_color, s=size, marker="s")  # marker="s" = square
plt.gca().invert_yaxis()
plt.axis("equal")
plt.axis("off")
plt.show()