import random
from chromosome import Chromosome

moves = {
        1: (1, 2),
        2: (2, 1),
        3: (2, -1),
        4: (1, -2),
        5: (-1, -2),
        6: (-2, -1),
        7: (-2, 1),
        8: (-1, 2),
    }
class Knight:
    

    def __init__(self, chromosome=None):
        self.chromosome=chromosome if chromosome else Chromosome()
        self.position=(0,0)
        self.fitness=0
        self.path=[self.position]
        

    def move_forward(self, direction):
      changement_X,changement_Y=moves[direction]
      x,y=self.position
      self.position=(x+changement_X,y+changement_Y)
      return  self.position
      

    def move_backward(self, direction):
        changement_X,changement_Y=moves[direction]
        x,y=self.position
        self.position=(x-changement_X,y-changement_Y)
        return  self.position

    def check_moves(self):
        
        cycle_dir = random.choice([1, -1])

        for i in range(len(self.chromosome.genes)):
            move = self.chromosome.genes[i]

            # Essayer mouvement initial
            self.move_forward(move)

            if not self.is_valid(self.position):
                # annuler
                self.move_backward(move)

                found_valid = False

                # essayer les 7 autres mouvements
                for k in range(1, 8):
                    next_move = ((move - 1 + cycle_dir * k) % 8) + 1
                    self.move_forward(next_move)

                    if self.is_valid(self.position):
                        self.chromosome.genes[i] = next_move
                        found_valid = True
                        break
                    else:
                        self.move_backward(next_move)

                # Dans tous les cas, ajouter la position finale
                # (que le mouvement soit valide ou non)
                self.path.append(self.position)

            else:
                # mouvement initial valide
                self.path.append(self.position)

     

    def is_valid(self, pos):
       x,y =pos 
       in_board = 0 <= x < 8 and 0 <= y < 8
       not_visited = pos not in self.path
       return in_board and not_visited

    def evaluate_fitness(self):
        visited = set()
        self.fitness = 0

        for pos in self.path:
            x, y = pos
            
            # Si la position est en dehors du plateau
            if not (0 <= x < 8 and 0 <= y < 8):
                break
            
            # Si la position a déjà été visitée avant
            if pos in visited:
                break
            
            visited.add(pos)
            self.fitness += 1

            # Si toutes les cases sont visitées
            if self.fitness == 64:
                break

        return self.fitness

