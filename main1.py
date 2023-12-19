import sys
from colorama import Fore, Style
from models import Base, Sepatu
from engine import engine
from tabulate import tabulate

from sqlalchemy import select
from sqlalchemy.orm import Session
from settings import DEV_SCALE

session = Session(engine)


def create_table():
    Base.metadata.create_all(engine)
    print(f'{Fore.GREEN}[Success]: {Style.RESET_ALL}Database has created!')


def review_data():
    query = select(Sepatu)
    for phone in session.scalars(query):
        print(Sepatu)


class BaseMethod():

    def __init__(self):
        # 1-5
        self.raw_weight = {'ukuran': 4, 'harga': 3,
                            'berat': 2, 'skor_kualitas': 7, 'tahun_terbit': 4}

    @property
    def weight(self):
        total_weight = sum(self.raw_weight.values())
        return {k: round(v/total_weight, 2) for k, v in self.raw_weight.items()}

    @property
    def data(self):
        query = select(Sepatu.no, Sepatu.nama_sepatu, Sepatu.ukuran, Sepatu.harga,
                       Sepatu.berat, Sepatu.skor_kualitas, Sepatu.tahun_terbit)
        result = session.execute(query).fetchall()
        return [{'no': Sepatu.no, 'nama_sepatu': Sepatu.nama_sepatu, 'ukuran': Sepatu.ukuran, 'harga': Sepatu.harga,
                 'berat': Sepatu.berat, 'skor_kualitas': Sepatu.skor_kualitas, 'tahun_terbit': Sepatu.tahun_terbit} for Sepatu in result]

    @property
    def normalized_data(self):
        # x/max [benefit]
        # min/x [cost]
        ukuran_values = []  # max
        berat_values = []  # max
        skor_kualitas_values = []  # max
        tahun_terbit_values = []  # max
        harga_values = []  # min

        for data in self.data:
            # ukuran
            ukuran_spec = data['ukuran']
            numeric_values = [int(value.split()[0]) for value in ukuran_spec.split(
                ',') if value.split()[0].isdigit()]
            max_ukuran_value = max(numeric_values) if numeric_values else 1
            ukuran_values.append(max_ukuran_value)

            # Berat
            berat_spec = data['berat']
            berat_numeric_values = [int(
                value.split()[0]) for value in berat_spec.split() if value.split()[0].isdigit()]
            max_berat_value = max(
                berat_numeric_values) if berat_numeric_values else 1
            berat_values.append(max_berat_value)

            # skor_kualitas
            skor_kualitas_spec = data['skor_kualitas']
            skor_kualitas_numeric_values = [
                int(value) for value in skor_kualitas_spec.split() if value.isdigit()]
            max_skor_kualitas_value = max(
                skor_kualitas_numeric_values) if skor_kualitas_numeric_values else 1
            skor_kualitas_values.append(max_skor_kualitas_value)

            # tahun_terbit
            tahun_terbit_value = DEV_SCALE['tahun_terbit'].get(data['tahun_terbit'], 1)
            tahun_terbit_values.append(tahun_terbit_value)

            # Harga
            harga_cleaned = ''.join(
                char for char in data['harga'] if char.isdigit())
            harga_values.append(float(harga_cleaned)
                                if harga_cleaned else 0)  # Convert to float

        return [
            {'no': data['no'],
             'ukuran': ukuran_value / max(ukuran_values),
             'berat': berat_value / max(berat_values),
             'skor_kualitas': skor_kualitas_value / max(skor_kualitas_values),
             'tahun_terbit': tahun_terbit_value / max(tahun_terbit_values),
             # To avoid division by zero
             'harga': min(harga_values) / max(harga_values) if max(harga_values) != 0 else 0
             }
            for data, ukuran_value, berat_value, skor_kualitas_value, tahun_terbit_value, harga_value
            in zip(self.data, ukuran_values, berat_values, skor_kualitas_values, tahun_terbit_values, harga_values)
        ]


class WeightedProduct(BaseMethod):
    @property
    def calculate(self):
        normalized_data = self.normalized_data
        produk = [
            {
                'no': row['no'],
                'produk': row['ukuran']**self.weight['ukuran'] *
                row['berat']**self.weight['berat'] *
                row['skor_kualitas']**self.weight['skor_kualitas'] *
                row['tahun_terbit']**self.weight['tahun_terbit'] *
                row['harga']**self.weight['harga']
            }
            for row in normalized_data
        ]
        sorted_produk = sorted(produk, key=lambda x: x['produk'], reverse=True)
        sorted_data = [
            {
                'no': product['no'],
                'ukuran': product['produk'] / self.weight['ukuran'],
                'berat': product['produk'] / self.weight['berat'],
                'skor_kualitas': product['produk'] / self.weight['skor_kualitas'],
                'tahun_terbit': product['produk'] / self.weight['tahun_terbit'],
                'harga': product['produk'] / self.weight['harga'],
                'score': product['produk']  # Nilai skor akhir
            }
            for product in sorted_produk
        ]
        return sorted_data



class SimpleAdditiveWeighting(BaseMethod):
    @property
    def calculate(self):
        weight = self.weight
        result = {row['no']:
                  round(row['ukuran'] * weight['ukuran'] +
                        row['berat'] * weight['berat'] +
                        row['skor_kualitas'] * weight['skor_kualitas'] +
                        row['tahun_terbit'] * weight['tahun_terbit'] +
                        row['harga'] * weight['harga'], 2)
                  for row in self.normalized_data
                  }
        sorted_result = dict(
            sorted(result.items(), key=lambda x: x[1], reverse=True))
        return sorted_result


def run_saw():
    saw = SimpleAdditiveWeighting()
    result = saw.calculate
    print(tabulate(result.items(), headers=['No', 'Score'], tablefmt='pretty'))


def run_wp():
    wp = WeightedProduct()
    result = wp.calculate
    headers = result[0].keys()
    rows = [
        {k: round(v, 4) if isinstance(v, float) else v for k, v in val.items()}
        for val in result
    ]
    print(tabulate(rows, headers="keys", tablefmt="grid"))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]

        if arg == 'create_table':
            create_table()
        elif arg == 'saw':
            run_saw()
        elif arg == 'wp':
            run_wp()
        else:
            print('command not found')

