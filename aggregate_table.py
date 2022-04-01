def aggregate_tables():
    import pandas as pd
    """
    aggregates occupancy costs, tenancy schedule and lease expiries tables

    """
    occupancy_costs = pd.read_excel('data/OccupancyCosts.xlsx')
    tenancy_schedule = pd.read_excel('data/The Glades Tenancy Schedule.xlsx',
                                skiprows = 1)
    
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
                                    .apply(lambda x: x.split(">>")[0])
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

    return clean_table
