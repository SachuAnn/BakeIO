import math

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees) using Haversine formula.
    """
    # Convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

def estimate_eta(distance_km):
    """
    Estimate delivery time in minutes based on distance.
    Formula: 10 mins prep/fixed + 3 mins per km.
    """
    if distance_km is None:
        return "20-30"
    
    base_time = 10
    travel_time = distance_km * 3
    total_min = int(base_time + travel_time)
    
    # Return a range
    return f"{total_min}-{total_min + 5}"
