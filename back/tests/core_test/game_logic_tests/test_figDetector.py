from core.game_logic.aux.figDetector import Color,get_board_figures



def test_figures0_1_2_3():
    #test for figures 1,2,3
    def initialize_board(rows : int, cols : int):
        board = []
        for x in range(1,rows +1):
            for y in range(1,cols +1 ):
                if (x==1 and (y==2 or y==3 or y==4)) or (y==3 and(x==2 or x==3)):
                    color = Color["BLUE"]
                elif (y==2 and(x==3 or x==4) or (y==3 and (x==4 or x==5 or x==6))):
                    color = Color["GREEN"]
                elif ((y==6 and (0<x<4) or (y==5 and (x==3 or x==4)))):
                    color = Color["YELLOW"]
                else:
                    color = Color["RED"]
                token = (x, y, color)
                board.append(token)
        return board

    board = initialize_board(6,6)
    assert get_board_figures('F1',board) == [[(1,3),(1,4),(1,2),(2,3),(3,3)]]
    assert get_board_figures('F2',board) == [[(3,2),(4,2),(4,3),(5,3),(6,3)]]
    assert get_board_figures('F3',board) == [[(1,6),(2,6),(3,6),(3,5),(4,5)]]



def test_figures0_4_5_6_7_8():

    def initialize_board(rows : int, cols : int):
        board1 = []
        for x in range(1,rows +1):
            for y in range(1,cols +1 ):
                if (y==1 and (1<x<7) or (y==4 and (1<x<6)) or (x==5 and y==3)):
                    color = Color["BLUE"]
                elif ((x==1 and (y==1 or y==2)) or (x==2 and y==2) or (y==3 and (x==2 or x==3)) 
                      or (y==5 and (x==4 or x==5 or x==6)) or (x==5 and y==6) or(x==6 and y==4)):
                    color = Color["YELLOW"]
                elif ((x==1 and (y==3 or y==4 or y==5)) or (y==5 and (x==2 or x==3)) or (y==2 and (2<x<7)) or (x==6 and y==3)):
                    color = Color["GREEN"]
                else:
                    color = Color["RED"]
                token = (x, y, color)
                board1.append(token)
        return board1

    board1 = initialize_board(6,6)
    assert get_board_figures('F4',board1) ==[[(2,2),(1,2),(1,1),(2,3),(3,3)]] 
    assert get_board_figures('F5',board1) ==[[(2,1),(3,1),(4,1),(5,1),(6,1)]]
    assert get_board_figures('F6',board1) ==[[(1,5),(1,4),(1,3),(2,5),(3,5)]]
    assert get_board_figures('F7',board1) ==[[(3,2),(4,2),(5,2),(6,2),(6,3)]]
    assert get_board_figures('F8',board1) ==[[(2,4),(3,4),(4,4),(5,4),(5,3)]]
    assert get_board_figures('F9',board1) ==[[(5,5),(4,5),(6,5),(6,4),(5,6)]]



def test_figures0_10_11_12_13_14():

    def initialize_board(rows : int, cols : int):
        board1 = []
        for x in range(1,rows +1):
            for y in range(1,cols +1 ):
                # 11 y 14
                if ((x==1 and (y==1 or y==2)) or (x==2 and (y==2 or y==3)) or (x==3 and y==2)
                    or (y==6 and (1<x<6)) or (x==4 and y==5)):
                    color = Color["BLUE"]
                #13 y 12
                elif ((y==1 and (1<x<6)) or (x==4 and y==2)
                      or (x==1 and (y==3 or y==4)) or (y==4 and (x==2 or x==3)) or (x==3 and y==5)):
                    color = Color["YELLOW"]
                #10
                elif ((x==6 and y==2) or (y==3 and (x==4 or x==5 or x==6)) or (x==4 and y==4)):
                    color = Color["GREEN"]
                else:
                    color = Color["RED"]
                token = (x, y, color)
                board1.append(token)
        return board1

    board1 = initialize_board(6,6)
    result = get_board_figures('F10',board1)
    result.append(get_board_figures('F11',board1)[0])
    result.append(get_board_figures('F12',board1)[0])
    result.append(get_board_figures('F13',board1)[0])
    result.append(get_board_figures('F14',board1)[0])
    assert result == [[(5, 3), (4, 3), (6, 3), (4, 4), (6, 2)], 
                      [(2, 2), (1, 2), (3, 2), (1, 1), (2, 3)], 
                      [(2, 4), (1, 4), (3, 4), (1, 3), (3, 5)], 
                      [(2, 1), (3, 1), (4, 1), (5, 1), (4, 2)], 
                      [(2, 6), (3, 6), (4, 6), (5, 6), (4, 5)]]



