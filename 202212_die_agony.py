# 202212 Die Agony

# https://www.janestreet.com/puzzles/die-agony-index/

# Allow indexing with pairs to make it easier for ourselves
class Mat:
    def __init__(self, mat):
        self._mat = mat
    @staticmethod
    def zero(m,n):
        return Mat([[0]*n for _ in range(m)])
    def __getitem__(self, pair):
        return self._mat[pair[0]][pair[1]]
    def __setitem__(self, pair, val):
        self._mat[pair[0]][pair[1]] = val

# >>> m = Mat.zero(2,3)
# >>> m._mat
# [[0, 0, 0], [0, 0, 0]]
# >>> m[(0,0)] = 100
# >>> m[(1,2)] = 300
# >>> m._mat
# [[100, 0, 0], [0, 0, 300]]
# >>> m[(1,2)]
# 300

grid = Mat(
    [
        [57, 33, 132,268,492,732],
        [81, 123,240,443,353,508],
        [186,42, 195,704,452,228],
        [-7, 2,  357,452,317,395],
        [5,  23, -4, 592,445,620],
        [0,  77, 32, 403,337,452]
    ]
)

# Fix numbering for die faces and directions (top down view, 0 at bottom):
#    1
#  +---+
# 4| 5 |2
#  +---+
#    3

# Orientation can be encoded by a pair "ori" so that
# ori[0] = face 0's direction (initially 0)
# ori[1] = face 1's direction (initially 1)

# opn - operator number:
# 0 - UP
# 1 - RIGHT
# 2 - DOWN
# 3 - LEFT
# 4 - CW
# 5 - CCW
#
# CW and CCW aren't possible in this problem but include them to make our life earier
UP, RIGHT, DOWN, LEFT, CW, CCW = range(6) # pyman's enum


# operators sending old direction numbers to new direction numbers:
# ops[opn][old_dn] = new_dn
# For example, ops[0][5] = 1 since after the die tips up the top side points up
ops = (
    # UP
    (3,0,2,5,4,1),
    # RIGHT
    (4,1,0,3,5,2),
    # DOWN
    (1,5,2,0,4,3),
    # LEFT
    (2,1,5,3,0,4),
    # CW
    (0,2,3,4,1,5),
    # CCW
    (0,4,1,2,3,5)
)

# f1d[f0d] = face 1's directions when face 0 is in f0d
# many steps below depend on this
f1d = (
    # 0 - CW*
    (1,2,3,4),
    # 1 - DOWN RIGHT*
    (5,2,0,4),
    # 2 - LEFT DOWN*
    (1,5,3,0),
    # 3 - UP LEFT*
    (0,2,5,4),
    # 4 - RIGHT UP*
    (1,0,3,5),
    # 5 - RIGHT RIGHT CCW*
    (1,4,3,2)
)

# all possible orientations:
oris = tuple((i, f1d[i][j]) for i in range(6) for j in range(4))

# apply ops[opn] to dm (direction map -- could be an ori) ct times
def oa(opn, dm, ct=1):
    n = 0
    ndm = dm
    while n < ct:
        ndm = tuple(ops[opn][ndm[i]] for i in range(len(dm)))
        n += 1
    return ndm

# tipping map:
# tm[opn][old_ori] == new_ori
# where opn in range(4)
tm = [{o:oa(i,o) for o in oris} for i in range(4)]

# initial map
im = (0,1,2,3,4,5)

# as in f1d
opnbyf0d = (
    CW,
    RIGHT,
    DOWN,
    LEFT,
    UP,
    CCW
)

imbyf0d = (
    im,
    oa(DOWN, im),
    oa(LEFT, im),
    oa(UP, im),
    oa(RIGHT, im),
    oa(RIGHT, im, 2)
)

# take dn that face 0 points to, and starting map, and returns a dict d such that
# d[(dn,i)][fn] = direction of fn when ori==(dn, i) 
def fmbyf0d(dn, sm):
    return {(dn,f1d[dn][i]):oa(opnbyf0d[dn], sm, i) for i in range(4)}

# face map:
# fm[ori][fn] = direction of fn in ori
fm = {k:d[k] for d in (fmbyf0d(i, imbyf0d[i]) for i in range(6)) for k in d}

# top[ori] = face number of the top side
top = {o:fm[o].index(5) for o in oris}

edge_tests = (
    # UP
    lambda loc: loc[0] == 0,
    # RIGHT
    lambda loc: loc[1] == 5,
    # DOWN
    lambda loc: loc[0] == 5,
    # LEFT
    lambda loc: loc[1] == 0
)
dlocs = (
    # UP
    (-1, 0),
    # RIGHT
    (0, 1),
    # DOWN
    (1, 0),
    # LEFT
    (0, -1)
)

