from geocoder import ip

def geoloc(command):
    g = ip('me')
    return f"Geolocation retrieved from ip : {g.ip}\ncity: {g.city}\ncountry: {g.country}\nlat: {g.latlng[0]}\nlong: {g.latlng[1]}"

OK = "[+]"
