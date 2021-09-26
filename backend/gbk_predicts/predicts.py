import os
import pandas as pd
from tensorflow.keras.models import load_model


def get_filename(name: str) -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), name)


models = {}
data_stats = pd.read_csv(get_filename('data_stats.csv'), index_col=0, encoding='gbk')
model_names = [
    'order', 'visible', 'visit'
]
data_columns = ['小包最低价', '小包最高价', '中包最低价', '中包最高价', '大包最低价', '大包最高价']


def norm(train_stats, x):
    # 数据规范化
    return (x - train_stats['mean']) / train_stats['std']


def predict_data(models_m, data):
    # 预测

    # 预测曝光人数
    data = norm(data_stats, data)
    data = data[['小包最低价', '小包最高价', '中包最低价', '中包最高价', '大包最低价', '大包最高价']]
    visible_num = models_m['visible'].predict(data).flatten()

    # 预测访问人数
    data['曝光人数'] = visible_num
    data = norm(data_stats, data)
    data = data[['曝光人数', '小包最低价', '小包最高价', '中包最低价', '中包最高价', '大包最低价', '大包最高价']]
    visit_num = models_m['visit'].predict(data).flatten()

    # 预测下单人数
    data['访问人数'] = visit_num
    data = norm(data_stats, data)
    data = data[['曝光人数', '访问人数', '小包最低价', '小包最高价', '中包最低价', '中包最高价', '大包最低价', '大包最高价']]
    order_num = models_m['order'].predict(data).flatten()

    prediction = {'visible': visible_num,
                  'visit': visit_num,
                  'order': order_num}

    return prediction


def init_models():
    global models
    for name in model_names:
        try:
            models[name] = load_model(get_filename(name))
        except OSError:
            models[name] = load_model(get_filename(name + '.h5'))


def predicts(data: dict):
    frame_data = pd.DataFrame(data, columns=data_columns)
    res = predict_data(models, frame_data)
    for k in res:
        res[k] = res[k].tolist()
    return res


init_models()
