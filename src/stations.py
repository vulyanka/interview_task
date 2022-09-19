import json
import time
import logging
from dataclasses import dataclass, field, asdict
from typing import List

from src.async_http_util import make_async_http_get


@dataclass
class CommonStation:
    ''' Common contract for station object.
    '''
    id: int
    name: str
    description: str
    boxes: int
    free_boxes: int
    free_bikes: int


@dataclass
class Station(CommonStation):
    ''' Contract for station business object.
    '''
    active: str
    free_ratio: float
    coordinates: List[float]
    address: str = field(init=False, default='Unknown', repr=True)

    def __repr__(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


@dataclass
class APIStation(CommonStation):
    ''' Contract for station API object.
    '''
    status: str
    longitude: float
    latitude: float
    internal_id: int
    station: Station = field(init=False)

    def __post_init__(self) -> None:
        ''' Post processing for mapping API object fields to station business object.
        '''
        self.station = Station(
            id=self.id, name=self.name, description=self.description, boxes=self.boxes,
            free_boxes=self.free_boxes, free_bikes=self.free_bikes,
            active=True if self.status == 'aktiv' else False,
            free_ratio=self.free_boxes / self.boxes if self.boxes else 0,
            coordinates=[self.longitude, self.latitude])


class Stations:
    ''' Stations aggregator.
    '''

    # Url for getting stations from web.
    STATIONS_URL = 'wegfinder.at/api/v1/stations'

    # Url for getting station addresses from web.
    STATIONS_ADDRESS_URL = 'api.i-mobility.at/routing/api/v1/nearby_address'

    def __init__(self) -> None:
        self.__loaded = False
        self.api_stations = None
        self.stations_by_bikes = None

    def load_actual_stations(self) -> None:
        ''' Function to load actual stations without additional info.
        '''
        if self.__loaded:
            return

        logging.info('Start getting actual stations from web...')
        t1 = time.time()

        r = make_async_http_get([f'https://{self.STATIONS_URL}'])
        data = r[0]
        logging.info(f'Getting actual stations: web response in {time.time() - t1} seconds')

        self.api_stations = []
        self.stations_by_bikes = {}
        for obj in data:
            try:
                api_station = APIStation(**obj)
                self.api_stations.append(api_station)
                if api_station.free_bikes not in self.stations_by_bikes:
                    self.stations_by_bikes[api_station.free_bikes] = [api_station.station]
                else:
                    self.stations_by_bikes[api_station.free_bikes].append(api_station.station)
            except Exception as err:
                logging.warn('Skipping station as the incoming station\'s format cannot fit '
                             f'the expected one: {str(obj)}. Error: {str(err)}')
        self.__loaded = True

        # Sort stations by name.
        logging.info('Applying sorting by name for stations...')
        for val in self.stations_by_bikes.values():
            val.sort(key=lambda x: x.name)

        logging.info(f'Getting actual stations: Done in {time.time() - t1} seconds')

    def load_station_addresses(self) -> None:
        ''' Function to load station addresses.
        '''
        self.load_actual_stations()

        logging.info('Start getting station addresses from web...')
        t1 = time.time()
        
        address_get_urls = []
        for api_station in self.api_stations:
            address_get_urls.append(
                f'https://{self.STATIONS_ADDRESS_URL}'
                f'?latitude={api_station.latitude}&longitude={api_station.longitude}')

        r = make_async_http_get(address_get_urls)
        logging.info(f'Getting station addresses: web response in {time.time() - t1} seconds')

        for api_station, api_address in zip(self.api_stations, r):
            if api_address and 'data' in api_address and 'name' in api_address['data']:
                api_station.station.address = api_address['data']['name']
            else:
                logging.warn(f'There is not valid address for {api_station.name} station'
                             f'with latitude={api_station.latitude} and longitude={api_station.longitude}')

        logging.info(f'Getting station addresses: Done in {time.time() - t1} seconds')

    def load_full_stations_data(self) -> None:
        ''' Function to load whole stations-related data.
        '''
        logging.info('Loading whole stations-related data...')
        self.load_actual_stations()
        self.load_station_addresses()

    def get_available_stations_by_free_bikes(self, min_free_bikes=1) -> List[Station]:
        ''' Function to get available stations sorted by free bikes.
        '''
        self.load_actual_stations()

        logging.info(f'Calculating available stations with at least {min_free_bikes} free bike(s)...')
        t1 = time.time()

        keys = list(self.stations_by_bikes.keys())
        keys.sort(reverse=True)

        res = []
        for key in keys:
            if key < min_free_bikes:
                break
            res.extend(self.stations_by_bikes[key])

        logging.info(f'Calculating available stations: Done in {time.time() - t1} seconds')
        return res
