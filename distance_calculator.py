import requests
import json
from tabulate import tabulate
from urllib.parse import quote_plus

# --- Nueva función para obtener coordenadas ---
def get_coordinates(city_name, api_key):
    """
    Obtiene las coordenadas (latitud, longitud) de una ciudad
    usando la API de Geocodificación de GraphHopper.
    """
    # Asegurarse de codificar el nombre de la ciudad para la URL
    encoded_city_name = quote_plus(city_name)
    geocode_url = f"https://graphhopper.com/api/1/geocode?q={encoded_city_name}&locale=es&limit=1&key={api_key}"

    try:
        response = requests.get(geocode_url)
        response.raise_for_status()
        data = response.json()

        if data and 'hits' in data and data['hits']:
            # Tomar el primer resultado más relevante
            point = data['hits'][0]['point']
            return f"{point['lat']},{point['lng']}" # Retorna "lat,lon"
        else:
            print(f"No se encontraron coordenadas para: {city_name}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener coordenadas para {city_name}: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Error al decodificar respuesta JSON para geocodificación de {city_name}.")
        return None

# --- Función get_route_info modificada ---
def get_route_info(origin, destination, vehicle_type, api_key):
    """
    Obtiene información de la ruta (distancia, duración, narrativa)
    entre dos ciudades usando la API de GraphHopper,
    convirtiendo primero los nombres de las ciudades a coordenadas.
    """
    # Obtener coordenadas para origen y destino
    origin_coords = get_coordinates(origin, api_key)
    destination_coords = get_coordinates(destination, api_key)

    if not origin_coords or not destination_coords:
        return None, None, None, None # No se pudieron obtener las coordenadas

    # La URL de la ruta ahora usa directamente las coordenadas
    url = f"https://graphhopper.com/api/1/route?point={origin_coords}&point={destination_coords}&vehicle={vehicle_type}&key={api_key}&locale=es"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data and 'paths' in data and data['paths']:
            path = data['paths'][0]
            distance_km = path['distance'] / 1000
            distance_miles = distance_km * 0.621371
            time_ms = path['time']

            total_seconds = time_ms // 1000
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            duration_str = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

            narrative = ""
            if 'instructions' in path:
                narrative_parts = [inst['text'] for inst in path['instructions']]
                narrative = "\n".join(narrative_parts)

            return distance_km, distance_miles, duration_str, narrative
        else:
            print("No se encontraron rutas para las ciudades especificadas con las coordenadas obtenidas.")
            return None, None, None, None
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con la API de GraphHopper (ruta): {e}")
        return None, None, None, None
    except json.JSONDecodeError:
        print("Error al decodificar la respuesta JSON de la API (ruta).")
        return None, None, None, None

def main():
    api_key = "49489c0f-67bd-4e70-abd8-6d2720f2259f" # TU CLAVE API REAL

    if api_key == "TU_CLAVE_API_GRAPHHOPPER":
        print("¡ADVERTENCIA: Por favor, reemplaza 'TU_CLAVE_API_GRAPHHOPPER' con tu clave API real de GraphHopper!")
        return

    print("--- Calculadora de Distancia y Duración de Viaje ---")
    print("Las ciudades deben ser ingresadas en formato 'Ciudad, País' o 'Ciudad, Provincia, País'.")
    print("Ejemplo: 'Santiago, Chile' o 'Mendoza, Argentina'.") # Ahora el formato con coma sí es válido para la geocodificación.

    while True:
        origin_city = input("\nIngrese la Ciudad de Origen (o 's' para salir): ")
        if origin_city.lower() == 's':
            print("Saliendo de la aplicación.")
            break

        destination_city = input("Ingrese la Ciudad de Destino (o 's' para salir): ")
        if destination_city.lower() == 's':
            print("Saliendo de la aplicación.")
            break

        print("\nSeleccione el medio de transporte:")
        print("  1. Coche (car)")
        print("  2. Bicicleta (bike)")
        print("  3. A pie (foot)")
        print("  4. Autobús (bus) - ¡Puede no estar disponible en todas las regiones!")
        print("  5. Moto (motorcycle)")

        vehicle_choice = input("Ingrese el número correspondiente al medio de transporte: ")

        vehicle_map = {
            '1': 'car',
            '2': 'bike',
            '3': 'foot',
            '4': 'bus',
            '5': 'motorcycle'
        }

        vehicle_type = vehicle_map.get(vehicle_choice, 'car')
        if vehicle_type == 'car' and vehicle_choice not in ['1']:
            print("Opción de transporte inválida. Usando 'coche' por defecto.")

        print(f"\nCalculando ruta de {origin_city} a {destination_city} en {vehicle_type}...")

        # Ahora get_route_info maneja la obtención de coordenadas internamente
        distance_km, distance_miles, duration_str, narrative = get_route_info(
            origin_city, destination_city, vehicle_type, api_key
        )

        if distance_km is not None:
            table_data = [
                ["Ciudad de Origen", origin_city],
                ["Ciudad de Destino", destination_city],
                ["Medio de Transporte", vehicle_type.capitalize()],
                ["Distancia (Km)", f"{distance_km:.2f}"],
                ["Distancia (Millas)", f"{distance_miles:.2f}"],
                ["Duración del Viaje", duration_str]
            ]
            print("\n" + tabulate(table_data, headers=["Concepto", "Valor"], tablefmt="grid"))

            print("\nNarrativa del Viaje:")
            print(narrative)

        else:
            print("No se pudo obtener la información de la ruta. Intente con otras ciudades o verifique su clave API.")

if __name__ == "__main__":
    main()
