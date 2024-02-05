# Networking Class Projects
#### This respository contains 3 projects from my networking module.

## 1. Data Integrity Checker and Binary Packet Extractor

### Features:
Checksum.py
- The checksum.py script calculates the CRC32 checksum of the content of a file specified as a command-line argument.
- This could be useful in scenarios where data integrity needs to be verified, as the CRC32 checksum provides a way to detect errors or corruption in the file.

PacketExtr.py
- The packetextr.py script is designed to extract and process binary data packets from the standard input.
- The data packets follow a specific protocol with a 6-byte header and size information, allowing the script to delineate and extract individual packets.

## 2. UnreliNET

This project showcases the implementation of a basic reliable data transfer protocol over an unreliable network. It employs sequence numbers, checksums, and acknowledgments (ACKs) to ensure data integrity in the face of an unreliable communication channel.

### Features:

- Reliable data transfer with sequence numbers.
- Checksums for data integrity validation.
- ACKs to confirm successful packet reception.

## 3. WebServer

This project involves the implementation of a TCP-based server that communicates with clients using an HTTP-like protocol. It's designed to function over an unreliable channel, demonstrating the resilience of the underlying communication architecture.

### Features:

- TCP-based server implementation.
- Communication using an HTTP-like protocol.
- Resilience to an unreliable communication channel.
