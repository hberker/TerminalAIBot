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
        self.destructorLocations = [[]]
        self.filterLocations = [[]]
        self.extraFilterLocations = [[]]
        gamelib.debug_write('Random seed: {}'.format(seed))
        self.encryptorCount = 0
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
        self.destructorLocations = [[1,12],[26,12],[7,10],[20,10],[11,7],[16,7],[19,10],[8,10],[25,11],[2,11],[15,6],[12,6]]
        self.filterLocations = [[7,11],[1,13],[26,13],[20,11],[6,11],[9,10],[0,13],[2,12],[3,11],[25,12],[27,13],[19,11],[8,11],[21,11],[22,11],[23,11],[5,11],[4,11],[18,10],[10,9],[17,9],[13,11],[14,11]]
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
        self.placeDefense(game_state)
        self.placeExtraDefense(game_state)
        self.placeEnc(game_state)
        self.empAttack(game_state)
        self.pingAttacks(game_state)
        game_state.submit_turn()

    def placeScram(self, gamestate):
        gamestate.attempt_spawn(SCRAMBLER, [14,1])

    def placeEnc(self, gamestate):
        gamestate.attempt_spawn(ENCRYPTOR, [[13,2],[14,2],[13,3],[14,3]])
        for spot in [[13,2],[14,2],[13,3],[14,3]]:
            if gamestate.contains_stationary_unit(spot):
                self.encryptorCount += 1

    def placeDefense(self, gamestate):
        gamestate.attempt_spawn(DESTRUCTOR,self.destructorLocations)
        return
    
    def placeExtraDefense(self,gamestate):
        gamestate.attempt_spawn(FILTER,self.filterLocations)
        return
    def empAttack(self,gamestate):
        if gamestate.number_affordable(EMP) >=5:
            gamestate.attempt_spawn(EMP, [13,0], 3)
            self.sentEMP = True
        return
    def pingAttacks(self, gamestate):
        
        if gamestate.number_affordable(PING) >= 5 and self.encryptorCount >= 4 and self.sentEMP :
            gamestate.attempt_spawn(PING, [13,0],5)
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
