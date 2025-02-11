import shelve

with shelve.open('app_data') as db:
    print(db.get('events'))