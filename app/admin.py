import hashlib

from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, BaseView, expose, AdminIndexView
from app import app, db, dao
from app.models import SanPham, TheLoai, SanPham_TheLoai, TaiKhoanNhanVien, TaiKhoanKhachHang, NhanVien, LoaiTaiKhoan
from flask_login import logout_user, current_user
from flask import redirect, request


class MyAdminIndex(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html', stats=dao.get_so_luong_sanpham_theo_the_loai())


admin = Admin(app=app, name='QUẢN LÝ ĐIỆN THOẠI', template_mode='bootstrap4', index_view=MyAdminIndex())


class AuthenticatedAdmin(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == LoaiTaiKhoan.ADMIN


class AuthenticatedUser(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and (
                current_user.user_role == LoaiTaiKhoan.NHANVIEN or current_user.user_role == LoaiTaiKhoan.ADMIN)


class AuthenticatedAdminBaseView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == LoaiTaiKhoan.ADMIN


class AuthenticatedNhanVienBaseView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == LoaiTaiKhoan.NHANVIEN


class SanPhamView(AuthenticatedAdmin):
    column_display_pk = True
    can_create = True
    column_list = ['id', 'tensanpham', 'gia', 'soluongtonkho', 'sanpham_theloai1']
    column_labels = {
        'id': 'ID',
        'tensanpham': 'Tên máy',
        'gia': 'Giá',
        'soluongtonkho': 'Số lượng tồn kho',
        'sanpham_theloai1': 'Thể loại',
        'mota': 'Mô tả',
        'ngayphathanh': 'Ngày phát hành',
        'anhbia': 'Ảnh bìa'
    }
    can_export = True
    column_searchable_list = ['tensanpham']
    column_filters = ['gia', 'tensanpham']
    column_editable_list = ['id', 'tensanpham', 'gia', 'anhbia', 'soluongtonkho']
    details_modal = True
    edit_modal = True
    form_columns = ['id', 'tensanpham', 'ngayphathanh', 'gia', 'anhbia', 'soluongtonkho', 'mota']


class TheLoaiView(AuthenticatedAdmin):
    column_list = ['id', 'tentheloai', 'ngaykhoitao']
    column_labels = {
        'id': 'ID',
        'tentheloai': 'Tên thể loại',
        'ngaykhoitao': 'Ngày khởi tạo'
    }
    can_export = True
    column_searchable_list = ['tentheloai']
    column_filters = ['tentheloai']
    column_editable_list = ['tentheloai']
    form_columns = ['tentheloai', 'ngaykhoitao']
    details_modal = True
    edit_modal = True


class SanPham_TheLoaiView(AuthenticatedAdmin):
    column_list = ['id', 'sanpham', 'theloai']
    column_labels = {
        'id': 'ID',
        'sanpham_id': 'Điện thoại ID',
        'theloai_id': 'Thể loại ID'
    }
    can_export = True


class NhanVienView(AuthenticatedAdmin):
    column_list = ['id', 'CCCD', 'hoten', 'gioitinh', 'taikhoannhanvien']
    form_columns = ['CCCD', 'hoten', 'gioitinh']
    column_labels = {
        'id': 'ID',
        'CCCD': 'CCCD',
        'hoten': 'Họ và tên',
        'gioitinh': 'Giới tính',
        'taikhoannhanvien': 'Tài khoản nhân viên'
    }


class LogoutView(AuthenticatedAdminBaseView):
    @expose("/")
    def index(self):
        logout_user()

        return redirect('/admin')


class StatsView(AuthenticatedUser):
    @expose("/")
    def index(self):
        kw = request.args.get('kw')
        year = request.args.get('year')
        if year:
            year = int(year)
        else:
            year = 2024
        return self.render('admin/stats.html', stats=dao.revenue_stats(kw=kw), mon_stats=dao.revenue_mon_stats(year=year),
                           year_stats=dao.revenue_year_stats())


class TaiKhoanNhanVienView(AuthenticatedAdmin):
    form_columns = ['nhanvien', 'name', 'username', 'password', 'avatar', 'user_role']
    column_labels = {
        'nhanvien': 'Nhân viên',
        'name': 'Họ và tên',
        'username': 'Username',
        'password': 'Password',
        'avatar': 'Avatar'
    }

    def on_model_change(self, form, model, is_created):
        # Hash the password when creating or updating the user
        if 'password' in request.form and request.form['password']:
            model.password = str(hashlib.md5(request.form['password'].encode('utf-8')).hexdigest())


class ReturnView(AuthenticatedNhanVienBaseView):
    @expose("/")
    def returnview(self):
        return redirect('/nhanvien')


admin.add_view(SanPhamView(SanPham, db.session, name='Sản Phẩm'))
admin.add_view(TheLoaiView(TheLoai, db.session, name='Thể loại'))
admin.add_view(SanPham_TheLoaiView(SanPham_TheLoai, db.session, name='Sản Phẩm_Thể loại'))
admin.add_view(TaiKhoanNhanVienView(TaiKhoanNhanVien, db.session, name='Tài khoản nhân viên'))
admin.add_view((NhanVienView(NhanVien, db.session, name='Nhân viên')))
admin.add_view(StatsView(name='Thống kê báo cáo'))
admin.add_view(ReturnView(name='Quay về'))
admin.add_view(LogoutView(name='Đăng xuất'))
