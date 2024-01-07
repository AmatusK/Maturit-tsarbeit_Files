# This program was written and tested with python 3.10

import random                            # Library used for random numbers
from datetime import datetime            # Library to access date/time
import sys                               # Library to access command line parameters

from numpy import random as numpyrandom  # Library used for random choice (numpy 1.23.5)
import matplotlib.pyplot as plt          # Library for graphics/plotting (matplotlib 3.7.1)
import osmnx as ox                       # Library to access OSM/OpenStreetMap for map data (osmnx 1.7.1)
import geopandas as gpd                  # Library to work with map data (geopandas 0.14.0)
import networkx as nx                    # Library to work with graph data, e.g. street network in maps (networkx 3.1)


# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
#c:/Users/amatus/ProgrammingProjects/Matur/venv/scripts/activate.ps1

# Key simulation parameters

simulation_length = 35 # In weeks
population_count = 50000
generate_maps = True


def weekday(day):
    return day in {'Mon', 'Tue', 'Wed', 'Thu', 'Fri'}

def weekend(day):
    return day in {'Sat', 'Sun'}

def time_to_quarter(time):
    return int(time[0:2])*4+int(time[3:5])//15

def quarter_to_time(quarter):
    hour = quarter // 4
    min = (quarter % 4) * 15
    return f'{hour:02}:{min:02}'


def subset(n,m): # Selects n out of m numbers
    set = [i for i in range(m)]
    selection = []
    for _ in range(n):
        item = random.choice(set)
        selection.append(item)
        set.remove(item)
    return selection


person_number =1

