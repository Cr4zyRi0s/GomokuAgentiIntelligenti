'''
moves = [(i,1) for i in range(2,6)]
for m in moves:
    state.make_move(m,True)
'''
'''
for j in range(state.grid.shape[1]):
    for i in range(state.grid.shape[0]):
        rand = random.randint(1,3)
        if rand > 1:
            if rand == 2:
                state.make_move((j,i), True)
            else:
                state.make_move((j,i), False)
'''
'''
print(state._get_line_45((2,2)))
print(state._get_line_45((2,1)))    
print(state._get_line_45((1,2)))
print(state._get_line_45((4,1)))
print(state._get_line_45((4,4)))
'''
'''
moves = [(i, 4-i) for i in range(5)]
for m in moves:
    state.make_move(m, True)
print(state.board_45)
print(state._get_line_45((2,2)))
'''
'''
moves = [(i,i) for i in range(4)]
moves.extend([(i,i + 2) for i in range(4)])
moves.extend([(i + 2,i) for i in range(4)])

for m in moves:
    state.make_move(m,True)

print(state.board_315)
print(state._get_line_315((0,0)))
print(state._get_line_315((0,2)))
print(state._get_line_315((2,0)))
'''
'''
test = [state._index_to_cr(state._cr_to_index(*m)) for m in moves]
test_90 = [state._90index_to_cr(state._cr_to_90index(*m)) for m in moves]
test_45 = [state._45index_to_cr(state._cr_to_45index(*m)) for m in moves]
test_315 = [state._315index_to_cr(state._cr_to_315index(*m)) for m in moves]

for i in range(5):
    if moves[i][0] != test[i][0] or moves[i][1] != test[i][1]:
        print('ERROR')
    if moves[i][0] != test_90[i][0] or moves[i][1] != test_90[i][1]:
        print('ERROR')
    if moves[i][0] != test_45[i][0] or moves[i][1] != test_45[i][1]:
        print('ERROR')
    if moves[i][0] != test_315[i][0] or moves[i][1] != test_315[i][1]:
        print('ERROR')

print('done')
'''
'''
state.make_move((0,1), True)
state.make_move((1,1), True)
state.make_move((2,1), True)
state.make_move((3,1), True)
state.make_move((4,1), True)
state.print_boards()

print('\n\nUNMAKING MOVES\n\n')
state.unmake_last_move()
state.unmake_last_move()
state.unmake_last_move()
state.unmake_last_move()
state.unmake_last_move()
state.print_boards()
'''

'''
for patt in patts:
    for match in re.finditer(patt, self.board):
        span = match.span()
        cells = [self._index_to_cr(i) for i in range(span[0], span[1])]
        threats[level].append(Threat(cells, match.group(), span, level))
    for match in re.finditer(patt,self.board_90):
        span = match.span()
        cells = [self._90index_to_cr(i) for i in range(span[0], span[1])]
        threats[level].append(Threat(cells, match.group(), span, level))
    for match in re.finditer(patt,self.board_45):
        span = match.span()
        cells = [self._45index_to_cr(i) for i in range(span[0], span[1])]
        threats[level].append(Threat(cells, match.group(), span, level))
    for match in re.finditer(patt,self.board_315):
        span = match.span()
        cells = [self._315index_to_cr(i) for i in range(span[0], span[1])]
        threats[level].append(Threat(cells, match.group(), span, level))
'''