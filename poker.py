from collections import Counter
import itertools
import random
#hands = (line.split() for line in open('p054_poker.txt'))

values = {r:i for i,r in enumerate('23456789TJQKA', 2)}
lvalues = {r:i for i,r in enumerate('A23456789TJQK', 1)}
straights = [(v, v-1, v-2, v-3, v-4) for v in range(14, 5, -1)] + [(14, 5, 4, 3, 2)]
lstraights = [(v, v-1, v-2, v-3, v-4) for v in range(13, 4, -1)] + [(13, 12, 11, 10, 1)]
ranks = [(1,1,1,1,1),(2,1,1,1),(2,2,1),(3,1,1),(),(),(3,2),(4,1)]
ranks3 = [(1,1,1),(2,1),(3,)]

def flatten(L):
    return list(itertools.chain.from_iterable(L))    


deck4 = [[v+'H',v+'S',v+'C',v+'D'] for v in values.keys()]
deck = flatten(deck4)

def getDeck():
    d = deck[:]
    random.shuffle(d)
    return d

def deal(d,np,nc):
    hands = [[] for _ in range(np)]
    for c in range(nc):
        for p in range(np):
            hands[p].append(d.pop())
    return hands

def hand_rank5(hand):
	score = zip(*sorted(((v, values[k]) for
		k,v in Counter(x[0] for x in hand).items()), reverse=True))
	score[0] = ranks.index(score[0])
	if len(set(card[1] for card in hand)) == 1: score[0] = 5  # flush
	if score[1] in straights: score[0] = 8 if score[0] == 5 else 4  # str./str. flush
	return score


def hand_rank5_low(hand):
	score = zip(*sorted(((v, lvalues[k]) for
		k,v in Counter(x[0] for x in hand).items()), reverse=True))
	score[0] = ranks.index(score[0])
	if len(set(card[1] for card in hand)) == 1: score[0] = 5  # flush
	if score[1] in lstraights: score[0] = 8 if score[0] == 5 else 4  # str./str. flush
	return score


def hand_rank3(hand):
	score = zip(*sorted(((v, values[k]) for
		k,v in Counter(x[0] for x in hand).items()), reverse=True))
        print(score)
	score[0] = ranks3.index(score[0])
        if score[0] == 0 and score[1] == (7,5,3):
            score[0] = 3
	return score


def best5(hand):
    fives = itertools.combinations(hand,5)
    fivesL = list(fives)
    szscors = sorted(fivesL,key=hand_rank5)
    return(szscors[-1])

def argsort(seq):
    # http://stackoverflow.com/questions/3071415/efficient-method-to-calculate-the-rank-vector-of-a-list-in-python
    return sorted(range(len(seq)), key=seq.__getitem__)

def handArgSort(hands):
    return sorted(range(len(hands)), key = lambda x: hand_rank5(hands[x])) 

def handArgSortLow(hands):
    return sorted(range(len(hands)), key = lambda x: hand_rank5_low(hands[x])) 


def low5(hand):
    fives = itertools.combinations(hand,5)
    fivesL = list(fives)
    szscors = sorted(fivesL,key=hand_rank5_low)
    return(szscors[0])

def make_psinfo(od={}):
    #short player info
    d = {'player_name':'',
         'player_stack':0,
         'down_cards':0,
         'up_cards':[],
         'pencil_setaside':0,
         'current_bet':0,
         'player_atrisk':0,
         'dealer':False,
         'status':'in'}
    d.update(od)
    return d
         

def make_pinfo(od={}):
    d = {'player_name':'',
         'room_name':'',
         'player_stack':0,
         'player_paid':0,
         'current_game':'',
         'game_rules':'',# shown modal click?
         'game_status':'',
         'down_cards':[],
         'up_cards':[],
         'pencil_setaside':0,
         'player_atrisk':0,
         'dealer':False,
         'button_list':[],
         'card_region':[],
         'player_number':-1,
         'status':'in',
         'other_cards_to_show':{}}
    d.update(od)
    return d

