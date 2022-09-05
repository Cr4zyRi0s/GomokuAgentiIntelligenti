from time import time
from experiment import Experiment

human = {
    'class' : 'human',
    'args' : {}
}

ai_sd2_v2_ov2 = {
    'class' : 'ai',
    'args' : {
        'search_depth' : 2,
        'version' : 2,
        'opening_version' : 2
    }
}

ai_sd3_v2_ov2 = {
    'class' : 'ai',
    'args' : {
        'search_depth' : 3,
        'version' : 2,
        'opening_version' : 2
    }
}

ai_sd4_v2_ov2 = {
    'class' : 'ai',
    'args' : {
        'search_depth' : 4,
        'version' : 2,
        'opening_version' : 2
    }
}


ai_sd2_v2 = {
    'class' : 'ai',
    'args' : {
        'search_depth' : 2,
        'version' : 2
    }
}

ai_sd3_v2 = {
    'class' : 'ai',
    'args' : {
        'search_depth' : 3,
        'version' : 2
    }
}

ai_sd4_v2 = {
    'class' : 'ai',
    'args' : {
        'search_depth' : 4,
        'version' : 2
    }
}

ai_sd2 = {
    'class' : 'ai',
    'args':{
    'search_depth' : 2
    }
}
ai_sd3 = {
    'class' : 'ai',
    'args':{
    'search_depth' : 3
    }
}
ai_sd4 = {
    'class' : 'ai',
    'args':{
    'search_depth' : 4
    }
}

players_defs = {
    'human' : human,
    'sd2v2' : ai_sd2_v2,
    'sd3v2' : ai_sd3_v2,
    'sd4v2' : ai_sd4_v2,
}

def run_human_vs_ai():
    start_time = time()
    match_list = [
        ('human','sd2v2'),    
        ('human','sd3v2'),    
        ('human','sd4v2'),
        ('sd2v2','human'),    
        ('sd3v2','human'),    
        ('sd4v2','human'),    
    ]
    experiment =  Experiment('human-vs-ai', player_defs=players_defs, match_list=match_list, repetitions=2)
    experiment.run()
    print('Experiment took %f to run.' % (round(time() - start_time,3)))    

def run_depth_variation():
    players_defs = {
        'sd2v2ov2' : ai_sd2_v2_ov2,    
        'sd3v2ov2' : ai_sd3_v2_ov2,   
        'sd4v2ov2' : ai_sd4_v2_ov2     
    }

    start_time = time()
    experiment =  Experiment('search-depth-var', player_defs=players_defs, repetitions=25)
    experiment.run()
    print('Experiment took %f to run.' % (round(time() - start_time,3)))    

def run_opening_v2():
    players_defs = {
        'sd4v2ov2' : ai_sd4_v2_ov2        
    }

    start_time = time()
    experiment =  Experiment('opening-v2', player_defs=players_defs, repetitions=50)
    experiment.run()
    print('Experiment took %f to run.' % (round(time() - start_time,3)))    

if __name__ == '__main__':
    run_depth_variation()