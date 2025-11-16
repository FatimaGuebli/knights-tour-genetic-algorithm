import random
from knight import Knight
from chromosome import Chromosome
class Population:

  #init(population_size)  
    def __init__(self, population_size):
       self.population_size = population_size
       self.generation = 1
       self.knights = []
    
    # tout les cheval de population initiale 
       for i in range(population_size):
          new_knight = Knight()  #  Utilise la classe Knight
          self.knights.append(new_knight)

#check_population()
    def check_population(self):
      for knight in self.knights:
        knight.check_moves()  #  Knight.check_moves()  de classe Knight()    

#evaluate()
    def evaluate(self):
      best_fitness = 0
      best_knight = None
    
      for knight in self.knights:
          # evaluates the fitness of every individual/knight using the function evaluate_fitness()
          knight.evaluate_fitness()  #  Knight.evaluate_fitness()
        
          if knight.fitness > best_fitness:  #  Knight.fitness
              best_fitness = knight.fitness
              best_knight = knight
    
    #returne best knight with its fitness
      return best_fitness, best_knight    
    
#tournament_selection(size) 
    def tournament_selection(self, size=3):
      # Prend 'size' chevale au hasard
      participants = random.sample(self.knights, size)
    
    # Trie par fitness (best first)
      participants.sort(key=lambda knight: knight.fitness, reverse=True)  
    
    # Retourne les 2 meilleurs
      return participants[0], participants[1]    
    

#create_new_generation() 
    def create_new_generation(self):
      new_knights = []
    #create a population for the new generation
      while len(new_knights) < self.population_size:
        # choose des best parents
          parent1, parent2 = self.tournament_selection(3)
        
        # Croisement des chromosomes pour creer des fils 
          child1_chromosome = parent1.chromosome.crossover(parent2.chromosome)  #  Chromosome.crossover()
          child2_chromosome = parent2.chromosome.crossover(parent1.chromosome)  #  Chromosome.crossover()
        
        # Mutation et melange pour changer sertines genes 
          child1_chromosome.mutation()  #  Chromosome.mutation()
          child2_chromosome.mutation()  #  Chromosome.mutation()
        
        # Creer les new chevals
          child1 = Knight(child1_chromosome)  # Knight()
          child2 = Knight(child2_chromosome)  # Knight()
        
          new_knights.append(child1)
          new_knights.append(child2)
    
    # Remplace ancien population avec la nouvelle generer 
      self.knights = new_knights
      self.generation += 1    

