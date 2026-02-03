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


for i in range(len(result)):
    print(f'plotting rect {i} : {result[i][0]}')
    rect_coordinates = result[i][0].split(',')
    rect_timestamp = result[i][1]

    # get rect coordinates
    rect_x1 = int(rect_coordinates[0])
    rect_y1 = int(rect_coordinates[1])
    rect_x2 = int(rect_coordinates[2])
    rect_y2 = int(rect_coordinates[3])



    # query pixels placed right before the rect
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
            WHERE x BETWEEN LEAST({rect_x1},{rect_x2}) - {BORDER_PAD}
                    AND GREATEST({rect_x1},{rect_x2}) + {BORDER_PAD}
            AND y BETWEEN LEAST({rect_y1},{rect_y2}) - {BORDER_PAD}
                    AND GREATEST({rect_y1},{rect_y2}) + {BORDER_PAD}
            AND timestamp <= '{rect_timestamp}'
        )
        WHERE rn = 1;

    """

    df = duckdb.sql(query_before_rect).df()

    # plot pixels
    x_range = df.x.max() - df.x.min() + 1
    y_range = df.y.max() - df.y.min() + 1
    size = (6*36/x_range)**2 

    plt.figure(figsize=(6,6))
    plt.scatter(df.x, df.y, c=df.pixel_color, s=size, marker="s")
    plt.gca().invert_yaxis()
    plt.axis("equal")
    plt.axis("off")
    plt.show()
