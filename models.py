from sqlalchemy import String, Integer, Column
from sqlalchemy.ext.declarative import declarative_base

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

    def __repr__(self):
        return f"Sepatu(nama_sepatu={self.nama_sepatu!r}, ukuran={self.ukuran!r}, harga={self.harga!r}, berat={self.berat!r}, skor_kualitas={self.skor_kualitas!r}, tahun_terbit={self.tahun_terbit!r})"