class GameConfig(object):
    
    def __init__(self,options, steplist, donecheck=lambda:True, loop=False):
        self.options = initDict(options,globalOptions)
        self.steplist = steplist
        self.donecheck = donecheck
        self.loop = loop

#game_step functions

def w_init(gr):
    """
    w_init initializes the game for the WAITING game step
     gr is a GameRoom object for the room in question
     this function side-effects the game room object.
    returns nothing

    NYI -- dealing with going back to a waiting state after starting a game

    """
    gr.players={}
    gr.status_message = 'waiting for players'

def w_handler(gr):
    """
    w_handler(gr) handles messages from clients for the WAITING game step 
     gr is a GameRoom object for the room in question
     this function side-effects the game room object.
    returns nothing

    This function needs to deal with messages that:
    -- deal with buy-ins for players
    -- deal with moving the optional active/pencil 

    """
    

        
class GameRoom(object):
    def __init__(self,name, gr_config):  #maybe later move this to a different func. 
        self.name = name
        self.config = gr_config
        self.games = game_configs  #later, we'll make these editable
        self.current_game_n = -1 #will be chosen
        self.current_game = [] #will be an instantiated game
        self.players = {}  #we need to add to this; this is primary set of players 
        self.stepn = 0
        self.state = {}
        self.status_message
        self.steps = [GameStep('Waiting',w_init,w_handler,w_donecheck),
                      GameStep('DealerChoice',dc_init,dc_handler,dc_donecheck),
                      GameStep('Play',play_init,play_handler,play_donecheck)]
        self.loop = True
        self.loop_start = 1  #only loop back to dealerChoice
        self.steps[0].init_function(self)

        
    def handle(self,msg):
        self.steps[self.stepn].handle(msg, self)
        if (self.steps[self.stepn].donecheck(self)):
            self.stepn = (self.stepn+1)
            if (self.stepn >= len(self.steps)):
                if self.loop:
                    stepn = self.loop_start
                else:
                    print('we are done')
            self.steps[self.stepn].init_function(self)
            
            
    def add_player(player):
        pi = make_player_info({'player_name':player,'room_name':name})
        assert (player not in players),"tried to add a player who is already in the game"
        players[player] = pi
        
#a game we're going to play 
class Game(object):
    def __init__(self,gc,players):
        self.options = initDict(gc.options)
        self.players = players
        self.steplist = gc.steplist
        self.donecheck = gc.donecheck
        self.loop = gc.loop
        self.deck = getDeck()
        self.initGame()

    def initGame():
        self.step_i = 0
        self.steplist[0].init_func(self)
        
    def handle(self, msg):
        #delegate handling to the function
        steplist[self.step_i].handle(msg)
        

class GameStep(object):
    def __init__(self, name, init_func, handler, donecheck):
        self.name = name
        self.init_func = init_func
        self.handle = handler
        self.donecheck = donecheck

#will need to deal with player disconnections...


         

if __name__ == "__main__":
    #print "P1 wins", sum(hand_rank(hand[:5]) > hand_rank(hand[5:]) for hand in hands)

    hand = ['7C','3S','3H']
    hand = ['AH','2D','3S','4C','5H']
    print(hand)
    print('score is ' + str(hand_rank5(hand)))
    print('low score is ' + str(hand_rank5_low(hand)))
    print("")
    print("")


    anod = getDeck()
    hs = deal(anod,6  ,8)  # deal 7 cards per player
    if 0:
        print('judging high')
        bhs = [best5(h) for h in hs] # id the best 5
        bhr = [hand_rank5(h) for h in bhs] #score the hands
        ho = handArgSort(bhs)
        for h in reversed(ho):
            print(str(bhs[h]) + '  ' + str(bhr[h]))
    else:
        print('judging low')
        lhs = [low5(h) for h in hs]
        lhr = [hand_rank5_low(h) for h in lhs]
        ho = handArgSortLow(lhs)
        for h in ho:
            print(str(lhs[h]) + '  ' + str(lhr[h]))

#make sure to check that aces can be low as well as high