def test_figures0_15_16_17_18_e1_e2():

    def initialize_board(rows : int, cols : int):
        board1 = []
        for x in range(1,rows +1):
            for y in range(1,cols +1 ):
                #15 17 e1
                if ((y==5 and (x==5 or x==6)) or (y==6 and (x==4 or x==5 or x==6))
                    or (x==2 and (y==3 or y==4 or y==5)) or (y==4 and (x==1 or x==3))
                    or (y==1 and (x==5 or x==6)) or (y==2 and (x==4 or x==5))):
                    color = Color["BLUE"]
                #16 18 e2
                elif ((y==5 and (x==1 or x==3)) or (y==6 and (x==1 or x==2 or x==3))
                      or (y==3 and (x==4 or x==5 or x==6)) or (y==4 and (x==5 or x==6))
                      or (x==1 and (y==1 or y==2)) or (x==2 and (y==1 or y==2))):
                    color = Color["YELLOW"]
                else:
                    color = Color["RED"]
                token = (x, y, color)
                board1.append(token)
        return board1

    board1 = initialize_board(6,6)
    result = get_board_figures('F15',board1)
    result.append(get_board_figures('F16',board1)[0])
    result.append(get_board_figures('F17',board1)[0])
    result.append(get_board_figures('F18',board1)[0])
    result.append(get_board_figures('FE1',board1)[0])
    result.append(get_board_figures('FE2',board1)[0])
    assert result == [[(5, 6), (4, 6), (6, 6), (5, 5), (6, 5)], 
                      [(1, 6), (2, 6), (3, 6), (1, 5), (3, 5)], 
                      [(2, 4), (1, 4), (3, 4), (2, 3), (2, 5)], 
                      [(5, 3), (4, 3), (6, 3), (5, 4), (6, 4)], 
                      [(5, 1), (5, 2), (4, 2), (6, 1)], 
                      [(1, 2), (1, 1), (2, 2), (2, 1)]]
    

def test_figures0_e3_e4_e5_e6_e7_90e6():

    def initialize_board(rows : int, cols : int):
        board1 = []
        for x in range(1,rows +1):
            for y in range(1,cols +1 ):
                #e3 e4 e7
                if ((y==1 and (x==1 or x==2)) or (y==2 and (x==2 or x==3))
                    or (y==6 and (x==1 or x==2 or x==3)) or (x==2 and y==5)
                    or (y==4 and (x==3 or x==4 or x==5)) or (x==5 and y==3)):
                    color = Color["BLUE"]
                #e5 e6 e6rot
                elif ((y==1 and (x==3 or x==4 or x==5)) or (x==5 and y==2)
                      or (y==3 and (0<x<5)) 
                      or (x==6 and (2<y<7))):
                    color = Color["YELLOW"]
                else:
                    color = Color["RED"]
                token = (x, y, color)
                board1.append(token)
        return board1

    board1 = initialize_board(6,6)
    result = get_board_figures('FE3',board1)
    result.append(get_board_figures('FE4',board1)[0])
    result.append(get_board_figures('FE5',board1)[0])
    result.append(get_board_figures('FE6',board1)[0])
    result.append(get_board_figures('FE6',board1))
    assert result == [[(2, 1), (1, 1), (2, 2), (3, 2)], 
                      [(2, 6), (3, 6), (1, 6), (2, 5)], 
                      [(3, 1), (4, 1), (5, 1), (5, 2)],
                      [(1, 3), (2, 3), (3, 3), (4, 3)], 
                      [[(1, 3), (2, 3), (3, 3), (4, 3)], [(6, 6), (6, 5), (6, 4), (6, 3)]]]
    
    


