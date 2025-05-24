import json
import logging

from file_interface import FileInterface

"""
* Class FileProtocol bertugas untuk memproses 
  data string dari client dan menerjemahkannya sesuai 
  protokol/aturan yang dibuat (dalam format JSON).
  
* Data yang diterima dari client berbentuk bytes, 
  lalu dikonversi menjadi string JSON, kemudian diproses.

* FileProtocol akan memanggil metode dari FileInterface 
  sesuai perintah ('command') dan parameter ('params') 
  yang diberikan dalam string JSON.
"""

class FileProtocol:
    def __init__(self):
        # Inisialisasi objek untuk menangani operasi file
        self.file_handler = FileInterface()

    def proses_string(self, input_string=''):
        # Log string yang diterima untuk diproses
        logging.warning(f"String diproses: {input_string}")
        try:
            # Parse string menjadi dictionary dari JSON
            request_data = json.loads(input_string)

            # Ambil perintah (command) dan ubah ke huruf kecil
            command = request_data.get('command', '').lower()
            logging.warning(f"Memproses command: {command}")

            # Ambil parameter (jika ada), default ke list kosong
            parameters = request_data.get('params', [])
            logging.warning(f"Parameter: {parameters}")

            # Panggil method dari file_handler sesuai nama command
            method = getattr(self.file_handler, command)
            result = method(parameters)

            # Kembalikan hasil dalam format JSON string
            return json.dumps(result)

        except Exception as error:
            # Log kesalahan jika terjadi error saat parsing atau eksekusi command
            logging.warning(f"Exception saat memproses perintah: {error}")
            return json.dumps({
                'status': 'ERROR',
                'data': str(error)
            })


if __name__ == '__main__':
    # Contoh penggunaan FileProtocol
    fp = FileProtocol()

    # Contoh input valid dalam format JSON
    print(fp.proses_string(json.dumps({"command": "list", "params": []})))
    print(fp.proses_string(json.dumps({"command": "get", "params": ["pokijan.jpg"]})))