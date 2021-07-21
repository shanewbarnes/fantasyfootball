# Creates classes for storing player data for processing

class Player:

    def __init__(self, name, age, year, fantasyPoints, opponentStrength):
        self.name = name
        self.age = age
        self.year = year
        self.fantasyPoints = fantasyPoints
        self.opponentStrength = opponentStrength


class QB(Player):

    def __init__(self, qbRate, oLineStrength):
        Player.__init__()
        self.qbRate = qbRate
        self.oLineStrength = oLineStrength


class RB(Player):

    def __init__(self, oLineStrength):
        Player.__init__()
        self.oLineStrength = oLineStrength


class WR_TE(Player):

    def __init__(self, qbStrength):
        Player.__init__()
        self.qbStrength = qbStrength

