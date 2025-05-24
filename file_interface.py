import os
import json
import base64
from glob import glob

class FileInterface:
    def __init__(self):
        # Tentukan direktori files/ relatif terhadap direktori kerja saat ini
        self.files_dir = os.path.join(os.getcwd(), 'files')
        # Buat direktori files/ jika belum ada
        if not os.path.exists(self.files_dir):
            os.makedirs(self.files_dir)

    def list(self, params=[]):
        try:
            # Gunakan path absolut ke direktori files/
            filelist = glob(os.path.join(self.files_dir, '*.*'))
            # Ekstrak hanya nama file, bukan path lengkap
            filelist = [os.path.basename(f) for f in filelist]
            return {
                'status': 'OK',
                'data': filelist
            }
        except Exception as e:
            return {
                'status': 'ERROR',
                'data': str(e)
            }

    def get(self, params=[]):
        try:
            filename = params[0]
            if not filename:
                return {
                    'status': 'ERROR',
                    'data': 'Filename or file data is empty'
                }

            file_path = os.path.join(self.files_dir, filename)
            with open(file_path, 'rb') as file_in:
                file_content = base64.b64encode(file_in.read()).decode()

            return {
                'status': 'OK',
                'data_namafile': filename,
                'data_file': file_content
            }
        except Exception as e:
            return {
                'status': 'ERROR',
                'data': str(e)
            }

    def upload(self, params=[]):
        try:
            filename, filedata_b64 = params[0], params[1]

            if not filename or not filedata_b64:
                return {
                    'status': 'ERROR',
                    'data': 'Filename or file data is empty'
                }

            # Pastikan base64 memiliki padding yang benar
            padding = len(filedata_b64) % 4
            if padding:
                filedata_b64 += '=' * (4 - padding)

            filedata = base64.b64decode(filedata_b64)
            file_path = os.path.join(self.files_dir, filename)

            with open(file_path, 'wb') as file_out:
                file_out.write(filedata)

            return {
                'status': 'OK',
                'data_namafile': filename
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'data': str(e)
            }

    def delete(self, params=[]):
        try:
            filename = params[0]

            if not filename:
                return {
                    'status': 'ERROR',
                    'data': 'Filename is empty'
                }

            file_path = os.path.join(self.files_dir, filename)

            if os.path.exists(file_path):
                os.remove(file_path)
                return {
                    'status': 'OK',
                    'data': f'File {filename} deleted successfully'
                }

            return {
                'status': 'ERROR',
                'data': f'File {filename} not found'
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'data': str(e)
            }


if __name__ == '__main__':
    f = FileInterface()
    print(f.list())
    print(f.get(['pokijan.jpg']))