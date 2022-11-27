import bbtp

class BitboxingSender:
    """
    Wraps BBTP requests with Python method calls.
    """
    
    def __init__(self, sender_id, version):
        """
        Constructor.
        
        @param {str} sender_id Username
        @param {str} version   BBTP version
        """
        
        self._id = sender_id
        self._version = version
    
    def id(self):
        """
        Gets the username of the active user.

        @return {str}
        """
        
        return self._id
    
    def version(self):
        """
        Gets the BBTP version in use.

        @return {str} BBTP version
        """

        return self._version
    
    def handle_register(self, password):
        """
        Generates a BBTP REGISTER request.

        @param {str} password
        """

        return bbtp.format_request(self._id, self._version, "REGISTER", password)
    
    def handle_login(self, password):
        """
        Generates a BBTP LOGIN request.

        @param {str} password
        """

        return bbtp.format_request(self._id, self._version, "LOGIN", password)
    
    def handle_find(self, cache):
        """
        Generates a BBTP FIND request.

        @param {str} cache Puzzle ID
        """

        return bbtp.format_request(self._id, self._version, "FIND", cache)
    
    def handle_hint(self, cache):
        """
        Generates a BBTP HINT request.

        @param {str} cache Puzzle ID
        """

        return bbtp.format_request(self._id, self._version, "HINT", cache)
    
    def handle_solve(self, cache, guess):
        """
        Generates a BBTP SOLVE request.

        @param {str} cache Puzzle ID
        @param {str} guess Player's guess for the puzzle solution
        """

        return bbtp.format_request(self._id, self._version, "SOLVE", cache, guess)
    
    def handle_score(self, player):
        """
        Generates a BBTP SCORE request.

        @param {str} player Username
        """

        return bbtp.format_request(self._id, self._version, "SCORE", player)
    
    def handle_leaderboard(self, count=-1):
        """
        Generates a BBTP LEADERBOARD request.

        @param {int} count Max number of players to show (default lets the receiver decide)
        """

        return bbtp.format_request(self._id, self._version, "LEADERBOARD", str(count))
        
    def handle_cache_leaderboard(self, cache, count=-1):
        """
        Generates a BBTP CACHE_LEADERBOARD request.

        @param {str} cache Puzzle ID
        @param {int} count Max number of players to show (default lets the receiver decide)
        """

        return bbtp.format_request(self._id, self._version, "CACHE_LEADERBOARD", cache, str(count))