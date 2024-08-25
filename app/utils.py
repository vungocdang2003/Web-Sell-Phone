#tương tác với dữ liệu
import smtplib
from email.message import EmailMessage

def send_mail(mailto, msg, subject):
    email_from = 'phuoclanh78@gmail.com' #email người gửi
    email_to = mailto # email người nhận
    password = 'gqaf whpx jipw ahjn' # password phải sinh ra trong bảo vệ 2 lớp bảo mật của google
    subject = subject
    body = msg
    em = EmailMessage()
    em['From'] = email_from
    em['To'] = email_to
    em['Subject'] = subject
    em.set_content(body)
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.ehlo()  # Định danh trong stmp server
        smtp.starttls()  # Thiết lập kết nối smtp trong chế độ TLS
        smtp.login(email_from, password)  # Đăng nhập vào tài khoản email sender
        smtp.send_message(em) # Gửi mail
        print('Check your email ;)')


def count_gio_sanpham(cart):
    total_amount, total_quantiy = 0, 0

    if cart:
        for c in cart.values():
            total_quantiy += c['quantity']
            total_amount += c['quantity']*c['price']

    return {
        "total_amount": total_amount,
        "total_quantity": total_quantiy
    }