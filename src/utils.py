from numpy import array, isin, dot, arange

def gen_dicts(array):
    
    ids = arange(len(array))
    
    id_to_array = dict(zip(ids, array))
    array_to_id = dict(zip(array, ids))

    return id_to_array, array_to_id


def popular_items(data, N=5000):
    """
    выделение в данных N популярных товаров
    """  
    popularity = data.groupby('item_id')['quantity'].sum().reset_index()
    popularity.rename(columns={'quantity': 'n_sold'}, inplace=True)
    
    top = popularity.sort_values('n_sold', ascending=False).head(N).item_id.tolist()
    
    data.loc[~data['item_id'].isin(top), 'item_id'] = 999999 
    
    return data


def prefilter_items(data):
    # Уберем самые популярные товары (их и так купят)
    popularity = data.groupby('item_id')['user_id'].nunique().reset_index() / data['user_id'].nunique()
    popularity.rename(columns={'user_id': 'share_unique_users'}, inplace=True)
    
    top_popular = popularity[popularity['share_unique_users'] > 0.5].item_id.tolist()
    data = data[~data['item_id'].isin(top_popular)]
    
    # Уберем самые НЕ популярные товары (их и так НЕ купят)
    top_notpopular = popularity[popularity['share_unique_users'] < 0.01].item_id.tolist()
    data = data[~data['item_id'].isin(top_notpopular)]
    
    # Уберем товары, которые не продавались за последние 12 месяцев
    
    # Уберем не интересные для рекоммендаций категории (department)
    
    # Уберем слишком дешевые товары (на них не заработаем). 1 покупка из рассылок стоит 60 руб. 
    
    # Уберем слишком дорогие товарыs
    return data
    

def postfilter_items(user_id, recommednations):
    pass
    

def hit_rate(recommended_list, bought_list):
    """
    был ли хотя бы 1 релевантный товар среди рекомендованных
    """     
    bought_list = array(bought_list)
    recommended_list = array(recommended_list)
    
    flags = isin(bought_list, recommended_list)
    
    hit_rate = (flags.sum() > 0) * 1
    
    return hit_rate


def hit_rate_at_k(recommended_list, bought_list, k=5):
    """
    был ли хотя бы 1 релевантный товар среди топ-k рекомендованных
    """        
    bought_list = array(bought_list)
    recommended_list = array(recommended_list[:k])
    
    flags = isin(bought_list, recommended_list)
    
    hit_rate = (flags.sum() > 0) * 1
    
    return hit_rate


def precision(recommended_list, bought_list):
    """
    (точность) какой % рекомендованных товаров купил пользователь 
    """     
    bought_list = array(bought_list)
    recommended_list = array(recommended_list)
    
    flags = isin(bought_list, recommended_list)
    
    precision = flags.sum() / len(recommended_list)
    
    return precision


def precision_at_k(recommended_list, bought_list, k=5):
    """
    (k-точность) какой % из k рекомендованных товаров купил пользователь
    """    
    bought_list = array(bought_list)
    recommended_list = array(recommended_list)
    
    try:
        recommended_list = recommended_list[:k]
    except:
        recommended_list = []
    
    flags = isin(bought_list, recommended_list)
    
    precision = flags.sum() / len(recommended_list)
    
    
    return precision

def money_precision_at_k(recommended_list, bought_list, prices_recommended, k=5):
    """
    считаем % выручки от рекомендованных k товаров
    """
    bought_list = array(bought_list)
    recommended_list = array(recommended_list)[:k]
    prices_recommended = array(prices_recommended)[:k]
    
    flags = isin(recommended_list, bought_list)
    
    precision = dot(prices_recommended, flags) / prices_recommended.sum()
    
    return precision