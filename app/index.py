import math
import random
import string
from datetime import datetime
from flask import redirect, render_template, request, session, jsonify, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from app import app, login, dao, utils, oauth
from app.models import LoaiTaiKhoan
from app.vnpay import vnpay


@app.route("/")
def trang_chu():
    kw = request.args.get('kw')
    theloai_id = request.args.get('theloai')
    page = request.args.get('page')
    price_range = request.args.get('price_range')
    order = request.args.get('order')
    if order == 'manual':
        order = None
    min_price = None
    max_price = None
    if price_range:
        price = price_range.split(':')
        min_price = int(price[0])
        max_price = (price[1])
        if max_price == 'max':
            max_price = None
        else:
            max_price = int(max_price)
    sanphams = {}
    page_size = app.config['PAGE_SIZE']
    if page is None:
        page = 1
    if kw:
        sanpham = dao.get_sanpham(kw=kw, theloai_id=theloai_id, page=page, min_price=min_price, max_price=max_price,
                            order=order)
        num = len(dao.get_sanpham(kw, theloai_id, min_price, max_price))
        return render_template('timkiem.html', sanpham=sanpham, pages=math.ceil(num / page_size), page=page, kw=kw,
                               price_range=price_range, order=order)
    if theloai_id is None:
        theloai = dao.get_the_loai()
        """
        sanphams = {
            "1": [{
                "sanpham_id": "1",
                "tensanpham": "Iphone 5S"
            },
                {
                "sanpham_id": "2",
                "tensanpham": "Iphone 8 Plus"
                }
            ],
            "2": [{

            }]
        }
        """
        for t in theloai:
            sanpham = dao.get_sanpham(kw, t.id, page, 5)  # điện thoại = nhiều điện thoại cho 1 thể loại
            sanphams[t.id] = []
            for s in sanpham:
                sanphams[t.id].append({
                    "id": s.id,
                    "tensanpham": s.tensanpham,
                    "gia": s.gia,
                    "anhbia": s.anhbia,
                    "soluongtonkho": s.soluongtonkho
                })
        return render_template('index.html', sanpham=sanphams)
    sanpham = dao.get_sanpham(kw=kw, theloai_id=theloai_id, page=page, min_price=min_price, max_price=max_price, order=order)
    print(sanpham)
    sanphams = {}
    sanphams[theloai_id] = []
    for s in sanpham:
        sanphams[theloai_id].append({
            "id": s.id,
            "tensanpham": s.tensanpham,
            "gia": s.gia,
            "anhbia": s.anhbia,
            "soluongtonkho": s.soluongtonkho
        })
    theloai = dao.get_the_loai(theloai_id)
    num = len(dao.get_sanpham(kw=None, theloai_id=theloai_id, min_price=min_price, max_price=max_price, order=order))

    return render_template('theloai.html', sanpham= sanphams, t=theloai, pages=math.ceil(num / page_size), page=page,
                           price_range=price_range, order=order)


@app.route('/admin/login', methods=['post'])
def admin_login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = dao.auth_user(username=username, password=password, loaitaikhoan=LoaiTaiKhoan.ADMIN, email=None)
    if user:
        login_user(user=user)
        session['user_role'] = "ADMIN"
    return redirect('/admin')

@app.route('/dangnhap', methods=['get', 'post'])
def dang_nhap():
    msg = request.args.get('msg', '')
    if request.method == "GET":
        if msg != '':
            return render_template('dangnhap.html', msg=msg)
        return render_template('dangnhap.html')
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        next_page = request.args.get('next')
        user = dao.auth_user(username=None, password=password, loaitaikhoan=LoaiTaiKhoan.KHACHHANG, email=email)
        if type(user) is str:
            return render_template('dangnhap.html', msg=user)
        else:
            login_user(user=user)
            session['user_role'] = "KHACHHANG"

            print(next_page)
            if next_page:
                print("hello")
                return redirect(next_page)
            return redirect('/')


@app.route('/google/login')
def google_login():
    google = oauth.create_client('google')
    redirect_uri = url_for('google_authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/login/google/authorize')
