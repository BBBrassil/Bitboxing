import bitboxing_data as bbdata
from functools import cmp_to_key
import sqlite3 as sqlite

DEBUG = True

class BitboxingSql:
    """
    Executes SQLite commands for BBTP requests.
    """

    def __init__(self, path):
        """
        Constructor
        
        @param {str} path Database file path
        """

        self._path = path
    
    def connect(self):
        """
        Opens a SQLite connection.
        
        @return {Connection}
        """

        return sqlite.connect(self._path)
    
    def setup(self):
        """
        Sets up the database by creating tables if they do not exist.
        """

        connection = self.connect()
        cursor = connection.cursor()
        
        good = True
        for x in ["Users", "Puzzles", "Finds"]:
            cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name=?", (x,))
            found = cursor.fetchone()
            if found == None:
                good = False
                break
        
        if not good or DEBUG:
            self.create()
        
        connection.close()
        
    def create(self):
        """
        Creates the database tables. Drops tables if they already exist.
        
        Users
        - username (str) pk
        - password (str)

        Puzzles
        - id (str) pk
        - question (str)
        - answer (str)
        - hint (str)

        Finds
        - player (str) pk, fk Users(username)
        - cache (str) pk, fk Puzzles(id)
        - time_found (int)
        - time_solved (int)
        - attempts (int)
        """
        
        connection = self.connect()
        cursor = connection.cursor()
        
        cursor.execute("DROP TABLE IF EXISTS Users")
        cursor.execute("CREATE TABLE Users(username TEXT NOT NULL, password TEXT NOT NULL, PRIMARY KEY(username))")
        
        cursor.execute("DROP TABLE IF EXISTS Puzzles")
        cursor.execute("CREATE TABLE Puzzles(id TEXT NOT NULL, question TEXT NOT NULL, answer TEXT NOT NULL, hint TEXT NOT NULL, PRIMARY KEY(id))")
        
        for cache, question, answer, hint in BitboxingSql._get_puzzle_data():
            cursor.execute("INSERT INTO PUZZLES VALUES(?, ?, ?, ?)", (cache, question, answer, hint,))
        
        cursor.execute("DROP TABLE IF EXISTS Finds")
        cursor.execute("CREATE TABLE Finds(player TEXT NOT NULL, cache TEXT NOT NULL, time_found INTEGER, time_solved INTEGER, attempts INTEGER, PRIMARY KEY(player, cache), FOREIGN KEY(player) REFERENCES Users(username), FOREIGN KEY(cache) REFERENCES Puzzles(id))")
        
        connection.commit()
        connection.close()
    
    def register(self, username, password):
        """
        Registers a new user with the given username and password.

        @param {str} username
        @param {str} password
        """

        connection = self.connect()
        cursor = connection.cursor()
        
        cursor.execute("INSERT INTO Users(username, password) VALUES(?, ?)", (username, password))
        
        connection.commit()
        connection.close()
    
    def find(self, player, cache, when):
        """
        Records that a player has found a cache and sets the time found.

        @param {str} player Username
        @param {str} cache  Puzzle ID
        @param {int} when   Time in Unix nanoseconds
        """

        connection = self.connect()
        cursor = connection.cursor()
        
        cursor.execute(
            "INSERT INTO Finds(player, cache, time_found, time_solved, attempts) VALUES(?, ?, ?, ?, ?)",
            (player, cache, when, None, 0)
        )

        connection.commit()
        connection.close()
    
    def try_to_solve(self, player, cache, guess, when):
        """
        Allows a player to attempt to solve a puzzle. Increments the player's
        number of attempts. If the guess is correct, sets the time the player
        solved the puzzle.

        @param  {str}  player Name
        @param  {str}  guess  Not case sensitive
        @param  {int}  when   Time in Unix nanoseconds
        @return {bool}        True if guess was correct
        """
        
        puzzle = self.puzzle(cache)

        connection = self.connect()
        cursor = connection.cursor()
        
        cursor.execute(
            "UPDATE Finds SET attempts=attempts+1 WHERE player=? AND cache=?",
            (player, cache)
        )
        is_correct = puzzle.answer().casefold() == guess.casefold()

        if is_correct:
            cursor.execute(
                "UPDATE Finds SET time_solved=? WHERE player=? AND cache=?",
                (when, player, cache)
            )
        
        connection.commit()
        connection.close()
        
        return is_correct
    
    def is_valid_user(self, username):
        """
        Checks if a user is registered.

        @param  {str}  username
        @return {bool} True if user with username exists.
        """

        connection = self.connect()
        cursor = connection.cursor()
        
        cursor.execute("SELECT * FROM Users WHERE username=?", (username,))
        found = cursor.fetchone()

        connection.close()
        
        return found != None
    
    def is_valid_password(self, username, password):
        """
        Checks if a username's password is correct.

        @param  {str}  username
        @param  {str}  password
        @return {bool} True if user exists and password matches the database record.
        """

        connection = self.connect()
        cursor = connection.cursor()
        
        cursor.execute("SELECT password FROM Users WHERE username=?", (username,))
        found = cursor.fetchone()
        
        connection.close()
        
        return found and found[0] == password
    
    def is_valid_cache(self, cache):
        """
        Checks if a cache exists in the database.

        @param  {str} cache Name
        @return {bool}      True if cache exists
        """

        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM Puzzles WHERE id=?", (cache,))
        found = cursor.fetchone()

        connection.close()

        return found != None

    
    def players(self):
        """
        Gets a list of all registered playres.

        @return {list of str} Player names
        """

        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("SELECT username FROM Users")
        found = cursor.fetchall()

        connection.close()

        return [x[0] for x in found] if found else []
    
    def puzzle(self, cache):
        """
        Gets a puzzle with a given puzzle ID.

        @return {Puzzle} Puzzle with matching ID, None if not found
        """

        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("SELECT question, answer, hint FROM Puzzles WHERE id=?", (cache,))
        found = cursor.fetchone()

        connection.close()

        return bbdata.Puzzle(found[0], found[1], found[2]) if found else None
    
    def find_status(self, player, cache):
        """
        Gets statistics for whether a player has found and solved this cache.

        @param  {str} player Username
        @param  {str} cache  Puzzle ID
        @return {FindStatus} Player find stats for the cache, empty if player hasn't found it
        """
        
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("SELECT time_found, time_solved, attempts FROM Finds WHERE player=? AND cache=?", (player, cache,))
        found = cursor.fetchone()

        connection.close()

        return BitboxingSql._make_find_status(found) if found else bbdata.FindStatus.empty()

    def history(self, player):
        """
        Gets a player's statistics for each cache in the database.

        @return {dict of str: FindStatus}
        """
        
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("SELECT cache, time_found, time_solved, attempts FROM Finds WHERE player=?", (player,))
        
        found = cursor.fetchall()
        d = {}

        for f in found:
            d[f[0]] = BitboxingSql._make_find_status(f[1:])
        
        connection.close()
        
        return d

    def score(self, player):
        """
        Gets a player's score, consisting of the number of caches they've found
        and the number of puzzles they've solved.

        @return {PlayerScore}
        """

        h = self.history(player)
        finds = 0
        solves = 0
        
        for v in h.values():
            finds += 1
            if v.solved():
                solves += 1
        
        return bbdata.PlayerScore(player, finds, solves)

    def leaderboard(self, count = 0):
        """
        Gets the best-performing players for the game overall.

        @param  {int} count           Max number of players to fetch
        @return {list of PlayerScore} Up to count number of objects
        """

        leaderboard = [self.score(p) for p in self.players()]
        leaderboard.sort(key=cmp_to_key(BitboxingSql.compare_scores))
        
        return leaderboard if count <= 0 else leaderboard[:count]
    
    def cache_leaderboard(self, cache, count = 0):
        """
        Gets the best-performing players for a cache.

        @param  {str} cache    Puzzle ID
        @param  {int} count    Max number of players to fetch
        @return {list of dict} 'player': player, 'status': FindStatus
        """

        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("SELECT player, time_found, time_solved, attempts FROM Finds WHERE cache=?", (cache,))
        found = cursor.fetchall()

        connection.close()

        leaderboard = [{'player': f[0], 'status': BitboxingSql._make_find_status(f[1:])} for f in found]
        leaderboard.sort(key=lambda x: x['status'])
        
        return leaderboard if count <= 0 else leaderboard[:count]

    @staticmethod
    def compare_scores(a, b):
        """"
        Compares player scores, based on the following:
        1. If a has more solves, a > b.
        2. If a and be have the same number of solves, but a has more finds,
           a > b.
        3. If a and b have the same number of finds, a == b.
        4. Otherwise, a < b.

        @param  {PlayerScore} a 1st player score
        @param  {PlayerScore} b 2nd player score
        @return {int} -1 if a > b, 0 if a == b, 1 if a < b
        """

        if a.solves() > b.solves():
            return -1
        elif a.solves() == b.solves():
            if a.finds() > b.finds():
                return -1
            elif a.finds() == b.finds():
                return 0
            else:
                return 1
        else:
            return 1
    
    @staticmethod
    def _get_puzzle_data():
        """
        Generates default puzzle data.

        @return {list of tuples (str, str, str, str)} (id, question, answer, hint)
        """
        
        return [
            (
                "TDQXO",
                "Dlsjvtl av Ipaivepun! Aopz pz aol mpyza wbggsl!",
                "Welcome to Bitboxing! This is the first puzzle!",
                "Julius"
            ),
            (
                "MVMKB",
                "What is the end of everything?",
                "G",
                "What is the end of \"everything\"?"
            ),
            (
                "JLPOY",
                "What is the 8th Fibonacci number?",
                "13",
                "0, 1, 1, 2..."
            ),
            (
                "XRUZD",
                "682 1**\n"
                "614 1*\n"
                "206 2*\n"
                "738 0\n"
                "870 1*\n"
                "???",
                "042",
                "* Correct value\n** Correct value and in the right place"
            ),
            (
                "IBQVH",
                "Five people were eating apples.\n"
                "A finished before B, but behind C.\n"
                "D finished before E, but behind B.\n"
                "What was the finishing order?",
                "CABDE",
                "Enter the letters in order without space or punctuation. (e.g. ABCDE)"
            ),
        ]
    
    @staticmethod
    def _make_find_status(t):
        """
        Constructs a FindStatus object from a SQL query.
        
        @param  {tuple (str, str, str)} (time_found, time_solved, attempts)
        @return {FindStatus}
        """
        return bbdata.FindStatus(int(t[0]) if t[0] else None, int(t[1]) if t[1] else None, int(t[2]) if t[2] else 0)