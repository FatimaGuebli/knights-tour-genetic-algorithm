import time


#  les mouvements valides du cavalier

def successor_fct(x, y, visited):
    moves = [
        (x+2, y+1), (x+2, y-1),
        (x-2, y+1), (x-2, y-1),
        (x+1, y+2), (x+1, y-2),
        (x-1, y+2), (x-1, y-2)
    ]

    valid_moves = []
    for nx, ny in moves:
        # vérifier les limites du plateau
        if 0 <= nx < 8 and 0 <= ny < 8:
            # vérifier qu'on n'a pas encore visité cette case
            if (nx, ny) not in visited:
                valid_moves.append((nx, ny))

    return valid_moves
  
     

# Backtracking simple

def backtracking(assignment):
    # Si on a parcourer les 64 donc retourn la solution trouver
    if len(assignment) == 64:
        return assignment

    # Position actuelle du cavalier
    current_x, current_y = assignment[-1]
    visited = set(assignment)

    # tous les successors valides
    successors = successor_fct(current_x, current_y, visited)

    # Essayer chaque successor
    for x, y in successors:
        assignment.append((x, y))
        result = backtracking(assignment)
        if result is not None:
            return result
        assignment.pop()  # backtrack

    return None



#main juste pour le tester apres sera remplacer dans l'interface 
start = time.time()

assignment = [(8,8)]
solution = backtracking(assignment)

end = time.time()

print("Solution trouvée :", solution)
print("Temps d'exécution :", end - start, "secondes")