# ======================= Tests 90degree rotations =======================

def test_figures90_1_2_3_4():
        
    def initialize_board(rows : int, cols : int):
        board = []
        for x in range(1,rows +1):
            for y in range(1,cols +1 ):
                #1 3
                if ((y==1 and (x==1 or x==2 or x==3)) or (x==2 and (y==2 or y==3))
                    or (x==5 and (y==1 or y==2 or y==3)) or (x==6 and (y==3 or y==4))):
                    color = Color["BLUE"]
                #2
                elif ((x==4 and (y==1 or y==2)) or (x==3 and (y==2 or y==3 or y==4))):
                    color = Color["GREEN"]
                #4 
                elif ((y==4 and (x==4 or x==5)) or (y==5 and (x==3 or x==4)) or (x==3 and y==6)):
                    color = Color["YELLOW"]
                else:
                    color = Color["RED"]
                token = (x, y, color)
                board.append(token)
        return board

    board2 = initialize_board(6,6)
    result = get_board_figures('F1',board2)
    result.append(get_board_figures('F2',board2)[0])
    result.append(get_board_figures('F3',board2)[0])
    result.append(get_board_figures('F4',board2)[0])
    assert result == [[(2, 1), (1, 1), (3, 1), (2, 2), (2, 3)], 
                      [(4, 1), (4, 2), (3, 2), (3, 3), (3, 4)], 
                      [(5, 1), (5, 2), (5, 3), (6, 3), (6, 4)], 
                      [(4, 5), (4, 4), (5, 4), (3, 5), (3, 6)]]
    

def test_figures90_5_6_7_8_9():

    def initialize_board(rows : int, cols : int):
        board = []
        for x in range(1,rows +1):
            for y in range(1,cols +1 ):
                #5 6
                if ((x==6 and (0<y<6))
                    or (x==1 and (y==1 or y==2 or y==3)) or (y==1 and (x==2 or x==3))):
                    color = Color["BLUE"]
                #7 9
                elif ((x==5 and (0<y<5)) or (x==4 and y==4)
                      or (x==2 and (y==4 or y==5 or y==6)) or (x==1 and y==5) or (x==3 and y==6)):
                    color = Color["GREEN"]
                # 8
                elif ((x==3 and (1<y<6)) or (x==4 and y==5)):
                    color = Color["YELLOW"]
                else:
                    color = Color["RED"]
                token = (x, y, color)
                board.append(token)
        return board

    board2 = initialize_board(6,6)
    result = get_board_figures('F5',board2)
    result.append(get_board_figures('F6',board2)[0])
    result.append(get_board_figures('F7',board2)[0])
    result.append(get_board_figures('F8',board2)[0])
    result.append(get_board_figures('F9',board2)[0])
    assert result == [[(6, 5), (6, 4), (6, 3), (6, 2), (6, 1)], 
                      [(1, 1), (2, 1), (3, 1), (1, 2), (1, 3)], 
                      [(5, 1), (5, 2), (5, 3), (5, 4), (4, 4)], 
                      [(3, 2), (3, 3), (3, 4), (3, 5), (4, 5)], 
                      [(2, 5), (2, 4), (2, 6), (3, 6), (1, 5)]]
    


