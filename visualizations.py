import sqlite3
import matplotlib.pyplot as plt

DB_PATH = "resort.db"   # change if your DB file has a different path/name


def get_tennis_court_usage(db_path=DB_PATH):
    """Return tennis court IDs and number of logged actions per court."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    query = """
    WITH tennis_courts AS (
        SELECT
            client_id,
            action,
            success,
            info,
            TRIM(SUBSTR(info, 7, instr(info || ',', ',') - 7)) AS court_id
        FROM activities
        WHERE amenity = 'Tennis Court'
          AND info LIKE 'Court %'
    )
    SELECT
        court_id,
        COUNT(*) AS total_actions_on_court
    FROM tennis_courts
    GROUP BY court_id
    ORDER BY total_actions_on_court DESC;
    """
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()

    court_ids = [row[0] for row in rows]
    counts = [row[1] for row in rows]
    return court_ids, counts


def get_vending_product_usage(db_path=DB_PATH):
    """Return vending product names and how many times each was bought."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    query = """
    WITH vending AS (
        SELECT
            client_id,
            info,
            TRIM(SUBSTR(info, 7, instr(info || ',', ',') - 7)) AS product
        FROM activities
        WHERE amenity = 'Coworking vending'
    )
    SELECT
        product,
        COUNT(*) AS times_bought
    FROM vending
    GROUP BY product
    ORDER BY times_bought DESC;
    """
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()

    products = [row[0] for row in rows]
    counts = [row[1] for row in rows]
    return products, counts


def get_gym_usage(db_path=DB_PATH):
    """Return gym actions (individual vs private class) and their counts."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    query = """
    SELECT
        action,
        COUNT(*) AS times
    FROM activities
    WHERE amenity = 'gym'
      AND action IN ('enter_individual', 'private_class')
    GROUP BY action
    ORDER BY action;
    """
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()

    actions = [row[0] for row in rows]
    counts = [row[1] for row in rows]
    return actions, counts


def get_spa_usage(db_path=DB_PATH):
    """
    Return how many distinct clients used:
    - a massage
    - a sauna
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    query = """
    SELECT
        category,
        COUNT(DISTINCT client_id) AS clients
    FROM (
        SELECT
            client_id,
            'massage' AS category
        FROM activities
        WHERE lower(amenity) = 'spa massage'
          AND action = 'Join massage'
          AND success = 1

        UNION ALL

        SELECT
            client_id,
            'sauna' AS category
        FROM activities
        WHERE lower(amenity) = 'spa sauna'
          AND success = 1
    )
    GROUP BY category
    ORDER BY category;
    """
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()

    categories = [row[0] for row in rows]
    counts = [row[1] for row in rows]
    return categories, counts


def get_padel_court_usage(db_path=DB_PATH):
    """Return padel court IDs and number of logged actions per court."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    query = """
    WITH padel_courts AS (
        SELECT
            client_id,
            action,
            success,
            info,
            TRIM(SUBSTR(info, 7, instr(info || ',', ',') - 7)) AS court_id
        FROM activities
        WHERE amenity = 'Padel Court'
          AND info LIKE 'Court %'
    )
    SELECT
        court_id,
        COUNT(*) AS total_actions_on_court
    FROM padel_courts
    GROUP BY court_id
    ORDER BY total_actions_on_court DESC;
    """
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()

    court_ids = [row[0] for row in rows]
    counts = [row[1] for row in rows]
    return court_ids, counts


def plot_tennis_court_usage():
    court_ids, counts = get_tennis_court_usage()
    if not court_ids:
        print("No tennis court data found in the database, because of raining.")
        return

    plt.figure()
    plt.bar(court_ids, counts)
    plt.xlabel("Tennis court ID")
    plt.ylabel("Number of logged actions")
    plt.title("Tennis court usage in resort simulation")
    plt.tight_layout()
    plt.show()


def plot_vending_product_usage():
    products, counts = get_vending_product_usage()
    if not products:
        print("No coworking vending data found in the database.")
        return

    plt.figure()
    plt.bar(products, counts)
    plt.xlabel("Product")
    plt.ylabel("Times bought")
    plt.title("Coworking vending: most purchased items")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()


def plot_gym_usage():
    actions, counts = get_gym_usage()
    if not actions:
        print("No gym data found in the database.")
        return

    plt.figure()
    plt.bar(actions, counts)
    plt.xlabel("Gym action")
    plt.ylabel("Number of logged actions")
    plt.title("Gym: individual vs private class")
    plt.tight_layout()
    plt.show()


def plot_spa_usage():
    categories, counts = get_spa_usage()
    if not categories:
        print("No spa/massage data found in the database.")
        return

    plt.figure()
    plt.bar(categories, counts)
    plt.xlabel("Spa service")
    plt.ylabel("Number of distinct clients")
    plt.title("Spa usage: massage vs sauna")
    plt.tight_layout()
    plt.show()


def plot_padel_court_usage():
    court_ids, counts = get_padel_court_usage()
    if not court_ids:
        print("No padel court data found in the database, because of raining.")
        return

    plt.figure()
    plt.bar(court_ids, counts)
    plt.xlabel("Padel court ID")
    plt.ylabel("Number of logged actions")
    plt.title("Padel court usage in resort simulation")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    plot_tennis_court_usage()
    plot_vending_product_usage()
    plot_gym_usage()
    plot_spa_usage()
    plot_padel_court_usage()