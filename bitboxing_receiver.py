from bbdb import CacheDatabase 
import bbtp
import json
import time

class BitboxingReceiver: 
    def __init__(self, version, path):
        self._version = version
        self._path = path
        
        try:
            with open(self._path, 'r') as f:
                print(f"Reading from '{path}'...")
                s = f.read()
                self._db = CacheDatabase.from_dict(json.loads(s))
                print("Success! Launching...")
        except Exception as ex:
            print(f"Error: '{repr(ex)}'!")
            print(f"Failed to read from '{path}'!")
            print("Launching without data...")
            self._db = CacheDatabase()
    
    def supports(self, version):
        return version == self._version
    
    def is_authenticated(self, sender):
        return True
    
    def handle_error(self, sender, error_code):
        print(f"Request from '{sender}' generated error '{error_code}'.")
        return bbtp.format_response(error_code)
    
    def handle_find(self, sender, cache):
        if not self._db.is_valid_cache(cache):
            return self.handle_error(bbtp.STATUS_NOT_FOUND)
        elif self._db[cache].stats(sender).found():
            return self.handle_error(bbtp.STATUS_OUT_OF_ORDER)
        else:
            self._db[cache].find(sender, time.time_ns())
            self.flush()
            return bbtp.format_response(bbtp.STATUS_OK, self._db[cache].puzzle().question())
    
    def handle_hint(self, sender, cache):
        if not self._db.is_valid_cache(cache):
            return self.handle_error(bbtp.STATUS_NOT_FOUND)
        elif not self._db[cache].stats(sender).found() or self._db[cache].stats(sender).solved():
            return self.handle_error(bbtp.STATUS_OUT_OF_ORDER)
        else:
            return bbtp.format_response(bbtp.STATUS_OK, self._db[cache].puzzle().hint())
    
    def handle_solve(self, sender, cache, guess):
        if not self._db.is_valid_cache(cache):
            return self.handle_error(bbtp.STATUS_NOT_FOUND)
        elif not self._db[cache].stats(sender).found() or self._db[cache].stats(sender).solved():
            return self.handle_error(bbtp.STATUS_OUT_OF_ORDER)
        else:
            is_correct = self._db[cache].try_to_solve(sender, guess, time.time_ns())
            self.flush()
            return bbtp.format_response(bbtp.STATUS_OK if is_correct else bbtp.STATUS_INCORRECT)
    
    def handle_stats(self, sender, player):
        return bbtp.format_response(bbtp.STATUS_OK, json.dumps(self._db.stats(player).to_dict(), indent=2))
    
    def handle_leaderboard_game(self, sender):
        return bbtp.format_response(bbtp.STATUS_OK)
    
    def handle_leaderboard_cache(self, sender, cache):
        return bbtp.format_response(bbtp.STATUS_OK)
    
    def flush(self):
        try:
            with open(self._path, 'w') as f:
                s = json.dumps(self._db.to_dict(), indent=2)
                f.write(s)
        except:
            print(f"Failed to write to '{self._path}'!")
            print("Exiting without saving data...")