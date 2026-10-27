"""Paleta do Tiaraju — tons de entardecer missioneiro (arenito, pampa, céu de fim de tarde)."""
from pixelart import rgba

HEX = {
    "outline": "#0f0c14",
    # pele / cabelo
    "hair": "#1c1826", "hair2": "#3a3148",
    "skin_d": "#7a4a2e", "skin": "#a0633a", "skin_l": "#c48a5a",
    "brown_hair": "#4a2e1e",
    # tecidos
    "white": "#f2e9d8", "white_s": "#cfc3ad", "white_d": "#9c8f7c",
    "red": "#b02a2a", "red_l": "#e04545", "red_d": "#701a22",
    "blue": "#243a6b", "blue_l": "#3a5aa0", "blue_ll": "#6b86c8", "blue_d": "#15224a",
    "black": "#15131a", "grey": "#3b3844",
    # materiais
    "wood": "#6b4632", "wood_l": "#8a5a3c", "wood_d": "#4a2f22",
    "steel": "#c9d2da", "steel_d": "#8d99a6", "steel_dd": "#5a6673",
    "gold": "#d8a73a", "gold_l": "#f2cf6b",
    # arenito das Missões
    "stone_dd": "#5e2a22", "stone_d": "#8c3f2e", "stone": "#b3573b", "stone_l": "#d9825a", "stone_ll": "#f0b48a",
    # pampa
    "grass_d": "#3f5a2c", "grass": "#6a8a3a", "grass_l": "#9ab04c", "grass_dry": "#c9b85a",
    "dirt_d": "#3a2419", "dirt": "#4a2f22", "dirt_l": "#6b4632", "dirt_ll": "#8a5a3c",
    "leaf_d": "#1f3326", "leaf": "#2f4d33", "leaf_l": "#4b6e3f",
    # fogo / luz
    "fire_y": "#ffdf6b", "fire_o": "#ff9a2e", "fire_r": "#e8432e",
    "cream": "#f4ecd6", "moon_s": "#d9ccb0", "star_dim": "#8c8aa6",
    # céu do entardecer
    "sky0": "#120d26", "sky1": "#2a1a45", "sky2": "#5c2a52", "sky3": "#a33a4a",
    "sky4": "#e0663a", "sky5": "#f2a94f", "sky6": "#f7d58a",
    # camadas de fundo (dessaturadas pela distância)
    "hill_far": "#3b2a56", "hill_far2": "#2a1a3f", "hill_near": "#1d1430",
    "ruin_d": "#4a2630", "ruin": "#6a3838", "ruin_l": "#8a4c40", "ruin_ll": "#a8634a",
    "tree_d": "#17221f", "tree": "#223328", "tree_l": "#2d4530",
    "fg": "#0b100d", "fg_l": "#132018",
}

P = {k: rgba(v) for k, v in HEX.items()}
