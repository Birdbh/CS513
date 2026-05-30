import pandas as pd
import sqlite3

def run():
    print("Loading datasets...")
    dishes = pd.read_csv('Dish.csv')
    menus = pd.read_csv('Menu.csv')
    menu_items = pd.read_csv('MenuItem.csv')
    menu_pages = pd.read_csv('MenuPage.csv')
    
    print("Creating in-memory SQLite database...")
    conn = sqlite3.connect(':memory:')
    dishes.to_sql('Dish', conn, index=False)
    menus.to_sql('Menu', conn, index=False)
    menu_items.to_sql('MenuItem', conn, index=False)
    menu_pages.to_sql('MenuPage', conn, index=False)
    
    query = """
    WITH MenuDecades AS (
        SELECT 
            id,
            CAST(SUBSTR(date, 1, 4) AS INTEGER) / 10 * 10 AS decade
        FROM Menu
        WHERE date IS NOT NULL
    ),
    DecadeDishStats AS (
        SELECT 
            md.decade,
            d.name AS dish_name,
            COUNT(*) AS frequency,
            AVG(mi.price) AS avg_price
        FROM MenuItem mi
        JOIN MenuPage mp ON mi.menu_page_id = mp.id
        JOIN MenuDecades md ON mp.menu_id = md.id
        JOIN Dish d ON mi.dish_id = d.id
        GROUP BY md.decade, d.name
    )
    SELECT decade, dish_name, frequency, avg_price
    FROM (
        SELECT 
            decade, 
            dish_name, 
            frequency, 
            avg_price,
            ROW_NUMBER() OVER(PARTITION BY decade ORDER BY frequency DESC) as rank
        FROM DecadeDishStats
    )
    WHERE rank <= 5
    ORDER BY decade, rank;
    """
    
    print("Executing query...")
    result = pd.read_sql_query(query, conn)
    
    # We filter out where decade is 0 to show some actual decades, but let's print all to show issues
    print("Top results per decade:")
    print(result.to_string())

if __name__ == '__main__':
    run()
