import bbtp
from bitboxing_sql import BitboxingSql 
import json
import time

class BitboxingReceiver:
    """
    Responds to BBTP requests using SQLite database.
    """
    
    def __init__(self, version, path):
        """
        Constructor.
        
        @param {str} version BBTP version
        @param {str} path    File path of SQLite database
        """

        self._version = version
        self._path = path
        
        sql = BitboxingSql(path)
        sql.setup()
        self._sql = sql
    
    def supports(self, version):
        """
        Checks if the receiver supports a given BBTP version.
        
        @param {str} version BBTP version
        """
        return version == self._version
    
    def is_authenticated(self, sender):
        """
        Checks if a user is registered.

        @param {str} sender Username
        @return {bool} True if user with username matching sender exists.
        """

        return self._sql.is_valid_user(sender)
    
    def handle_error(self, sender, error_code, msg=""):
        """
        Logs an error.

        @param  {str} sender     Username
        @param  {str} error_code Error status code
        @param  {str} msg        Error message
        @return {str}            BBTP response with status code status_code
        """

        print(f"Request from '{sender}' generated error '{error_code}'.")
        if msg != "":
            print(msg)
        return bbtp.format_response(error_code, "")
    
    def handle_register(self, sender, password):
        """
        Registers a new user if no user with that username already exists.

        @param  {str} sender   Username
        @param  {str} password
        @return {str}          BBTP response with
                               STATUS_OUT_OF_ORDER if user already exists,
                               STATUS_OK if user was created
        """

        if self._sql.is_valid_user(sender):
            print(f"User '{sender} already exists!")
            return self.handle_error(sender, bbtp.STATUS_OUT_OF_ORDER)
        else:
            self._sql.register(sender, password)
            print(f"Created user '{sender}' with password '{password}'.")
            return bbtp.format_response(bbtp.STATUS_OK)
    
    def handle_login(self, sender, password):
        """
        Validates user login.

        @param  {str} sender   Authenticated username
        @param  {str} password Password attempt
        @return {str}          BBTP response with
                               STATUS_INCORRECT if password is wrong,
                               STATUS_OK if login successful
        """
        
        if not self._sql.is_valid_password(sender, password):
            print(f"User '{sender} attempted an invalid password!")
            return self.handle_error(sender, bbtp.STATUS_INCORRECT)
        else:
            return bbtp.format_response(bbtp.STATUS_OK)
    
    def handle_find(self, sender, cache):
        """
        Records that a player has found a cache.

        @param  {str} sender Authenticated username
        @param  {str} cache  Puzzle ID
        @return {str}        BBTP response with
                             STATUS_NOT_FOUND if cache is invalid,
                             STATUS_WITHOUT_CHANGE if sender already found cache,
                             STATUS_OK if cache found successfully
        """
        
        if not self._sql.is_valid_cache(cache):
            return self.handle_error(sender, bbtp.STATUS_NOT_FOUND)
        elif self._sql.find_status(sender, cache).found():
            msg = self._sql.puzzle(cache).question()
            return bbtp.format_response(bbtp.STATUS_WITHOUT_CHANGE, msg)
        else:
            self._sql.find(sender, cache, time.time_ns())
            msg = self._sql.puzzle(cache).question()
            return bbtp.format_response(bbtp.STATUS_OK, msg)
    
    def handle_hint(self, sender, cache):
        """
        Fetches a hint for a cache.

        @param  {str} sender Authenticated username
        @param  {str} cache  Puzzle ID
        @return {str}        BBTP response with
                             STATUS_NOT_FOUND if cache is invalid,
                             STATUS_OUT_OF_ORDER if sender hasn't found cache,
                             STATUS_OK if hint was fetched successfully,
                             body containing puzzle question as simple string
        """
        
        if not self._sql.is_valid_cache(cache):
            return self.handle_error(sender, bbtp.STATUS_NOT_FOUND)
        elif not self._sql.find_status(sender, cache).found() or self._sql.find_status(sender, cache).solved():
            return self.handle_error(sender, bbtp.STATUS_OUT_OF_ORDER)
        else:
            msg = self._sql.puzzle(cache).hint()
            return bbtp.format_response(bbtp.STATUS_OK, msg)
    
    def handle_solve(self, sender, cache, guess):
        """
        Records that a player has found a cache.

        @param  {str} sender Authenticated username
        @param  {str} cache  Puzzle ID
        @param  {str} guess  Player's guess for the puzzle solution
        @return {str}        BBTP response with status code
                             STATUS_NOT_FOUND if cache is invalid,
                             STATUS_WITHOUT_CHANGE if sender hasn't found cache or already solved,
                             STATUS_OK if solved
        """
        
        if not self._sql.is_valid_cache(cache):
            return self.handle_error(sender, bbtp.STATUS_NOT_FOUND)
        elif not self._sql.find_status(sender, cache).found() or self._sql.find_status(sender, cache).solved():
            return self.handle_error(sender, bbtp.STATUS_OUT_OF_ORDER)
        else:
            is_correct = self._sql.try_to_solve(sender, cache, guess, time.time_ns())
            return bbtp.format_response(bbtp.STATUS_OK if is_correct else bbtp.STATUS_INCORRECT)
    
    def handle_score(self, sender, player):
        """
        Fetches a player's score.

        @param  {str} sender Authenticated username
        @param  {str} player Username
        @return {str}        BBTP response with status code
                             STATUS_NOT_FOUND if cache is invalid,
                             STATUS_WITHOUT_CHANGE if sender hasn't found cache or already solved,
                             STATUS_OK if solved,
                             body containing PlayerScore as JSON-formatted string
        """
        
        data = self._sql.score(player).to_dict()
        msg = BitboxingReceiver._to_json(data)
        return bbtp.format_response(bbtp.STATUS_OK, msg)
    
    def handle_leaderboard(self, sender, count):
        """
        Fetches leaderboard containing the top-scoring players for the game overall.

        @param  {str} sender Authenticated username
        @param  {str} count  Max number of players to fetch (default 10 if count < 0)
        @return {str}        BBTP response with status code STATUS OK,
                             body containing list of PlayerScore objects as JSON-formatted string
        """
        
        n = 10 if int(count) < 0 else int(count)
        data = [x.to_dict() for x in self._sql.leaderboard(n)]
        msg = BitboxingReceiver._to_json(data)
        return bbtp.format_response(bbtp.STATUS_OK, msg)
    
    def handle_cache_leaderboard(self, sender, cache, count):
        """
        Fetches the leaderboard containing the top-scoring playres for a given cache.

        @param  {str} sender Authenticated username
        @param  {str} cache  Puzzle ID
        @param  {str} count  Max number of players to fetch (default 10 if count < 0)
        @return {str}        BBTP response with status code STATUS OK,
                             body containing list of player names as JSON-formatted string
        """
        
        if not self._sql.is_valid_cache(cache):
            return self.handle_error(sender, bbtp.STATUS_NOT_FOUND)
        else:
            n = 10 if int(count) < 0 else int(count)
            data = [x['player'] for x in self._sql.cache_leaderboard(cache, n)]
            msg = BitboxingReceiver._to_json(data)
            return bbtp.format_response(bbtp.STATUS_OK, msg)
    
    @staticmethod
    def _to_json(data):
        """
        Converts data to a JSON-formatted string.

        @param {data} JSON-serializable data
        @return {str} JSON-formatted string
        """
        
        return json.dumps(data, indent=2)
    