class Person:
    
    def __init__(self, person_type):
        global person_number
        global lastnames
        global residential, schools, residential_coords, school_coords

        self.type = person_type
        
        self.pers_number = person_number

        self.lastname = 'n/a'
        self.firstname = 'n/a'

        self.health = 'healthy'
        self.days_ill = 0
        self.infection_location = 'none'
        self.quarantine = 'no'

        if random.randint(1,100) <= simul_options['vaccination']:
            self.vaccinated = 'yes'
        else:
            self.vaccinated = 'no'
        
        
        self.home = random.randint(0,home_count-1)
        #print(self.home)
        self.home_x = residential_coords[homes[self.home]][0]
        self.home_y = residential_coords[homes[self.home]][1]
        #print(self.home_x,self.home_y)
        #self.address = residential['addr:street'][self.home] + ' ' + residential['addr:housenumber'][self.home] + ', PLZ ' + str(residential['addr:postcode'][self.home])
        
        self.hobby = hobbies[random.randint(0,hobby_count-1)]
        
        person_number +=1
        if person_number%1000 == 0:
            print(f'Population generation: {person_number:7d} done')
        
        match person_type:
            case "Infant":
                self.age = random.randint(0,5)
            case "Pupil":
                self.age = random.randint(6,18)

                # Assign to nearest school
                nearest_school = -1
                distance = 10000000000000000
                for school_nr in range(school_count):
                    d = (school_coords[schools[school_nr]][0]-self.home_x)**2+(school_coords[schools[school_nr]][1]-self.home_y)**2
                    if d < distance:
                        nearest_school=school_nr
                        distance = d
                self.school = nearest_school
                if nearest_school==-1:
                    print("Error: Missing school assignment")

                self.school_travel = random.randint(1,3)
                self.school_start = {}
                self.school_end = {}
                for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']:
                    self.school_start[day] = time_to_quarter(numpyrandom.choice(["07:30", "08:30", "09:15"], p=[0.333, 0.334, 0.333]))
                    self.school_end[day] = time_to_quarter(numpyrandom.choice(["14:30", "15:30", "16:15"], p=[0.333, 0.334, 0.333]))

            case "Student":
                self.age = random.randint(19,25)

                self.uni = unis[random.randint(0,uni_count-1)]

                self.uni_travel = random.randint(1,3)
                self.uni_start = {}
                self.uni_end = {}
                for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']:
                    self.uni_start[day] = time_to_quarter(numpyrandom.choice(["09:30", "10:30", "11:15"], p=[0.333, 0.334, 0.333]))
                    self.uni_end[day] = time_to_quarter(numpyrandom.choice(["15:30", "16:30", "17:15"], p=[0.333, 0.334, 0.333]))

            case "Working adult":
                self.age = random.randint(18,64)

                self.workplace = workplaces[random.randint(0,workplaces_count-1)]

                self.work_travel = random.randint(2,4)
                self.work_start = {}
                self.work_end = {}
                for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']:
                    self.work_start[day] = time_to_quarter(numpyrandom.choice(["07:30", "07:45", "08:00", "08:15","08:30", "08:45", "09:00", "09:15",], p=[0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125]))
                    self.work_end[day] = time_to_quarter(numpyrandom.choice(["16:00", "16:15", "16:30", "16:45","17:00", "17:15", "17:30", "17:45",], p=[0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125]))

                
                if random.randint(1,100) <= simul_options['home office']:
                    self.homeoffice = 'yes'
                else:
                    self.homeoffice = 'no'

            case "Non-working adult":
                self.age = random.randint(18,64)
            case "Pensioner":
                self.age = random.randint(65,85)

        self.daycount = 0
        self.days = []

    def print_person(self):
        print("---------------------------------------------------------")
        print("Person number: " + str(self.pers_number))
        print("Name: " + self.firstname + ' ' + self.lastname)
        print("Type: "+ self.type)
        print("Age: " + str(self.age))
        print("Health: " + self.health)
        print("Vaccinated: " + self.vaccinated)
    
    def generate_day(self, day):

        activities = []
        activities.append(day)
        match self.type:
            case "Infant":
                activities.append(["00:00","home", self.home])
                activities.append(["24:00","end"])

            case "Pupil":
                activities.append(["00:00","home", self.home])
                if weekday(day):
                    school_start = self.school_start[day]
                    school_travel_time = self.school_travel
                    travel_to_school = school_start - school_travel_time
                    leave_school = self.school_end[day]
                    
                    activities.append([quarter_to_time(travel_to_school),"travel school"])
                    activities.append([quarter_to_time(school_start),"school", self.school])
                    activities.append(["12:00","school restaurant", self.school])
                    activities.append(["13:45","school", self.school])
                    if random.randint(0,3) != 0:
                        activities.append([quarter_to_time(leave_school),"travel school"])
                        activities.append([quarter_to_time(leave_school+school_travel_time),"home", self.home])
                    else:
                        travel_time = random.randint(1,2)
                        back_at_home = time_to_quarter(numpyrandom.choice(["18:00", "18:15", "18:30", "18:45", "19:00", "19:15", "19:30", "19:45", "20:00", "20:15"], p=[0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]))
                        activities.append([quarter_to_time(leave_school),"travel hobby"])
                        activities.append([quarter_to_time(leave_school+travel_time),"hobby", self.hobby])
                        activities.append([quarter_to_time(back_at_home-travel_time),"travel hobby"])
                        activities.append([quarter_to_time(back_at_home),"home", self.home])                
                else:
                    if random.randint(0,1) != 0:
                        start = time_to_quarter("09:00")+random.randint(0,12)
                        travel = random.randint(0,2)
                        at_event = start+travel
                        end_event = at_event+random.randint(4,24)
                        at_home = end_event+travel
                        activities.append([quarter_to_time(start),"travel hobby"])
                        activities.append([quarter_to_time(at_event),"hobby", self.hobby])
                        activities.append([quarter_to_time(end_event),"travel hobby"])
                        activities.append([quarter_to_time(at_home),"home", self.home])
                activities.append(["24:00","end"])
        
            case "Student":
                activities.append(["00:00","home", self.home])
                if weekday(day):
                    uni_start = self.uni_start[day]
                    uni_travel_time = self.uni_travel
                    travel_to_uni = uni_start - uni_travel_time
                    leave_uni = self.uni_end[day]
                    
                    activities.append([quarter_to_time(travel_to_uni),"travel uni"])
                    activities.append([quarter_to_time(uni_start),"uni", self.uni])
                    activities.append(["12:00","uni restaurant", self.uni])
                    activities.append(["13:45","uni", self.uni])
                    if random.randint(0,3) != 0:
                        activities.append([quarter_to_time(leave_uni),"travel uni"])
                        activities.append([quarter_to_time(leave_uni+uni_travel_time),"home", self.home])
                    else:
                        travel_time = random.randint(1,2)
                        back_at_home = time_to_quarter(numpyrandom.choice(["18:00", "18:15", "18:30", "18:45", "19:00", "19:15", "19:30", "19:45", "20:00", "20:15"], p=[0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]))
                        match numpyrandom.choice(["hobby", "shop", "restaurant"], p=[0.25, 0.5, 0.25]):
                            case "hobby":
                                activities.append([quarter_to_time(leave_uni),"travel hobby"])
                                activities.append([quarter_to_time(leave_uni+travel_time),"hobby", self.hobby])
                                activities.append([quarter_to_time(back_at_home-travel_time),"travel hobby"])
                            case "shop":
                                activities.append([quarter_to_time(leave_uni),"travel shop"])
                                activities.append([quarter_to_time(leave_uni+travel_time),"shop", shops[random.randint(0,shop_count-1)]])
                                activities.append([quarter_to_time(back_at_home-travel_time),"travel shop"])
                            case "restaurant":
                                activities.append([quarter_to_time(leave_uni),"travel restaurant"])
                                activities.append([quarter_to_time(leave_uni+travel_time),"restaurant", restaurants[random.randint(0,restaurant_count-1)]])
                                activities.append([quarter_to_time(back_at_home-travel_time),"travel restaurant"])
                        activities.append([quarter_to_time(back_at_home),"home", self.home])                
                else:
                    if random.randint(0,1) != 0:
                        start = time_to_quarter("09:00")+random.randint(0,12)
                        travel = random.randint(0,2)
                        at_event = start+travel
                        end_event = at_event+random.randint(4,24)
                        at_home = end_event+travel
                        match numpyrandom.choice(["hobby", "restaurant"], p=[0.5, 0.5]):
                            case "hobby":
                                activities.append([quarter_to_time(start),"travel hobby"])
                                activities.append([quarter_to_time(at_event),"hobby", self.hobby])
                                activities.append([quarter_to_time(end_event),"travel hobby"])
                            case "restaurant":
                                activities.append([quarter_to_time(start),"travel restaurant"])
                                activities.append([quarter_to_time(at_event),"restaurant", restaurants[random.randint(0,restaurant_count-1)]])
                                activities.append([quarter_to_time(end_event),"travel restaurant"])
                        activities.append([quarter_to_time(at_home),"home", self.home])
                activities.append(["24:00","end"])
            
            case "Working adult":
                activities.append(["00:00","home", self.home])
                if weekday(day):
                    work_start = self.work_start[day]
                    work_travel_time = self.work_travel
                    travel_to_work = work_start - work_travel_time
                    leave_work = self.work_end[day]
                    
                    activities.append([quarter_to_time(travel_to_work),"travel work"])
                    activities.append([quarter_to_time(work_start),"work", self.workplace])
                    activities.append(["12:00","restaurant", restaurants[random.randint(0,restaurant_count-1)]])
                    activities.append(["13:30","work", self.workplace])
                    if random.randint(0,3) != 0:
                        activities.append([quarter_to_time(leave_work),"travel work"])
                        activities.append([quarter_to_time(leave_work+work_travel_time),"home", self.home])
                    else:
                        travel_time = random.randint(1,2)
                        back_at_home = time_to_quarter(numpyrandom.choice(["18:00", "18:15", "18:30", "18:45", "19:00", "19:15", "19:30", "19:45", "20:00", "20:15"], p=[0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]))
                        match numpyrandom.choice(["hobby", "shop", "restaurant"], p=[0.25, 0.5, 0.25]):
                            case "hobby":
                                activities.append([quarter_to_time(leave_work),"travel hobby"])
                                activities.append([quarter_to_time(leave_work+travel_time),"hobby", self.hobby])
                                activities.append([quarter_to_time(back_at_home-travel_time),"travel hobby"])
                            case "shop":
                                activities.append([quarter_to_time(leave_work),"travel shop"])
                                activities.append([quarter_to_time(leave_work+travel_time),"shop", shops[random.randint(0,shop_count-1)]])
                                activities.append([quarter_to_time(back_at_home-travel_time),"travel shop"])
                            case "restaurant":
                                activities.append([quarter_to_time(leave_work),"travel restaurant"])
                                activities.append([quarter_to_time(leave_work+travel_time),"restaurant", restaurants[random.randint(0,restaurant_count-1)]])
                                activities.append([quarter_to_time(back_at_home-travel_time),"travel restaurant"])
                        activities.append([quarter_to_time(back_at_home),"home", self.home])                
                else:
                    if random.randint(0,1) != 0:
                        start = time_to_quarter("09:00")+random.randint(0,12)
                        travel = random.randint(0,2)
                        at_event = start+travel
                        end_event = at_event+random.randint(4,24)
                        at_home = end_event+travel
                        match numpyrandom.choice(["hobby", "restaurant"], p=[0.5, 0.5]):
                            case "hobby":
                                activities.append([quarter_to_time(start),"travel hobby"])
                                activities.append([quarter_to_time(at_event),"hobby", self.hobby])
                                activities.append([quarter_to_time(end_event),"travel hobby"])
                            case "restaurant":
                                activities.append([quarter_to_time(start),"travel restaurant"])
                                activities.append([quarter_to_time(at_event),"restaurant", restaurants[random.randint(0,restaurant_count-1)]])
                                activities.append([quarter_to_time(end_event),"travel restaurant"])
                        activities.append([quarter_to_time(at_home),"home", self.home])
                activities.append(["24:00","end"])

            case "Non-working adult" | "Pensioner":
                activities.append(["00:00","home", self.home])
                if weekday(day):
                    if random.randint(0,1) != 0:
                        start = time_to_quarter("09:00")+random.randint(0,12)
                        travel = random.randint(0,2)
                        at_event = start+travel
                        end_event = at_event+random.randint(4,24)
                        at_home = end_event+travel
                        match numpyrandom.choice(["hobby", "shop", "restaurant"], p=[0.25, 0.5, 0.25]):
                            case "hobby":
                                activities.append([quarter_to_time(start),"travel hobby"])
                                activities.append([quarter_to_time(at_event),"hobby", self.hobby])
                                activities.append([quarter_to_time(end_event),"travel hobby"])
                            case "shop":
                                activities.append([quarter_to_time(start),"travel shop"])
                                activities.append([quarter_to_time(at_event),"shop", shops[random.randint(0,shop_count-1)]])
                                activities.append([quarter_to_time(end_event),"travel shop"])
                            case "restaurant":
                                activities.append([quarter_to_time(start),"travel restaurant"])
                                activities.append([quarter_to_time(at_event),"restaurant", restaurants[random.randint(0,restaurant_count-1)]])
                                activities.append([quarter_to_time(end_event),"travel restaurant"])
                        activities.append([quarter_to_time(at_home),"home", self.home])                
                else:
                    if random.randint(0,1) != 0:
                        start = time_to_quarter("09:00")+random.randint(0,12)
                        travel = random.randint(0,2)
                        at_event = start+travel
                        end_event = at_event+random.randint(4,24)
                        at_home = end_event+travel
                        match numpyrandom.choice(["hobby", "restaurant"], p=[0.5, 0.5]):
                            case "hobby":
                                activities.append([quarter_to_time(start),"travel hobby"])
                                activities.append([quarter_to_time(at_event),"hobby", self.hobby])
                                activities.append([quarter_to_time(end_event),"travel hobby"])
                            case "restaurant":
                                activities.append([quarter_to_time(start),"travel restaurant"])
                                activities.append([quarter_to_time(at_event),"restaurant", restaurants[random.randint(0,restaurant_count-1)]])
                                activities.append([quarter_to_time(end_event),"travel restaurant"])
                        activities.append([quarter_to_time(at_home),"home", self.home])
                activities.append(["24:00","end"])                

        #print(activities)
        self.daycount += 1
        self.days.append(activities)

    def generate_all_days(self):
        for i in range(simulation_length):
            for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
                self.generate_day(day)

    def print_day(self, daycount):
        print("Day " + f'{daycount:03}: ', end='')
        print(self.days[daycount])
    
    def print_all_days(self):
        for daycount in range(0, self.daycount):
            self.print_day(daycount)

