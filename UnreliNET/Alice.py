import zlib, sys, socket, math

def create_packet(seq_num, data):
    checksum = hex(zlib.crc32(data))[2:].zfill(8)
    packet = str(seq_num).encode() + checksum.encode() + data
    return packet

def send_packet(packet, dest_port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(packet, ('localhost', dest_port))
    except socket.error as e:
        print(f"Error sending packet: {e}")

def create_packets(message, packet_size):
    return [message[i:i+packet_size] for i in range(0, len(message), packet_size)]

def main(dest_port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        message = sys.stdin.buffer.read()
        sequence_number = 0
        packet_size = 55  # Define the packet size, decided to use 55 cuz im using 8 bit for checksum in hex :)
        max_retransmissions = 4
        packets = create_packets(message, packet_size)

        for i, pkt in enumerate(packets):
            final_pkt = create_packet(sequence_number, pkt)
            retransmissions = 0

            while True:
                s.settimeout(0.05)
                try:
                    s.sendto(final_pkt, ('localhost', dest_port))

                    ack_sequence, address = s.recvfrom(64)

                    if ack_sequence == str(sequence_number).encode():
                        break
                except socket.timeout:
                    s.sendto(final_pkt, ('localhost', dest_port))
                    retransmissions += 1
                    if retransmissions >= max_retransmissions:
                        #print(f"Max retransmissions reached for packet {i + 1}. Aborting.")
                        break

            if sequence_number == 0:
                sequence_number = 1
            elif sequence_number == 1:
                sequence_number = 0


if __name__ == "__main__":
    dest_port = int(sys.argv[1])
    main(dest_port)
