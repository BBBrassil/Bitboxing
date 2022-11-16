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
            print("Launching with default data...")
            self._db = CacheDatabase()
            self.flush()
    
    def supports(self, version):
        return version == self._version
    
    def is_authenticated(self, sender):
        return True
    
    def handle_error(self, sender, error_code, msg=""):
        print(f"Request from '{sender}' generated error '{error_code}'.")
        return bbtp.format_response(error_code, msg)
    
    def handle_find(self, sender, cache):
        if not self._db.is_valid_cache(cache):
            return self.handle_error(sender, bbtp.STATUS_NOT_FOUND)
        elif self._db[cache].stats(sender).found():
            msg = self._db[cache].puzzle().question()
            return bbtp.format_response(bbtp.STATUS_WITHOUT_CHANGE, msg)
        else:
            self._db[cache].find(sender, time.time_ns())
            self.flush()
            msg = self._db[cache].puzzle().question()
            return bbtp.format_response(bbtp.STATUS_OK, msg)
    
    def handle_hint(self, sender, cache):
        if not self._db.is_valid_cache(cache):
            return self.handle_error(sender, bbtp.STATUS_NOT_FOUND)
        elif not self._db[cache].stats(sender).found() or self._db[cache].stats(sender).solved():
            return self.handle_error(sender, bbtp.STATUS_OUT_OF_ORDER)
        else:
            msg = self._db[cache].puzzle().hint()
            return bbtp.format_response(bbtp.STATUS_OK, msg)
    
    def handle_solve(self, sender, cache, guess):
        if not self._db.is_valid_cache(cache):
            return self.handle_error(sender, bbtp.STATUS_NOT_FOUND)
        elif not self._db[cache].stats(sender).found() or self._db[cache].stats(sender).solved():
            return self.handle_error(sender, bbtp.STATUS_OUT_OF_ORDER)
        else:
            is_correct = self._db[cache].try_to_solve(sender, guess, time.time_ns())
            self.flush()
            return bbtp.format_response(bbtp.STATUS_OK if is_correct else bbtp.STATUS_INCORRECT)
    
    def handle_stats(self, sender, player):
        data = self._db.stats(player).to_dict()
        msg = BitboxingReceiver._to_json(data)
        return bbtp.format_response(bbtp.STATUS_OK, msg)
    
    def handle_leaderboard(self, sender, count):
        try:
            n = 10 if int(count) < 0 else int(count)
            data = [x.to_dict() for x in self._db.top(n)]
            msg = BitboxingReceiver._to_json(data)
            return bbtp.format_response(bbtp.STATUS_OK, msg)
        except Exception as ex:
            return self.handle_error(sender, bbtp.STATUS_EXCEPTION, repr(ex))
        
    
    def handle_cache_leaderboard(self, sender, cache, count):
        if not self._db.is_valid_cache(cache):
            return self.handle_error(sender, bbtp.STATUS_NOT_FOUND)
        else:
            try:
                n = 10 if int(count) < 0 else int(count)
                data = [x.to_dict() for x in self._db[cache].top(n)]
                msg = BitboxingReceiver._to_json(data)
                return bbtp.format_response(bbtp.STATUS_OK, msg)
            except Exception as ex:
                return self.handle_error(sender, bbtp.STATUS_EXCEPTION, repr(ex))
    
    def flush(self):
        try:
            with open(self._path, 'w') as f:
                data = self._db.to_dict()
                s = BitboxingReceiver._to_json(data)
                f.write(s)
        except:
            print(f"Failed to write to '{self._path}'!")
            print("Exiting without saving data...")
    
    @staticmethod
    def _to_json(data):
        return json.dumps(data, indent=2)
    