import uvicorn
from fastapi import FastAPI, Query

from services import find_by_geonameid, find_by_page, find_by_cities, find_by_part_name

app = FastAPI(title='Timonin Nikita test task Infotecs')


@app.get("/city")
async def get_city(geonameid: int = Query(None, description='Get information about city by geonameid')):
    data = find_by_geonameid(str(geonameid))
    if data is None:
        data = {'error': 'Not found'}
    return data


@app.get("/city/names")
async def get_city(part_of_name: str = Query(..., description='Get information about city by part of name')):
    data = find_by_part_name(part_of_name)
    if data is None:
        data = {'error': 'Not found'}
    return data


@app.get("/cities_list")
async def get_cities_by_page(page: int = Query(..., description='Page number (numeration from 0)', gt=0),
                             count: int = Query(..., description='Amount of cities per page', gt=-1)):
    data = find_by_page(page, count)
    if data is None:
        data = {'error': 'Not found'}
    return data


@app.get("/cities")
async def get_cities_by_names(city1: str = Query(..., description='Russian name of first city'),
                              city2: str = Query(..., description='Russian name of second city')):
    data = find_by_cities(city1, city2)
    return data


if __name__ == "__main__":
    uvicorn.run('script:app', host='127.0.0.1', port=8000, reload=True)
