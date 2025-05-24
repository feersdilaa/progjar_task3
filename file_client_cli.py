import socket
import json
import base64
import logging
import os
import shlex # Import shlex for robust command parsing

server_address = ('172.16.16.103', 45000) 

def send_command(command_payload):
    """
    Mengirim perintah JSON ke server dan menerima respons.
    command_payload: dict, berisi 'command' dan 'params'.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(server_address)
        logging.warning(f"connecting to {server_address}")
        logging.warning(f"sending message ")

        # Mengubah payload perintah menjadi string JSON dan menambahkan delimiter
        command_json_str = json.dumps(command_payload) + '\r\n\r\n'
        sock.sendall(command_json_str.encode())

        data_received = ""
        while True:
            # Menerima data secara bertahap
            data = sock.recv(8192) # Ukuran buffer ditingkatkan
            if data:
                data_received += data.decode()
                # Cek apakah delimiter akhir pesan sudah diterima
                if "\r\n\r\n" in data_received:
                    break
            else:
                # Tidak ada data lagi, hentikan proses
                break
        
        # Mengurai respons JSON dari server
        # Asumsi respons server juga diakhiri dengan '\r\n\r\n'
        # Hapus delimiter sebelum parsing JSON
        if "\r\n\r\n" in data_received:
            data_received = data_received.split("\r\n\r\n", 1)[0]

        hasil = json.loads(data_received)
        logging.warning("data received from server:")
        return hasil
    except ConnectionRefusedError:
        logging.error(f"Error: Connection refused. Is the server running at {server_address}?")
        return False
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON response from server: {e}. Received: '{data_received}'")
        return False
    except Exception as e:
        logging.error(f"Error during data sending/receiving: {e}")
        return False
    finally:
        sock.close() # Pastikan socket selalu ditutup

def remote_list():
    command_payload = {
        'command': 'LIST',
        'params': []
    }
    hasil = send_command(command_payload)
    if hasil and hasil.get('status') == 'OK':
        print("daftar file : ")
        if 'data' in hasil and isinstance(hasil['data'], list):
            for nmfile in hasil['data']:
                print(f"- {nmfile}")
        else:
            print("Tidak ada file yang terdaftar atau format data tidak valid.")
        return True
    else:
        print(f"Gagal: {hasil.get('message', 'Unknown error') if hasil else 'No response from server'}")
        return False

def remote_get(filename=""):
    command_payload = {
        'command': 'GET',
        'params': [filename]
    }
    hasil = send_command(command_payload)
    if hasil and hasil.get('status') == 'OK':
        try:
            namafile = hasil['data_namafile']
            isifile_b64 = hasil['data_file']
            isifile = base64.b64decode(isifile_b64)
            download_dir = 'downloads'
            os.makedirs(download_dir, exist_ok=True)
            local_filepath = os.path.join(download_dir, namafile)

            with open(local_filepath, 'wb+') as fp:
                fp.write(isifile)
            print(f"File '{namafile}' berhasil diunduh ke '{local_filepath}'.")
            return True
        except Exception as e:
            print(f"Error saat menyimpan file '{filename}': {e}")
            return False
    else:
        # Menampilkan pesan error dari server jika ada
        print(f"Gagal: {hasil.get('message', 'Unknown error') if hasil else 'No response from server'}")
        return False
        
def remote_upload(filename=""):
    if not os.path.exists(filename):
        print(f"File lokal '{filename}' tidak ditemukan.")
        return False

    try:
        with open(filename, "rb") as fp:
            file_content = fp.read()
        encoded_content = base64.b64encode(file_content).decode('utf-8')
        command_payload = {
            'command': 'UPLOAD',
            'params': [os.path.basename(filename), encoded_content]
        }
        hasil = send_command(command_payload)
        if hasil and hasil.get('status') == 'OK':
            print(f"File '{filename}' berhasil diupload.")
            return True
        else:
            print(f"Gagal upload: {hasil.get('message', 'Unknown error') if hasil else 'No response from server'}")
            return False
    except Exception as e:
        print(f"Error saat upload: {e}")
        return False
        
def remote_delete(filename=""):
    if not filename:
        print("Nama file tidak boleh kosong untuk DELETE.")
        return False

    command_payload = {
        'command': 'DELETE',
        'params': [filename]
    }
    hasil = send_command(command_payload)
    if hasil and hasil.get('status') == 'OK':
        print(f"File '{filename}' berhasil dihapus.")
        return True
    else:
        print(f"Gagal hapus: {hasil.get('message', 'Unknown error') if hasil else 'No response from server'}")
        return False

if __name__ == '__main__':
    command_handlers = {
        'LIST': remote_list,
        'GET': remote_get,
        'UPLOAD': remote_upload,
        'DELETE': remote_delete
    }

    while True:
        try:
            perintah = input("$ ").strip()
            if not perintah:
                continue

            tokens = shlex.split(perintah)
            cmd = tokens[0].upper() # Ambil perintah utama dan ubah ke huruf besar

            if cmd == 'EXIT':
                print("Keluar dari aplikasi.")
                break
            elif cmd in command_handlers:
                if cmd == 'LIST':
                    command_handlers[cmd]() # LIST tidak butuh parameter dari tokens
                elif len(tokens) >= 2: # GET, UPLOAD, DELETE butuh minimal 1 parameter (namafile)
                    command_handlers[cmd](tokens[1])
                else:
                    print(f"Format: {cmd} <namafile>")
            else:
                print("Perintah tidak dikenal.")
        except KeyboardInterrupt:
            print("\nKeluar dari aplikasi.")
            break
        except Exception as e:
            print(f"Terjadi kesalahan tak terduga: {e}")