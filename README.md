# /*
#  * Author: Group 10 : Gia Bao - Hoang Son - Duy Doan - The Anh
#  *
#  * Description: set up moi truong cho  program
#  */

## Chú Ý !!!!!!
> Công cụ này chỉ có thể được sử dụng cho mục đích pháp lý.<br>
> Người dùng chịu hoàn toàn trách nhiệm về mọi hành động được thực hiện bằng công cụ này.<br>
> Tác giả không chịu trách nhiệm pháp lý về những thiệt hại do công cụ này gây ra.<br>
> Nếu bạn không chấp nhận những điều khoản này thì đừng sử dụng công cụ này.


## Làm thế nào nó hoạt động
- Tạo thư mục lưu trữ thông tin tạm thời để lọc ra
- Nhận tất cả thông tin mạng cần thiết -> lưu trữ vào tệp nhật ký &ensp; (mất khoảng một phút rưỡi)
- Lấy ssid và mật khẩu của mạng không dây trong tệp dữ liệu XML
- Truy xuất phần cứng hệ thống và thông tin quy trình/dịch vụ đang chạy
- Nếu trên Windows và clipboard được kích hoạt và chứa bất cứ thứ gì -> lưu vào file log
- Lịch sử duyệt web được truy xuất dưới dạng tệp dữ liệu JSON sau đó được chuyển vào tệp nhật ký
- Sau đó sử dụng đa xử lý 4 tính năng hoạt động đồng thời trong khoảng thời gian mặc định là 5 phút:

1. Ghi lại các phím đã nhấn
2. Chụp ảnh màn hình cứ sau 5 giây
3. Ghi micro theo từng đoạn một phút
4. Chụp ảnh webcam 5 giây một lần

- Sau khi tất cả các file .txt và .xml được nhóm lại với nhau và mã hóa để bảo vệ dữ liệu nhạy cảm
- Sau đó theo thư mục riêng, các tập tin được nhóm lại và gửi qua email theo loại tập tin với phép thuật biểu thức chính quy
- Cuối cùng, thư mục Log bị xóa và chương trình lặp lại từ đầu để lặp lại quá trình tương tự


## Điều kiện tiên quyết
Chương trình này chạy trên Windows 10 và Linux dựa trên Debian, được viết bằng Python 3.8 và được cập nhật lên phiên bản 3.10.6

## Cài đặt
- Chạy tập lệnh setup.py để xây dựng môi trường ảo và cài đặt tất cả các gói bên ngoài trong venv đã tạo.

> Ví dụ:<br>
> &emsp;&emsp;- Windows: `python setup.py venv`<br>
> &emsp;&emsp;- Linux: `python3 setup.py venv`

- Khi env ảo được xây dựng sẽ đi qua thư mục (Scripts-Windows hoặc bin-Linux) trong thư mục môi trường vừa tạo.
- Đối với Windows, trong thư mục venv\Scripts, thực thi tập lệnh `activate` hoặc `activate.bat` để kích hoạt môi trường ảo.
- Đối với Linux, trong thư mục venv/bin thực thi `source activate` để kích hoạt môi trường ảo.
- Nếu vì lý do nào đó mà tập lệnh thiết lập gặp sự cố, giải pháp thay thế là tạo môi trường theo cách thủ công, kích hoạt nó, sau đó chạy pip install -r packages.txt trong thư mục gốc của dự án.
- Để thoát khỏi môi trường ảo khi hoàn tất, hãy thực hiện `hủy kích hoạt`.

## Cách sử dụng
- Trong tài khoản google thiết lập xác thực đa yếu tố và tạo mật khẩu ứng dụng cho Gmail để cho phép sử dụng API
- Khi bắt đầu hàm send_mail(), hãy nhập email đầy đủ của bạn (tên người dùng@gmail.com) và mật khẩu ứng dụng đã tạo
- Mở cửa sổ lệnh và chạy chương trình
- Thay đổi thư mục chứa chương trình và thực hiện nó
- Mở trình quản lý tệp đồ họa và vào thư mục được đặt ở đầu hàm main() để xem chương trình đang hoạt động
- Sau khi các tập tin được mã hóa và gửi đến email, hãy tải chúng xuống và đặt chúng vào thư mục được chỉ định trong
 decryptFile.py và chạy chương trình trong dấu nhắc lệnh.

## Bố cục chức năng
-- the_advanced_keylogger.py --
> smtp_handler &nbsp;-&nbsp; Tạo điều kiện thuận lợi cho việc gửi email có dữ liệu được mã hóa để lọc.

-- the_advanced_keylogger.py --

smtp_handler - Tạo điều kiện thuận lợi cho việc gửi email có dữ liệu được mã hóa để lọc.

email_attach - Tạo đối tượng đính kèm email và trả về nó.

email_header - Định dạng tiêu đề và nội dung email.

send_mail - Tạo điều kiện thuận lợi cho việc gửi email theo kiểu phân đoạn dựa trên các kết quả phù hợp với biểu thức chính quy.

Encrypt_data - Mã hóa tất cả dữ liệu tệp trong danh sách tham số của tệp sẽ được lọc.

RegObject - Đối tượng Regex chứa nhiều biểu thức được biên dịch được nhóm lại với nhau.

webcam - Chụp ảnh webcam cứ năm giây một lần.

micrô - Tích cực ghi âm micrô trong khoảng thời gian 60 giây.

ảnh chụp màn hình - Chụp ảnh màn hình cứ năm giây một lần.

log_keys - Phát hiện và ghi lại các phím được người dùng nhấn.

get_browser_history - Lấy tên người dùng trình duyệt, đường dẫn đến cơ sở dữ liệu trình duyệt và toàn bộ lịch sử trình duyệt.

get_clipboard - Thu thập nội dung của clipboard và ghi đầu ra vào tệp đầu ra của clipboard.

get_system_info - Chạy một loạt lệnh để thu thập thông tin hệ thống và phần cứng. Tất cả đầu ra được chuyển hướng đến tệp đầu ra thông tin hệ thống.

linux_wifi_query - Chạy các lệnh nmcli để truy vấn danh sách SSID Wi-Fi mà hệ thống đã gặp phải. Danh sách SSID sau đó được lặp lại từng dòng để truy vấn từng cấu hình bao gồm mật khẩu. Tất cả đầu ra được chuyển hướng đến tệp đầu ra thông tin Wi-Fi.

get_network_info - Chạy một loạt lệnh để truy vấn thông tin mạng, chẳng hạn như cấu hình mạng, mật khẩu, cấu hình ip, bảng arp, bảng định tuyến, cổng tcp/udp và cố gắng truy vấn API ipify.org cho địa chỉ IP công cộng. Tất cả đầu ra được chuyển hướng đến tệp đầu ra thông tin mạng.

main - Thu thập thông tin mạng, nội dung clipboard, lịch sử trình duyệt, bắt đầu đa xử lý, gửi kết quả được mã hóa, dọn sạch dữ liệu đã lọc và lặp lại từ đầu.

print_err - Hiển thị thông báo lỗi được truyền qua stderr.

-- decrypt_file.py --

print_err - Hiển thị thông báo lỗi được truyền qua stderr.

main - Giải mã nội dung được mã hóa trong Thư mục DecryptDock.

Mã thoát
-- the_advanced_keylogger.y & decrypt_file.py --

0 - Thao tác thành công
1 - Xảy ra lỗi không mong muốn

