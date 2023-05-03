from cloudipsp import Api, Checkout

api = Api(merchant_id = 1396424, secret_key = 'test')
checkout = Checkout(api = api)