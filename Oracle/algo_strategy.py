import gamelib
import random
import math
import warnings
from sys import maxsize
import json

class AlgoStrategy(gamelib.AlgoCore):

    def __init__(self):
        super().__init__()
        seed = random.randrange(maxsize)
        random.seed(seed)
        gamelib.debug_write('Random seed: {}'.format(seed))
    def on_game_start(self, config):
        
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global FILTER, ENCRYPTOR, DESTRUCTOR, PING, EMP, SCRAMBLER
        FILTER = config["unitInformation"][0]["shorthand"]
        ENCRYPTOR = config["unitInformation"][1]["shorthand"]
        DESTRUCTOR = config["unitInformation"][2]["shorthand"]
        PING = config["unitInformation"][3]["shorthand"]
        EMP = config["unitInformation"][4]["shorthand"]
        SCRAMBLER = config["unitInformation"][5]["shorthand"]
        self.scored_on_locations = []
        self.destructorLocations = [[25,12],[2,12], [11,5],[16,5]]
        self.filterLocations = [[ 0, 13],[ 1, 13],[ 2, 13],[ 25, 13],[ 26, 13],[ 27, 13],[ 3, 12],[ 24, 12],[ 4, 11],[ 23, 11],[ 5, 10],[ 22, 10],[ 6, 9],[ 21, 9],[ 7, 8],[ 20, 8],[ 8, 7],[ 19, 7],[ 9, 6],[ 10, 6],[ 11, 6],[ 16, 6],[ 17, 6],[ 18, 6],[ 12, 5],[ 15, 5]]
        self.spawnLoc = [10,3]
        self.scramSpawn = [[7,7],[16,2]]
        self.encryptLoc = [[10,5],[11,4],[12,3],[13,2],[13,3],[12,4],[13,4]]
        self.encryptorCount = 0

    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        game_state.suppress_warnings(True)  #Comment or remove this line to enable warnings.
        self.sentEMP = False
        
        self.placeWall(game_state)
        self.placeDefense(game_state)
        self.placeEnc(game_state)
        self.pingAttacks(game_state)
        self.placeScram(game_state)
       # self.empAttack(game_state)
        
        game_state.submit_turn()
    def placeScram(self, gamestate):
        
        gamestate.attempt_spawn(SCRAMBLER, self.scramSpawn,1)

    def placeEnc(self, gamestate):
        gamestate.attempt_spawn(ENCRYPTOR, self.encryptLoc)
        for spot in self.encryptLoc:
            if gamestate.contains_stationary_unit(spot):
                self.encryptorCount += 1

    def placeDefense(self, gamestate):
        gamestate.attempt_spawn(DESTRUCTOR,self.destructorLocations)
        return
    
    def placeWall(self,gamestate):
        gamestate.attempt_spawn(FILTER,self.filterLocations)
        return
    def empAttack(self,gamestate):
        if gamestate.number_affordable(EMP) >=5:
            gamestate.attempt_spawn(EMP, self.spawnLoc, 3)
            self.sentEMP = True
        return
    def pingAttacks(self, gamestate):
        numPos =  gamestate.number_affordable(PING)

        if gamestate.number_affordable(PING) >= 10 and self.encryptorCount >= 4:
            gamestate.attempt_spawn(PING, self.spawnLoc, numPos)
        return

    def on_action_frame(self, turn_string):
        """
        This is the action frame of the game. This function could be called 
        hundreds of times per turn and could slow the algo down so avoid putting slow code here.
        Processing the action frames is complicated so we only suggest it if you have time and experience.
        Full doc on format of a game frame at: https://docs.c1games.com/json-docs.html
        """
        # Let's record at what position we get scored on
        state = json.loads(turn_string)
        events = state["events"]
        breaches = events["breach"]
        for breach in breaches:
            location = breach[0]
            unit_owner_self = True if breach[4] == 1 else False
            # When parsing the frame data directly, 
            # 1 is integer for yourself, 2 is opponent (StarterKit code uses 0, 1 as player_index instead)
            if not unit_owner_self:
                gamelib.debug_write("Got scored on at: {}".format(location))
                self.scored_on_locations.append(location)
                gamelib.debug_write("All locations: {}".format(self.scored_on_locations))


if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
