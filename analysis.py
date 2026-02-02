import duckdb
# 2k rows have second precision, pretty much all different uuids
# no null timestamps
# all uuids of same length ending in ==

# 12,147 fast actions

# ROW
# (datetime.datetime(2022, 4, 4, 1, 14, 3, 649000), 'lu9LCmRw34gF/N3h03n6EfMjIv9b29OCrDNDhkaWnZH1NPpLDFtnk3R4dURK4fQAoOBHQTUnyXYwpgWGD3v04w==', '#94B3FF', '97,1974')


def analyze_parquet():

    # analyze_rects()
    analyze_bots()


    query4 = """
    SELECT *
    FROM read_parquet('../asgn3/r_place.parquet')
    WHERE user_int_id = 6447529
    """

    
def analyze_bots():

    query_fast_placements = """
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
    query_fast_placements_count = """
        SELECT COUNT(*)
        FROM (
        SELECT user_int_id,
                timestamp,
                timestamp - LAG(timestamp) OVER (PARTITION BY user_int_id ORDER BY timestamp) AS diff
        FROM read_parquet('../asgn3/r_place.parquet')
        )
        WHERE diff < INTERVAL '4.9 minutes'    
    """

    count_fast_placements = duckdb.sql(query_fast_placements_count).fetchall()[0][0]

    print(f'There were {count_fast_placements} placements made with less than 5 minutes between actions.\n')
    print(f'Fast placements:\n')
    fast_placements = duckdb.sql(query_fast_placements).fetchall()
    for placement in fast_placements:
        print(f'User ID: {placement[0]}, Fast Actions: {placement[1]}')

    query_timed_placements = """
    """



def analyze_rects():
    
    # get count of rect placements
    query_rects = """
    SELECT COUNT(*)
    FROM read_csv('../asgn1/2022_place_canvas_history.csv')
    WHERE LENGTH(coordinate) - LENGTH(REPLACE(coordinate, ',', '')) > 1
    """

    count = duckdb.sql(query_rects).fetchall()[0]
    print(f"There are {count[0]} placements with more than two coordinates.")

    # get colors of rect placements
    query_colors = """
    SELECT DISTINCT pixel_color, COUNT(*) AS count
    FROM read_csv('../asgn1/2022_place_canvas_history.csv')
    WHERE LENGTH(coordinate) - LENGTH(REPLACE(coordinate, ',', '')) > 1
    GROUP BY pixel_color
    ORDER BY count DESC
    """

    colors = duckdb.sql(query_colors).fetchall()
    print("Colors of rectangle placements:")
    for color in colors:
        print(f'Color: {color[0]}, Count: {color[1]}')

    # get placement area of each rect placement
    rect_areas = """
    SELECT user_id, (x2 - x1) * (y2 - y1) AS area, coordinate, pixel_color
    FROM (
        SELECT user_id,
               CAST(SPLIT_PART(coordinate, ',', 1) AS INTEGER) AS x1,
               CAST(SPLIT_PART(coordinate, ',', 2) AS INTEGER) AS y1,
               CAST(SPLIT_PART(coordinate, ',', 3) AS INTEGER) AS x2,
               CAST(SPLIT_PART(coordinate, ',', 4) AS INTEGER) AS y2,
               pixel_color,
               coordinate
        FROM read_csv('../asgn1/2022_place_canvas_history.csv')
        WHERE LENGTH(coordinate) - LENGTH(REPLACE(coordinate, ',', '')) > 1
    ) AS rects
    ORDER BY area DESC
    """
    areas = duckdb.sql(rect_areas).fetchall()
    print("Placement areas of rectangle placements:")
    for area in areas:
        print(f'User ID: {area[0]}, Area: {area[1]}, Coordinate: {area[2]}, Color: {area[3]}')





analyze_parquet()

'''
some coordinates have four points: 
('1372,1472,1406,1497',)
('1375,1355,1424,1399',)
('1349,1718,1424,1752',)
('1373,1400,1419,1436',)
('1371,1438,1418,1472',)
('298,1805,329,1839',)
('257,1736,296,1780',)
('271,1835,296,1859',)
('298,1770,334,1803',)
('297,1750,364,1813',)
('251,1805,296,1812',)
('551,1311,562,1342',)
('547,1330,550,1342',)
('44,1652,165,1899',)
('51,1691,154,1807',)
('23,1523,172,1792',)
('871,546,878,550',)
('862,540,868,544',)
('862,540,873,545',)



'''