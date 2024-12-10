import socket
import os
import struct
import sys
import time

CHUNK_SIZE = 1000
TIMEOUT = 1  # Timeout in seconds
MAX_TIMEOUTS = 3

# Helper function to print error and exit
def error_exit(message):
    sys.stderr.write(message + '\n')
    sys.exit(-1)

if len(sys.argv) != 5:
    error_exit("Uso: python file-sender.py <ficheiro> <host_servidor> <porta_servidor> <tamanho_janela>")

file_path = sys.argv[1]
server_host = sys.argv[2]
server_port = int(sys.argv[3])
send_window_size = int(sys.argv[4])

if not os.path.isfile(file_path):
    error_exit("Erro: o ficheiro '{}' nao existe.".format(file_path))

if not (1 <= send_window_size <= 32):
    error_exit("Erro: o tamanho da janela de envio deve estar entre 1 e 32.")

# Create UDP socket
try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(TIMEOUT)
except socket.error as e:
    error_exit("Erro ao criar o socket: {}".format(e))

# Read file and split into chunks
with open(file_path, "rb") as f:
    file_chunks = []
    seq_num = 1
    while True:
        data = f.read(CHUNK_SIZE)
        if not data:
            break
        file_chunks.append((seq_num, data))
        seq_num += 1

num_chunks = len(file_chunks)
print("Numero total de chunks: {}".format(num_chunks))

# Control variables
base = 0
next_seq_num = 0
timeouts = 0
acked = [False] * num_chunks

while base < num_chunks:
    # Send chunks within the window
    while next_seq_num < base + send_window_size and next_seq_num < num_chunks:
        seq, chunk = file_chunks[next_seq_num]
        packet = struct.pack("!I", seq) + chunk
        client_socket.sendto(packet, (server_host, server_port))
        print("Enviado chunk {}".format(seq))
        next_seq_num += 1

    try:
        # Wait for ACKs
        while True:
            ack_packet, _ = client_socket.recvfrom(8)
            ack_base, selective_acks = struct.unpack("!II", ack_packet)

            if ack_base > base:
                for i in range(base, ack_base):
                    acked[i] = True
                base = ack_base
                print("ACK recebido para base: {}".format(base))

            # Process selective ACKs
            for i in range(32):
                if selective_acks & (1 << i):
                    index = base + i + 1
                    if index < num_chunks:
                        acked[index] = True

            # Advance the window
            while base < num_chunks and acked[base]:
                base += 1

            timeouts = 0
    except socket.timeout:
        # Handle timeout
        timeouts += 1
        print("Timeout! Retransmitindo chunks nao confirmados.")
        if timeouts >= MAX_TIMEOUTS:
            error_exit("Maximo de timeouts atingido. Abortando transmissao.")
        for i in range(base, min(base + send_window_size, num_chunks)):
            if not acked[i]:
                seq, chunk = file_chunks[i]
                packet = struct.pack("!I", seq) + chunk
                client_socket.sendto(packet, (server_host, server_port))

print("Transmissao concluida com sucesso!")
client_socket.close()
