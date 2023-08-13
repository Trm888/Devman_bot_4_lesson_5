import asyncio
import sys

import requests
from environs import Env
from loguru import logger
import aiohttp

env = Env()
env.read_env()


# logger.add('debug.log',
#            format='{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}',
#            level='INFO',
#            rotation="1 MB",
#            compression='zip',
#            retention="2 days")
# logger.add(sys.stdout,
#            format='{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}',
#            level='INFO')

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

async def get_products(access_token):
    api_base_url = 'https://useast.api.elasticpath.com/pcm/products'
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


async def fetch_products():
    client_secret = env.str("ELASTICPATH_CLIENT_SECRET")
    client_id = env.str("ELASTICPATH_CLIENT_ID")
    access_token = await get_access_token(client_id, client_secret)
    products = await get_products(access_token)
    return products
    # products = get_products(access_token)['data']
    # print(products)
    # print(product['id'])
    # access_token = get_access_token(client_id, client_secret)
    # print(add_existing_product_to_cart(access_token, product['id'], '2122'))
    # print(get_products_from_cart(access_token, '2122'))


    # logger.success(products)


if __name__ == '__main__':
    main()