def get_recommendation(weather_condition, temp, occasion=None):
    suggestions = []

    if weather_condition and "rain" in weather_condition.lower():
        suggestions.extend(["Jacket", "Dark Pants", "Boots"])

    if weather_condition and "snow" in weather_condition.lower():
        suggestions.extend(["Heavy Jacket", "Thermal", "Boots", "Gloves"])

    if temp is not None:
        if temp > 30:
            suggestions.extend(["Cotton T-Shirt", "Shorts", "Sandals"])
        elif temp > 25:
            suggestions.extend(["T-Shirt", "Light Pants", "Sneakers"])
        elif temp < 15:
            suggestions.extend(["Jacket", "Sweater", "Closed Shoes"])
        elif temp < 5:
            suggestions.extend(["Heavy Coat", "Thermal Layer", "Boots"])

    if occasion:
        occasion_map = {
            "Interview": ["White Shirt", "Black Pants", "Formal Shoes"],
            "Formal": ["Shirt", "Trousers", "Formal Shoes"],
            "Casual": ["T-Shirt", "Jeans", "Sneakers"],
            "Party": ["Stylish Top", "Dark Jeans", "Boots"],
            "Sports": ["T-Shirt", "Shorts", "Running Shoes"],
        }
        suggestions.extend(occasion_map.get(occasion, []))

    return list(dict.fromkeys(suggestions))
