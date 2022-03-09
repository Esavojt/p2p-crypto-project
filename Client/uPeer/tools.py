def extract_port_and_ip_from_data(data: bytes) -> tuple:
    """Extracts port and ip data from supplied data

    Returns a tuple with the remote ip address, remote port and local port

    (remote_ip, remote_port, local_port)
    """

    # Convert the supplied IPv4 address from raw bytes to str
    remote_ip = str(int.from_bytes(data[1:2], byteorder="little")) + "." + \
        str(int.from_bytes(data[2:3], byteorder="little")) + "." + \
        str(int.from_bytes(data[3:4], byteorder="little")) + "." + \
        str(int.from_bytes(data[4:5], byteorder="little"))

    # Convert the int16 from raw form
    remote_port = int.from_bytes(data[5:7], byteorder="little")
    local_port = int.from_bytes(data[7:9], byteorder="little")

    return (remote_ip, remote_port, local_port)
