import pandas as pd
import random
import numpy as np
from pyxlsb import convert_date
import csv


def get_shop_dict(filepath):
    dict_from_csv = {}
    with open(filepath, mode='r') as inp:
        reader = csv.reader(inp)
        dict_from_csv = {rows[0]:rows[1] for rows in reader}
    return dict_from_csv


def harmonize_shop_names(df, name_dict):
    df['Name'] = df['Name'].apply(lambda x: x.lower() if isinstance(x, str) else '')
    df = df.replace(name_dict) 
    return df


def transform_occupancy(occupancy_costs, shop_dictionary):
    occupancy_costs['mainCategory'] = occupancy_costs['Category']\
                                    .apply(lambda x: x.split(">>")[0])\
                                    .apply(lambda x: x.rstrip())

    clean_occupancy = harmonize_shop_names(occupancy_costs, shop_dictionary)
    return clean_occupancy


def transform_tenancy_schedule(tenancy_schedule, shop_dictionary):
    tenancy_schedule.rename(columns = {'Shop': 'Name'}, inplace = True)
    clean_tenancy_schedule = harmonize_shop_names(tenancy_schedule, shop_dictionary)

    return clean_tenancy_schedule


def transform_lease_expiries(lease_expiries, shop_dictionary):
    lease_expiries.rename(columns = {'Name':'Number', 'Shop':'Name'},
                      inplace = True)

    clean_lease_expiries = harmonize_shop_names(lease_expiries, shop_dictionary)
    return clean_lease_expiries
    

def transform_footfall(footfall):
    times = ['morning', 'afternoon', 'evening', 'night']
    footfall['time'] = random.choices(times, k=footfall.shape[0])

    #extract month, year and day from date
    footfall['month'] = footfall['Date'].dt.month
    footfall['year'] = footfall['Date'].dt.year
    footfall['day'] = footfall['Date'].dt.day

    # fill missing values in weather with 'sunny'
    footfall['WeatherDesc'] = footfall['WeatherDesc'].fillna('Sunny')

    #put in ages with a given distribution
    footfall['Age'] = random.choices(range(1,60), k=footfall.shape[0])

    #segments? Need to check with Mark

    #save synthetic dataset to csv
    footfall_time_of_day = pd.DataFrame(footfall.groupby(['month', 'day', 'time']).sum()['Quantity'])
    #footfall_time_of_day.to_csv( write_path + '/footfall_time_of_day.csv')
    return footfall


def synthetic_profitability(names):
    # synthetic target ROTA
    target = np.random.randint(low =5, high = 50, size = len(names))

    # synthetic actual ROTA
    actual = np.random.randint(low = 30, high = 50, size = len(names))

    #compute profitability
    profitability = (actual - target)/target *100

    #create df with profitability
    rota= pd.DataFrame({'name': names, 
                        'target': target,
                        'actual': actual, 
                        'profitability': profitability})

    return rota


def syntetic_environmental_data(names):
    environmental = pd.DataFrame(names, columns = ['name'])

    #synthetic raw bream score
    environmental['bream_score'] = random.choices(range(40, 95), k = environmental.shape[0])

    def breeam_cat(score):
        if score <= 30:
            return 'Unclassified'
        elif score <= 45 and score > 30:
            return 'Pass'
        elif score <= 55 and score > 45:
            return 'Good'
        elif score <= 70 and score > 55:
            return 'Very Good'
        elif score <= 85 and score > 70:
            return 'Excellent'
        else:
            return 'Outstanding'

    #convert scores to categories
    environmental['bream_cat'] = environmental['bream_score'].apply(lambda x: breeam_cat(x))

    #scheme implementation
    environmental['scheme_implemenatation'] = random.choices([0,1], k = environmental.shape[0])

    # energy consumption
    environmental['energy_consumption'] = random.choices(range(190, 300), k = environmental.shape[0])

    # target energy consumption
    environmental['target_consumption'] = random.choices(range(190, 220), k = environmental.shape[0])

    # recycling percentage
    environmental['recycling_percentage'] = random.choices(range(20, 50), k = environmental.shape[0])

    # target recycling percentage
    environmental['target_recycling'] = random.choices(range(70,90), k = environmental.shape[0])

    # carbon usage
    environmental['carbon_usage'] = random.choices(range(70,90), k = environmental.shape[0])

    # target carbon usage
    environmental['target_carbon'] = random.choices(range(10, 20), k = environmental.shape[0])

    return environmental


if __name__ == "main":
    shop_dictionary = get_shop_dict('shop_dictionary.txt')
    occupancy_costs = pd.read_excel('data/OccupancyCosts.xlsx')
    tenancy_schedule = pd.read_excel('data/The Glades Tenancy Schedule.xlsx',
                                skiprows = 1)
    footfall = pd.read_excel('data/footfall.xlsx')
    lease_expiries = pd.read_excel('data/lease_expiries.xlsx',
                                usecols=lambda x: 'Unnamed' not in x,
                                skiprows = 1, 
                                engine = 'pyxlsb')


    # read in shop dictionary first
    shop_dictionary = get_shop_dict('shop_dictionary.txt')

    clean_occupancy = transform_occupancy(occupancy_costs, shop_dictionary)
    clean_footfall = transform_footfall(footfall)
    clean_lease_expiries = transform_lease_expiries(lease_expiries, shop_dictionary)
    clean_tenancy_schedule = transform_tenancy_schedule(tenancy_schedule, shop_dictionary)

    names = clean_tenancy_schedule.Name
    rota =synthetic_profitability(names)
    environmental = syntetic_environmental_data(names)

    #write tables to csv
    clean_occupancy.to_csv('clean_occupancy.csv')
    clean_footfall.to_csv('clean_footfall.csv')
    clean_lease_expiries.to_csv('clean_lease_expiries.csv')
    clean_tenancy_schedule.to_csv('clean_tenancy_schedule.csv')
    rota.to_csv('rota.csv')
    environmental.to_csv('environmental.csv')
