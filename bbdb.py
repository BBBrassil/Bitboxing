from functools import cmp_to_key

class Puzzle:
    """
    Stores data relating to an individual puzzle.
    """

    def __init__(self, question, answer, hint):
        """
        Constructor.

        @param {str} question
        @param {str} answer
        @param {str} hint
        """

        self._question = question
        self._answer = answer
        self._hint = hint
    
    def question(self):
        """
        Gets the question prompt associated with this puzzle.

        @return {str} question
        """

        return self._question
    
    def answer(self):
        """
        Gets the answer associated with this puzzle.

        @return {str} answer
        """

        return self._answer

    def hint(self):
        """
        Gets the hint associated with this puzzle.
        
        @return {str} hint
        """

        return self._hint

    def __str__(self):
        """
        Gets a human-readable string.

        @return {str}
        """

        return str(self.to_dict())
    
    def __repr__(self):
        """
        Gets a printable representation.

        @return {str}
        """

        return str(self.to_dict())
    

    def to_dict(self):
        """
        Converts to a Python dictionary.

        @return {dict}
        """

        return {'question': self._question, 'answer': self._answer, 'hint': self._hint}

    @staticmethod
    def from_dict(d):
        """
        Converts from a Python dictionary.

        @param  {dict}   d Dictionary to read
        @return {Puzzle}
        """

        return Puzzle(d['question'], d['answer'], d['hint'])

class FindStats:
    """
    Stores data relating to when a cache was found and solved and how many attempts were used.
    """

    def __init__(self, time_found, time_solved = None, attempts = 0):
        """
        Constructor.

        @param {int} time_found  Time in Unix nanoseconds
        @param {int} time_solved Time in Unix nanoseconds
        @param {int} attempts    How many guesses made
        """

        self._time_found = time_found
        self._time_solved = time_solved
        self._attempts = attempts
    
    def found(self):
        """
        Gets whether the cache has been found.

        @return {bool} True if found
        """
        
        return self._time_found != None
    
    def time_found(self):
        """
        Gets when the cache was found.

        @return {int} Time in Unix nanoseconds or None if not found
        """

        return self._time_found

    def solved(self):
        """
        Gets whether the cache puzzle was solved.
        
        @return {bool} True if solved
        """

        return self._time_solved != None
    
    def time_solved(self):
        """
        Gets when the cache was solved.

        @return {int} Time in Unix nanoseconds or None if not found
        """

        return self._time_solved
    
    def how_long(self):
        """
        Gets the amount of time it took to solve the cache puzzle.

        @return {int} Time in Unix nanoseconds or None if not solved
        """

        return self._time_solved - self._time_found if self.solved() else None
    
    def attempts(self):
        """
        Gets the number of times someone has attempted to solve the puzzle.

        @return {int} How many guesses made
        """

        return self._attempts
    
    def with_attempt(self):
        """
        Clones the object, adding one attempt.

        @return {FindStats} Clone with attempts increased by 1
        """

        return FindStats(self._time_found, self._time_solved, self._attempts + 1)
    
    def with_solution(self, when):
        """
        Clones the object, adjusting for specified solution time.

        @param  {int}       when  Time in Unix nanoseconds
        @return {FindStats}       Clone with time solved set to when
        """

        return FindStats(self._time_found, when, self._attempts + 1)
    
    def __eq__(self, other):
        """
        == operator

        @param  {FindStats} other
        @return {bool}      True if this object's time found, time solved, and attempts match other object's
        """

        return self.time_found() == other.time_found() \
            and self.time_solved() == other.time_solved() \
            and self.attempts() == other.attempts()
    
    def __ne__(self, other):
        """
        != operator
        Equivalent to not __eq__.

        @param  {FindStats} other
        @return {bool}      True if this object != other object
        """

        return not self == other
    
    def __lt__(self, other):
        """
        < operator
        Checks if this object's stats are better than another object's based on the following:
        1. If one has been found and another hasn't, the one that has been found wins.
        2. If one has been solved and another hasn't, the one that has been solved wins.
        4. If both have been found but not solved (tie for #1), prioritize attempts -> time found.
        3. If both have been solved (tie for #2), prioritize how_long -> attempts -> time_found.

        @param  {FindStats} other
        @return {bool}      True if this object's stats beat other object's
        """

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
            return True
        else:
            return False
    
    def __le__(self, other):
        """
        <= operator
        Equivalent to __eq__ or __lt__

        @param  {FindStats} other
        @return {bool}      True if this object <= other object
        """

        return self == other or self < other
    
    def __gt__(self, other):
        """
        > operator
        Equivalent to not __le__

        @param  {FindStats} other
        @return {bool}      True if this object <= other object
        """
        
        return not self <= other
    
    def __ge__(self, other):
        """
        >= operator
        Equivalent to not __lt__

        @param  {FindStats} other
        @return {bool}      True if this object <= other object
        """
        
        return not self < other
    
    def __str__(self):
        """
        Gets a human-readable string.

        @return {str}
        """

        return str(self.to_dict())
    
    def __repr__(self):
        """
        Gets a printable representation.

        @return {str}
        """

        return str(self.to_dict())
    
    def to_dict(self):
        """
        Converts to a Python dictionary.

        @return {dict}
        """

        return {'time_found': self._time_found, 'time_solved': self._time_solved, 'attempts': self._attempts}
    
    @staticmethod
    def from_dict(d):
        """
        Converts from a Python dictionary.

        @param  {dict}      d Dictionary to read
        @return {FindStats}
        """

        return FindStats(d['time_found'], d['time_solved'], d['attempts'])
    
    @staticmethod
    def empty():
        """
        Gets a default empty object that has not been found or solved and has no attempts.

        @return {FindStats} with time_found = None, time_solved = None, attempts = 0
        """

        return FindStats(None)

