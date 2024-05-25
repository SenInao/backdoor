from psutil import net_connections

def listconnections(command):
    command.progress = f"{OK} Retrieving active network connections"

    connections = net_connections()
    result = []

    for conn in connections:
        result.append(f"Family: {conn.family}, Type: {conn.type}, Local Address: {conn.laddr}, Remote Address: {conn.raddr}, Status: {conn.status}, PID: {conn.pid}")

    return "\n".join(result)

OK = "[+]"