def test_figures90_10_11_12_13_14_15():

    def initialize_board(rows : int, cols : int):
        board = []
        for x in range(1,rows +1):
            for y in range(1,cols +1 ):
                #10 12
                if ((y==1 and (x==1 or x==2)) or (x==2 and (y==3 or y==2)) or (x==3 and y==3)
                    or (x==6 and y==2) or (x==5 and (1<y<5)) or (x==4 and y==4)):
                    color = Color["BLUE"]
                #11 13 14
                elif ((y==1 and (x==4 or x==5)) or (y==2 and (x==3 or x==4)) or (x==4 and y==3)
                      or (x==6 and (1<y<7)) or (x==5 and y==5)
                      or (x==1 and (1<y<6)) or (x==2 and y==4)):
                    color = Color["GREEN"]
                # 15
                elif ((x==3 and (y==4 or y==5 or y==6)) or (x==4 and (y==5 or y==6))):
                    color = Color["YELLOW"]
                else:
                    color = Color["RED"]
                token = (x, y, color)
                board.append(token)
        return board

    board2 = initialize_board(6,6)
    result = get_board_figures('F10',board2)
    result.append(get_board_figures('F11',board2)[0])
    result.append(get_board_figures('F12',board2)[0])
    result.append(get_board_figures('F13',board2)[0])
    result.append(get_board_figures('F14',board2)[0])
    result.append(get_board_figures('F15',board2)[0])
    assert result == [[(2, 2), (2, 3), (2, 1), (3, 3), (1, 1)], 
                      [(4, 2), (4, 1), (4, 3), (5, 1), (3, 2)], 
                      [(5, 3), (5, 4), (5, 2), (4, 4), (6, 2)], 
                      [(6, 3), (6, 4), (6, 5), (6, 6), (5, 5)], 
                      [(1, 2), (1, 3), (1, 4), (1, 5), (2, 4)], 
                      [(3, 5), (3, 4), (3, 6), (4, 5), (4, 6)]]
    

def test_figures90_16_18_e1_e3_e4_e5_e7():

    def initialize_board(rows : int, cols : int):
        board = []
        for x in range(1,rows +1):
            for y in range(1,cols +1 ):
                #16 18 e5
                if ((x==1 and (y==1 or y==2 or y==3)) or (x==2 and (y==1 or y==3))
                    or (x==6 and (y==1 or y==2 or y==3)) or (x==5 and (y==2 or y==3))
                    or (x==4 and (y==4 or y==5 or y==6)) or (x==3 and y==6)):
                    color = Color["BLUE"]
                #e1 e4 e7
                elif ((x==3 and (y==1 or y==2)) or (x==4 and (y==2 or y==3))
                      or (x==5 and (y==4 or y==5 or y==6)) or (x==6 and y==5)
                      or (x==1 and (y==4 or y==5 or y==6)) or (x==2 and y==6)):
                    color = Color["GREEN"]
                # e3
                elif (x==3 and (y==3 or y==4) or (x==2 and (y==4 or y==5))):
                    color = Color["YELLOW"]
                else:
                    color = Color["RED"]
                token = (x, y, color)
                board.append(token)
        return board

    board2 = initialize_board(6,6)
    result = get_board_figures('F16',board2)
    result.append(get_board_figures('F18',board2)[0])
    result.append(get_board_figures('FE1',board2)[0])
    result.append(get_board_figures('FE3',board2)[0])
    result.append(get_board_figures('FE4',board2)[0])
    result.append(get_board_figures('FE5',board2)[0])
    result.append(get_board_figures('FE7',board2)[0])
    assert result == [[(1, 1), (1, 2), (1, 3), (2, 1), (2, 3)], 
                      [(6, 2), (6, 1), (6, 3), (5, 2), (5, 3)], 
                      [(3, 2), (4, 2), (4, 3), (3, 1)], 
                      [(2, 4), (2, 5), (3, 4), (3, 3)],
                      [(5, 5), (5, 6), (5, 4), (6, 5)], 
                      [(4, 4), (4, 5), (4, 6), (3, 6)], 
                      [(1, 4), (1, 5), (1, 6), (2, 6)]]
    


# ======================= Tests 180degree rotations =======================

