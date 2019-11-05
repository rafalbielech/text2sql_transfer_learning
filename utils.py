import socket

def get_ip_address():
    # Get the ip address by connectingn to the port 80
    # return the ip address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]