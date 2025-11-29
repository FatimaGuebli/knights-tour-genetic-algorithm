import time

# mouvements valides du cavalier
def successor_fct(x, y, visited):
    moves = [
        (x+2, y+1), (x+2, y-1),
        (x-2, y+1), (x-2, y-1),
        (x+1, y+2), (x+1, y-2),
        (x-1, y+2), (x-1, y-2)
    ]

    valid = []
    for nx, ny in moves:
        if 0 <= nx < 8 and 0 <= ny < 8:
            if (nx, ny) not in visited:
                valid.append((nx, ny))
    return valid



def MRV(successors, visited):
    return sorted(
        successors,
        key=lambda pos: len(successor_fct(pos[0], pos[1], visited))
    )



# Trie les successors par ceux qui gênent le moins le futur

def LCV(successors, visited):
    def constraining_value(pos):
        x, y = pos
        future_moves = successor_fct(x, y, visited)
        return len(future_moves)
    
    return sorted(successors, key=constraining_value)



def backtracking(assignment):
    
    if len(assignment) == 64:
        return assignment

    current_x, current_y = assignment[-1]
    visited = set(assignment)

    # Successors respectant les contraintes
    successors = successor_fct(current_x, current_y, visited)

    # MRV
    successors = MRV(successors, visited)
    # LCV
    successors = LCV(successors, visited)

    # Parcours des successors
    for x, y in successors:
        assignment.append((x, y))
        result = backtracking(assignment)
        if result is not None:
            return result
        assignment.pop()

    return None



# main juste pour le tester apres sera remplacer dans l'interface 
start = time.time()

assignment = [(0, 0)]
solution = backtracking(assignment)

end = time.time()

print("Solution trouvée :", solution)
print("Temps d'exécution :", end - start, "secondes")
