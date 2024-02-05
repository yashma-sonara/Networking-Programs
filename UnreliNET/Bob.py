import socket
import zlib
import sys

def extract_data(packet):
    # Extract data from a received packet
    sequence_number = packet.decode()[0]
    checksum = packet.decode()[1:9]
    data = packet[9:64]
    return sequence_number, checksum, data

def create_ack(sequence_number):
    # Create an ACK packet
    header = f"{sequence_number:04d}ACK"  # Indicates ACK packet
    packet = header.encode()
    return packet

def send_ack(packet, sender_address, unreliNetPort):
    # Send an ACK packet to Alice
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(packet, ('localhost', unreliNetPort))
    except socket.error as e:
        print(f"Error sending ACK packet: {e}")

def validate_checksum(data, received_checksum):
    # Calculate checksum for received data and compare it to the received checksum
    calculated_checksum = hex(zlib.crc32(data))[2:].zfill(8)
    return calculated_checksum == received_checksum

def main(rcvPort):

    expected_sequence_number = 0
    prev_ack = 0
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(('localhost', rcvPort))
        sender_address = ('localhost', rcvPort)
        while True:
            packet, sender = s.recvfrom(64)
            #print("B got p")# Adjust buffer size as needed
            #if packet[4:8] == b'ACK':
             #   continue
            sequence_number, checksum, data = extract_data(packet)
            #print("received" + str(data)))
            # Check if the packet is an ACK sent by Bob
            if sender == sender_address and data == b'ACK':
                continue  # Ignore ACK packets sent by Bob

            #print("before validation")
            if validate_checksum(data, checksum):
                #print("validated")
                if sequence_number == str(expected_sequence_number):
                    # Print the recieived message from Alice
                    #print("send ack")
                    sys.stdout.write(data.decode())
                    sys.stdout.flush()
                    #print("send ack")
                    s.sendto(str(expected_sequence_number).encode(), sender)
                    #send_ack(str(expected_sequence_number).encode(), sender_address, rcvPort)
                    if expected_sequence_number == 0:
                        expected_sequence_number = 1
                    elif expected_sequence_number == 1:
                        expected_sequence_number = 0
                                        #print("finish pkt")

                else:
                    # Handle out-of-order data packets or duplicatesi
                    #print("sending prev ack")
                    send_ack(str(prev_ack).encode(), sender_address, rcvPort)
                    if prev_ack == 0:
                        prev_ack = 1
                    elif prev_ack == 1:
                        prev_ack = 0

            else:
                #print("Bob received a corrupted data packet from Alice")
                send_ack(str(prev_ack).encode(), sender_address, rcvPort)
                if prev_ack == 0:
                    prev_ack = 1
                elif prev_ack == 1:
                    prev_ack = 0


if __name__ == "__main__":
    rcvPort = int(sys.argv[1])  # Get the receiving port from the command line
    main(rcvPort)
