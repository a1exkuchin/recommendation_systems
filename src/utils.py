from numpy import array, isin, dot, arange
from scipy.sparse import csr_matrix

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
    
    # ...

  


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



def get_similar_items_recommendation(model, data, c_ui, N=5):
    """
    Рекомендуем товары, похожие на топ-N купленных юзером товаров
    На выходе датафрейм, состоящий из двух колонок 'user_id' и 'similar_items_rec'
    """
    itemids = c_ui.columns.values
    id_to_itemid, itemid_to_id = gen_dicts(itemids)

    # формируем топ-N купленных товаров
    popularity = data.groupby(['user_id', 'item_id'])['quantity'].count().reset_index()
    popularity.sort_values('quantity', ascending=False, inplace=True)
    popularity = popularity[popularity['item_id'] != 999999]
    popularity = popularity.groupby('user_id').head(N+5)
    popularity.sort_values('user_id', ascending=False, inplace=True)
    
    def get_rec(model, x):
        recs = model.similar_items(itemid_to_id[x], N=2)
        top_rec = recs[1][0]
        return id_to_itemid[top_rec]

    
    # находим один товар близкий (похожий) к каждому товару из топ-N
    popularity['similar_items_rec'] = popularity['item_id'].apply(lambda x: get_rec(model, x))
    popularity = popularity[popularity['similar_items_rec'] != 999999]
    popularity = popularity.groupby('user_id').head(N)
    recommendation_similar_items = popularity.groupby('user_id')['similar_items_rec'].unique().reset_index()
    
    recommendation_similar_items.columns=['user_id', 'similar_items_rec']
      
    return recommendation_similar_items

def get_similar_users_recommendation(model, data, c_ui, N=5):
    """
    Рекомендуем те товары, которые купили N похожих пользователей
    На выходе датафрейм, состоящий из двух колонок 'user_id' и 'similar_users_rec'
    """
    # формируем словари индексов
    itemids = c_ui.columns.values
    id_to_itemid, itemid_to_id = gen_dicts(itemids)
    
    userids = c_ui.index.values
    id_to_userid, userid_to_id = gen_dicts(userids)
        
    # находим N похожих пользователей
    def get_users(user, N=5):
        result = []
        similar_users = model.similar_users(userid_to_id[user], N=N+1)[1:]
        for row in similar_users:
            result.append(row[0])
        return result
 
    # для каждого пользователя из списка пользователей рекомендуем 2 популярных товара, 
    # потом выбираем уникальные товары и берем из них N штук 
    def get_rec(users, model, N=2):
        res = []
        for user in users:
            try:
                res += [id_to_itemid[rec[0]] for rec in 
                        model.recommend(userid=userid_to_id[user], 
                                        user_items=csr_matrix(c_ui).tocsr(),   # на вход user-item matrix
                                        N=N, 
                                        filter_already_liked_items=False, 
                                        filter_items=[itemid_to_id[999999]],  # фильтруем 999999
                                        recalculate_user=True)]
            except KeyError:
                res = []
        res = list(set(res))
        return res
    
    # берем всех уникальных пользователей из выбоки данных и для каждого рекомендуем N товаров
    result = data.groupby(['user_id'])['item_id'].count().reset_index()
    result['similar_users'] = result['user_id'].apply(lambda x: get_users(x))
    result['similar_users_rec'] = result['similar_users'].apply(lambda x: get_rec(x, model)[:N])
    
    return result[['user_id', 'similar_users_rec']]
