from http import HTTPStatus
from flask import Flask, request, abort
from flask_restful import Resource, Api 
from models import Mobil as MerekMobil
from engine import engine
from sqlalchemy import select
from sqlalchemy.orm import Session

session = Session(engine)

app = Flask(__name__)
api = Api(app)        

class BaseMethod():

    def __init__(self):
        self.raw_weight = {'harga': 4, 'thn_produksi': 3, 'kekuatan_mesin': 5, 'konsumsi_bhn_bakar': 3}

    @property
    def weight(self):
        total_weight = sum(self.raw_weight.values())
        return {k: round(v/total_weight, 2) for k, v in self.raw_weight.items()}

    @property
    def data(self):
        query = select(MerekMobil.id_mobil, MerekMobil.harga, MerekMobil.thn_produksi, MerekMobil.kekuatan_mesin, MerekMobil.konsumsi_bhn_bakar)
        result = session.execute(query).fetchall()
        print(result)
        return [{'id_mobil': mobil.id_mobil, 'harga': mobil.harga, 'thn_produksi': mobil.thn_produksi, 'kekuatan_mesin': mobil.kekuatan_mesin, 'konsumsi_bhn_bakar': mobil.konsumsi_bhn_bakar, } for mobil in result]

    @property
    def normalized_data(self):
        harga_values = []
        thn_produksi_values = []
        kekuatan_mesin_values = []
        konsumsi_bhn_bakar_values = []

        for data in self.data:
            harga_values.append(data['harga'])
            thn_produksi_values.append(data['thn_produksi'])
            kekuatan_mesin_values.append(data['kekuatan_mesin'])
            konsumsi_bhn_bakar_values.append(data['konsumsi_bhn_bakar'])
            
        return [
            {'id_mobil': data['id_mobil'],
             'harga': min(harga_values) / data['harga'],
             'thn_produksi': data['thn_produksi'] / max(thn_produksi_values),
             'kekuatan_mesin': data['kekuatan_mesin'] / max(kekuatan_mesin_values),
             'konsumsi_bhn_bakar': data['konsumsi_bhn_bakar'] / max(konsumsi_bhn_bakar_values),
             }
            for data in self.data
        ]

    def update_weights(self, new_weights):
        self.raw_weight = new_weights

class WeightedProductCalculator(BaseMethod):
    def update_weights(self, new_weights):
        self.raw_weight = new_weights

    @property
    def calculate(self):
        normalized_data = self.normalized_data
        produk = []

        for row in normalized_data:
            product_score = (
                row['harga'] ** self.raw_weight['harga'] *
                row['thn_produksi'] ** self.raw_weight['thn_produksi'] *
                row['kekuatan_mesin'] ** self.raw_weight['kekuatan_mesin'] *
                row['konsumsi_bhn_bakar'] ** self.raw_weight['konsumsi_bhn_bakar']
            )

            produk.append({
                'id_mobil': row['id_mobil'],
                'produk': product_score
            })

        sorted_produk = sorted(produk, key=lambda x: x['produk'], reverse=True)

        sorted_data = []

        for product in sorted_produk:
            sorted_data.append({
                'id_mobil': product['id_mobil'],
                'score': product['produk']
            })

        return sorted_data


class WeightedProduct(Resource):
    def get(self):
        calculator = WeightedProductCalculator()
        result = calculator.calculate
        return result, HTTPStatus.OK.value
    
    def post(self):
        new_weights = request.get_json()
        calculator = WeightedProductCalculator()
        calculator.update_weights(new_weights)
        result = calculator.calculate
        return {'data': result}, HTTPStatus.OK.value
    

class SimpleAdditiveWeightingCalculator(BaseMethod):
    @property
    def calculate(self):
        weight = self.weight
        result = {row['id_mobil']:
                  round(row['harga'] * weight['harga'] +
                        row['thn_produksi'] * weight['thn_produksi'] +
                        row['kekuatan_mesin'] * weight['kekuatan_mesin'] +
                        row['konsumsi_bhn_bakar'] * weight['konsumsi_bhn_bakar'], 2)
                  for row in self.normalized_data
                  }
        sorted_result = dict(
            sorted(result.items(), key=lambda x: x[1], reverse=True))
        return sorted_result

    def update_weights(self, new_weights):
        self.raw_weight = new_weights

class SimpleAdditiveWeighting(Resource):
    def get(self):
        saw = SimpleAdditiveWeightingCalculator()
        result = saw.calculate
        return result, HTTPStatus.OK.value

    def post(self):
        new_weights = request.get_json()
        saw = SimpleAdditiveWeightingCalculator()
        saw.update_weights(new_weights)
        result = saw.calculate
        return {'data': result}, HTTPStatus.OK.value


class Mobil(Resource):
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
            abort(404, description=f'Halaman {page} tidak ditemukan.') 
        return {
            'page': page, 
            'page_size': page_size,
            'next': next_page, 
            'prev': prev_page,
            'Results': list[start:end]
        }

    def get(self):
        query = select(MerekMobil)
        data = [{'id_mobil': mobil.id_mobil, 'harga': mobil.harga, 'thn_produksi': mobil.thn_produksi, 'kekuatan_mesin': mobil.kekuatan_mesin, 'konsumsi_bhn_bakar': mobil.konsumsi_bhn_bakar} for mobil in session.scalars(query)]
        return self.get_paginated_result('mobil/', data, request.args), HTTPStatus.OK.value


api.add_resource(Mobil, '/mobil')
api.add_resource(WeightedProduct, '/wp')
api.add_resource(SimpleAdditiveWeighting, '/saw')

if __name__ == '__main__':
    app.run(port='5005', debug=True)
