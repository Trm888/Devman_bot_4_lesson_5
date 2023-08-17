import asyncio

import aiohttp


async def get_pcm_products(token):
    api_base_url = 'https://useast.api.elasticpath.com/pcm/products'
    headers = {'Authorization': f'Bearer {token}',
               "Content-Type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.get(api_base_url, headers=headers) as response:
            response.raise_for_status()
            pcm_products_info = await response.json()
            return pcm_products_info['data']


async def get_products(token):
    api_base_url = 'https://useast.api.elasticpath.com/catalog/products'
    headers = {'Authorization': f'Bearer {token}',
               "Content-Type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.get(api_base_url, headers=headers) as response:
            response.raise_for_status()
            products_info = await response.json()
            return products_info['data']


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
            token_info = await response.json()
            return token_info["access_token"], token_info["expires"]


async def add_existing_product_to_cart(product_id, user_id, token, quantity):
    api_base_url = f'https://useast.api.elasticpath.com/v2/carts/{user_id}/items/'
    headers = {
        'Authorization': f'Bearer {token}',
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
            cart_response = await response.json()
            return cart_response


async def get_image_url(token, main_image_id):
    api_base_url = f'https://useast.api.elasticpath.com/v2/files/{main_image_id}'
    headers = {'Authorization': f'Bearer {token}',
               "Content-Type": "application/json"}

    async with aiohttp.ClientSession() as session:
        async with session.get(api_base_url, headers=headers) as response:
            response.raise_for_status()
            image_info = await response.json()
            return image_info['data']['link']['href']


async def fetch_products(token):
    products_information = []
    products, products_pcm = await asyncio.gather(get_products(token), get_pcm_products(token))
    pcm_description_map = {}
    for product in products_pcm:
        url = await get_image_url(token, product['relationships']['main_image']['data']['id'])
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


async def get_total_price_cart(cart_ref, token):
    api_base_url = f'https://useast.api.elasticpath.com/v2/carts/{cart_ref}'
    headers = {'Authorization': f'Bearer {token}',
               "Content-Type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.get(api_base_url, headers=headers) as response:
            response.raise_for_status()
            cart_info = await response.json()
            return cart_info['data']['meta']['display_price']['with_tax']['formatted']


async def get_items_cart(cart_ref, token):
    cart_url = f'https://useast.api.elasticpath.com/v2/carts/{cart_ref}/items/'
    headers = {
        'Authorization': f'Bearer {token}',
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(cart_url, headers=headers) as response:
            response.raise_for_status()
            response_content = await response.json()
            cart_items = response_content['data']
            products = []
            for item in cart_items:
                products.append({'id': item['id'],
                                 'name': item['name'],
                                 'quantity': item['quantity'],
                                 'price': item['meta']['display_price']['with_tax']['value']['formatted']})
            return products


async def delete_item(cart_ref, cart_item_id, token):
    api_base_url = f'https://useast.api.elasticpath.com/v2/carts/{cart_ref}/items/{cart_item_id}'
    headers = {
        'Authorization': f'Bearer {token}',
    }
    async with aiohttp.ClientSession() as session:
        async with session.delete(api_base_url, headers=headers) as response:
            response.raise_for_status()
            item_info = await response.json()
            return item_info


async def create_user(user_id, mail, token):
    api_base_url = f'https://useast.api.elasticpath.com/v2/customers/'
    headers = {
        'Authorization': f'Bearer {token}',
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
            user_info = await response.json()
            return user_info
