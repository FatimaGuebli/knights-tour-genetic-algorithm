"""Small runner to launch the interface menu.

Running this file should open a Pygame window showing a static "Main Menu" header.
Close the window manually to exit.
"""
from interface import menu
from interface.play import run_play
from population import Population




def main():
    population_size = 50
    
    # 1. Création population initiale
    population = Population(population_size)  
    
    while True:
        # 2. Vérification des mouvements
        population.check_population() 
        
        # 3. Évaluation
        max_fitness, best_knight = population.evaluate() 
        
        # 4. Condition d'arrêt
        if max_fitness == 64:
            break
        
        # 5. Nouvelle génération
        population.create_new_generation()  
    
    # 6. Affichage solution
    run_play(best_knight)  
    
if __name__ == "__main__":
    # Lance le menu principal
    menu.run_menu()