class State:
    def __init__(self, val, loc, ori, sco, mvn, prev):
        self._val = val
        self._loc = loc
        self._ori = ori
        self._sco = sco
        self._mvn = mvn
        self._prev = prev
    
    def _newstate(self, at_edge, dloc, dn):
        if at_edge(self._loc):
            return None
        new_loc = (self._loc[0]+dloc[0], self._loc[1]+dloc[1])
        new_ori = tm[dn][self._ori]
        new_mvn = self._mvn + 1
        ntn = top[new_ori]
        new_topval = self._val[ntn]
        if new_topval is None:
            new_sco = grid[new_loc]
            if (new_sco - self._sco)%new_mvn != 0:
                return None
            new_topval = (grid[new_loc] - self._sco)//new_mvn
            new_val = self._val[0:ntn]+(new_topval,)+self._val[ntn+1:]
            return State(new_val, new_loc, new_ori, new_sco, new_mvn, self)
        else:
            new_val = self._val          
            new_sco = self._sco + new_mvn*new_topval
            if new_sco == grid[new_loc]:
                return State(new_val, new_loc, new_ori, new_sco, new_mvn, self)
            else:
                return None

    def tip(self, dn):
        return self._newstate(edge_tests[dn], dlocs[dn], dn)

    def isfinal(self):
        return self._loc == (0,5)

    def prev(self):
        return self._prev

    def loc(self):
        return self._loc

    def val(self):
        return self._val

def find_final(rightfirst):
    state = State((None,)*6, (5,0), (0,1), 0, 0, None)
    fringe = []
    next_state = None
    if rightfirst:
        rg = range(4)
    else:
        rg = range(3,-1,-1)
    while True:
        if state.isfinal():
            return state
        for dn in rg:
            next_state = state.tip(dn)
            if next_state:
                fringe.append(next_state)
        try:
            state = fringe.pop()
        except IndexError:
            return None
    
def solve(rightfirst):
    final = find_final(rightfirst)
    rpath = [final.loc()]
    prev = final.prev()
    while prev:
        rpath.append(prev.loc())
        prev = prev.prev()
    visited = set(rpath)
    print('rpath: ', rpath)
    print('visited: ', visited)
    print('val: ', final.val())
    total = sum((grid[(i,j)] for i in range(6) for j in range(6)))
    pathsum = sum((grid[loc] for loc in visited))
    return total - pathsum
    
# >>> solve(True)
# rpath:  [(0, 5), (1, 5), (1, 4), (1, 3), (2, 3), (3, 3), (3, 4), (3, 5), (4, 5), (5, 5), (5, 4), (5, 3), (4, 3), (3, 3), (3, 2), (2, 2), (2, 1), (2, 0), (1, 0), (1, 1), (1, 2), (0, 2), (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (5, 2), (4, 2), (4, 1), (4, 0), (5, 0)]
# visited:  {(1, 3), (2, 1), (5, 1), (4, 0), (1, 2), (3, 3), (5, 5), (1, 5), (5, 0), (2, 2), (4, 1), (1, 1), (5, 4), (3, 2), (4, 5), (5, 2), (1, 4), (0, 5), (2, 3), (4, 2), (1, 0), (5, 3), (3, 5), (0, 1), (3, 1), (2, 0), (4, 3), (3, 4), (0, 2)}
# val:  (7, -9, -3, 5, 9, 9)
# 1935
# >>> solve(False)
# rpath:  [(0, 5), (1, 5), (1, 4), (1, 3), (2, 3), (3, 3), (3, 4), (3, 5), (4, 5), (5, 5), (5, 4), (5, 3), (4, 3), (3, 3), (3, 2), (2, 2), (2, 1), (2, 0), (1, 0), (1, 1), (1, 2), (0, 2), (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (5, 2), (4, 2), (4, 1), (4, 0), (5, 0)]
# visited:  {(1, 3), (2, 1), (5, 1), (4, 0), (1, 2), (3, 3), (5, 5), (1, 5), (5, 0), (2, 2), (4, 1), (1, 1), (5, 4), (3, 2), (4, 5), (5, 2), (1, 4), (0, 5), (2, 3), (4, 2), (1, 0), (5, 3), (3, 5), (0, 1), (3, 1), (2, 0), (4, 3), (3, 4), (0, 2)}
# val:  (7, -9, -3, 5, 9, 9)
# 1935
# >>> 
