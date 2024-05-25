
import argparse
import os
import sys
import venv
from pathlib import Path
from subprocess import Popen, PIPE, TimeoutExpired
from threading import Thread
from urllib.parse import urlparse
from urllib.request import urlretrieve
# /*
#  * Author: Group 10 : Gia Bao - Hoang Son - Duy Doan - The Anh
#  *
#  * Description: set up moi truong cho  program
#  */


PACKAGE_FILENAME = 'packages.txt'


def system_cmd(cmd: list, exec_time):
    """
     Thực thi lệnh shell hệ thống và trả về kết quả đầu ra. Nếu kiểu dữ liệu không đúng trong cú pháp lệnh
     danh sách hoặc lỗi xảy ra trong quá trình thực thi lệnh, lỗi được hiển thị qua stderr và được ghi lại,
     và Sai được trả về hoạt động thất bại được chỉ định.
     :param cmd: Lệnh sẽ được thực thi.
     :param exec_time: Thời gian chờ thực thi để ngăn quá trình bị treo.
     """
    try:
        # Thiết lập tiến trình con trong trình quản lý bối cảnh, dẫn đầu ra và lỗi để trả về các biến #
        with Popen(cmd, stdout=sys.stdout, stderr=sys.stderr) as command:
            # Thực thi quá trình hết thời gian chờ (None=blocking) #
            command.communicate(timeout=exec_time)

    # Nếu quá trình hết thời gian #
    except TimeoutExpired:
        # Lỗi in và nhật ký log #
        print_err(f'Process for {cmd} timed out before finishing execution')

    # Nếu lệnh nhập có dữ liệu khác chuỗi #
    except TypeError:
        # Lỗi in và nhật ký log #
        print_err(f'Input in {cmd} contains data type other than string')