def test_figures180_1_2_3_4():

    def initialize_board(rows : int, cols : int):
        board = []
        for x in range(1,rows +1):
            for y in range(1,cols +1 ):
                #1 4
                if ((x==6 and (y==1 or y==2 or y==3)) or (y==2 and (x==4 or x==5))
                    or (y==3 and (x==1 or x==2)) or (y==4 and (x==2 or x==3)) or (x==3 and y==5)):
                    color = Color["BLUE"]
                #2 
                elif ((y==2 and (x==1 or x==2 or x==3)) or (y==3 and (x==3 or x==4))):
                    color = Color["GREEN"]
                # 3
                elif ((y==5 and (x==4 or x==5 or x==6)) or (y==6 and (x==3 or x==4))):
                    color = Color["YELLOW"]
                else:
                    color = Color["RED"]
                token = (x, y, color)
                board.append(token)
        return board

    board3 = initialize_board(6,6)
    result = get_board_figures('F1',board3)
    result.append(get_board_figures('F2',board3)[0])
    result.append(get_board_figures('F3',board3)[0])
    result.append(get_board_figures('F4',board3)[0])
    assert result == [[(6, 2), (6, 1), (6, 3), (5, 2), (4, 2)], 
                      [(4, 3), (3, 3), (3, 2), (2, 2), (1, 2)], 
                      [(6, 5), (5, 5), (4, 5), (4, 6), (3, 6)], 
                      [(2, 4), (3, 4), (3, 5), (2, 3), (1, 3)]]
    

def test_figures180_6_7_8_9_11():

    def initialize_board(rows : int, cols : int):
        board = []
        for x in range(1,rows +1):
            for y in range(1,cols +1 ):
                #6 7
                if ((y==1 and (x==3 or x==4 or x==5)) or (x==5 and (y==2 or y==3))
                    or (x==1 and (y==5 or y==6)) or (y==6 and (x==2 or x==3 or x==4))):
                    color = Color["BLUE"]
                #8 11
                elif ((y==2 and (0<x<5)) or (x==1 and y==3)
                      or (x==5 and y==4) or (y==5 and (x==4 or x==5 or x==6)) or (x==6 and y==6)):
                    color = Color["GREEN"]
                # 9
                elif ((x==3 and y==3) or (y==4 and (x==2 or x==3 or x==4)) or (x==2 and y==5)):
                    color = Color["YELLOW"]
                else:
                    color = Color["RED"]
                token = (x, y, color)
                board.append(token)
        return board

    board3 = initialize_board(6,6)
    result = get_board_figures('F6',board3)
    result.append(get_board_figures('F7',board3)[0])
    result.append(get_board_figures('F8',board3)[0])
    result.append(get_board_figures('F9',board3)[0])
    result.append(get_board_figures('F11',board3)[0])
    assert result == [[(5, 1), (5, 2), (5, 3), (4, 1), (3, 1)], 
                      [(4, 6), (3, 6), (2, 6), (1, 6), (1, 5)], 
                      [(4, 2), (3, 2), (2, 2), (1, 2), (1, 3)], 
                      [(3, 4), (4, 4), (2, 4), (2, 5), (3, 3)], 
                      [(5, 5), (6, 5), (4, 5), (6, 6), (5, 4)]]


def test_figures180_13_14_15_16_18():

    def initialize_board(rows : int, cols : int):
        board = []
        for x in range(1,rows +1):
            for y in range(1,cols +1 ):
                #13 14 
                if ((y==6 and (0<x<5) or (x==2 and y==5))
                    or (y==1 and (2<x<7)) or (x==4 and y==2)):
                    color = Color["BLUE"]
                #15 18
                elif ((y==2 and (x==1 or x==2 or x==3)) or (y==3 and (x==1 or x==2))
                      or (y==3 and (x==4 or x==5)) or (y==4 and (x==4 or x==5 or x==6))):
                    color = Color["GREEN"]
                # 16
                elif ((y==4 and (x==1 or x==2 or x==3)) or (y==5 and (x==1 or x==3))):
                    color = Color["YELLOW"]
                else:
                    color = Color["RED"]
                token = (x, y, color)
                board.append(token)
        return board

    board3 = initialize_board(6,6)
    result = get_board_figures('F13',board3)
    result.append(get_board_figures('F14',board3)[0])
    result.append(get_board_figures('F15',board3)[0])
    result.append(get_board_figures('F16',board3)[0])
    result.append(get_board_figures('F18',board3)[0])
    assert result == [[(4, 6), (3, 6), (2, 6), (1, 6), (2, 5)], 
                      [(6, 1), (5, 1), (4, 1), (3, 1), (4, 2)], 
                      [(2, 2), (3, 2), (1, 2), (2, 3), (1, 3)], 
                      [(3, 4), (2, 4), (1, 4), (3, 5), (1, 5)],
                      [(5, 4), (6, 4), (4, 4), (5, 3), (4, 3)]]
    

