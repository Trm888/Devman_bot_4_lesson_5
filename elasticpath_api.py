import aiohttp
from environs import Env

env = Env()
env.read_env()


async def get_access_token(client_id, client_secret):
    token_url = "https://useast.api.elasticpath.com/oauth/access_token"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(token_url, headers=headers, data=payload) as response:
            response.raise_for_status()
            data = await response.json()
            return data.get("access_token")


async def get_pcm_products(access_token):
    api_base_url = 'https://useast.api.elasticpath.com/pcm/products'
    headers = {'Authorization': f'Bearer {access_token}',
               "Content-Type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.get(api_base_url, headers=headers) as response:
            response.raise_for_status()
            data = await response.json()
            return data['data']


async def get_products(access_token):
    api_base_url = 'https://useast.api.elasticpath.com/catalog/products'
    headers = {'Authorization': f'Bearer {access_token}',
               "Content-Type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.get(api_base_url, headers=headers) as response:
            response.raise_for_status()
            data = await response.json()
            return data['data']


# def get_access_token(client_id, client_secret):
#     token_url = "https://useast.api.elasticpath.com/oauth/access_token"
#     headers = {
#         'Content-Type': 'application/x-www-form-urlencoded',
#     }
#     payload = {
#         "client_id": client_id,
#         "client_secret": client_secret,
#         "grant_type": "client_credentials"
#     }
#     response = requests.post(token_url, headers=headers, data=payload)
#     response.raise_for_status()
#     return response.json().get("access_token")

# def get_products(access_token):
#     api_base_url = 'https://useast.api.elasticpath.com/pcm/products'
#     headers = {'Authorization': f'Bearer {access_token}',
#                "Content-Type": "application/json"}
#     response = requests.get(api_base_url, headers=headers, )
#     response.raise_for_status()
#     return response.json()
#
#
# def get_cart(access_token, cart_ref):
#     api_base_url = f'https://useast.api.elasticpath.com/v2/carts/{cart_ref}'
#     headers = {'Authorization': f'Bearer {access_token}',
#                "Content-Type": "application/json"}
#     response = requests.get(api_base_url, headers=headers)
#     response.raise_for_status()
#     return response.json()
#
# def add_custom_product_to_cart(access_token, cart_ref):
#     api_base_url = f'https://useast.api.elasticpath.com/v2/carts/'
#     headers = {
#         'Authorization': f'Bearer {access_token}',
#         'Content-Type': 'application/json',
#     }
#     payload = {
#         "id": cart_ref,
#         "items": "items",
#         "data": {
#             "type": "custom_item",
#             "name": "Rainbow trout",
#             "quantity": 1,
#             "description": "Fresh from the farm",
#             "sku": "dsfds3453",
#             "price": {
#                 "amount": 11
#             },
#
#         }
#     }
#     response = requests.post(api_base_url, headers=headers, json=payload)
#     response.raise_for_status()
#     return response.json()
#
#
# def add_existing_product_to_cart(access_token, product_id, cart_ref, quantity=1):
#     api_base_url = f'https://useast.api.elasticpath.com/v2/carts/{cart_ref}/items/'
#     headers = {
#         'Authorization': f'Bearer {access_token}',
#         'Content-Type': 'application/json',
#     }
#     payload = {
#         "data": {
#             "id": product_id,
#             "type": "cart_item",
#             "quantity": quantity,
#         }
#     }
#     response = requests.post(api_base_url, headers=headers, json=payload)
#     response.raise_for_status()
#     return response.json()
#
#
#
# def get_products_from_cart(access_token, cart_ref):
#     cart_url = f'https://useast.api.elasticpath.com/v2/carts/{cart_ref}/items/'
#     headers = {
#             'Authorization': f'Bearer {access_token}',
#         }
#     response = requests.get(cart_url, headers=headers)
#     response.raise_for_status()
#     return response.json()

async def get_image_url(access_token, main_image_id):
    api_base_url = f'https://useast.api.elasticpath.com/v2/files/{main_image_id}'
    headers = {'Authorization': f'Bearer {access_token}',
               "Content-Type": "application/json"}

    async with aiohttp.ClientSession() as session:
        async with session.get(api_base_url, headers=headers) as response:
            response.raise_for_status()
            data = await response.json()
            return data['data']['link']['href']


async def fetch_products():
    client_secret = env.str("ELASTICPATH_CLIENT_SECRET")
    client_id = env.str("ELASTICPATH_CLIENT_ID")
    products_information = []
    access_token = await get_access_token(client_id, client_secret)
    products = await get_products(access_token)
    products_pcm = await get_pcm_products(access_token)
    # urls = await get_image_url(access_token, '2bc62498-a0dc-4c22-a3e3-ea03a9139349')
    # print(urls)
    pcm_description_map = {}
    for product in products_pcm:
        product_id = product['id']
        description = product['attributes']['description']
        main_image_id = product['relationships']['main_image']['data']['id']

        pcm_description_map[product_id] = {
            'description': description,
            'main_image_id': main_image_id
        }
    print(pcm_description_map)

    for product in products:
        url = await get_image_url(access_token, pcm_description_map.get(product['id'], None)['main_image_id'])
        products_information.append({'id': product['id'],
                                     'name': product['attributes']['name'],
                                     'sku': product['attributes']['sku'],
                                     'price': product['meta']['display_price']['with_tax']['formatted'],
                                     'description': pcm_description_map.get(product['id'], None)['description'],
                                     'url': url})
    # print(products_pcm)

    return products_information

# async def fetch_pcm_products():
#     client_secret = env.str("ELASTICPATH_CLIENT_SECRET")
#     client_id = env.str("ELASTICPATH_CLIENT_ID")
#     access_token = await get_access_token(client_id, client_secret)
#     products = await get_pcm_products(access_token)
#     return products