occupations = ["Infant", "Pupil", "Student", "Working adult", "Non-working adult", "Pensioner"]

#
# OUTPUT STATISTICS
#

def print_statistics(population):
    global occupations

    # Occupation distribution
    occupation_dist = dict.fromkeys(occupations, 0)
    for person in population:
        occupation_dist[person.type] += 1
    print("Occupation        Count   Percentage")
    print("----------------- ------- ----------")
    for type in occupations:
        percent = occupation_dist[type]/len(population)*100
        print(f'{type:17} {occupation_dist[type]:7d}     {percent:5.1f}%')
    print("----------------- ------- ----------")
    print(f'{"Total":17} {len(population):7d}     {100:5.1f}%')

    print("")

    # Age distribution (5-step)
    age_dist = dict.fromkeys([i for i in range(20)], 0)
    for person in population:
        age_dist[person.age//5] += 1
    print("Age   Count   Percentage")
    print("----- ------- ----------")
    for age in age_dist:
        percent = age_dist[age]/len(population)*100
        age_lower = age*5
        age_upper = age_lower+4
        print(f'{age_lower:2d}-{age_upper:2d} {age_dist[age]:7d}     {percent:5.1f}%')
    print("----- ------- ----------")
    print(f'{"Total":5} {len(population):7d}     {100:5.1f}%')

    print("")

    # Vaccination distribution
    vaccination_dist = dict.fromkeys(['yes', 'no'], 0)
    for person in population:
        vaccination_dist[person.vaccinated] += 1
    print("Vacination        Count   Percentage")
    print("----------------- ------- ----------")
    for type in ['yes', 'no']:
        percent = vaccination_dist[type]/len(population)*100
        print(f'{type:17} {vaccination_dist[type]:7d}     {percent:5.1f}%')
    print("----------------- ------- ----------")
    print(f'{"Total":17} {len(population):7d}     {100:5.1f}%')    

total_spread_of_infection = 0
maximum_infections = 0
maximum_hospitalization = 0
total_deaths = 0

def print_health_statistics(population):
    global inflist,suslist,reclist,deadlist
    global total_spread_of_infection, maximum_infections, maximum_hospitalization, total_deaths

    # Statistics by health status
    health_distribution = dict.fromkeys(['healthy', 'ill_phase1', 'ill_phase2', 'ill_phase3', 'hospitalized', 'recovered', 'deceased'], 0)
    for person in population:
        health_distribution[person.health] += 1

    print("Health            Count   Percentage")
    print("----------------- ------- ----------")
    for type in ['healthy', 'ill_phase1', 'ill_phase2', 'ill_phase3', 'hospitalized', 'recovered', 'deceased']:
        percent = health_distribution[type]/len(population)*100
        print(f'{type:17} {health_distribution[type]:7d}     {percent:5.1f}%')
    print("----------------- ------- ----------")
    print(f'{"Total":17} {len(population):7d}     {100:5.1f}%')
    print("")

    # Calculate some key values
    current_infection = health_distribution['ill_phase1']+health_distribution['ill_phase2']+health_distribution['ill_phase3']+health_distribution['hospitalized']
    total_spread_of_infection = current_infection + health_distribution['recovered']+health_distribution['deceased']
    if maximum_infections < current_infection:
        maximum_infections = current_infection
    if maximum_hospitalization < health_distribution['hospitalized']:
        maximum_hospitalization = health_distribution['hospitalized']
    total_deaths = health_distribution['deceased']

    # Statistics by infection location
    infection_distribution = dict.fromkeys(['none', 'home', 'school', 'uni', 'work', 'restaurant', 'hobby', 'shop', 'travel'], 0)
    for person in population:
        infection_distribution[person.infection_location] += 1

    print("Infection Location  Count   Percentage")
    print("------------------- ------- ----------")
    for type in ['none', 'home', 'school', 'uni', 'work', 'restaurant', 'hobby', 'shop', 'travel']:
        percent = infection_distribution[type]/len(population)*100
        print(f'{type:19} {infection_distribution[type]:7d}     {percent:5.1f}%')
    print("----------------- ------- ----------")
    print(f'{"Total":19} {len(population):7d}     {100:5.1f}%')
    print("")

    # And update Simulation Graph
    inflist.append(current_infection) # All infected/ill persons
    suslist.append(health_distribution["healthy"])
    reclist.append(health_distribution["recovered"])
    deadlist.append(health_distribution["deceased"])
    update_graph(inflist,suslist,reclist,deadlist)

def print_end_statistics():
    print(f'Total spread of infection: {total_spread_of_infection} ({total_spread_of_infection/len(population)*100:.1f}%)')
    print(f'Maximum infections: {maximum_infections} ({maximum_infections/len(population)*100:.1f}%)')
    print(f'Maximum hospitalization: {maximum_hospitalization} ({maximum_hospitalization/len(population)*100:.1f}%)')
    print(f'Total deaths: {total_deaths} ({total_deaths/len(population)*100:.1f}%)')
    
#
# OUTPUT GRAPH
#

inflist = []
suslist = []
reclist = []
deadlist = []
simulation_graph_figure = 0

def initiate_graph():
    global simulation_graph_figure

    simulation_graph_figure = plt.figure(figsize=(10,10))
    print("Simulation Graph: ", simulation_graph_figure)
    plt.ion() # Interactive mode on

def update_graph(inf,sus,rec,dead):
    global simulation_length, scenario
    global simulation_graph_figure

    plt.figure(simulation_graph_figure)
    plt.cla()
    plt.xlim([0,simulation_length*7])
    plt.title("Simulation Graph - Scenario "+scenario)
    plt.xlabel("Number of Days in Simulation")
    plt.ylabel("# Persons")
    plt.plot(inf, label="Infected", color="red")
    plt.plot(sus, label="Healthy", color="blue")
    plt.plot(rec, label="Recovered", color="springgreen")
    plt.plot(dead, label="Deceased", color="black")
    plt.legend(loc="upper right")
    #plt.show(block=False)
    simulation_graph_figure.show()
    plt.pause(0.01)

def save_graph():
    global simulation_graph_figure

    plt.figure(simulation_graph_figure)
    # Get current date/time for filename
    now = datetime.now()
    date = now.strftime("%d-%m-%Y %H:%M:%S")
    plt.savefig("Simulation Graph - Scenario "+scenario+" "+date+".png")

#
# OUTPUT GRAPH
#

simulation_map_figure = 0
simulation_map_ax = 0

def read_osm_map_data():
    global buildings, residential, water, leisure, schools, residential_coords, school_coords, graph, edge_color

    # Set Area
    place = "Zurich, Switzerland"
    north = 47.4346662
    south = 47.3202187
    west = 8.4480061
    east = 8.6254413

    # Get feature information (buildings)
    print("Load features")
    tags_building = {'building': True }
    buildings = ox.project_gdf(ox.features_from_bbox(north, south, east, west, tags_building))
    tags_residential = {'building': ['yes', 'apartments', 'house', 'semidetached_house', 'bungalow', 'residential']}
    residential = ox.project_gdf(ox.features_from_bbox(north, south, east, west, tags_residential))
    tags_water = {'water':True}
    water = ox.project_gdf(ox.features_from_bbox(north, south, east, west, tags_water))
    tags_leisure = {'leisure':True, 'natural':True, 'landuse': 'forest'}
    leisure = ox.project_gdf(ox.features_from_bbox(north, south, east, west, tags_leisure))
    tags_schools = {'amenity': 'school'}
    schools = ox.project_gdf(ox.features_from_bbox(north, south, east, west, tags_schools))
    print("Finished loading features")
    residential_coords = list(zip(list(residential.centroid.x),list(residential.centroid.y)))
    school_coords = list(zip(list(schools.centroid.x),list(schools.centroid.y)))    

    # Get network information (streets, rails)
    print("Load networks")
    streets = ox.projection.project_graph(ox.graph_from_bbox(north, south, east, west, network_type='drive'))
    rails = ox.projection.project_graph(ox.graph_from_bbox(north, south, east, west, custom_filter='["railway"~"rail"]'))
    graph = nx.compose(streets, rails)
    edge_color = ['0.8' if 'highway' in d else '0.2' for _, _, _, d in graph.edges(keys=True, data=True)]
    print("Finished loading networks")

def initiate_map():
    global simulation_map_figure, simulation_map_ax

    read_osm_map_data()
    if generate_maps:
        simulation_map_figure, simulation_map_ax = plt.subplots(figsize=(20,20))
        simulation_map_ax.set_facecolor('0.5')

        print("Simulation Map: ", simulation_map_figure)
        plt.ion() # Interactive mode on

def update_map(day):
    global simulation_map_figure, simulation_map_ax
    global buildings, residential, water, leisure, schools, residential_coords, school_coords, graph, edge_color
    global scenario

    if generate_maps:
        plt.figure(simulation_map_figure)
        plt.cla()
        plt.title("Simulation Map - Scenario "+scenario+" - Day "+str(day))
        buildings.plot(color='black', markersize=1, ax=simulation_map_ax)
        leisure.plot(color='darkgreen', markersize=1, ax=simulation_map_ax)
        water.plot(color='royalblue', markersize=1, ax=simulation_map_ax)
        #schools.plot(color='red', markersize=1, ax=simulation_map_ax)
        ox.plot_graph(graph, edge_color=edge_color, node_size=0, edge_linewidth=0.5, show=False, close=False, ax=simulation_map_ax)
        for person in population:
            if person.health in ['ill_phase1', 'ill_phase2', 'ill_phase3']:
                plt.plot(person.home_x, person.home_y, marker=".", markersize=15, markerfacecolor='red', markeredgecolor='red')
        #plt.show(block=False)
        simulation_map_figure.show()
        plt.pause(0.01)

def save_map(day):
    global simulation_map_figure, simulation_map_ax

    if generate_maps:
        plt.figure(simulation_map_figure)
        plt.savefig("Simulation Map - Scenario "+scenario+" - Day "+f'{day:03d}'+".png", bbox_inches='tight')
#
# SIMULATION OPTIONS
#
# Vaccination
#  1. Vaccination              % of vaccinated population (https://www.swr3.de/aktuell/fake-news-check/artikel-faktencheck-corona-impfung-ansteckung-100.html)
#     1a Existing vaccination  Infection rate drops by 1/3, reduced symptoms (simulation: no death)
#     1b Super vaccination     Infection rate drops to 0, reduced symptoms (simulation: no death) - unfortunately does not exist
#
# Behaviour changes
#  2. Home office
#  3. Masks in public (work, school, transportation etc.)
#  4. Quarantine
#  5. Mandatory corona test at school
#  6. Limit number of people in location (shops, restaurants)
#
# Limit public life
#  7. Closing of schools (virtual leaning)
#  8. Closing of restaurants for non-vaccinated (2G regime)
#  9. Closing of restaurants
# 10. Closing of extracurricular activities (e.g. hobbies)

scenario = 'Basis'
if len(sys.argv)>1:
    scenario = sys.argv[1]
print("Selected Scenario: "+scenario)
print("")

# Basis scenario
simul_options = {}
simul_options['vaccination'] = 0  # 0% vaccinated (value 0-100)
simul_options['home office'] = 0  # 0% homeoffice (value 0-100)
simul_options['masks in public'] = 'no'
simul_options['quarantine'] = 'no'
simul_options['corona test at school'] = 'no'
simul_options['limited number of people'] = 'no'
simul_options['closing schools'] = 'no'
simul_options['2g regime'] = 'no'
simul_options['closing restaurants'] = 'no'
simul_options['closing extracurricular'] = 'no'

# Select scenario based on command line parameter (not nice code, but works)
if scenario == 'Basis':
    pass
elif scenario == 'Existing vaccination':
    simul_options['vaccination'] = 60  # 60% vaccinated
    vaccination_type = 'existing'
elif scenario == 'Super vaccination':
    simul_options['vaccination'] = 60  # 60% vaccinated
    vaccination_type = 'super'
elif scenario == 'Home office':
    simul_options['home office'] = 30  # 30% homeoffice (value 0-100)
elif scenario == 'Masks in public':
    simul_options['masks in public'] = 'yes'
elif scenario == 'Quarantine':
    simul_options['quarantine'] = 'yes'
elif scenario == 'Corona test at school':
    simul_options['corona test at school'] = 'yes'
elif scenario == 'Limited number of people':
    simul_options['limited number of people'] = 'yes'
elif scenario == 'Closing schools':
    simul_options['closing schools'] = 'yes'
elif scenario == '2g regime':
    simul_options['2g regime'] = 'yes'
elif scenario == 'Closing restaurants':
    simul_options['closing restaurants'] = 'yes'
elif scenario == 'Closing extracurricular':
    simul_options['closing extracurricular'] = 'yes'
elif scenario == 'Limit public life':
    simul_options['closing schools'] = 'yes'
    simul_options['2g regime'] = 'yes'
    simul_options['closing restaurants'] = 'yes'
    simul_options['closing extracurricular'] = 'yes'
elif scenario == 'Behaviour changes':
    simul_options['home office'] = 30 # 30% home office of working population
    simul_options['masks in public'] = 'yes'
    simul_options['quarantine'] = 'yes'
    simul_options['corona test at school'] = 'yes'
    simul_options['limited number of people'] = 'yes'
else:
    print("Error Scenario")




def calculate_infections(location_in_quarter, type, chance):
    for location in location_in_quarter:
        is_somebody_infected = False
        for person in location:
            if (type == 'school' or type == 'uni') and  simul_options['corona test at school'] == 'yes':
                if person.health == 'ill_phase1': # Tests work 98%, assumption they work 100% correct
                    person.quarantine = 'yes'
            elif person.health == 'ill_phase2' or person.health == 'ill_phase3':
                if person.vaccinated == 'yes':
                    if vaccination_type == 'existing':
                        # Infection rate reduced by approx. 1/3 (https://www.br.de/nachrichten/wissen/coronavirus-wie-ansteckend-sind-geimpfte,SoSzBuw)
                        if random.randint(1,3)<=2:
                            is_somebody_infected = True
                    elif vaccination_type == 'super':
                        # Vaccinated person is not infected
                        pass
                else:   
                    is_somebody_infected = True
        if is_somebody_infected:
            for person in location:
                if person.health == 'healthy':
                    if random.randint(0, chance)==0:
                        if simul_options['masks in public'] == 'yes' and simul_options['limited number of people'] == 'yes' and (type == 'shop' or type == 'restaurant'):
                            if random.randint(1,100) >20: # Measures reduce infections by approx. 20% (estimates to be higher than masks only)
                                person.health = 'infected'
                                person.infection_location = type
                        elif simul_options['masks in public'] == 'yes' and type != 'home':
                            if random.randint(1,100) >15: # Op Masks reduce infections by approx. 15% (https://pubmed.ncbi.nlm.nih.gov/33205991/)
                                person.health = 'infected'
                                person.infection_location = type
                        elif simul_options['limited number of people'] == 'yes' and (type == 'shop' or type == 'restaurant'):
                            if random.randint(1,100) >5: # Measure reduce infections by approx. 5% (estimates to be lower than masks)
                                person.health = 'infected'
                                person.infection_location = type
                        else:
                            person.health = 'infected'
                            person.infection_location = type    

#
# MAIN PROGRAM
#

print("Initialize graphics")
initiate_graph()
initiate_map()
print("")

#
# GENERATE LOCATIONS
#

home_count = population_count//3
homes = subset(home_count, len(residential_coords))
school_count = population_count//1000
schools = subset(school_count, len(school_coords))
uni_count = 7
unis = [i for i in range(uni_count)]
workplaces_count = population_count//50
workplaces = [i for i in range(workplaces_count)]
restaurant_count = population_count//500
restaurants = [i for i in range(restaurant_count)]
hobby_count = population_count//200
hobbies = [i for i in range(hobby_count)]
shop_count = population_count//100
shops = [i for i in range(shop_count)]

#
# GENERATE POPULATION
#

# read_names()
population = [ Person(numpyrandom.choice(occupations, p=[0.065, 0.122, 0.033, 0.303, 0.303, 0.174])) for i in range(population_count) ]

print("")
print_statistics(population)
print("")

for person in population:
    person.generate_all_days()
    if (person.pers_number+1)%1000 == 0:
        print(f'Activity generation: {person.pers_number+1:7d} done')
print('')

#
# SIMULATE
#

print("")
print("Start Simulation")
print("")

# Patient "Zero" can infect others
population[0].health = 'ill_phase2'

for day in range(7*simulation_length):

    #
    # CALCULATE LOCATION AND INFECTION FOR EACH PERSON PER QUARTER    
    #
    for quarter in range(4*24):
        # Calculate location of each üerson
        homes_occupancy_in_quarter = [[] for i in range(home_count)]
        school_occupancy_in_quarter = [[] for i in range(school_count)]
        uni_occupancy_in_quarter = [[] for i in range(uni_count)]
        workplaces_occupancy_in_quarter = [[] for i in range(workplaces_count)]
        restaurants_occupancy_in_quarter = [[] for i in range(restaurant_count)]
        hobbies_occupancy_in_quarter = [[] for i in range(hobby_count)]
        shops_occupancy_in_quarter = [[] for i in range(shop_count)]
        travel_occupancy_in_quarter = [[]]
        for person in population:
            if person.quarantine == 'no':
                today_activities = person.days[day]
                i=0
                while time_to_quarter(today_activities[i+1][0])<= quarter:
                    i +=1
                activity_in_quarter = today_activities[i][1]
                match activity_in_quarter:
                    case "home":
                        homes_occupancy_in_quarter[today_activities[i][2]].append(person)
                    case "school" | "school restaurant" | "travel school":
                        if simul_options['closing schools'] == 'no':
                            if activity_in_quarter == "travel school":
                                travel_occupancy_in_quarter[0].append(person)
                            else:
                                school_occupancy_in_quarter[today_activities[i][2]].append(person)
                        else:
                            homes_occupancy_in_quarter[person.home].append(person)
                    case "uni" | "uni restaurant" | "travel uni":
                        if simul_options['closing schools'] == 'no':
                            if activity_in_quarter == "travel uni":
                                travel_occupancy_in_quarter[0].append(person)
                            else:
                                uni_occupancy_in_quarter[today_activities[i][2]].append(person)
                        else:
                            homes_occupancy_in_quarter[person.home].append(person)
                    case "work" | "travel work":
                        if person.homeoffice == 'yes':
                            homes_occupancy_in_quarter[person.home].append(person)
                        else:
                            if activity_in_quarter == "travel work":
                                travel_occupancy_in_quarter[0].append(person)
                            else:
                                workplaces_occupancy_in_quarter[today_activities[i][2]].append(person)
                    case "restaurant" | "travel restaurant":
                        if simul_options['closing restaurants'] == 'no':
                            if simul_options['2g regime'] == 'yes' and person.vaccinated == 'no':
                                homes_occupancy_in_quarter[person.home].append(person)
                            else:
                                if activity_in_quarter == "travel restaurant":
                                    travel_occupancy_in_quarter[0].append(person)
                                else:
                                    restaurants_occupancy_in_quarter[today_activities[i][2]].append(person)
                        else:
                            homes_occupancy_in_quarter[person.home].append(person)
                    case "hobby" | "travel hobby": 
                        if simul_options['closing extracurricular'] == 'no':
                            if activity_in_quarter == "travel hobby":
                                travel_occupancy_in_quarter[0].append(person)
                            else:
                                hobbies_occupancy_in_quarter[today_activities[i][2]].append(person)
                        else:
                            homes_occupancy_in_quarter[person.home].append(person)
                    case "shop":
                        shops_occupancy_in_quarter[today_activities[i][2]].append(person)
                    case "travel" | "travel shop":
                        travel_occupancy_in_quarter[0].append(person)
                    case _:
                        print("Error: " + activity_in_quarter)
            else:
                homes_occupancy_in_quarter[person.home].append(person)

        # Calculate infections
        calculate_infections(homes_occupancy_in_quarter, 'home', 1000)
        calculate_infections(school_occupancy_in_quarter, 'school', 1000)
        calculate_infections(uni_occupancy_in_quarter, 'uni', 1000)
        calculate_infections(workplaces_occupancy_in_quarter, 'work', 1000)
        calculate_infections(restaurants_occupancy_in_quarter, 'restaurant', 1000)
        calculate_infections(hobbies_occupancy_in_quarter, 'hobby', 1000)
        calculate_infections(shops_occupancy_in_quarter, 'shop', 1000)
        calculate_infections(travel_occupancy_in_quarter, 'travel', 1000*10)


    #
    # CALCULATE HEALTH STATUS CHANGES (e.g. death/recovery) of each person at end of day
    #
    # Corona develops in three phases for each infected person
    # 1) Person is infected, but does not yet have symptoms, nor can infect others (on average 7 days)
    # 2) Person, does not yet have sympthons, but can already infect others (on average 2 days)
    # 3) Person, develops sympthoms and can infect others (on average 8 days)

    # The following heath status for a person exist in the simulation:
    # healthy       The person is healthy and has not been infected yet
    # infected      The person has just been infected that day
    # ill_phase1    The person is infected (without symptoms, and cannot infect others)
    # ill_phase2    The person is infected (without symptoms, and can infect others)
    # ill_phase3    The person is infected (with symptoms, and can infect others)
    # hospitalized  The person is ill with heavy symptoms in hospital (approx. 3%)
    # recovered     The person is fully recoved and will not be infected again
    # deceased      The person died (approx 0.5% died in Switzerland overall, approx. 11% of all hospitalized patients - https://www.bfs.admin.ch/asset/de/23568268)
    #               This means approx. 0.2% of the non-hospitalized patients die 
    for person in population:
        if person.health == 'infected':
            person.health = 'ill_phase1'
            person.days_ill = 0
        elif person.health == 'ill_phase1':
            person.days_ill += 1
            if person.days_ill>=7:
                person.health = 'ill_phase2'
        elif person.health == 'ill_phase2':
            person.days_ill += 1
            if person.days_ill>=9:
                if person.vaccinated == 'no':
                    person.health = numpyrandom.choice(['ill_phase3', 'hospitalized'], p=[0.97, 0.03]) # 3% hospitalized
                else:
                    person.health = 'ill_phase3'
        elif person.health == 'ill_phase3':
            if simul_options['quarantine'] == 'yes':
                person.quarantine = 'yes'  # Go into quatantine when first symptoms kick in
            person.days_ill += 1
            if person.days_ill>=17:
                if person.vaccinated == 'no':
                    person.health = numpyrandom.choice(['recovered', 'deceased'], p=[0.998, 0.002]) # 0.2% of non-hospitalized patients die
                else:
                    person.health = 'recovered'
        elif person.health == 'hospitalized':
            person.days_ill += 1
            if person.days_ill>=17:
                person.health = numpyrandom.choice(['recovered', 'deceased'], p=[0.89, 0.11]) # 11% of hospitalized patients die   
        
                
    #
    # PRINT END OF DAY HEALTH STATISTICS
    #
    print("Day: " + str(day+1))
    print_health_statistics(population)
    update_map(day+1)
    save_map(day+1)


print_end_statistics()
save_graph()





"""
print("")
print("Example Daily Routine")
print("")

person = Person("Working adult")
person.print_person()
person.generate_all_days()
person.print_all_days()
"""

"""
for person in population[0:50]:
    person.print_person()
"""
