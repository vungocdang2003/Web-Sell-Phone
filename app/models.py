import hashlib
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Enum, CheckConstraint
from sqlalchemy.orm import relationship
from app import db, app
from flask_login import UserMixin
import enum


class BaseModel(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    ngaykhoitao = Column(DateTime, default=datetime.now())

class LoaiTaiKhoan(enum.Enum):
    NHANVIEN = 1
    KHACHHANG = 2
    ADMIN = 3


class GioiTinh(enum.Enum):
    Nam = 1
    Nu = 2


class TaiKhoan(db.Model, UserMixin):
    __abstract__ = True
    name = Column(String(100), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(1000), nullable=False)
    avatar = Column(String(100),
                    default='https://res.cloudinary.com/dxxwcby8l/image/upload/v1688179242/hclq65mc6so7vdrbp7hz.jpg')
    user_role = Column(Enum(LoaiTaiKhoan))

    def __str__(self):
        return self.username


class TaiKhoanKhachHang(TaiKhoan):
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    giohang = relationship("GioHang", back_populates="taikhoankhachhang", uselist=False)
    binhluan = relationship("BinhLuan", backref="taikhoankhachhang2", lazy=True)
    def __str__(self):
        return self.name


class DiaChi(BaseModel):
    diachi = Column(String(1000), nullable=False)
    taikhoankhachhang_id = Column(Integer, ForeignKey(TaiKhoanKhachHang.id), nullable=False)
    taikhoankhachhang = relationship("TaiKhoanKhachHang", backref="diachi", lazy=True)
    hoadon = relationship('HoaDon', backref='diachi', lazy=True)

class SDT(BaseModel):
    sdt = Column(String(10), nullable=False)
    taikhoankhachhang_id = Column(Integer, ForeignKey(TaiKhoanKhachHang.id), nullable=False)
    taikhoankhachhang = relationship("TaiKhoanKhachHang", backref="sdt")
    hoadon = relationship('HoaDon', backref='sdt', lazy=True)

class GioHang(db.Model):
    id = Column(Integer, ForeignKey(TaiKhoanKhachHang.id), primary_key=True)
    taikhoankhachhang = relationship("TaiKhoanKhachHang", back_populates="giohang", uselist=False)
    ngaykhoitao = Column(DateTime, default=datetime.now())

class NhanVien(BaseModel):
    CCCD = Column(String(20), nullable=False, unique=True)
    hoten = Column(String(100), nullable=False)
    gioitinh = Column(Enum(GioiTinh), nullable=False)
    taikhoannhanvien = relationship("TaiKhoanNhanVien", back_populates="nhanvien", uselist=False)

    def __str__(self):
        return self.hoten


class TaiKhoanNhanVien(TaiKhoan):
    id = Column(Integer, ForeignKey(NhanVien.id), primary_key=True)
    nhanvien = relationship("NhanVien", back_populates="taikhoannhanvien", uselist=False)

    def __str__(self):
        return self.name


class TheLoai(BaseModel):
    __tablename__ = 'theloai'
    tentheloai = Column(String(100), nullable=False, unique=True)

    def __str__(self):
        return self.tentheloai

class SanPham(db.Model):
    __tablename__ = 'sanpham'
    id = Column(String(10), primary_key=True, nullable=False)
    tensanpham = Column(String(100), nullable=False, unique=True)
    gia = Column(Float, default=0)
    anhbia = Column(String(2000))
    soluongtonkho = Column(Integer)
    ngayphathanh = Column(DateTime, default=datetime.now(), nullable=False)
    mota = Column(String(5000), nullable=False, default="San phẩm không có mô tả")
    binhluan = relationship("BinhLuan", backref="sanpham3", lazy=True)
    def __str__(self):
        return self.tensanpham

class BinhLuan(BaseModel):
    sanpham_id = Column(String(10), ForeignKey(SanPham.id), nullable=False)
    taikhoankhachhang_id = Column(Integer, ForeignKey(TaiKhoanKhachHang.id), nullable=False)
    noidung = Column(String(1000), nullable=False)

class GioHang_SanPham(BaseModel):
    giohang_id = Column(Integer, ForeignKey(GioHang.id), nullable=False)
    sanpham_id = Column(String(10), ForeignKey(SanPham.id), nullable=False)
    soluong = Column(Integer, nullable=False)

class SanPham_TheLoai(BaseModel):
    __tablename__ = 'sanpham_theloai'
    sanpham_id = Column(String(10), ForeignKey(SanPham.id), nullable=False)
    theloai_id = Column(Integer, ForeignKey(TheLoai.id), nullable=False)
    sanpham = relationship('SanPham', backref='sanpham_theloai1', lazy=True)
    theloai = relationship('TheLoai', backref='sanpham_theloai2', lazy=True)

class HoaDon(db.Model):
    id = Column(String(6), primary_key=True, nullable=False)
    taikhoankhachhang_id = Column(Integer, ForeignKey(TaiKhoanKhachHang.id), nullable=True)
    taikhoannhanvien_id = Column(Integer, ForeignKey(TaiKhoanNhanVien.id), nullable=True)
    diachi_id = Column(Integer, ForeignKey(DiaChi.id), nullable=True)
    sdt_id = Column(Integer, ForeignKey(SDT.id), nullable=True)
    ngaykhoitao = Column(DateTime, default=datetime.now())
    taikhoankhachhang = relationship('TaiKhoanKhachHang', backref='hoadon1', lazy=True)
    taikhoannhanvien = relationship('TaiKhoanNhanVien', backref='hoadon2', lazy=True)
    __table_args__ = (
        CheckConstraint('taikhoankhachhang_id IS NOT NULL OR taikhoannhanvien_id IS NOT NULL'),
    )
    tongsoluong = Column(Integer, default=0)
    tongtien = Column(Float, default=0)

class ChiTietHoaDon(BaseModel):
    hoadon_id = Column(String(6), ForeignKey(HoaDon.id), nullable=False)
    sanpham_id = Column(String(10), ForeignKey(SanPham.id), nullable=False)
    soluong = Column(Integer, nullable=False)



if __name__ == '__main__':
    with app.app_context():
        pass
        # db.create_all() #1
        # nv1 = NhanVien(CCCD='1234567', hoten='Nguyen Van A', gioitinh=GioiTinh.Nam)  # 2
        # db.session.add(nv1)
        # db.session.commit()
        # nv2 = NhanVien(CCCD='789654', hoten='Nguyen Van B', gioitinh=GioiTinh.Nam) #4
        # db.session.add(nv2)
        # db.session.commit()
        # import hashlib
        # tk_admin = TaiKhoanNhanVien(name='Nguyen Van A', username='admin', password=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()), user_role=LoaiTaiKhoan.ADMIN, id=2)  # 3
        # db.session.add(tk_admin)
        # db.session.commit()
        # import hashlib
        # tk_nhanvien = TaiKhoanNhanVien(name='Nguyen Van B', username='NVB', password=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()), user_role=LoaiTaiKhoan.NHANVIEN, id=1)
        # db.session.add(tk_nhanvien)
        # db.session.commit()

        # tk_khachhang = TaiKhoanKhachHang(email='dohuy4546@gmail.com',name='Đỗ Gia Huy', username='dohuy4546',
        #           password=str(hashlib.md5('123'.encode('utf-8')).hexdigest()), user_role=LoaiTaiKhoan.KHACHHANG)
        # db.session.add(tk_khachhang)
        # db.session.commit()

