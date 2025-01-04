from geopy.geocoders import Nominatim
def geopy_location(latitide, longitude):
    geolocator = Nominatim(user_agent="my_app")
    location = geolocator.reverse(f"{latitide}, {longitude}")
    return location