def google_authorize():
    try:
        google = oauth.create_client('google')
        token = google.authorize_access_token()
        user_info = google.get('userinfo').json()
        email = user_info['email']
        user = dao.get_tk_khach_hang_by_email(email)
        if not user:
            print("hello")
            name = user_info['name']
            id = user_info['id']
            hash_tag = dao.get_so_luong_tk_khach_hang() + 1
            username = "#" + str(hash_tag) + " " + name
            password = id[3:8]
            dao.add_tk_khach_hang(name=name, email=email, username=username, password=password)
            user = dao.get_tk_khach_hang_by_email(email)
            login_user(user=user)
        else:
            print("hello")
            login_user(user=user)
            session['user_role'] = "KHACHHANG"
    except Exception as error:
        print(error)
    return redirect(url_for('trang_chu'))


@app.route('/dangxuat')
def dang_xuat():
    logout_user()
    del session['user_role']
    return redirect('/')


@app.route('/nhanvien/logout')
def nhan_vien_dang_xuat():
    logout_user()
    del session['user_role']
    if "giosanpham" in session:
        del session['giosanpham']
    return redirect('/nhanvien')


@app.route('/otp', methods=['get', 'post'])
def otp():
    referrer = request.referrer
    if referrer and ('otp' in referrer or 'dangky' or 'quenmatkhau' in referrer):
        email = session['email']
        otp = session['otp']
        otp = str(otp)
        if request.method == "GET":
            msg = "Mã xác thực tài khoản của bạn là: " + otp
            subject = "Email xác nhận tài khoản"
            utils.send_mail(email, msg, subject)
            return render_template("otp.html")
        if request.method == "POST":
            input_otp = request.form.get('input_otp')
            next_page = request.args.get('next')
            if otp == input_otp:
                if next_page:
                    session['doimatkhau'] = True
                    del session['otp']
                    return redirect(next_page)
                else:
                    username = session['username']
                    password = session['password']
                    name = session['name']
                    dao.add_tk_khach_hang(name, email, username, password)
                    del session['otp']
                    del session['name']
                    del session['email']
                    del session['username']
                    del session['password']
                    return redirect(url_for('dang_nhap', msg="Tài khoản đã được dăng ký thành công!"))
            else:
                return render_template("otp.html", msg="Nhập sai mã otp")


@app.route('/dangky', methods=['get', 'post'])
def dang_ky():
    if request.method == "GET":
        return render_template('dangky.html')
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        msg = dao.check_tai_khoan(email, username)
        if msg:
            return render_template("dangky.html", msg=msg)
        random_number = random.randint(10000, 99999)
        session['otp'] = random_number
        session['name'] = name
        session['email'] = email
        session['username'] = username
        session['password'] = password
        return redirect('/otp')


@app.route("/quenmatkhau", methods=['get', 'post'])
def quen_mat_khau():
    msg = request.args.get('msg')
    if request.method == "POST":
        otp = random.randint(10000, 99999)
        email = request.form.get("email")
        check = dao.get_tk_khach_hang_by_email(email)
        if not check:
            return redirect(url_for('quen_mat_khau', msg="Tài khoản không tồn tại!"))
        session['otp'] = otp
        session['email'] = email
        return redirect(url_for("otp", next="/quenmatkhau"))
    doimatkhau = False
    if 'doimatkhau' in session and session['doimatkhau'] is True:
        doimatkhau = True
    return render_template("quenmatkhau.html", doimatkhau=doimatkhau, msg=msg)


@app.route("/doimatkhau", methods=['post'])
def doi_mat_khau():
    password = request.form.get('password')
    email = session['email']
    dao.doi_mat_khau_tk_khach_hang(email, password)
    del session['doimatkhau']
    return redirect(url_for("dang_nhap", msg="Mật khẩu được thay đổi thành công"))


@app.route("/api/cart", methods=['post'])
def add_to_cart():
    data = request.json

    sanpham_id = str(data.get("sanpham_id"))
    soluong = int(data.get("soluong"))
    khachhang_id = current_user.id
    dao.add_gio_hang(khachhang_id, sanpham_id, soluong)

    """
        {
            "1": {
                "id": "1",
                "name": "...",
                "price": 123,
                "quantity": 2
            },  "2": {
                "id": "2",
                "name": "...",
                "price": 1234,
                "quantity": 1
            }
        }
    """

    return jsonify(dao.get_total_gio_hang(current_user.id))


@app.route("/api/cart/<product_id>", methods=['put'])
def update_cart(product_id):
    cart = dao.get_gio_hang(current_user.id)
    if cart and product_id in cart:
        soluong = request.json.get('soluong')
        dao.update_gio_hang(current_user.id, product_id, soluong)
    return jsonify(dao.get_total_gio_hang(current_user.id))


