from implicit.als import AlternatingLeastSquares
from scipy.sparse import csr_matrix

model = AlternatingLeastSquares(factors=20, 
                                regularization=0.001,
                                iterations=15, 
                                calculate_training_loss=True, 
                                use_gpu=False)


"""
model.fit(csr_matrix(user_item_matrix).T.tocsr(),  # На вход item-user matrix
          show_progress=True)


def get_recommendations(user, model, N=5):
    res = [id_to_itemid[rec[0]] for rec in 
                    model.recommend(userid=userid_to_id[user], 
                                    user_items=csr_matrix(user_item_matrix).tocsr(),   # на вход user-item matrix
                                    N=N, 
                                    filter_already_liked_items=False, 
                                    filter_items=[itemid_to_id[999999]],  # !!! 
                                    recalculate_user=True)]
    return res

model.similar_users(userid_to_id[10], N=6)

own = ItemItemRecommender(K=1, num_threads=4) # K - кол-во билжайших соседей

own.fit(csr_matrix(user_item_matrix).T.tocsr(), 
          show_progress=True)

recs = model.recommend(userid=userid_to_id[1], 
                        user_items=csr_matrix(user_item_matrix).tocsr(),   # на вход user-item matrix
                        N=5, 
                        filter_already_liked_items=False, 
                        filter_items=None, 
                        recalculate_user=False)

get_recommendations(user=1, model=own, N=1)


# Функция дает список из N-1 id_items близких (похожих) к товару с индексом х
def get_item_rec(model, x, N=2):
    recs = model.similar_items(itemid_to_id[x], N=N)
    result = []
    for i in range(1, N):
        top_rec = recs[i][0]
        result.append(id_to_itemid[top_rec])
    return result

"""