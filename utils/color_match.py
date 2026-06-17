COLOR_RULES = {
    "White": ["Any Color"],
    "Black": ["Any Color"],
    "Blue": ["White", "Black", "Gray", "Beige"],
    "Red": ["Black", "White", "Gray", "Navy"],
    "Green": ["White", "Black", "Beige", "Brown"],
    "Yellow": ["White", "Blue", "Black", "Gray"],
    "Pink": ["White", "Gray", "Black", "Navy"],
    "Purple": ["White", "Black", "Gray", "Pink"],
    "Gray": ["White", "Black", "Navy", "Red"],
    "Brown": ["White", "Beige", "Blue", "Green"],
    "Navy": ["White", "Gray", "Beige", "Red"],
    "Beige": ["White", "Brown", "Navy", "Black"],
    "Orange": ["White", "Black", "Navy", "Gray"],
}


def get_compatible_colors(color):
    matches = COLOR_RULES.get(color, ["White", "Black"])
    if matches == ["Any Color"]:
        return list(COLOR_RULES.keys())
    return matches