class PlayerFindStats:
    """
    Associates a player name with a FindStats object.
    """

    def __init__(self, player, stats):
        """
        Constructor.

        @param {str}       Player name
        @param {FindStats} Cache statistics
        """

        self._player = player
        self._stats = stats
    
    def player(self):
        """
        Gets the player assoicated with these stats.

        @return {str} Player name
        """

        return self._player
    
    def stats(self):
        """
        Gets the actual statistics.

        @return {FindStats}
        """

        return self._stats
    
    def __str__(self):
        """
        Gets a human-readable string.

        @return {str}
        """

        return str(self.to_dict())
    
    def __repr__(self):
        """
        Gets a printable representation.

        @return {str}
        """

        return str(self.to_dict())
    
    def to_dict(self):
        """
        Converts to a Python dictionary.

        @return {dict}
        """

        return {'player': self._player, 'stats': self._stats.to_dict()}
    
    @staticmethod
    def from_dict(d):
        """
        Converts from a Python dictionary.

        @param  {dict}            d Dictionary to read
        @return {PlayerFindStats}
        """

        return PlayerFindStats(d['player'], FindStats.from_dict(d['stats']))

class PlayerScore:
    """
    Holds data relating to how many puzzle caches a player has found and solved.
    """

    def __init__(self, player, finds = 0, solves = 0):
        """
        Constructor.

        @param {string} player Name
        @param {int}    finds  Number of caches found
        @param {int}    solves Number of puzzles solved
        """

        self._player = player
        self._finds = finds
        self._solves = solves
    
    def player(self):
        """"
        Gets the player's name.
        @return {str} Name
        """
        
        return self._player
    
    def finds(self):
        """
        Gets the number of caches the player has found.

        @return {int}
        """
        
        return self._finds
    
    def solves(self):
        """
        Gets the number of puzzles the player has solved.

        @return {int}
        """
        
        return self._solves
    
    def __str__(self):
        """
        Gets a human-readable string.

        @return {str}
        """

        return str(self.to_dict())
    
    def __repr__(self):
        """
        Gets a printable representation.

        @return {str}
        """

        return str(self.to_dict())
    
    def to_dict(self):
        """
        Converts to a Python dictionary.

        @return {dict}
        """

        return {'player': self._player, 'finds': self._finds, 'solves': self._solves}
    
    @staticmethod
    def from_dict(d):
        """
        Converts from a Python dictionary.

        @param  {dict}        d Dictionary to read
        @return {PlayerScore}
        """

        return PlayerScore(d['player'], d['finds'], d['solves'])

class CacheRecord:
    """"
    Stores data relating to a puzzle cache, including the question and ansewr and which players have found and solved it.
    """

    def __init__(self, puzzle, stats = None):        
        """
        Constructor.

        @param {Puzzle}            puzzle Puzzle associated with this cache
        @param {list of FindStats} stats  Find statistics (default empty)
        """

        self._puzzle = puzzle
        self._stats = stats if stats else {}
    
    def find(self, player, when):
        """
        Sets the time a player has found the cache.

        @param {str} player Name
        @param {int} when   Time in Unix nanosecons
        """

        self._stats[player] = FindStats(when)
    
    def try_to_solve(self, player, guess, when):
        """
        Allows a player to attempt to solve a puzzle. Increments the player's
        number of attempts. If the guess is correct, sets the time the player
        solved the puzzle.

        @param {str}   player Name
        @param {str}   guess  Not case sensitive
        @param {int}   when   Time in Unix nanoseconds
        @return {bool}        True if guess was correct
        """

        if guess.casefold() == self._puzzle.answer().casefold():
            self._stats[player] = self._stats[player].with_solution(when)
            return True
        else:
            self._stats[player] = self._stats[player].with_attempt()
            return False
    
    def puzzle(self):
        """
        Gets the puzzle associated with this cache.

        @return {Puzzle}
        """

        return self._puzzle
    
    def players(self):
        """
        Gets a list of all players who have found this cache.

        @return {list of str} Player names
        """

        return self._stats.keys()
    
    def stats(self, player):
        """
        Gets statistics for whether a player has found and solved this cache.

        @return {FindStats} Player stats or empty if player hasn't found this cache
        """

        if player in self._stats.keys():
            return self._stats[player]
        else:
            return FindStats.empty()
    
    def top(self, count):
        """
        Gets the best-performing players for this cache.

        @param  {int} count               Max number of players to retrieve
        @return {list of PlayerFindStats} Up to count number of objects
        """

        player_stats = [PlayerFindStats(k, v) for k, v in self._stats.items()]
        player_stats.sort(key=lambda x: x.stats())
        
        return player_stats[:count]
    
    def __str__(self):
        """
        Gets a human-readable string.

        @return {str}
        """

        return str(self.to_dict())
    
    def __repr__(self):
        """
        Gets a printable representation.

        @return {str}
        """

        return str(self.to_dict())
    
    def to_dict(self):
        """
        Converts to a Python dictionary.

        @return {dict}
        """

        return {'puzzle': self._puzzle.to_dict(), 'stats': {k: v.to_dict() for k, v in self._stats.items()}}
    
    @staticmethod
    def from_dict(d):
        """
        Converts from a Python dictionary.

        @param  {dict}        d Dictionary to read
        @return {CacheRecord}
        """

        return CacheRecord(Puzzle.from_dict(d['puzzle']), {k: FindStats.from_dict(v) for k, v in d['stats'].items()})

