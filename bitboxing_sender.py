import bbtp

class BitboxingSender:
    def __init__(self, sender_id, version):
        self._id = sender_id
        self._version = version
    
    def handle_find(self, cache):
        return bbtp.format_request(self._id, self._version, "FIND", cache)
    
    def handle_hint(self, cache):
        return bbtp.format_request(self._id, self._version, "HINT", cache)
    
    def handle_solve(self, cache, guess):
        return bbtp.format_request(self._id, self._version, "SOLVE", cache, guess)
    
    def handle_stats(self, player):
        return bbtp.format_request(self._id, self._version, "STATS", player)
    
    def handle_leaderboard_game(self):
        return bbtp.format_request(self._id, self._version, "LEADERBOARD")
        
    def handle_leaderboard_cache(self, cache):
        return bbtp.format_request(self._id, self._version, "LEADERBOARD", cache)