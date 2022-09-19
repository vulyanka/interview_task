from src.stations import Stations

# logger = logging.getLogger('simple_example')
# logger.setLevel(logging.INFO)
# logging.basicConfig(level=logging.INFO)
# logging.error('start')

def main():
    ''' TODO
    '''
    s = Stations()
    s.load_full_stations_data()
    r = s.get_available_stations_by_free_bikes()
    with open('result.json', 'w') as f:
        f.write(str(r))


if __name__ == '__main__':
    main()
