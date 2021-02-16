import interpreter

def scoreFromList(list):
    return list[1]

def leaderboard(player_data, equation):
    scores = []
    for person in player_data:
        score = round(float(interpreter.interpret(player_data[person], equation)), 2)
        scores.append([person, score])
    scores = sorted(scores, key=scoreFromList, reverse=True)
    return scores
