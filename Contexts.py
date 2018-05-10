class Context(object):
    def __init__(self,name):
        self.lifespan = 2
        self.name = name
        self.active = False
        self.placeholder = ''
        
    def activate_context(self):
        self.active = True
    
    def deactivate_context(self):
        self.active = False
    
    def decrease_lifespan(self):
        self.lifespan -= 1
        if self.lifespan == 0:
            self.deactivate_context()

class FirstGreeting(Context):
    def __init__(self):
        #print('context: FirstGreeting')
        self.lifespan = 1
        self.name = 'FirstGreeting'
        self.placeholder = ''
        self.active = True


class ResetContext(Context):
    def __init__(self):
        self.lifespan = 1
        self.name = 'ResetContext'
        self.placeholder = ''
        self.active = True

class IntentComplete(Context):
    def __init__(self):
        self.lifespan = 1
        self.name = 'IntentComplete'
        self.placeholder = ''
        self.active = True

class GetCuisine(Context):
    def __init__(self):
        self.lifespan = 1
        self.name = 'GetCuisine'
        self.placeholder = '$cuisine'
        self.active = True

class GetRestaurantLocation(Context):
    def __init__(self):
        self.lifespan = 1
        self.name = 'GetRestaurantLocation'
        self.placeholder = '$location'
        self.active = True

class GetCostrange(Context):
    def __init__(self):
        self.lifespan = 1
        self.name = 'GetCostrange'
        self.placeholder = '$costrange'
        self.active = True

class GetRestaurantName(Context):
    def __init__(self):
        self.lifespan = 1
        self.name = 'GetRestaurantName'
        self.placeholder = '$restname'
        self.active = True

class GetCabLocation(Context):
    def __init__(self):
        self.lifespan = 1
        self.name = 'GetCabLocation'
        self.placeholder = '$location'
        self.active = True

class GetLuggage(Context):
     def __init__(self):
        self.lifespan = 1
        self.name = 'GetLuggage'
        self.placeholder = '$luggage'
        self.active = True

class GetPassengers(Context):
     def __init__(self):
        self.lifespan = 1
        self.name = 'GetPassengers'
        self.placeholder = '$passengers'
        self.active = True
