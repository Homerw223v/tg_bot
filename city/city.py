cities = []


async def create_cities():
    with open('city/City.txt', 'r', encoding='utf-8') as file:
        for city in file:
            cities.append(city.strip().lower())
    print('-----List of city created')