@app.route("/api/cart/<product_id>", methods=['delete'])
def delete_cart(product_id):
    cart = dao.get_gio_hang(current_user.id)
    if cart and product_id in cart:
        dao.delete_sanpham_gio_hang(current_user.id, product_id)
    return jsonify(dao.get_total_gio_hang(current_user.id))


@app.route('/giohang')
@login_required
def gio_hang():
    if current_user.user_role == LoaiTaiKhoan.KHACHHANG:
        giohang = dao.get_gio_hang(current_user.id)
        msg = request.args.get('msg')
        soluongtonkho = {}
        for g in giohang.values():
            sanpham = dao.get_sanpham_by_id(g['sanpham_id'])
            soluongtonkho[g['sanpham_id']] = sanpham.soluongtonkho
        return render_template("giohang.html", gioHang=giohang, msg=msg, soluongtonkho=soluongtonkho)
    else:
        return ("Có vẻ đã có lỗi xảy ra!")

 #vnpay
@app.route('/vnpay/payment', methods=['GET', 'POST'])
def payment():
    referrer = request.referrer
    if request.method == 'POST':
        # Process input data and build URL payment
        order_type = request.form['order_type']
        order_id = request.form['order_id']
        amount = float(request.form['amount'].replace(',', ''))
        order_desc = request.form['order_desc']
        bank_code = request.form['bank_code']
        language = request.form['language']
        ipaddr = request.remote_addr

        # Build URL Payment
        vnp = vnpay()  # Replace Vnpay() with the actual Vnpay object from your library
        vnp.requestData['vnp_Version'] = '2.1.0'
        vnp.requestData['vnp_Command'] = 'pay'
        vnp.requestData['vnp_TmnCode'] = 'X05C9ARB'  # Replace with your TMN code I7B7Y3V2
        vnp.requestData['vnp_Amount'] = int(amount * 100)
        vnp.requestData['vnp_CurrCode'] = 'VND'
        vnp.requestData['vnp_TxnRef'] = order_id
        vnp.requestData['vnp_OrderInfo'] = order_desc
        vnp.requestData['vnp_OrderType'] = order_type

        # Check language, default: vn
        if language and language != '':
            vnp.requestData['vnp_Locale'] = language
        else:
            vnp.requestData['vnp_Locale'] = 'vn'

        # Check bank_code, if bank_code is empty, the customer will select a bank on VNPAY
        if bank_code and bank_code != "":
            vnp.requestData['vnp_BankCode'] = bank_code

        vnp.requestData['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')
        vnp.requestData['vnp_IpAddr'] = ipaddr
        vnp.requestData['vnp_ReturnUrl'] = 'http://localhost:5000/payment_return'  # Replace with your return URL
        vnpay_payment_url = vnp.get_payment_url('https://sandbox.vnpayment.vn/paymentv2/vpcpay.html',
                                                'DZGERGFXNBOUCRHIKYOQJTRSNIMTRTLA')  # Replace with your payment URL and hash secret key
        # print(vnpay_payment_url) FCSMFKVRWSMMEXPIZQAVFGPUXTGVYUGS

        # Redirect to VNPAY
        return redirect(vnpay_payment_url)
    elif referrer and 'giohang' in referrer:
        id = current_user.id
        random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        hoadon_id = str(id) + random_string
        return render_template("payment.html", title="Thanh toán", hoadon_id=hoadon_id)


@app.route('/payment_return', methods=['GET'])
def payment_return():
    vnp = vnpay()  # Thay thế Vnpay() bằng cách tạo đối tượng Vnpay từ thư viện của bạn

    inputData = request.args
    if inputData:
        vnp.responseData = dict(inputData)
        order_id = inputData['vnp_TxnRef']
        amount = int(inputData['vnp_Amount']) / 100
        order_desc = inputData['vnp_OrderInfo']
        vnp_TransactionNo = inputData['vnp_TransactionNo']
        vnp_ResponseCode = inputData['vnp_ResponseCode']
        print(current_user)
        if vnp.validate_response(
                "DZGERGFXNBOUCRHIKYOQJTRSNIMTRTLA"):  # Thay YOUR_HASH_SECRET_KEY bằng secret key của bạn
            if vnp_ResponseCode == "00":
                msg = (
                        "Đơn hàng " + order_id + " của bạn đã được thanh toán thành công.\n" + "Đơn hàng sẽ được gửi đến "
                        + str(session.get('diachi')) + ".\n" + "Số điện thoại liên lạc của đơn hàng: "
                        + str(
                    session.get('sdt')) + "\n" + "Cảm ơn vì đã đặt hàng. Chúng tôi sẽ làm việc nhanh nhất có thể.")
                khachhang = dao.get_tk_khach_hang_by_id(current_user.id)
                subject = "Xác nhận thông tin thanh toán đơn hàng"
                utils.send_mail(khachhang.email, msg, subject)
                dao.lap_hoa_don(id=order_id, taikhoankhachhang_id=current_user.id, diachi=session['diachi'],
                                sdt=session['sdt'])
                del session['diachi']
                del session['sdt']
                return redirect(url_for("gio_hang", msg="Chúc mừng bạn đã đặt hàng thành công"))
            else:
                return redirect(url_for("gio_hang", msg="Có vẽ đã có lỗi xảy ra! Thanh toán không thành công!"))
        else:
            return redirect(url_for("gio_hang", msg="Có vẽ đã có lỗi xảy ra! Thanh toán không thành công!"))
    else:
        return redirect(url_for("gio_hang", msg="Có vẽ đã có lỗi xảy ra! Thanh toán không thành công!"))


