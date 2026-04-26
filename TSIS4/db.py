import psycopg2
from config import load_config

def connect():
    """Подключение к БД"""
    try:
        return psycopg2.connect(**load_config())
    except Exception as e:
        print(f"Ошибка БД: {e}")
        return None

def init_db():
    """Создает таблицы, если их еще нет"""
    conn = connect()
    if not conn: return
    with conn.cursor() as cur:
        # Таблица игроков
        cur.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL
            );
        """)
        # Таблица игровых сессий (результаты)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS game_sessions (
                id SERIAL PRIMARY KEY,
                player_id INTEGER REFERENCES players(id),
                score INTEGER NOT NULL,
                level_reached INTEGER NOT NULL,
                played_at TIMESTAMP DEFAULT NOW()
            );
        """)
        conn.commit()
    conn.close()
    print("База данных успешно инициализирована!")

def get_or_create_player(username):
    """Ищет игрока по имени, если нет - создает"""
    conn = connect()
    if not conn: return None
    player_id = None
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM players WHERE username = %s", (username,))
        result = cur.fetchone()
        if result:
            player_id = result[0]
        else:
            cur.execute("INSERT INTO players (username) VALUES (%s) RETURNING id", (username,))
            player_id = cur.fetchone()[0]
            conn.commit()
    conn.close()
    return player_id

def save_session(username, score, level):
    """Сохраняет результат после Game Over"""
    player_id = get_or_create_player(username)
    if not player_id: return
    conn = connect()
    with conn.cursor() as cur:
        cur.execute("INSERT INTO game_sessions (player_id, score, level_reached) VALUES (%s, %s, %s)",
                    (player_id, score, level))
        conn.commit()
    conn.close()

def get_personal_best(username):
    """Достает личный рекорд игрока"""
    conn = connect()
    if not conn: return 0
    best_score = 0
    with conn.cursor() as cur:
        cur.execute("""
            SELECT MAX(s.score) FROM game_sessions s
            JOIN players p ON s.player_id = p.id
            WHERE p.username = %s
        """, (username,))
        result = cur.fetchone()
        if result and result[0] is not None:
            best_score = result[0]
    conn.close()
    return best_score

def get_leaderboard():
    """Достает Топ-10 игроков"""
    conn = connect()
    if not conn: return []
    lb = []
    with conn.cursor() as cur:
        cur.execute("""
            SELECT p.username, s.score, s.level_reached, s.played_at::date
            FROM game_sessions s
            JOIN players p ON s.player_id = p.id
            ORDER BY s.score DESC
            LIMIT 10
        """)
        lb = cur.fetchall()
    conn.close()
    return lb

# Запуск создания таблиц при прямом запуске файла
if __name__ == "__main__":
    init_db()