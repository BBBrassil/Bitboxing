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

class FindStatus:
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

        return FindStatus(d['time_found'], d['time_solved'], d['attempts'])
    
    @staticmethod
    def empty():
        """
        Gets a default empty object that has not been found or solved and has no attempts.

        @return {FindStats} with time_found = None, time_solved = None, attempts = 0
        """

        return FindStatus(None)

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