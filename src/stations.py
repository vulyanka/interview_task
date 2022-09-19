import json
from typing import List
import logging
from dataclasses import dataclass, field, asdict

from src.async_http_util import make_async_http_get


@dataclass
class CommonStation:
    ''' TODO
    '''
    id: int
    name: str
    description: str
    boxes: int
    free_boxes: int
    free_bikes: int


@dataclass
class Station(CommonStation):
    ''' TODO
    '''
    active: str
    free_ratio: float
    coordinates: List[float]
    address: str = field(init=False, default='Unknown', repr=True)

    def __repr__(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


@dataclass
class APIStation(CommonStation):
    ''' TODO
    '''
    status: str
    longitude: float
    latitude: float
    internal_id: int
    station: Station = field(init=False)

    def __post_init__(self):
        self.station = Station(
            id=self.id, name=self.name, description=self.description, boxes=self.boxes,
            free_boxes=self.free_boxes, free_bikes=self.free_bikes,
            active=True if self.status == 'aktiv' else False,
            free_ratio=self.free_boxes / self.boxes if self.boxes else 0,
            coordinates=[self.longitude, self.latitude])


class Stations:
    ''' TODO
    '''

    # TODO
    STATIONS_URL = 'wegfinder.at/api/v1/stations'

    def __init__(self) -> None:
        self.__loaded = False
        self.stations = None
        self.stations_by_bikes = None

    def load_actual_stations(self) -> None:
        ''' TODO
        '''
        if self.__loaded:
            return

        ### TO LIB + try
        r = make_async_http_get([f'https://{self.STATIONS_URL}'])
        data = r[0]
        ###

        self.stations = []
        self.stations_by_bikes = {}
        for obj in data:
            try:
                api_station = APIStation(**obj)
                self.stations.append(api_station.station)
                if api_station.free_bikes not in self.stations_by_bikes:
                    self.stations_by_bikes[api_station.free_bikes] = [api_station.station]
                else:
                    self.stations_by_bikes[api_station.free_bikes].append(api_station.station)
            except Exception as err:
                logging.warn('Skipping station as the incoming station\'s format cannot fit '
                             f'the expected one: {str(obj)}. Error: {str(err)}')
        self.__loaded = True

        # TODO
        for val in self.stations_by_bikes.values():
            val.sort(key=lambda x: x.name)

    def load_station_addresses(self) -> None:
        ''' TODO
        '''
        self.load_actual_stations()
        # TODO ...

    def load_full_stations_data(self) -> None:
        ''' TODO
        '''
        self.load_actual_stations()
        self.load_station_addresses()

    def get_available_stations_by_free_bikes(self, min_free_bikes=1):
        ''' TODO
        '''
        self.load_actual_stations()

        keys = list(self.stations_by_bikes.keys())
        keys.sort(reverse=True)
        
        res = []
        for key in keys:
            if key < min_free_bikes:
                break
            res.extend(self.stations_by_bikes[key])

        return res