class CacheDatabase:
    """
    Stores data for puzzle for every cache and statistics about whether players
    have found and solved them.
    """

    def __init__(self, d = None):
        """
        Constructor.
        Generates data with just puzzle info and no player info if no data is
        passed.

        @param {dict} d Python dictionary containing cache data (optional)
        """

        self._dict = d if d else CacheDatabase._get_default_data()
    
    @staticmethod
    def _get_default_data():
        """
        Generates default cache data.

        @return {dict}
        """
        
        return {
            'TDQXO' : CacheRecord(Puzzle(
                "Dlsjvtl av Ipaivepun! Aopz pz aol mpyza wbggsl!",
                "Welcome to Bitboxing! This is the first puzzle!",
                "Julius"
            )),
            'MVMKB' : CacheRecord(Puzzle(
                "What is the end of everything?",
                "G",
                "What is the end of \"everything\"?"
            )),
            'JLPOY' : CacheRecord(Puzzle(
                "What is the 8th Fibonacci number?",
                "13",
                "0, 1, 1, 2..."
            )),
            'XRUZD' : CacheRecord(Puzzle(
                "682 1**\n"
                "614 1*\n"
                "206 2*\n"
                "738 0\n"
                "870 1*\n"
                "???",
                "042",
                "* Correct value\n** Correct value and in the right place"
            )),
            'IBQVH' : CacheRecord(Puzzle(
                "Five people were eating apples.\n"
                "A finished before B, but behind C.\n"
                "D finished before E, but behind B.\n"
                "What was the finishing order?",
                "CABDE",
                "Enter the letters in order without space or punctuation. (e.g. ABCDE)"
            )),
        }

    def is_valid_cache(self, cache):
        """
        Checks if a cache exists in the database.

        @param {str} cache Name
        @return {bool} True if cache exists
        """
        
        return cache in self._dict.keys()
    
    def players(self):
        """
        Gets a list of all players who have found any caches.

        @return {list of str} Player names
        """

        s = set()
        
        for v in self._dict.values():
            for p in v.players():
                s.add(p)
        
        return list(s)
    
    def history(self, player):
        """
        Gets a player's statistics for each cache in the database.

        @return {dict of str: FindStats}
        """
        d = {}
        
        for k, v in self._dict.items():
            s = v.stats(player)
            if s != FindStats.empty():
                d[k] = s
        
        return d
    
    def stats(self, player):
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
        
        return PlayerScore(player, finds, solves)
    
    @staticmethod
    def _compare_stats(a, b):
        """"
        Compares player stats, based on the following:
        1. If a has more solves, a > b.
        2. If a and be have the same number of solves, but a has more finds,
           a > b.
        3. If a and b have the same number of finds, a == b.
        4. Otherwise, a < b.

        @param {str} a 1st player name
        @param {str} b 2nd player name
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
    
    def top(self, count = 0):
        """
        Gets the best-performing players for the game overall.

        @param  {int} count           Max number of players to retrieve
        @return {list of PlayerScore} Up to count number of objects
        """

        s = [self.stats(p) for p in self.players()]
        
        s.sort(key=cmp_to_key(CacheDatabase._compare_stats))
        
        return s if count <= 0 else s[:count]
    
    def __getitem__(self, key):
        """
        [] operator
        
        @param {str} key
        @return {CacheRecord}
        """

        return self._dict[key]
    
    def __str__(self):
        """
        Gets a human-readable string.

        @return {str}
        """

        return str(self.to_dict())
    
    def __repr__(self):
        """
        Gets a printable representation.

        @return {str}
        """

        return str(self.to_dict())
    
    def to_dict(self):
        """
        Converts to a Python dictionary.

        @return {dict}
        """

        return {'dict': {k: v.to_dict() for k, v in self._dict.items()}}
    
    @staticmethod
    def from_dict(d):
        """
        Converts from a Python dictionary.

        @param  {dict}        d Dictionary to read
        @return {CacheDatabase}
        """

        return CacheDatabase({k: CacheRecord.from_dict(v) for k, v in d['dict'].items()})