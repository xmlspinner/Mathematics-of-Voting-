import math
import itertools
import random
import copy


def dict_maker(list):
    """ a helper function that takes in a list and a function(can be numerical) and returns a dictionary with the unique
        elements of the list as keys and the function in the list as values.
        Used frequently in the classes below to convert a list of ballots into a schedule dictionary.
    """ 
    dict = {}
    for item in list:
        if item not in dict:
            dict[item] = 1
        else:
            dict[item] += 1
    return dict 

def random_Ballots(n,m):
    """ n candidates, m ballots """
    ballots = []
    for i in range(m):
        Letters = [chr(x) for x in range(65,65+n)]
        ballot = []
        for j in range(n): 
            candidate = random.choice(Letters)
            ballot.append(candidate)
            Letters.remove(candidate)
        ballots.append(tuple(ballot))
    return ballots 


class Schedule():
    """ Schedule is initialized by a dictionary with ballots as keys and the number of such ballots
        as values. Ballots must be represented by a tuple to be hashable.
    """

    def __init__(self, schedule):
        """  """
        self.schedule = schedule

    def candidates(self):
        """ returns the list/set of candidates that appear on the ballots """
        names = []
        for ballot in self.schedule:
            for name in ballot:
                if name not in names:
                    names.append(name)
        return names
    
    def add_ballot(self, newballot):
        """ adds new ballot to the schedule by updating ballots and schedule """
        if newballot in self.schedule:
            self.schedule[newballot] += 1
        else:
            self.schedule[newballot] = 1
    
    def delete_candidate(self, candidate):
        """ removes a candidate from every ballot, assumeing that
            the candidate appears in one of the ballots. Used for runoff systems.
        """
        new_schedule = {}
        for ballot in self.schedule:
            if candidate in ballot:
                old_ballot = list(ballot)       # must convert to list to make changes to ballot
                old_ballot.remove(candidate)
                new_ballot = tuple(old_ballot)  
                # taking possible repeated ballots after removal into account
                if new_ballot in new_schedule:
                    new_schedule[new_ballot] += self.schedule[ballot]
                else:
                    new_schedule[new_ballot] = self.schedule[ballot]
        self.schedule = new_schedule     #updates schedule



class Election():
    
    def __init__(self, ballots):
        """ initialized by a list or dictionary of ballots """
        if type(ballots) == list:
            self.ballots = ballots  #represent self.schedule as a class
            self.schedule = dict_maker(ballots)
            S = Schedule(self.schedule)
            self.candidates = S.candidates()
        if type(ballots) == dict:
            self.schedule = ballots
            S = Schedule(self.schedule)
            self.candidates = S.candidates()
    
    def get_scoreboard(self):
        """ returns a sorted list of tuples (score, list of candidates with that score) """
        scoreboard = {}
        scores = self.scores
        for candidate in scores:
            a = scores[candidate]
            if a not in scoreboard:
                scoreboard[a] = [candidate]
            else:
                scoreboard[a] += [candidate]
        scoreboard_list = sorted([(a, scoreboard[a]) for a in scoreboard])
        return scoreboard_list    # ordered from lowest ranked to highest
    
    def results(self):
        """ print the results of the election """
        place_counter = 1
        for item in reversed(self.get_scoreboard()):
            print('%s place is %s' % (place_counter, item[1]))
            place_counter += len(item[1])
    
    def headTohead(self, C1, C2):
        """ returns the winner of a headTohead race between two candidates """
        C1score = 0
        C2score = 0

        for order in self.schedule:
            C1i = order.index(C1)
            C2i = order.index(C2)
            if C1i > C2i:
                C2score += self.schedule[order]
            elif C1i < C2i:
                C1score += self.schedule[order]

        if C1score> C2score:
            return C1
        else:
            return C2
    
    def isMajority(self):
        """ returns True if there exists a majority winner """
        nVoters = sum(self.schedule.values())
        D = Plurality(self.schedule)
        maxVotes = max(D.scores.values())
        if 2*maxVotes > nVoters:
            return True
        else:
            return False
    
    def isCondorcet(self):
        """ returns True if there exists a Condorcet winner """
        P_election = Pairwise_comparison(self.schedule)
        n = len(self.candidates)
        if n-1 in P_election.scores.values():
            return True
        return False



    
class Plurality(Election):

    def __init__(self, ballots):
        Election.__init__(self, ballots)

        self.scores = {}    
        scores = self.scores
        for candidate in self.candidates:
            scores[candidate] = 0
        for ballot in self.schedule:
            scores[ballot[0]] += self.schedule[ballot]

class Bordacount(Election):

    def __init__(self, ballots):
        Election.__init__(self, ballots)

        self.scores = {}
        scores = self.scores
        n = len(self.candidates)
        for candidate in self.candidates:
            scores[candidate] = 0
        for ballot in self.schedule:
            for i, candidate in enumerate(ballot):
                scores[candidate] += (n-1-i)*self.schedule[ballot] 

class Positional(Election):

    def __init__(self, ballots, weights):
        Election.__init__(self, ballots)
        self.weights = weights

        self.scores = {}
        scores = self.scores
        n = len(self.candidates)
        for candidate in self.candidates:
            scores[candidate] = 0
        for ballot in self.schedule:
            for i, candidate in enumerate(ballot):
                scores[candidate] += self.weights[i]*self.schedule[ballot] 

class Instant_Runoff(Election):
    """ if ties occur in a runoff round, all tied candidates are eliminated """
    def __init__(self, ballots):
        Election.__init__(self, ballots)
    
        self.scores = {}
        runoff_schedule = Schedule(self.schedule)
        scorer = 0

        while len(runoff_schedule.candidates()) != 0:
            plurality_losers = Plurality(runoff_schedule.schedule).get_scoreboard()[0][1]
            for loser in plurality_losers:
                self.scores[loser] = scorer
                runoff_schedule.delete_candidate(loser)
            scorer += 1

class Pairwise_comparison(Election):
        """ allows ties(0.5 points for each candidate)  """

        def __init__(self, ballots):
            Election.__init__(self, ballots)

            S = Schedule(self.schedule)
            C = self.candidates
            n = len(C)

            self.scores = {}
            for candidate in C:
                self.scores[candidate] = 0
            for index1 in range(n):
                for index2 in range(index1+1, n):
                    hthwinner = self.headTohead(C[index1], C[index2])
                    if hthwinner == C[index1]:
                        self.scores[C[index1]] += 1
                    elif hthwinner == C[index2]:
                        self.scores[C[index2]] += 1
                    else:
                        self.scores[C[index1]] += 0.5
                        self.scores[C[index2]] += 0.5



# import time

# t1 = time.clock()

# test_ballots = random_Ballots(10,1000)
# test = Instant_Runoff(test_ballots)    
# print(test.results())
# print(test.isCondorcet())
# t2 = time.clock()
# print(t2-t1)

# import Math_of_Voting_Simulations 
# from Math_of_Voting_Simulations import Election


# test_Election = Election(15)
# test_Election.schedule = [list(x) for x in test_ballots]
# t3 = time.clock()
# t = test_Election.Instant_Runoff_1()
# t4 = time.clock()
# print(t)
# print(t4-t3)

# test
# test_ballots = [['C','B'],['A','B','C'],['B','C','A'],['B','A','C']]
# test_ballots = [tuple(x) for x in test_ballots]
# test = Bordacount(test_ballots)
# print(test.get_Winner())

# test_schedule = {('A','B'):2, ('B','A'):3}
# test = Schedule(test_schedule)


    
