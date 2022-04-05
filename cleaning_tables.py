import pandas as pd
import random
import numpy as np
from pyxlsb import convert_date

def aggregate_tables(write_path = '~/data'):
    """
    processes occupancy costs, footfall tenancy schedule and lease expiries tables

    returns:
    no direct returns. writes output to csv files in specified directory (`write_path`)

    """
    occupancy_costs = pd.read_excel('data/OccupancyCosts.xlsx')
    tenancy_schedule = pd.read_excel('data/The Glades Tenancy Schedule.xlsx',
                                skiprows = 1)
    footfall = pd.read_excel('data/footfall.xlsx')
    
    name_dict = {'black cab coffee co': 'black cab coffee', 
             'apple store': 'apple',
            'and cut hair & beauty': 'and cut', 
            'caffè nero': 'caffe nero', 
            'crew clothing co.': 'crew clothing co', 
            'crystal palace football club': 'crystal palace f.c',
             'intime ': 'intime',
             'suit direct ': 'suit direct'
            }
    
    occupancy_costs['mainCategory'] = occupancy_costs['Category']\
                                    .apply(lambda x: x.split(">>")[0])\
                                    .apply(lambda x: x.rstip())

    occupancy_costs['Name'] = occupancy_costs['Name']\
                .apply(lambda x: x.lower() if isinstance(x, str) else '')
    occupancy_costs = occupancy_costs.replace(name_dict)

    tenancy_schedule.rename(columns = {'Shop': 'Name'}, inplace = True)
    tenancy_schedule['Name'] = tenancy_schedule['Name']\
                .apply(lambda x: x.lower() if isinstance(x, str) else '')
    tenancy_schedule = tenancy_schedule.replace(name_dict) 

    lease_expiries = pd.read_excel('data/lease_expiries.xlsx',
                               usecols=lambda x: 'Unnamed' not in x,
                               skiprows = 1, 
                               engine = 'pyxlsb')

    lease_expiries.rename(columns = {'Name':'Number', 'Shop':'Name'},
                      inplace = True)

    lease_expiries['Name'] = lease_expiries['Name']\
                            .apply(lambda x: x.lower() if isinstance(x, str) else '')

    lease_expiries = lease_expiries.replace(name_dict) 

    fact_table = occupancy_costs.merge(tenancy_schedule,
                                   on = 'Name', how = 'outer')\
                            .merge(lease_expiries, 
                                   on = 'Name',
                                   how = 'outer')\
                            .sort_values(by = 'Name') \
                            .drop_duplicates()
    clean_table = fact_table[fact_table.Name !=''].sort_values(by='Name')
    clean_table['rent_review'] = clean_table['Rent Type Of Review'].apply(lambda x: 1 if isinstance(x, str) else 0)
    clean_table['Lease Review'] = clean_table['Lease Review'].apply(lambda x: format(convert_date(x), '%Y-%m-%d'))
    clean_table['Lease Expiry_y'] = clean_table['Lease Expiry_y'].apply(lambda x: format(convert_date(x), '%Y-%m-%d'))
    clean_table = clean_table.drop(['Lease Expiry_x'], axis=1)

    clean_table.to_csv(write_path + 'lasalle-retailers.csv')
    
    # retailer by category
    retailer_by_cat = clean_table.groupby('mainCategory').count()['Name']
    retailer_by_cat.to_csv(write_path +'retailer_by_category.csv')

    
    #generate profitability data for stores

    # synthetic target ROTA
    target = np.random.randint(low =5, high = 50, size = 122)

    # synthetic actual ROTA
    actual = np.random.randint(low = 30, high = 50, size = 122)

    #assign these ROTAs to companies
    name = clean_table.Name.unique()

    #compute profitability
    profitability = (actual - target)/target *100

    #create df with profitability
    rota= pd.DataFrame({'name': name, 
                        'target': target,
                        'actual': actual, 
                        'profitability': profitability})

    #save rota to csv
    rota.to_csv(write_path + '/rota.csv')

    #synthetic time of day
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
    footfall_time_of_day.to_csv( write_path + '/footfall_time_of_day.csv')
    footfall.to_csv(write_path + '/footfall.csv')

    environmental = pd.DataFrame(name, columns = ['name'])

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

    environmental.to_csv(write_path + 'environmental_data.csv')
