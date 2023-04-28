import redis

r = redis.Redis(host='localhost', port=6379, db=1, password='')

keys = r.keys('cached:*')

print(f'There are {len(keys)} keys in the database.')
if input('Proceed to clear cache? (Y/n): ') in ['Y', 'y']:
    for key in keys:
        r.delete(key)
    print('Cache cleared.')
else:
    print('Aborted.')
