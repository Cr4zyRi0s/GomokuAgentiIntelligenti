import os
import sys
from time import sleep
from match import ReplayMatch

exp_list = os.listdir('experiments')
sel_exp = input('Select experiment to examine ' + str(list(zip(range(len(exp_list)),exp_list))) + '\n')
sel_exp = int(sel_exp)

experiment = exp_list[sel_exp]
print('Selected experiment:', experiment)
match_types = set([(fname.split('_')[1], fname.split('_')[3]) for fname in os.listdir(os.path.join('experiments', experiment))])
match_repetitions = set([fname.split('.')[0].split('_')[-1] for fname in os.listdir(os.path.join('experiments', experiment))])

match_types = list(match_types)
match_types.sort()
match_repetitions = list(match_repetitions)
match_repetitions.sort()

while True:
    sel_match_type = input('Select match type:' + str(list(zip(range(len(match_types)),match_types))) + '\n')
    if sel_match_type == 'exit':
        sys.exit()
    else:
        sel_match_type = int(sel_match_type)
        match_type = match_types[sel_match_type]
        sel_match = input('Select match: '+ str(list(match_repetitions)) + '\n')
        sel_match = int(sel_match)
        match_name = '_'.join(['match', match_type[0], 'bl',match_type[1], 'wh', str(sel_match)]) + '.json'
        rep_match = ReplayMatch(os.path.join('experiments', experiment, match_name))
        while not rep_match.is_over():
            rep_match.update()
            sleep(1)

