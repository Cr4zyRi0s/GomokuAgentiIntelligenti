import itertools
import re
import networkx as nx
import time
import json 
from tqdm import tqdm

def replace_char(string : str, index : int, char):
    return string[:index] + char + string[index + 1:]

def generate_all_sequences_of_len(length : int) -> set:
    all_seqs = set(itertools.product('01', repeat = length))
    all_seqs = {''.join(s) for s in all_seqs}
    all_seqs.remove(''.join(['0' for _ in range(length)]))    

    to_remove = set()
    for s in all_seqs:
        if len(re.findall('1{6,}',s)) > 0:
            to_remove.add(s)

        #elif len(re.findall('10{2,}1',s)) > 0:
        #    to_remove.add(s)
        
        elif length > 5 and s.count('1') >= length - 1:
            to_remove.add(s)

    all_seqs.difference_update(to_remove)
    return all_seqs

def generate_threat_info(seq : str, lvl : int):    
    if len(list(re.finditer('(?<!1)1{5}(?!1)', seq))) == 1:
        return {seq},{},{}

    n_ones = seq.count('1')
    zeros_pos = [m.span()[0] for m in re.finditer('0', seq)]
    perms = itertools.product('01', repeat=len(zeros_pos))    

    possible_moves = set()
    possible_5s = set()
    for p in perms:        
        candidate = seq[:]

        for i in range(len(zeros_pos)):
            candidate = replace_char(candidate, zeros_pos[i], p[i])

        cand_n_ones = candidate.count('1')

        if cand_n_ones < 5:
            continue            
        if cand_n_ones > 5 and n_ones < 5:
            continue
        if p.count('1') != 5 - lvl:
            continue                

        win_seq_match = list(re.finditer('(?<!1)1{5}(?!1)', candidate))
        if len(win_seq_match) == 1:
            possible_5s.add(candidate)
            ones_pos = [zeros_pos[m.span()[0]] for m in re.finditer('1', ''.join(p))]
            for i in range(len(ones_pos)):
                possible_moves.add((ones_pos[i]))

    best_defences = get_best_defence_for_threat(seq,possible_5s)
    return possible_5s, possible_moves, best_defences    

def get_best_defence_for_threat(threat : str, possible_5s : set) -> list:
    zeros_pos = [m.span()[0] for m in re.finditer('0', threat)]
    n_of_blocks = [0 for _ in range(len(zeros_pos))]
    for five in possible_5s:
        for zi in range(len(zeros_pos)):
            if five[zeros_pos[zi]] == '1':
                n_of_blocks[zi] += 1
    
    max_blocks = max(n_of_blocks)
    best_def = {zeros_pos[i] for i in range(len(zeros_pos)) if n_of_blocks[i] == max_blocks}
    return best_def


def precompute_threats(max_seq_len = 7) -> dict:
    threats = {i:dict() for i in range(5, max_seq_len + 1)}
    all_seqs = {i: generate_all_sequences_of_len(i) for i in range(5, max_seq_len + 1)}
    
    for s in all_seqs[5]:
        lvl = s.count('1')
        p_5s,p_moves,b_def = generate_threat_info(s, lvl)
        sev = len(p_5s)
        if sev == 0:
            continue        
        threats[5][s] = {'type' : (lvl, sev), 'p_moves' : list(p_moves), 'b_def' : list(b_def)}

    for l in tqdm(range(6,max_seq_len + 1)):
        for s in all_seqs[l]:
            lvl = max([threats[5][s[i : i + 5]]['type'][0] for i in range(0, l - 4) if s[i : i + 5] in threats[5].keys()])
            p_5s,p_moves,b_def = generate_threat_info(s,lvl)
            sev = len(p_5s)
            if sev == 0:
                continue
            threats[l][s] = {'type' : (lvl, sev), 'p_moves' : list(p_moves), 'b_def' : list(b_def)}
    return threats

def generate_dependency_graph(threats : dict, max_seq_len : int = 7) -> dict:    
    graphs = {}
    for l in range(5,max_seq_len + 1):
        curr_g = nx.DiGraph()
        curr_g.add_nodes_from(threats[l].keys())
        for seq,info in threats[l].items():
            for m in info['p_moves']:
                curr_g.add_edge(seq, replace_char(seq,m,'1'), move = m)   
        graphs[l] = curr_g
                
    return graphs        

def load_precomputed_threats(filename = 'threat_data.json'):
    with open('threat_data.json', 'r') as file:
        l_threats = json.load(file)
    return l_threats


if __name__ == '__main__':
    t = time.time()
    threats = precompute_threats(15)
    with open('threat_data.json', 'w') as file:
        json.dump(threats, file)
    print('elapsed time:', round(time.time() - t,4))

    t = time.time()
    with open('threat_data.json', 'r') as file:
        l_threats = json.load(file)
    print('elapsed time:', round(time.time() - t,4))