@app.route('/checkthongtin', methods=['post'])
def check_thong_tin():
    giohang = dao.get_gio_hang(current_user.id)
    for g in giohang.values():
        check = dao.check_hang_ton_kho(g['sanpham_id'], g['soluong'])
        print(check)
        if check is False:
            msg = "Có vẻ đã có lỗi xảy ra. Sản phẩm " + str(g['tensanpham']) + " không đủ hàng tồn kho."
            return redirect(url_for("gio_hang", msg=msg))
    sdt = request.form.get('sdt')
    diachi = request.form.get('diachi')
    phuongthucthanhtoan = request.form.get('phuongthucthanhtoan')
    if phuongthucthanhtoan == "vnpay":
        session['sdt'] = sdt
        session['diachi'] = diachi
        return redirect("/vnpay/payment")
    elif phuongthucthanhtoan == "tienmat":
        random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        hoadon_id = str(current_user.id) + random_string
        khachhang = dao.get_tk_khach_hang_by_id(current_user.id)
        subject = "Xác nhận thông tin thanh toán đơn hàng"
        msg = ("Đơn hàng " + hoadon_id + " của bạn đã được thanh toán thành công.\n" + "Đơn hàng sẽ được gửi đến "
               + str(diachi) + ".\n" + "Số điện thoại liên lạc của đơn hàng: "
               + str(sdt) + "\n" + "Cảm ơn vì đã đặt hàng. Chúng tôi sẽ làm việc nhanh nhất có thể.")
        utils.send_mail(khachhang.email, msg, subject)
        dao.lap_hoa_don(id=hoadon_id, taikhoankhachhang_id=current_user.id, diachi=diachi, sdt=sdt)
        return redirect(url_for("gio_hang", msg="Chúc mừng bạn đã đặt hàng thành công"))


@app.route('/sanpham/<sanpham_id>')
def chi_tiet_san_pham(sanpham_id):
    page = request.args.get('page')
    page_size = 4 #hiển thị 4 sản phẩm
    if page:
        page = int(page)
    else:
        page = 1
    sanpham = dao.get_sanpham_by_id(sanpham_id)
    theloai = dao.get_the_loai_sanpham_by_sanpham_id(sanpham_id)
    binhluan = dao.get_binh_luan(sanpham_id, page=page, page_size=page_size)
    num = len(dao.get_binh_luan(sanpham_id))
    soluongdaban = dao.get_so_luong_da_ban(sanpham_id)
    return render_template('chitietsanpham.html', sanpham=sanpham, theLoai=theloai,
                           binhluan=binhluan, pages=math.ceil(num / page_size), page=page, soluongbinhluan=num,
                           soluongdaban=soluongdaban)


@app.route('/api/binhluan', methods=['post'])
@login_required
def them_binh_luan():
    data = request.json
    sanpham_id = str(data.get("sanpham_id"))
    khachhang_id = current_user.id
    binhluan = str(data.get("binhluan"))
    check = dao.check_binh_luan(sanpham_id, khachhang_id)
    if check is True:
        dao.them_binh_luan(sanpham_id, khachhang_id, binhluan)
    return jsonify(check)


