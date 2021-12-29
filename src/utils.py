import pandas as pd
import numpy as np


def prefilter_items(data, take_n_popular=5000, item_features=None):
    # Уберем самые популярные товары (их и так купят)
    popularity = data.groupby('item_id')['user_id'].nunique().reset_index() / data['user_id'].nunique()
    popularity.rename(columns={'user_id': 'share_unique_users'}, inplace=True)

    top_popular = popularity[popularity['share_unique_users'] > 0.2].item_id.tolist()
    data = data[~data['item_id'].isin(top_popular)]

    # Уберем самые НЕ популярные товары (их и так НЕ купят)
    top_notpopular = popularity[popularity['share_unique_users'] < 0.02].item_id.tolist()
    data = data[~data['item_id'].isin(top_notpopular)]

    # Уберем товары, которые не продавались за последние 12 месяцев

    # Уберем не интересные для рекоммендаций категории (department)
    if item_features is not None:
        department_size = pd.DataFrame(item_features.\
                                        groupby('department')['item_id'].nunique().\
                                        sort_values(ascending=False)).reset_index()

        department_size.columns = ['department', 'n_items']
        rare_departments = department_size[department_size['n_items'] < 150].department.tolist()
        items_in_rare_departments = item_features[item_features['department'].isin(rare_departments)].item_id.unique().tolist()

        data = data[~data['item_id'].isin(items_in_rare_departments)]


    # Уберем слишком дешевые товары (на них не заработаем). 1 покупка из рассылок стоит 60 руб.
    data['price'] = data['sales_value'] / (np.maximum(data['quantity'], 1))
    data = data[data['price'] > 2]

    # Уберем слишком дорогие товарыs
    data = data[data['price'] < 50]

    # Возбмем топ по популярности
    popularity = data.groupby('item_id')['quantity'].sum().reset_index()
    popularity.rename(columns={'quantity': 'n_sold'}, inplace=True)

    top = popularity.sort_values('n_sold', ascending=False).head(take_n_popular).item_id.tolist()
    
    # Заведем фиктивный item_id (если юзер покупал товары из топ-5000, то он "купил" такой товар)
    data.loc[~data['item_id'].isin(top), 'item_id'] = 999999
    
    # ...

    return data

def features_generation(data, target):
    
    df = data.groupby(['item_id', 'department'])['quantity'].sum().reset_index()
    df = df.groupby('item_id')['quantity'].mean().reset_index()
    df.columns = ['item_id', 'mean_item_count_by_dep']
        
    result = target.merge(df, on='item_id')
    # средняя трата пользователя 
    df = data.groupby(['user_id', 'basket_id'])['sales_value'].sum().reset_index()
    df = df.groupby('user_id')['sales_value'].mean().reset_index()
    df.columns = ['user_id', 'mean_sales']
        
    result = result.merge(df, on='user_id')
    # среднее число покупок конкретной категории товара в неделю
    df = data.groupby(['department', 'week_no'])['quantity'].sum().reset_index()
    df = df.groupby('department')['quantity'].mean().reset_index()
    df.columns = ['department', 'week_mean_count_by_dep']
            
    result = result.merge(df, on='department')
    # среднее количество покупок пользователя в каждой категории товаров
    df = data.groupby(['user_id', 'department'])['quantity'].sum().reset_index()
    df = df.groupby('user_id')['quantity'].mean().reset_index()
    df.columns = ['user_id', 'mean_count_by_dep']
        
    result = result.merge(df, on='user_id')
    
    return result



def postfilter_items(user_id, recommednations):
    pass