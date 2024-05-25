# /*
#  * Author: Group 10 : Gia Bao - Hoang Son - Duy Doan - The Anh
#  *
#  * Description: code giai  ma
#  */

import os
import re
import sys
from pathlib import Path

from cryptography.fernet import Fernet


def print_err(msg: str):
    """
     Hiển thị thông báo lỗi được truyền qua stderr.
     :param msg: Thông báo lỗi sẽ được hiển thị.
     """
    print(f'\n* [ERROR] {msg} *\n', file=sys.stderr)


def main():
    """
     Giải mã nội dung được mã hóa trong Thư mục DecryptDock.

     """
    encrypted_files = ['e_network_info.txt', 'e_system_info.txt',
                       'e_browser_info.txt', 'e_key_logs.txt']

    # If the OS is Windows #
    if os.name == 'nt':
        re_xml = re.compile(r'.{1,255}\.xml$')

        # Thêm bất kỳ tệp xml nào trong thư mục vào danh sách tệp được mã hóa #
        [encrypted_files.append(file.name) for file in os.scandir(decrypt_path)
         if re_xml.match(file.name)]

        encrypted_files.append('e_clipboard_info.txt')
    else:
        encrypted_files.append('e_wifi_info.txt')

    key = b'T2UnFbwxfVlnJ1PWbixcDSxJtpGToMKotsjR4wsSJpM='

    # Lặp lại các tập tin cần giải mã #
    for file_decrypt in encrypted_files:
        # Đặt đường dẫn tệp được mã hóa và giải mã #
        crypt_path = decrypt_path / file_decrypt
        plain_path = decrypt_path / file_decrypt[2:]
        try:
            # Đọc dữ liệu file được mã hóa #
            with crypt_path.open('rb') as in_file:
                data = in_file.read()

            # Giải mã dữ liệu file bị mã hóa #
            decrypted = Fernet(key).decrypt(data)

            # Ghi dữ liệu đã giải mã vào tập tin mới #
            with plain_path.open('wb') as loot:
                loot.write(decrypted)

            # Xóa các tập tin được mã hóa gốc #
            crypt_path.unlink()

        # Nếu file IO xảy ra lỗi #
        except OSError as io_err:
            print_err(f'Error occurred during {file_decrypt} decryption: {io_err}')
            sys.exit(1)


if __name__ == '__main__':
    # Lấy thư mục làm việc hiện tại #
    decrypt_path = Path.cwd() / 'DecryptDock'

    # Nếu dock tập tin giải mã không tồn tại #
    if not decrypt_path.exists():
        # Tạo DecryptDock bị thiếu #
        decrypt_path.mkdir()
        # In thông báo lỗi và thoát #
        print_err('DecryptDock created due to not existing .. place encrypted components in it '
                  'and restart the program')
        sys.exit(1)

    try:
        main()

    except KeyboardInterrupt:
        print('* Ctrl + C detected...program exiting *')

    sys.exit(0)