class ExtendedEnvBuilder(venv.EnvBuilder):
    """
     Trình tạo này cài đặt setuptools và pip để bạn có thể pip hoặc easy_install các gói khác
     vào môi trường ảo đã tạo.
     :param gật đầu: Nếu đúng, setuptools và pip không được cài đặt vào ảo đã tạo
     môi trường.
     :param nopip: Nếu đúng, pip chưa được cài đặt vào môi trường ảo đã tạo.
     :param tiến trình: Nếu setuptools hoặc pip được cài đặt, tiến trình cài đặt có thể
     được theo dõi bằng cách chuyển một tiến trình có thể gọi được. Nếu được chỉ định, nó được gọi với
     hai đối số: một chuỗi biểu thị một số tiến trình và một ngữ cảnh biểu thị
     chuỗi đến từ đâu. Đối số bối cảnh có thể có một trong ba
     các giá trị: 'chính', cho biết rằng nó được gọi từ chính virtualize() và
     'stdout' và 'stderr', có được bằng cách đọc các dòng từ đầu ra
     các luồng của quy trình con được sử dụng để cài đặt ứng dụng. Nếu một cuộc gọi được là
     không được chỉ định, thông tin tiến trình mặc định sẽ được xuất ra sys.stderr.
     """
    def __init__(self, *args, **kwargs):
        self.nodist = kwargs.pop('nodist', False)
        self.nopip = kwargs.pop('nopip', False)
        self.progress = kwargs.pop('progress', None)
        self.verbose = kwargs.pop('verbose', False)
        super().__init__(*args, **kwargs)

    def install_setuptools(self, context):
        """
         Cài đặt setuptools trong môi trường ảo.
         :param context: Thông tin cho yêu cầu tạo môi trường ảo.
         """
        url = 'https://github.com/abadger/setuptools/blob/master/ez_setup.py'
        self.install_script(context, 'setuptools', url)

        # Xóa kho lưu trữ setuptools được tải xuống #
        pred = lambda o: o.startswith('setuptools-') and o.endswith('.tar.gz')
        files = filter(pred, os.listdir(context.bin_path))

        # Lặp lại các tập tin trong đường dẫn bin và xóa #
        for file in files:
            file = os.path.join(context.bin_path, file)
            os.unlink(file)

    def install_pip(self, context):
        """
         Cài đặt pip trong môi trường ảo.
         :param context: Thông tin cho yêu cầu tạo môi trường ảo.
         """
        url = 'https://bootstrap.pypa.io/get-pip.py'
        self.install_script(context, 'pip', url)

    def post_setup(self, context):
        """
         Thiết lập bất kỳ gói nào cần được cài đặt sẵn vào môi trường ảo
         tạo.
         :param context: Thông tin cho yêu cầu tạo môi trường ảo.
         """
        os.environ['VIRTUAL_ENV'] = context.env_dir

        # Nếu không có công cụ thiết lập #
        if not self.nodist:
            # Cài đặt công cụ thiết lập #
            self.install_setuptools(context)

        # Nếu không có pip và setuptools #
        if not self.nopip and not self.nodist:
            # Cài đặt chúng #
            self.install_pip(context)

        # Lấy thư mục làm việc hiện tại #
        path = Path.cwd()
        venv_path = Path(context.env_dir)
        # Định dạng đường dẫn gói #
        package_path = path / PACKAGE_FILENAME

        #  Windows #
        if os.name == 'nt':
            # Định dạng đường dẫn cài đặt pip trong venv #
            pip_path = venv_path / 'Scripts' / 'pip.exe'
        #  Linux #
        else:
            # Định dạng đường dẫn cài đặt pip trong venv #
            pip_path = venv_path / 'bin' / 'pip'

        # Thực thi lệnh nâng cấp pip như tiến trình con #
        command = [str(pip_path), 'install', '--upgrade', 'pip']
        system_cmd(command, 60)

        # Nếu tệp danh sách gói tồn tại #
        if package_path.exists():
            # Thực thi pip -r vào venv dựa trên danh sách gói #
            command = [str(pip_path), 'install', '-r', str(package_path)]
            system_cmd(command, 300)

    def reader(self, stream, context):
        """
         Đọc các dòng từ luồng đầu ra của quy trình con và chuyển tới tiến trình có thể gọi được
         (nếu được chỉ định) hoặc ghi thông tin tiến trình vào sys.stderr.
         :paramstream: Luồng đầu ra của quy trình con.
         :param context: Thông tin cho yêu cầu tạo môi trường ảo.
         """
        progress = self.progress

        while True:
            # Đọc dòng từ luồng quy trình con #
            proc_stream = stream.readline()

            # Nếu không còn dữ liệu để đọc #
            if not proc_stream:
                break

            # Nếu tiến trình không có dữ liệu #
            if progress is not None:
                progress(proc_stream, context)
            # Nếu có tiến triển #
            else:
                # Nếu không được đặt thành chi tiết #
                if not self.verbose:
                    sys.stderr.write('.')
                # Nếu đặt mức độ chi tiết #
                else:
                    sys.stderr.write(proc_stream.decode('utf-8'))

                sys.stderr.flush()

        stream.close()

    def install_script(self, context, name, url):

        367 / 5.000
        """
         Truy xuất nội dung từ url được truyền và cài đặt vào env ảo.
         :param context: Thông tin cho yêu cầu tạo môi trường ảo.
         :param name: Tên tiện ích sẽ được cài đặt vào môi trường.
         :param url: Url nơi tiện ích có thể được truy xuất từ ​​internet.
       
         """
        _, _, path, _, _, _ = urlparse(url)
        file_name = os.path.split(path)[-1]
        binpath = context.bin_path
        distpath = os.path.join(binpath, file_name)

        # Nếu URL bắt đầu bằng http #
        if url.lower().startswith('http'):
            # Tải tập lệnh vào thư mục nhị phân của môi trường ảo #
            urlretrieve(url, distpath)
        # Đã phát hiện URL bất thường #
        else:
            print_err('Improper URL format attempted to be passed into urlretrieve')
            sys.exit(2)

        progress = self.progress

        if self.verbose:
            term = '\n'
        else:
            term = ''

        # Nếu tiến trình được thiết lập #
        if progress is not None:
            progress(f'Installing {name} .. {term}', 'main')
        # Nếu tiến trình ko được thiết lập #
        else:
            sys.stderr.write(f'Installing {name} .. {term}')
            sys.stderr.flush()

        args = [context.env_exe, file_name]

        # Cài đặt trong môi trường ảo #
        with Popen(args, stdout=PIPE, stderr=PIPE, cwd=binpath) as proc:
            thread_1 = Thread(target=self.reader, args=(proc.stdout, 'stdout'))
            thread_1.start()
            thread_2 = Thread(target=self.reader, args=(proc.stderr, 'stderr'))
            thread_2.start()

            proc.wait()
            thread_1.join()
            thread_2.join()

        if progress is not None:
            progress('done.', 'main')
        else:
            sys.stderr.write('done.\n')

        # Dọn dẹp - không còn cần thiết#
        os.unlink(distpath)


