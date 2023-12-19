from http import HTTPStatus
from flask import Flask, request, abort
from flask_restful import Resource, Api
from models import Sepatu as SepatuModel
from engine import engine
from sqlalchemy import select
from sqlalchemy.orm import Session
from tabulate import tabulate

session = Session(engine)

app = Flask(__name__)
api = Api(app)


class BaseMethod():

    def __init__(self):
        self.raw_weight = {'ukuran': 4, 'harga':3,'berat': 2, 'skor_kualitas': 7, 'tahun_terbit': 4}

    @property
    def weight(self):
        total_weight = sum(self.raw_weight.values())
        return {k: round(v/total_weight, 2) for k, v in self.raw_weight.items()}

    @property
    def data(self):
        query = select(SepatuModel.no, SepatuModel.nama_sepatu, SepatuModel.ukuran, SepatuModel.harga,
                       SepatuModel.berat, SepatuModel.skor_kualitas, SepatuModel.tahun_terbit)
        result = session.execute(query).fetchall()
        print(result)
        return [{'no': Sepatu.no,'nama_sepatu': Sepatu.nama_sepatu, 'ukuran': Sepatu.ukuran,
                'harga': Sepatu.harga, 'berat': Sepatu.berat, 'skor_kualitas': Sepatu.skor_kualitas, 'tahun_terbit': Sepatu.tahun_terbit} for Sepatu in result]
    
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
            tahun_terbit_spec = data['tahun_terbit']
            tahun_terbit_numeric_values = [
                int(value) for value in tahun_terbit_spec.split() if value.isdigit()]
            max_tahun_terbit_value = max(
                tahun_terbit_numeric_values) if tahun_terbit_numeric_values else 1
            tahun_terbit_values.append(max_tahun_terbit_value)

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

    def update_weights(self, new_weights):
        self.raw_weight = new_weights

class WeightedProductCalculator(BaseMethod):
    def update_weights(self, new_weights):
        self.raw_weight = new_weights

    @property
    def calculate(self):
        normalized_data = self.normalized_data
        produk = [
            {
                'no': row['no'],
                'produk': row['ukuran']**self.weight['ukuran'] *
                row['berat']**self.weight['berat'] *
                row['skor_kualitas']**self.weight['skor_kualitas'] *
                row['tahun_terbit']**self.weight['tahun_terbit'],
                'harga': row.get('harga', '')            }
            for row in normalized_data
        ]
        sorted_produk = sorted(produk, key=lambda x: x['produk'], reverse=True)
        sorted_data = [
            {
                'no': product['no'],
                'score': round(product['produk'], 3)
            }
            for product in sorted_produk
        ]
        return sorted_data


class WeightedProduct(Resource):
    def get(self):
        calculator = WeightedProductCalculator()
        result = calculator.calculate
        return sorted(result, key=lambda x: x['score'], reverse=True), HTTPStatus.OK.value

    def post(self):
        new_weights = request.get_json()
        calculator = WeightedProductCalculator()
        calculator.update_weights(new_weights)
        result = calculator.calculate
        return {'sepatu': sorted(result, key=lambda x: x['score'], reverse=True)}, HTTPStatus.OK.value

class SimpleAdditiveWeightingCalculator(BaseMethod):
    @property
    def calculate(self):
        weight = self.weight
        result = [
            {
                'ID': row['no'],
                'Score': round(row['ukuran'] * weight['ukuran'] +
                               row['berat'] * weight['berat'] +
                               row['skor_kualitas'] * weight['skor_kualitas'] +
                               row['tahun_terbit'] * weight['tahun_terbit'] +
                               row['harga'] * weight['harga'], 3)
            }
            for row in self.normalized_data
        ]
        sorted_result = sorted(result, key=lambda x: x['Score'], reverse=True)
        return sorted_result

    def update_weights(self, new_weights):
        self.raw_weight = new_weights


class SimpleAdditiveWeighting(Resource):
    def get(self):
        saw = SimpleAdditiveWeightingCalculator()
        result = saw.calculate
        return sorted(result, key=lambda x: x['Score'], reverse=True), HTTPStatus.OK.value

    def post(self):
        new_weights = request.get_json()
        saw = SimpleAdditiveWeightingCalculator()
        saw.update_weights(new_weights)
        result = saw.calculate
        return {'sepatu': sorted(result, key=lambda x: x['Score'], reverse=True)}, HTTPStatus.OK.value

class Sepatu(Resource):
    def get_paginated_result(self, url, list, args):
        page_size = int(args.get('page_size', 10))
        page = int(args.get('page', 1))
        page_count = int((len(list) + page_size - 1) / page_size)
        start = (page - 1) * page_size
        end = min(start + page_size, len(list))

        if page < page_count:
            next_page = f'{url}?page={page+1}&page_size={page_size}'
        else:
            next_page = None
        if page > 1:
            prev_page = f'{url}?page={page-1}&page_size={page_size}'
        else:
            prev_page = None

        if page > page_count or page < 1:
            abort(404, description=f'Data Tidak Ditemukan.')
        return {
            'page': page,
            'page_size': page_size,
            'next': next_page,
            'prev': prev_page,
            'Results': list[start:end]
        }

    def get(self):
        query = session.query(SepatuModel).order_by(SepatuModel.no)
        result_set = query.all()
        data = [{'no': row.no,'nama_sepatu': row.nama_sepatu, 'ukuran': row.ukuran,
                'harga': row.harga, 'berat': row.berat, 'skor_kualitas': row.skor_kualitas, 'tahun_terbit': row.tahun_terbit}
                for row in result_set]
        return self.get_paginated_result('sepatu/', data, request.args), 200


api.add_resource(Sepatu, '/sepatu')
api.add_resource(WeightedProduct, '/wp')
api.add_resource(SimpleAdditiveWeighting, '/saw')

if __name__ == '__main__':
    app.run(port='5005', debug=True)