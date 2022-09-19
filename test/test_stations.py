import json
from unittest.mock import patch

import src.stations as st


def get_test_stations():
    with open('test/data/stations_api.json') as f:
        data = f.read()
    return [json.loads(data)]


def get_test_result_stations():
    with open('test/data/stations_result.json') as f:
        data = f.read()
    return json.loads(data)


@patch('src.stations.make_async_http_get', return_value=get_test_stations())
def test_load_actual_stations(mock_make_async_http_get):
    stations = st.Stations()
    assert stations.api_stations == None
    assert stations.stations_by_bikes == None

    stations.load_actual_stations()
    mock_make_async_http_get.assert_called_once_with(
        ['https://wegfinder.at/api/v1/stations'])

    assert len(stations.api_stations) == 5
    assert len(stations.stations_by_bikes.keys()) == 4
    assert stations.stations_by_bikes[5] == [stations.api_stations[1].station, \
                                             stations.api_stations[0].station]
    assert stations.stations_by_bikes[0] == [stations.api_stations[2].station]
    assert stations.stations_by_bikes[1] == [stations.api_stations[3].station]
    assert stations.stations_by_bikes[12] == [stations.api_stations[4].station]


@patch('src.stations.make_async_http_get', return_value=get_test_stations())
def test_get_available_stations_by_free_bikes(mock_make_async_http_get):
    stations = st.Stations()

    r = stations.get_available_stations_by_free_bikes(min_free_bikes=3)
    mock_make_async_http_get.assert_called_once_with(
        ['https://wegfinder.at/api/v1/stations'])

    assert len(r) == 3
    assert json.loads(str(r)) == get_test_result_stations()


@patch('src.stations.make_async_http_get')
def test_load_station_addresses(mock_make_async_http_get):
    mock_make_async_http_get.return_value = get_test_stations()
    stations = st.Stations()

    stations.load_actual_stations()
    mock_make_async_http_get.assert_called_once()

    stations.load_actual_stations()
    mock_make_async_http_get.assert_called_once()

    mock_make_async_http_get.return_value = [
        {'data': {'name': 'One'}},
        {'data': {}},
        {'data': {'name': 'Three'}},
        None,
        {'data': {'name': 'Five'}}
    ]

    stations.load_station_addresses()
    assert mock_make_async_http_get.call_count == 2
    # Check the number of urls in args.
    assert type(mock_make_async_http_get.call_args[0][0]) == list
    assert len(mock_make_async_http_get.call_args[0][0]) == 5

    for api_station, address in zip(stations.api_stations,
                                    ['One', 'Unknown', 'Three', 'Unknown', 'Five']):
        assert api_station.station.address == address


@patch('src.stations.make_async_http_get')
def test_load_full_stations_data(mock_make_async_http_get):
    stations = st.Stations()

    stations.load_full_stations_data()
    assert mock_make_async_http_get.call_count == 2
