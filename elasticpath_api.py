import asyncio

import aiohttp
import requests
from environs import Env

env = Env()
env.read_env()


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


def get_access_token(client_id, client_secret):
    token_url = "https://useast.api.elasticpath.com/oauth/access_token"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    }
    response = requests.post(token_url, headers=headers, data=payload)
    response.raise_for_status()
    return response.json().get("access_token")


async def add_existing_product_to_cart(product_id, user_id, quantity=1):
    client_secret = env.str("ELASTICPATH_CLIENT_SECRET")
    client_id = env.str("ELASTICPATH_CLIENT_ID")
    access_token = get_access_token(client_id, client_secret)
    api_base_url = f'https://useast.api.elasticpath.com/v2/carts/{user_id}/items/'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    payload = {
        "data": {
            "id": product_id,
            "type": "cart_item",
            "quantity": quantity,
        }
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(api_base_url, headers=headers, json=payload) as response:
            response.raise_for_status()
            data = await response.json()
            return data


def get_cart(cart_ref):
    client_secret = env.str("ELASTICPATH_CLIENT_SECRET")
    client_id = env.str("ELASTICPATH_CLIENT_ID")
    access_token = get_access_token(client_id, client_secret)
    api_base_url = f'https://useast.api.elasticpath.com/v2/carts/{cart_ref}'
    headers = {'Authorization': f'Bearer {access_token}',
               "Content-Type": "application/json"}
    response = requests.get(api_base_url, headers=headers)
    response.raise_for_status()
    total_price = response.json()['data']['meta']['display_price']['with_tax']['formatted']
    return total_price


def get_products_from_cart(cart_ref):
    client_secret = env.str("ELASTICPATH_CLIENT_SECRET")
    client_id = env.str("ELASTICPATH_CLIENT_ID")
    access_token = get_access_token(client_id, client_secret)
    cart_url = f'https://useast.api.elasticpath.com/v2/carts/{cart_ref}/items/'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get(cart_url, headers=headers)
    response.raise_for_status()
    cart_items = response.json()['data']
    products = []
    print(cart_items)
    for item in cart_items:
        products.append({'name': item['name'],
                         'quantity': item['quantity'],
                         'price': item['meta']['display_price']['with_tax']['value']['formatted']})
    return products


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
    access_token = get_access_token(client_id, client_secret)
    products, products_pcm = await asyncio.gather(get_products(access_token), get_pcm_products(access_token))
    pcm_description_map = {}
    for product in products_pcm:
        url = await get_image_url(access_token, product['relationships']['main_image']['data']['id'])
        product_id = product['id']
        description = product['attributes']['description']

        pcm_description_map[product_id] = {
            'description': description,
            'url': url
        }

    for product in products:
        products_information.append({'id': product['id'],
                                     'name': product['attributes']['name'],
                                     'sku': product['attributes']['sku'],
                                     'price': product['meta']['display_price']['with_tax']['formatted'],
                                     'description': pcm_description_map.get(product['id'], None)['description'],
                                     'url': pcm_description_map.get(product['id'], None)['url']})
    return products_information


async def get_total_price_cart(cart_ref):
    client_secret = env.str("ELASTICPATH_CLIENT_SECRET")
    client_id = env.str("ELASTICPATH_CLIENT_ID")
    access_token = get_access_token(client_id, client_secret)
    api_base_url = f'https://useast.api.elasticpath.com/v2/carts/{cart_ref}'
    headers = {'Authorization': f'Bearer {access_token}',
               "Content-Type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.get(api_base_url, headers=headers) as response:
            response.raise_for_status()
            data = await response.json()
            return data['data']['meta']['display_price']['with_tax']['formatted']


async def get_items_cart(cart_ref):
    client_secret = env.str("ELASTICPATH_CLIENT_SECRET")
    client_id = env.str("ELASTICPATH_CLIENT_ID")
    access_token = get_access_token(client_id, client_secret)
    cart_url = f'https://useast.api.elasticpath.com/v2/carts/{cart_ref}/items/'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(cart_url, headers=headers) as response:
            response.raise_for_status()
            data = await response.json()
            cart_items = data['data']
            products = []
            for item in cart_items:
                products.append({'id': item['id'],
                                 'name': item['name'],
                                 'quantity': item['quantity'],
                                 'price': item['meta']['display_price']['with_tax']['value']['formatted']})
            return products


async def delete_item(cart_ref, cart_item_id):
    client_secret = env.str("ELASTICPATH_CLIENT_SECRET")
    client_id = env.str("ELASTICPATH_CLIENT_ID")
    access_token = get_access_token(client_id, client_secret)
    api_base_url = f'https://useast.api.elasticpath.com/v2/carts/{cart_ref}/items/{cart_item_id}'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    async with aiohttp.ClientSession() as session:
        async with session.delete(api_base_url, headers=headers) as response:
            response.raise_for_status()
            data = await response.json()
            return data


async def create_user(user_id, mail):
    client_secret = env.str("ELASTICPATH_CLIENT_SECRET")
    client_id = env.str("ELASTICPATH_CLIENT_ID")
    access_token = get_access_token(client_id, client_secret)
    api_base_url = f'https://useast.api.elasticpath.com/v2/customers/'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    payload = {
        'data': {
            'type': 'customer',
            'name': user_id,
            'email': mail,
        }
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(api_base_url, headers=headers, json=payload) as response:
            response.raise_for_status()
            data = await response.json()
            return data


def get_user():
    client_secret = env.str("ELASTICPATH_CLIENT_SECRET")
    client_id = env.str("ELASTICPATH_CLIENT_ID")
    access_token = get_access_token(client_id, client_secret)
    api_base_url = f'https://useast.api.elasticpath.com/v2/customers/'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get(api_base_url, headers=headers)
    response.raise_for_status()
    return response.json()
