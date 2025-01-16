from typing import List, Tuple
from enum import Enum
from core.game_logic.aux.colorValidator import validate_forbidden_color
from models import engine
from sqlalchemy.orm import sessionmaker
from models.tables import Game, gameToken
from schemas.board import BoardFigureModel, GameTokenModel

class Color(str, Enum):
    RED = "RED"
    BLUE = "BLUE"
    GREEN = "GREEN"
    YELLOW = "YELLOW"

token = Tuple[int, int, Color]


def get_color_at(board, x: int, y: int):
    for token in board:
        if token[0] == x and token[1] == y:
            return token[2]
    return None


def get_rotations(base_shape: List[Tuple[int, int]], rotations_count : int):
    rotations = [base_shape]
    
    if rotations_count == 4:
        rot_90 = [(y, -x) for (x, y) in base_shape]
        rotations.append(rot_90)

        rot_180 = [(-x, -y) for (x, y) in base_shape]
        rotations.append(rot_180)

        rot_270 = [(-y, x) for (x, y) in base_shape]
        rotations.append(rot_270)
    elif rotations_count == 2:
        rot_90 = [(y, -x) for (x, y) in base_shape]
        rotations.append(rot_90)

    return rotations

# Verificar si la figura está en el tablero a partir de una coordenada inicial
def matches_shape(board: List[token], x_start: int, y_start: int, shape: List[Tuple[int, int]], color: Color):
    
    #las coordenadas relativas a partir de x_start e y_start
    figure_positions = set((x_start + dx, y_start + dy) for (dx, dy) in shape)

    #chequear colores 
    for (dx, dy) in shape:
        x, y = x_start + dx, y_start + dy
        if not (1 <= x <= 6 and 1 <= y <= 6):
            return False
        if get_color_at(board, x, y) != color:
            return False


    #revisar bordes
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  #adyacencias a cada token
    for (dx, dy) in shape:
        x, y = x_start + dx, y_start + dy
        for dir_x, dir_y in directions:
            adj_x, adj_y = x + dir_x, y + dir_y

            if 1 <= adj_x <= 6 and 1 <= adj_y <= 6 and (adj_x, adj_y) not in figure_positions:
                adjacent_color = get_color_at(board, adj_x, adj_y)
                if adjacent_color == color:
                    return False
    
    return True


def search_figure(board: List[token], base_shape: List[Tuple[int, int]], rotations_count : int):
    res = []
    
    # Obtener todas las rotaciones posibles de la figura
    rotations = get_rotations(base_shape, rotations_count)
    
    for y in range(1, 7):
        for x in range(1, 7):
            
            color = get_color_at(board, x, y)
            
            # Para cada rotación
            for shape in rotations:
                if matches_shape(board, x, y, shape, color):
                    
                    coords = [(x+dx , y+dy) for (dx, dy) in shape]
                    res.append(coords)
    
    return res



def get_board_figures(type : str, board : List[token]):
    result = []
    match type:
        case 'F1':
            fig1 = [(0, 0), (0, 1), (0, -1), (1, 0), (2, 0)]
            result = search_figure(board, fig1,4)
        case 'F2':
            fig2 = [(0,0),(1,0),(1,1),(2,1),(3,1)]
            result = search_figure(board, fig2,4)
        case 'F3':
            fig3 = [(0,0),(1,0),(2,0),(2,-1),(3,-1)]
            result = search_figure(board, fig3,4)
        case 'F4':
            fig4 = [(0,0),(-1,0),(-1,-1),(0,1),(1,1)]
            result = search_figure(board, fig4,4)
        case 'F5':
            fig5 = [(0,0),(1,0),(2,0),(3,0),(4,0)]
            result = search_figure(board, fig5,2)
        case 'F6':
            fig6 = [(0,0),(0,-1),(0,-2),(1,0),(2,0)]
            result = search_figure(board, fig6,4)
        case 'F7':
            fig7 =[(0,0),(1,0),(2,0),(3,0),(3,1)]
            result = search_figure(board, fig7,4)
        case 'F8':
            fig8 = [(0,0),(1,0),(2,0),(3,0),(3,-1)]
            result = search_figure(board, fig8,4)
        case 'F9':
            fig9 = [(0,0),(-1,0),(1,0),(1,-1),(0,1)]
            result = search_figure(board, fig9,4)
        case 'F10':
            fig10 = [(0,0),(-1,0),(1,0),(-1,1),(1,-1)]
            result = search_figure(board, fig10,2)
        case 'F11':
            fig11 = [(0,0),(-1,0),(1,0),(-1,-1),(0,1)]
            result = search_figure(board, fig11,4)
        case 'F12':
            fig12 = [(0,0),(-1,0),(1,0),(-1,-1),(1,1)]
            result = search_figure(board, fig12,2)
        case 'F13':
            fig13 = [(0,0),(1,0),(2,0),(3,0),(2,1)]
            result = search_figure(board, fig13,4)
        case 'F14':
            fig14 = [(0,0),(1,0),(2,0),(3,0),(2,-1)]
            result = search_figure(board, fig14,4)
        case 'F15':
            fig15 = [(0,0),(-1,0),(1,0),(0,-1),(1,-1)]
            result = search_figure(board, fig15,4)
        case 'F16':
            fig16 = [(0,0),(1,0),(2,0),(0,-1),(2,-1)]
            result = search_figure(board, fig16,4)
        case 'F17':
            fig17 = [(0,0),(-1,0),(1,0),(0,-1),(0,1)]
            result = search_figure(board, fig17,1)
        case 'F18':
            fig18 = [(0,0),(-1,0),(1,0),(0,1),(1,1)]
            result = search_figure(board, fig18,4)
        case 'FE1':
            fige1 = [(0,0),(0,1),(-1,1),(1,0)]
            result = search_figure(board,fige1,2)
        case 'FE2':
            fige2 = [(0,0),(0,-1),(1,0),(1,-1)]
            result = search_figure(board,fige2,1)
        case 'FE3':
            fige3 = [(0,0),(-1,0),(0,1),(1,1)]
            result = search_figure(board,fige3,2)
        case 'FE4':
            fige4 = [(0,0),(-1,0),(1,0),(0,1)]
            result = search_figure(board,fige4,4)
        case 'FE5':
            fige5 = [(0,0),(1,0),(2,0),(2,1)]
            result = search_figure(board,fige5,4)
        case 'FE6':
            fige6 = [(0,0),(1,0),(2,0),(3,0)]
            result = search_figure(board,fige6,2)
        case 'FE7':
            fige7 = [(0,0),(1,0),(2,0),(2,-1)]
            result = search_figure(board,fige7,4)
    return result


Session = sessionmaker(bind=engine)

def get_figures(game_id: int, coords: List[List[Tuple[int, int]]], session):
    tokens =  []
    for figure in coords:
        tokens_figure = []
        for coord_token in figure:
            token = session.query(gameToken).filter_by(game_id=game_id, x_coordinate = coord_token[0], y_coordinate = coord_token[1]).first()
            if token and validate_forbidden_color(game_id, token.id, session):
                tokens_figure.append(token)

        if len(tokens_figure) > 0:
            tokens.append([GameTokenModel.from_db(token) for token in tokens_figure])

    return tokens



    





