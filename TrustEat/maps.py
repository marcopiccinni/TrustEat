from .settings import GOOGLE_MAPS_SECRET_API_KEY
import googlemaps
import datetime


def distance_time(origin, arrival):
    gmaps = googlemaps.Client(key=GOOGLE_MAPS_SECRET_API_KEY)
    try:
        trip = gmaps.distance_matrix(origins=origin, destinations=arrival)
        return trip['rows'][0]['elements'][0]['distance']['text'], trip['rows'][0]['elements'][0]['duration']['text']
    except:
        try:
            trip = gmaps.directions(origin=origin, destination=arrival)
            return trip[0]['legs'][0]['distance']['text'], trip[0]['legs'][0]['duration']['text']
        except:
            return None, None


def geocode(address):
    gmaps = googlemaps.Client(key=GOOGLE_MAPS_SECRET_API_KEY)
    try:
        location = gmaps.geocode(address=address)
        return location[0]['geometry']['location']['lat'], location[0]['geometry']['location']['lng']
    except:
        return 0, 0