@app.route('/nhanvien')
def nhan_vien():
    msg = request.args.get('msg')
    kw = request.args.get('kw')
    page = request.args.get('page')
    if not page:
        page = 1
    sanpham = dao.get_sanpham(kw=kw, page=page, page_size=1)
    pages = len(dao.get_sanpham(kw=kw))
    giosanpham = None
    if "giosanpham" in session:
        giosanpham = session.get('giosanpham')
    return render_template('nhanvien.html', sanpham=sanpham, giosanpham=giosanpham,
                           total_gio_sanpham=utils.count_gio_sanpham(giosanpham), page=page, kw=kw, pages=pages, msg=msg)


@app.route("/api/giosanpham", methods=['post'])
def add_gio_sanpham():
    data = request.json
    giosanpham = session.get('giosanpham')
    if giosanpham is None:
        giosanpham = {}

    id = str(data.get("id"))
    if id in giosanpham:
        giosanpham[id]['quantity'] += 1
    else:
        giosanpham[id] = {
            "id": id,
            "name": data.get("name"),
            "price": data.get("price"),
            "quantity": 1
        }
    session['giosanpham'] = giosanpham
    return jsonify(utils.count_gio_sanpham(giosanpham))


@app.route("/api/giosanpham/<product_id>", methods=['put'])
def update_gio_sanpham(product_id):
    giosanpham = session.get('giosanpham')
    if giosanpham and product_id in giosanpham:
        quantity = request.json.get('quantity')
        giosanpham[product_id]['quantity'] = int(quantity)

    session['giosanpham'] = giosanpham
    return jsonify(utils.count_gio_sanpham(giosanpham))


@app.route("/api/giosanpham/<product_id>", methods=['delete'])
def delete_gio_sanpham(product_id):
    giosanpham = session.get('giosanpham')
    if giosanpham and product_id in giosanpham:
        del giosanpham[product_id]

    session['giosanpham'] = giosanpham
    return jsonify(utils.count_gio_sanpham(giosanpham))


@login.user_loader
def get_user(user_id):
    user_role = session.get('user_role')
    if user_role == "ADMIN" or user_role == "NHANVIEN":
        return dao.get_tk_nhan_vien_by_id(user_id)
    elif user_role == "KHACHHANG":
        return dao.get_tk_khach_hang_by_id(user_id)


@app.context_processor
def common_response():
    if current_user.is_authenticated:
        return {
            'theloai': dao.get_the_loai(),
            'giohang': dao.get_total_gio_hang(current_user.id)
        }
    return {
        'theloai': dao.get_the_loai()
    }


@app.route('/nhanvien/login', methods=['post'])
def nhanvien_login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = dao.auth_user(username=username, password=password, loaitaikhoan=LoaiTaiKhoan.NHANVIEN, email=None)
    if user:
        login_user(user=user)
        session['user_role'] = "NHANVIEN"
    return redirect('/nhanvien')

@app.route("/nhanvien/payment", methods=['post'])
@login_required
def lap_hoa_don():
    giohang = session.get('giosanpham')
    for g in giohang.values():
        check = dao.check_hang_ton_kho(g['id'], g['quantity'])
        if check is False:
            msg = "Có vẻ đã có lỗi xảy ra. Sản phẩm " + str(g['name']) + " không đủ hàng tồn kho."
            return redirect(url_for("nhan_vien", msg=msg))
    random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    hoadon_id = str(current_user.id) + random_string
    nhanvien = dao.get_tk_nhan_vien_by_id(current_user.id)
    dao.lap_hoa_don(id=hoadon_id, taikhoannhanvien_id=current_user.id)
    session['hoadon_id'] = hoadon_id
    return redirect('/hoadon')

@app.route("/hoadon")
def hoa_don():
    referrer = request.referrer
    if referrer and 'nhanvien' in referrer:
        hoadon = None
        sanphams = None
        if 'hoadon_id' in session and session['hoadon_id']:
            hoadon_id = session.get('hoadon_id')
            del session['hoadon_id']
            hoadon = dao.get_hoa_don_by_id(hoadon_id)
            chitiethoadon = dao.get_chi_tiet_hoa_don_by_id(hoadon_id)
            sanphams = {}
            for g in chitiethoadon:
                sanpham = dao.get_sanpham_by_id(g.sanpham_id)
                sanphams[g.id] = {
                    "id": g.sanpham_id,
                    "tensanpham": sanpham.tensanpham,
                    "gia": sanpham.gia,
                    "soluong": g.soluong
                }
        return render_template("hoadon.html", hoadon=hoadon, chitiethoadon=sanphams)
    else:
        return "Có lỗi xảy ra"

if __name__ == '__main__':
    from app import admin

    app.run(host='localhost', port=5000, debug=True)
