USER = 'postgres'
PASSWORD = '123'
HOST = 'localhost'
PORT = '5432'
DATABASE_NAME = 'db_sepatu'

DEV_SCALE = {
    'ukuran': {
        '43 - 33': 5,
        '30 - 42': 3,
        '38 - 39': 1,

    },
    'harga': {
        '110 - 150': 5,
        '90 - 100': 3, 
        '55 - 80': 1,

    },
    'berat': {
        '0.6 - 0.7 Kg': 5,
        '0.5 Kg': 3,
        '0.4 Kg': 1,

    },
    'skor_kualitas': {
        '9.5': 5,
        '8.0 - 8.5': 3,
        '7.0 - 7.9': 1,

    },
    'tahun_terbit': {
        '2023': 5,
        '2022 - 2021': 3,
        '2020': 1,

    },
}

# https://github.com/agungperdananto/spk_model
# https://github.com/agungperdananto/SimpleCart
