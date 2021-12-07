#from numpy import array, isin, dot, arange
from scipy.sparse import csr_matrix
from .utils import gen_dicts

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
