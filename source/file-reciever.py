import socket
import struct
import sys

CHUNK_SIZE = 1000

# Helper function to print error and exit
def error_exit(message):
    sys.stderr.write(message + '\n')
    sys.exit(-1)

if len(sys.argv) != 4:
    error_exit("Uso: python file-receiver.py <ficheiro_destino> <porta_servidor> <tamanho_janela>")

output_file = sys.argv[1]
server_port = int(sys.argv[2])
recv_window_size = int(sys.argv[3])

if not (1 <= recv_window_size <= 32):
    error_exit("Erro: o tamanho da janela de recepcao deve estar entre 1 e 32.")

# Create UDP socket
try:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(("", server_port))
except socket.error as e:
    error_exit("Erro ao criar o socket: {}".format(e))

print("Servidor aguardando na porta {}...".format(server_port))

# Control variables
received_chunks = {}
base = 1
sender_address = None

with open(output_file, "wb") as f:
    while True:
        packet, address = server_socket.recvfrom(1024)

        if sender_address is None:
            sender_address = address
        elif sender_address != address:
            print("Pacote de origem desconhecida ignorado.")
            continue

        seq_num = struct.unpack("!I", packet[:4])[0]
        data = packet[4:]

        if seq_num < base or seq_num >= base + recv_window_size:
            print("Chunk {} fora da janela. Descartado.".format(seq_num))
            continue

        print("Recebido chunk {}".format(seq_num))
        received_chunks[seq_num] = data

        # Send ACKs
        selective_acks = 0
        for i in range(1, recv_window_size):
            if base + i in received_chunks:
                selective_acks |= (1 << (i - 1))

        ack_packet = struct.pack("!II", base, selective_acks)
        server_socket.sendto(ack_packet, sender_address)
        print("ACK enviado: base={}, selective_acks={:032b}".format(base, selective_acks))

        # Write contiguous chunks to file and advance window
        while base in received_chunks:
            f.write(received_chunks.pop(base))
            base += 1

        # End condition: all chunks received and written
        if len(data) < CHUNK_SIZE:
            print("Ultimo chunk recebido. Transferencia concluida.")
            break

server_socket.close()
