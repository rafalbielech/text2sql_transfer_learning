import socket

def get_ip_address():
    # Get the ip address by connectingn to the port 80
    # return the ip address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def load_available_dbs(data_mapper, start, end):
    return [data_mapper[str(item)] for item in range(start, end + 1)]