def test_figures180_e4_e5_e7():

    def initialize_board(rows : int, cols : int):
        board = []
        for x in range(1,rows +1):
            for y in range(1,cols +1 ):
                #e4 e5 e7
                if ((y==6 and (x==4 or x==5 or x==6)) or (x==5 and y==5)
                    or (x==1 and y==1) or (y==2 and (x==1 or x==2 or x==3))
                    or (y==3 and (x==4 or x==5 or x==6)) or (x==4 and y==4)):
                    color = Color["BLUE"]
                else:
                    color = Color["RED"]
                token = (x, y, color)
                board.append(token)
        return board

    board3 = initialize_board(6,6)
    result = get_board_figures('FE4',board3)
    result.append(get_board_figures('FE5',board3)[0])
    result.append(get_board_figures('FE7',board3)[0])
    assert result == [[(5, 6), (6, 6), (4, 6), (5, 5)], 
                      [(3, 2), (2, 2), (1, 2), (1, 1)], 
                      [(6, 3), (5, 3), (4, 3), (4, 4)]]
    
# ======================= Tests 270degree rotations =======================

def test_figures270_1_2_3_4():

    def initialize_board(rows : int, cols : int):
        board = []
        for x in range(1,rows +1):
            for y in range(1,cols +1 ):
                #1 4
                if ((y==6 and (x==4 or x==5 or x==6)) or (x==5 and y==5) or (x==5 and y==4)
                    or (x==4 and (y==1 or y==2)) or (x==3 and (y==2 or y==3)) or (x==2 and y==3)):
                    color = Color["BLUE"]
                #2 3
                elif ((x==5 and (y==1 or y==2 or y==3)) or (x==4 and (y==3 or y==4))
                      or (x==1 and (y==3 or y==4)) or (x==2 and (y==4 or y==5 or y==6))):
                    color = Color["GREEN"]
                else:
                    color = Color["RED"]
                token = (x, y, color)
                board.append(token)
        return board

    board4 = initialize_board(6,6)
    result = get_board_figures('F1',board4)
    result.append(get_board_figures('F2',board4)[0])
    result.append(get_board_figures('F3',board4)[0])
    result.append(get_board_figures('F4',board4)[0])
    assert result == [[(5, 6), (6, 6), (4, 6), (5, 5), (5, 4)], 
                      [(4, 4), (4, 3), (5, 3), (5, 2), (5, 1)], 
                      [(2, 6), (2, 5), (2, 4), (1, 4), (1, 3)], 
                      [(3, 2), (3, 3), (2, 3), (4, 2), (4, 1)]]



