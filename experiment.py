import os
import inspect
import sys
from typing import List

from players import Player

class Experiment:
    def __init__(self, experiment_name : str, player_ids : List[str], repetitions : int = 10, experiment_data_path : str = 'experiments'):
        self.player_types = self._get_player_types()
        
        for id in player_ids:
            self._check_player_id(id)        
        
        self.player_ids = player_ids
        self.repetitions = repetitions
        self.experiment_data_path = experiment_data_path
        self.experiment_name=experiment_name
        

    def run(self):
        self._create_dir()
        for i in range(self.repetitions):
            pass      

    def _check_player_id(self, id):
        if id not in self.player_types:
            raise Exception('Id \'%s\' does not correspond to an existing player type.' % (id))

    def _get_player_types(self):
        clsmembers = inspect.getmembers(sys.modules['players'], inspect.isclass)
        return {mem[0].lower().replace('player', '') : mem[1] for mem in clsmembers if mem[0].lower() != 'player'}

    def _create_dir(self):
        dir_name_parts = [self.experiment_name,self.player1_id.lower(),self.player2_id.lower()]
        self.full_path = os.path.join(self.experiment_data_path, '-'.join(dir_name_parts))
        try:
            os.makedirs(self.full_path)
        except OSError as e:
            pass

if __name__ == '__main__':
    pass
    exp = Experiment('test',['ai'])
    # print(exp._get_player_types())