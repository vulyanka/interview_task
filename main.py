from src.stations import Stations

# logger = logging.getLogger('simple_example')
# logger.setLevel(logging.INFO)
# logging.basicConfig(level=logging.INFO)
# logging.error('start')

def main():
    ''' TODO
    '''
    s = Stations()
    r = s.get_available_stations_by_free_bikes()
    print(r)


if __name__ == '__main__':
    main()
