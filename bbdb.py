from functools import cmp_to_key

class Puzzle:
    def __init__(self, question, answer, hint):
        self._question = question
        self._answer = answer
        self._hint = hint
    
    def question(self):
        return self._question
    
    def answer(self):
        return self._answer
    
    def hint(self):
        return self._hint
    
    def __str__(self):
        return str(self.to_dict())
    
    def __repr__(self):
        return str(self.to_dict())
    
    def to_dict(self):
        return {'question': self._question, 'answer': self._answer, 'hint': self._hint}
    
    @staticmethod
    def from_dict(d):
        return Puzzle(d['question'], d['answer'], d['hint'])

class FindStats:
    def __init__(self, time_found, time_solved = None, attempts = 0):
        self._time_found = time_found
        self._time_solved = time_solved
        self._attempts = attempts
    
    def found(self):
        return self._time_found != None
    
    def time_found(self):
        return self._time_found
    
    def solved(self):
        return self._time_solved != None
    
    def time_solved(self):
        return self._time_solved
    
    def how_long(self):
        return self._time_solved - self._time_found if self.solved() else None
    
    def attempts(self):
        return self._attempts
    
    def with_attempt(self):
        return FindStats(self._time_found, self._time_solved, self._attempts + 1)
    
    def with_solution(self, when):
        return FindStats(self._time_found, when, self._attempts + 1)
    
    def __eq__(self, other):
        return self.time_found() == other.time_found() \
            and self.time_solved() == other.time_solved() \
            and self.attempts() == other.attempts()
    
    def __ne__(self, other):
        return not self == other
    
    def __lt__(self, other):
        if self.found() and not other.found():
            return True
        elif self.found() and other.found():
            if self.solved() and not other.solved():
                return True
            elif self.solved() and other.solved():
                if self.how_long() < other.how_long():
                    return True
                elif self.how_long() == other.how_long():
                    if self.attempts() < other.attempts():
                        return True
                    else:
                        return self.attempts == other.attempts() \
                            and self.time_found() < other.time_found()
                else:
                    return False
            elif not self.solved() and not other.solved():
                if self.attempts() < other.attempts():
                    return True
                else:
                    return self.attempts() == other.attempts() \
                        and self.time_found() < other.time_found()
            else:
                return False
        elif not self.found() and not other.found():
            return self.time_found() < other.time_found()
        else:
            return False
        
    def __le__(self, other):
        return self == other or self < other
    
    def __gt__(self, other):
        return not self <= other
    
    def __ge__(self, other):
        return not self < other
    
    def __str__(self):
        return str(self.to_dict())
    
    def __repr__(self):
        return str(self.to_dict())
    
    def to_dict(self):
        return {'time_found': self._time_found, 'time_solved': self._time_solved, 'attempts': self._attempts}
    
    @staticmethod
    def from_dict(d):
        return FindStats(d['time_found'], d['time_solved'], d['attempts'])
    
    @staticmethod
    def empty():
        return FindStats(None)

class PlayerFindStats:
    def __init__(self, player, stats):
        self._player = player
        self._stats = stats
    
    def player(self):
        return self._player
    
    def stats(self):
        return self._stats
    
    def __str__(self):
        return str(self.to_dict())
    
    def __repr__(self):
        return str(self.to_dict())
    
    def to_dict(self):
        return {'player': self._player, 'stats': self._stats.to_dict()}
    
    @staticmethod
    def from_dict(d):
        return PlayerFindStats(d['player'], FindStats.from_dict(d['stats']))

class PlayerScore:
    def __init__(self, player, finds = 0, solves = 0):
        self._player = player
        self._finds = finds
        self._solves = solves
    
    def player(self):
        return self._player
    
    def finds(self):
        return self._finds
    
    def solves(self):
        return self._solves
    
    def __str__(self):
        return str(self.to_dict())
    
    def __repr__(self):
        return str(self.to_dict())
    
    def to_dict(self):
        return {'player': self._player, 'finds': self._finds, 'solves': self._solves}
    
    @staticmethod
    def from_dict(d):
        return PlayerScore(d['player'], d['finds'], d['solves'])

class CacheRecord:
    def __init__(self, puzzle, stats = None):
        self._puzzle = puzzle
        self._stats = stats if stats else {}
    
    def find(self, player, when):
        self._stats[player] = FindStats(when)
    
    def try_to_solve(self, player, guess, when):
        if guess.casefold() == self._puzzle.answer().casefold():
            self._stats[player] = self._stats[player].with_solution(when)
            return True
        else:
            self._stats[player] = self._stats[player].with_attempt()
            return False
    
    def puzzle(self):
        return self._puzzle
    
    def players(self):
        return self._stats.keys()
    
    def stats(self, player):
        if player in self._stats.keys():
            return self._stats[player]
        else:
            return FindStats.empty()
    
    def top(self, count):
        player_stats = [PlayerFindStats(k, v) for k, v in self._stats.items()]
        player_stats.sort(key=lambda x: x.stats())
        
        return player_stats[:count]
    
    def __str__(self):
        return str(self.to_dict())
    
    def __repr__(self):
        return str(self.to_dict())
    
    def to_dict(self):
        return {'puzzle': self._puzzle.to_dict(), 'stats': {k: v.to_dict() for k, v in self._stats.items()}}
    
    @staticmethod
    def from_dict(d):
        return CacheRecord(Puzzle.from_dict(d['puzzle']), {k: FindStats.from_dict(v) for k, v in d['stats'].items()})

class CacheDatabase:
    def __init__(self, d = None):
        self._dict = d if d else CacheDatabase._get_default_data()
    
    @staticmethod
    def _get_default_data():
        record1 = CacheRecord(Puzzle("Is 3 prime? (y/n)", "y", "Use math"))
        record2 = CacheRecord(Puzzle("Is 4 prime? (y/n)", "n", "Use math again"))
        
        return {'1': record1, '2': record2}
    
    def is_valid_cache(self, cache):
        return cache in self._dict.keys()
    
    def players(self):
        s = set()
        
        for v in self._dict.values():
            for p in v.players():
                s.add(p)
        
        return list(s)
    
    def history(self, player):
        d = {}
        
        for k, v in self._dict.items():
            s = v.stats(player)
            if s != FindStats.empty():
                d[k] = s
        
        return d
    
    def stats(self, player):
        h = self.history(player)
        finds = 0
        solves = 0
        
        for v in h.values():
            finds += 1
            if v.solved():
                solves += 1
        
        return PlayerScore(player, finds, solves)
    
    @staticmethod
    def _compare_stats(a, b):
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
    
    def top(self, count = 0):
        s = [self.stats(p) for p in self.players()]
        
        s.sort(key=cmp_to_key(CacheDatabase._compare_stats))
        
        return s if count <= 0 else s[:count]
    
    def __getitem__(self, key):
        return self._dict[key]
    
    def __str__(self):
        return str(self.to_dict())
    
    def __repr__(self):
        return str(self.to_dict())
    
    def to_dict(self):
        return {'dict': {k: v.to_dict() for k, v in self._dict.items()}}
    
    @staticmethod
    def from_dict(d):
        return CacheDatabase({k: CacheRecord.from_dict(v) for k, v in d['dict'].items()})