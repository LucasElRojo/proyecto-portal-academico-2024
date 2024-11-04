def score_grade(score):
    if score >= 6.0:
        return "Sobresaliente"
    elif score >= 5.0:
        return "Bueno"
    elif score >= 4.0:
        return "Aprobado"
    else:
        return "Insuficiente"