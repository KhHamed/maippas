import requests
import geocoder
import reverse_geocoder as rg
import sys

def main():
	try:
		lat, lon = get_lat_lng_from_ip()
	except Exception as e:
		print('Error getting lat/lon:', e)
		sys.exit(1)

	print('Latitude:', lat)
	print('Longitude:', lon)

	loc = pretty_location(lat, lon)
	if loc:
		name = loc.get('name')
		admin1 = loc.get('admin1')
		cc = loc.get('cc')
		print(f"Closest place: {name}, {admin1} ({cc})")
	else:
		print('Reverse geocoding returned no result')

	try:
		weather = get_current_weather_open_meteo(lat, lon)
	except Exception as e:
		print('Error fetching weather:', e)
		sys.exit(1)

	# Open-Meteo returns current_weather with temperature (°C), windspeed, etc.
	current = weather.get('current_weather')
	if not current:
		print('No current weather data in response')
		sys.exit(1)

	temp = current.get('temperature')
	wind = current.get('windspeed')
	weather_time = current.get('time')

	print('\nCurrent weather:')
	print(f"  Time: {weather_time}")
	print(f"  Temperature: {temp} °C")
	print(f"  Wind speed: {wind} km/h")


def get_lat_lng_from_ip():
	g = geocoder.ip('me')
	lat = g.lat
	lng = g.lng
	if lat is None or lng is None:
		raise RuntimeError('Could not determine location from IP. Is internet or geocoder service available?')
	return lat, lng

def pretty_location(lat, lng):
	# reverse_geocoder expects an iterable of (lat, lon) tuples
	results = rg.search([(lat, lng)])
	if not results:
		return None
	return results[0]

def get_current_weather_open_meteo(lat, lon):
	# Open-Meteo current weather endpoint (no API key required)
	url = 'https://api.open-meteo.com/v1/forecast'
	params = {
		'latitude': lat,
		'longitude': lon,
		'current_weather': True,
		'timezone': 'auto'
	}
	resp = requests.get(url, params=params, timeout=10)
	resp.raise_for_status()
	return resp.json()


if __name__ == '__main__':
	main()

