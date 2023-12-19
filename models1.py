from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Sepatu(Base):
    __tablename__ = "tbl_sepatu"
    no = Column(Integer, primary_key=True)
    nama_sepatu = Column(String(255))
    ukuran = Column(String(255))
    harga = Column(String(255))
    berat = Column(String(255))
    skor_kualitas = Column(String(255))
    tahun_terbit = Column(String(255))

    def __init__(self, nama_sepatu, ukuran, harga, berat, skor_kualitas, tahun_terbit):
        self.nama_sepatu = nama_sepatu
        self.ukuran = ukuran
        self.harga = harga
        self.berat = berat
        self.skor_kualitas = skor_kualitas
        self.tahun_terbit = tahun_terbit

    def calculate_score(self, dev_scale):
        score = 0
        score += self.ukuran * dev_scale['ukuran']
        score += self.harga * dev_scale['harga']
        score += self.berat * dev_scale['berat']
        score += self.skor_kualitas * dev_scale['skor_kualitas']
        score -= self.tahun_terbit * dev_scale['tahun_terbit']
        return score

    def __repr__(self):
        return f"Sepatu(nama_sepatu={self.nama_sepatu!r}, ukuran={self.ukuran!r}, harga={self.harga!r}, berat={self.berat!r}, skor_kualitas={self.skor_kualitas!r}, tahun_terbit={self.tahun_terbit!r})"
