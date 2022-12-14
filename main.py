import time
import logging
from src.stations import Stations

logging.basicConfig(level=logging.INFO)


def main() -> None:
    ''' Main function to receive available Stations in JSON.
    '''
    logging.info('Start.')
    t1 = time.time()

    stations = Stations()
    stations.load_full_stations_data()
    r = stations.get_available_stations_by_free_bikes()

    logging.info('Dumping results to file...')
    with open('result.json', 'w') as f:
        f.write(str(r))

    logging.info(f'Done in {time.time() - t1} seconds')


if __name__ == '__main__':
    main()