def print_err(msg: str):
    """
     In thông báo lỗi qua stderr.
     :param msg: Thông báo lỗi sẽ được hiển thị qua stderr.
     """
    print(f'\n* [ERROR] {msg} *\n', file=sys.stderr)


def main(args=None):
    """
     Chạy qua các chương trình thiết lập và kiểm tra đối số khác nhau
     :param args: Không có theo mặc định, nhưng có sẵn nhiều tùy chọn.
     """
    if sys.version_info < (3, 3) or not hasattr(sys, 'base_prefix'):
        raise ValueError('This script is only for use with Python 3.3 or later')

    parser = argparse.ArgumentParser(prog=__name__,
                                     description='Creates virtual Python environments in one'
                                                 ' or more target directories.')
    parser.add_argument('dirs', metavar='ENV_DIR', nargs='+',
                        help='A directory in which to create the virtual environment.')
    parser.add_argument('--no-setuptools', default=False, action='store_true', dest='nodist',
                        help='Don\'t install setuptools or pip in the virtual environment.')
    parser.add_argument('--no-pip', default=False, action='store_true', dest='nopip',
                        help='Don\'t install pip in the virtual environment.')
    parser.add_argument('--system-site-packages', default=False, action='store_true',
                        dest='system_site', help='Give the virtual environment access to the '
                             'system site-packages dir.')

    if os.name == 'nt':
        use_symlinks = False
    else:
        use_symlinks = True

    parser.add_argument('--symlinks', default=use_symlinks, action='store_true',
                        dest='symlinks', help='Try to use symlinks rather than copies, when '
                                              'symlinks are not the default for the platform.')
    parser.add_argument('--clear', default=False, action='store_true', dest='clear',
                        help='Delete the contents of the virtual environment directory if it '
                             'already exists, before virtual environment creation.')
    parser.add_argument('--upgrade', default=False, action='store_true', dest='upgrade',
                        help='Upgrade the virtual environment directory to use this version of '
                        'Python, assuming Python has been upgraded in-place.')
    parser.add_argument('--verbose', default=False, action='store_true', dest='verbose',
                        help='Display the output from the scripts which install setuptools and '
                             'pip.')
    options = parser.parse_args(args)

    if options.upgrade and options.clear:
        raise ValueError('you cannot supply --upgrade and --clear together.')

    builder = ExtendedEnvBuilder(system_site_packages=options.system_site, clear=options.clear,
                                 symlinks=options.symlinks, upgrade=options.upgrade,
                                 nodist=options.nodist, nopip=options.nopip,
                                 verbose=options.verbose)

    [builder.create(d) for d in options.dirs]


if __name__ == '__main__':
    RET = 0
    try:
        main()

    except Exception as err:
        print_err(f'Unexpected error occurred: {err}')
        RET = 1

    sys.exit(RET)
