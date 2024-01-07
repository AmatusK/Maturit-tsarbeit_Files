import tkinter as tk
import time
import random
import matplotlib.pyplot as plt



areax=1000
areay=1000
border=20

inflist = []
reclist = []
suslist = []
infcount = 0
reccount = 0
suscount = 0

def open_simul_window():
    global window, area
    #
    # Initilize window
    #
    window = tk.Tk()
    window.title("Simulation Window")         # set window title
    window.resizable(False, False)            # set window non-resizeable
    window.geometry("+1000+200")              # set window 1000,200 from screen border (otherwise it would glue at the top left)

    area = tk.Canvas(window, width=areax+2*border, height=areay+2*border, bg='white', borderwidth=0, highlightthickness=0)
    area.pack(fill="both", expand=True)

    window.update()



radius = 5

def draw_circle(x, y, color):
    area.create_oval(x-radius+border, areay+2*border-(y-radius+border), x+radius+border, areay+2*border-(y+radius+border), fill=color)

def draw_graph():

    plt.figure(figsize=(10, 10))
    plt.xlim([0, 80])
    plt.title("SIR Modell")
    plt.xlabel("Krankheitsverlauf in Schritten")
    plt.ylabel("Verhältniss")
    plt.legend(loc="upper right")

    plt.show(block = False)



# Our person simulation object

recovery_time = 1           # 1 days 
simulation_step = 1.0/24/30 # 2min 
chance = 30 #mind that this is the chance of Infection
class Person:


    def __init__(self):
        self.x = float(random.randint(1,areax+1))
        self.y = float(random.randint(1,areay+1))
        self.health = 'susceptible'
        self.ill_counter = 0

        self.vx = (float(random.randint(1,10))-5)/5
        self.vy = (float(random.randint(1,10))-5)/5

    def draw(self):

        global suscount,infcount,reccount

        if self.health == 'susceptible':
            draw_circle(self.x, self.y, 'blue')
            suscount += 1
        if self.health == 'maybe':
            draw_circle(self.x, self.y, 'blue')
            suscount += 1
        elif self.health == 'infected':
            draw_circle(self.x, self.y, 'red')
            infcount += 1
        elif self.health == 'immune':
            draw_circle(self.x, self.y, 'green')
            reccount += 1
        elif self.health == 'dead':
            draw_circle(self.x, self.y, 'black')

    def Update_Graph(self):
        global infcount,suscount,reccount,inflist,reclist,suslist

        inflist.append(infcount)
        reclist.append(reccount)
        suslist.append(suscount)

        plt.plot(suslist, label="Anfällige Menschen", color="blue")
        plt.plot(inflist, label="Infizierte Menschen", color="red")
        plt.plot(reclist, label ="Immun/Verstorbene Menschen", color="springgreen")

        plt.xlim(0, len(inflist)+80)
        if random.randint(1,50) == 2:
            plt.draw()

    def move(self):
        self.x += self.vx
        if self.x < 1 or self.x > areax:
            self.vx = -self.vx

        self.y += self.vy
        if self.y < 1 or self.y > areay:
            self.vy = -self.vy

    def is_touching_person(self, person):
        distance_squared = (person.x - self.x)**2 + (person.y - self.y)**2
        radius_sum_squared = (2 * radius)**2 
        
        if distance_squared <= radius_sum_squared:
            return 1
        return None
    
    def infect(self):
        if self.health == "infected":
            for person in persons:
                if person != self:
                    if self.is_touching_person(person) == 1 and person.health == "susceptible":
                        person.health = 'maybe'
                        
        if self.health == 'infected':
            self.ill_counter = self.ill_counter+1
            if self.ill_counter >= recovery_time/simulation_step:
                self.health = 'immune'
        
        if self.health == 'maybe':
            touching_anyone = any(self.is_touching_person(person) for person in persons if person != self)
            if not touching_anyone:
                if random.randint(1, 100) <= chance:
                    self.health = 'infected'
                    self.ill_counter = 0
                else:
                    self.health = "susceptible"


# Generate Persons

persons = [Person() for x in range(250)]
persons[0].health = 'infected'

open_simul_window()
draw_graph()
while __name__ == "__main__":
    # Simulate Persons
    for person in persons:
        person.move()
    for person in persons:
        person.infect()

    # Draw Persons
    area.delete("all")
    suscount,infcount,reccount = 0,0,0
    for person in persons:
        person.draw()
    window.update()
    person.Update_Graph()
