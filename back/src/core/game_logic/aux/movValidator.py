from schemas.card import MoveType

def is_valid_mov(type : MoveType, coords1 : tuple[int,int], coords2 : tuple[int,int]):
    
    #(x1,y1) siempre es la menor coordenada en terminos de x y luego de y
    if coords1[0] < coords2[0]:
        x1 = coords1[0]
        y1 = coords1[1]

        x2 = coords2[0]
        y2 = coords2[1]
    elif coords1[0] == coords2[0]:
        x1 = coords1[0]
        y1 = min(coords1[1],coords2[1])

        y2 = max(coords1[1],coords2[1])
        x2 = coords1[0]
            
    else:
        x1 = coords2[0]
        y1 = coords2[1]

        x2 = coords1[0]
        y2 = coords1[1]

    match type:
        case "NO_SKIP_LINE":
            return check_no_skip_line(x1,x2,y1,y2)

        case "SKIP_ONE_LINE":
            return check_skip_one_line(x1,x2,y1,y2)

        case "SHORT_DIAG":
            return check_short_diag(x1,x2,y1,y2)

        case "LONG_DIAG":
            return check_long_diag(x1,x2,y1,y2)

        case "NORMAL_L":
            return check_normal_l(x1,x2,y1,y2)

        case "INVERSED_L":
            return check_inversed_l(x1,x2,y1,y2)

        case "SKIP_THREE_LINES":
            return check_skip_three_lines(x1,x2,y1,y2)


def check_no_skip_line(x1 : int, x2 : int, y1 : int, y2 : int):

    #si estan en la misma fila
    if y1 == y2:
        return (x2-x1 == 1)
    #si estan en la misma columna
    elif x1 == x2:
        return (y2-y1 == 1)
    else:
        return False


def check_skip_one_line(x1 : int, x2 : int, y1 : int, y2 : int):

    if y1 == y2:
        return (x2-x1 == 2)
    elif x1 == x2:
        return (y2-y1 == 2)
    else:
        return False

def check_short_diag(x1 : int, x2 : int, y1 : int, y2 : int):

    if x2-x1 == 1:
        return (max(y1,y2)-min(y1,y2) == 1)
    else:
        return False


def check_long_diag(x1 : int, x2 : int, y1 : int, y2 : int):

    if x2-x1 == 2:
        return (max(y1,y2)-min(y1,y2) == 2)
    else:
        return False

def check_normal_l(x1 : int, x2 : int, y1 : int, y2 : int):

    #si la distancia en x es de 2, la coord de la izquierda(y1) debe estar uno mas abajo
    if x2-x1 == 2:
        return (y1-y2 == 1)
    #si la distancia en x es de 1, la coord de la izquierda(y1) debe estar 2 mas arriba
    elif x2-x1 == 1:
        return (y2-y1 == 2)
    else:
        return False

def check_inversed_l(x1 : int, x2 : int, y1 : int, y2 : int):

    #si la distancia en x es de 2, la coord de la izquierda(y1) debe estar uno mas arriba
    if x2-x1 == 2:
        return(y2-y1 == 1)
    #si la distancia en x es de 1, la coord de la izquierda(y1) debe estar 2 mas abajo
    elif x2-x1 == 1:
        return(y1-y2 == 2)
    else:
        return False

def check_skip_three_lines(x1 : int, x2 : int, y1 : int, y2 : int):

    if y1 == y2 and x1 != x2:
        return(x1 == 1 or x2 == 6)
    if x1 == x2 and y1 !=y2:
        return(y1 == 1 or y2 == 6)
    else:
        return False

'''
(1,1) (2,1) (3,1) (4,1) (5,1) (6,1)
(1,2) (2,2) (3,2) (4,2) (5,2) (6,2)
(1,3) (2,3) (3,3) (4,3) (5,3) (6,3)
(1,4) (2,4) (3,4) (4,4) (5,4) (6,4)
(1,5) (2,5) (3,5) (4,5) (5,5) (6,5)
(1,6) (2,6) (3,6) (4,6) (5,6) (6,6)
'''




