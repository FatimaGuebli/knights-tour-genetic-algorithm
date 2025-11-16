import random

class Chromosome:
    def __init__(self, genes=None, length=63):
        self.length = length
        
        if genes is None:
            self.genes = [random.randint(1, 8) for _ in range(length)]
        else:
            self.genes = genes
        
    def crossover(self, partner):
        # Un point de coupure entre 1 et length-1
        point = random.randint(1, self.length - 1)

        # Gènes de l'enfant
        child_genes = self.genes[:point] + partner.genes[point:]

        return Chromosome(child_genes)

    def mutation(self, mutation_rate=0.01):
        # Probabilité de muter chaque gène
        for i in range(self.length):
            if random.random() < mutation_rate:
                self.genes[i] = random.randint(1, 8)

"""test =Chromosome()
print(test.genes)"""
