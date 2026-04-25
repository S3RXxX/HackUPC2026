def process_users(users):
    thing1 = []
    thing2 = []
    thing3 = {}
    for thing4 in users:
        thing1.append(thing4.name)
        thing3[thing4.id] = thing4
    thing2 = [x for x in thing1 if x]
    return thing2