def test_figures270_6_7_8_9_11():

    def initialize_board(rows : int, cols : int):
        board = []
        for x in range(1,rows +1):
            for y in range(1,cols +1 ):
                #6 7
                if ((x==6 and (y==3 or y==4 or y==5)) or (y==5 and (x==4 or x==5 or y==6))
                    or (x==1 and (y==1 or y==2 or y==3 or y==4)) or (x==2 and y==1)):
                    color = Color["BLUE"]
                #8 11
                elif ((y==1 and (x==4 or x==5)) or (x==5 and (y==2 or y==3 or y==4))
                      or (x==1 and y==6) or (x==2 and (y==4 or y==5 or y==6)) or (x==3 and y==5)):
                    color = Color["GREEN"]
                # 9
                elif ((y==2 and (x==2 or x==3)) or (x==3 and (y==3 or y==4)) or (x==4 and y==3)):
                    color = Color["YELLOW"]
                else:
                    color = Color["RED"]
                token = (x, y, color)
                board.append(token)
        return board

    board4 = initialize_board(6,6)
    result = get_board_figures('F6',board4)
    result.append(get_board_figures('F7',board4)[0])
    result.append(get_board_figures('F8',board4)[0])
    result.append(get_board_figures('F9',board4)[0])
    result.append(get_board_figures('F11',board4)[0])
    assert result == [[(6, 5), (5, 5), (4, 5), (6, 4), (6, 3)], 
                      [(1, 4), (1, 3), (1, 2), (1, 1), (2, 1)], 
                      [(5, 4), (5, 3), (5, 2), (5, 1), (4, 1)], 
                      [(3, 3), (3, 4), (3, 2), (2, 2), (4, 3)], 
                      [(2, 5), (2, 6), (2, 4), (1, 6), (3, 5)]]
    

def test_figures270_13_14_15_16_18():

    def initialize_board(rows : int, cols : int):
        board = []
        for x in range(1,rows +1):
            for y in range(1,cols +1 ):
                #13 14 
                if ((x==1 and (0<y<5)) or (x==2 and y==2)
                    or (x==6 and (2<y<7)) or (x==5 and y==4) or (x==1 and y==6)):
                    color = Color["BLUE"]
                #15 18
                elif ((x==4 and (y==1 or y==2)) or (x==5 and (y==1 or y==2 or y==3))
                      or (x==3 and (y==4 or y==5 or y==6)) or (x==4 and (y==4 or y==5))):
                    color = Color["GREEN"]
                # 16
                elif ((x==2 and (y==1 or y==3)) or (x==3 and (y==1 or y==2 or y==3))):
                    color = Color["YELLOW"]
                else:
                    color = Color["RED"]
                token = (x, y, color)
                board.append(token)
        return board
    
    board4 = initialize_board(6,6)
    result = get_board_figures('F13',board4)
    result.append(get_board_figures('F14',board4)[0])
    result.append(get_board_figures('F15',board4)[0])
    result.append(get_board_figures('F16',board4)[0])
    result.append(get_board_figures('F18',board4)[0])
    assert result == [[(1, 4), (1, 3), (1, 2), (1, 1), (2, 2)], 
                      [(6, 6), (6, 5), (6, 4), (6, 3), (5, 4)], 
                      [(5, 2), (5, 3), (5, 1), (4, 2), (4, 1)], 
                      [(3, 3), (3, 2), (3, 1), (2, 3), (2, 1)], 
                      [(3, 5), (3, 6), (3, 4), (4, 5), (4, 4)]]


def test_figures270_e4_e5_e7():

    def initialize_board(rows : int, cols : int):
        board = []
        for x in range(1,rows +1):
            for y in range(1,cols +1 ):
                #e4 e5 e7
                if ((x==1 and (y==4 or y==5 or y==6)) or (x==2 and y==5)
                    or (x==5 and (y==1 or y==2 or y==3)) or (x==6 and y==1)
                    or (x==3 and y==4) or (x==4 and (y==4 or y==5 or y==6))):
                    color = Color["BLUE"]
                else:
                    color = Color["RED"]
                token = (x, y, color)
                board.append(token)
        return board

    board4 = initialize_board(6,6)
    result = get_board_figures('FE4',board4)
    result.append(get_board_figures('FE5',board4)[0])
    result.append(get_board_figures('FE7',board4)[0])
    assert result == [[(1, 5), (1, 6), (1, 4), (2, 5)], 
                      [(5, 3), (5, 2), (5, 1), (6, 1)], 
                      [(4, 6), (4, 5), (4, 4), (3, 4)]]