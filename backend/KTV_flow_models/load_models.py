import os
import pandas as pd
import tensorflow as tf


def norm(train_stats, x):
    # 数据规范化
    return (x - train_stats['mean']) / train_stats['std']


def load_models():
    # 加载模型
    models_ = {}
    changed_dir = False
    path_origin = os.path.abspath(os.curdir)
    if 'KTV_flow_models' in os.listdir("."):
        os.chdir("KTV_flow_models")
        changed_dir = True
    models_['visible'] = tf.keras.models.load_model('visible_model')
    models_['visit'] = tf.keras.models.load_model('visit_model')
    models_['order'] = tf.keras.models.load_model('order_model')
    if changed_dir:
        os.chdir(path_origin)
    return models_


def predict_data(models, data):
    # 预测

    # 预测曝光人数
    data = norm(data_stats, data)
    data = data[['小包最低价', '小包最高价', '中包最低价', '中包最高价', '大包最低价', '大包最高价']]
    visible_num = models['visible'].predict(data).flatten()

    # 预测访问人数
    data['曝光人数'] = visible_num
    data = norm(data_stats, data)
    data = data[['曝光人数', '小包最低价', '小包最高价', '中包最低价', '中包最高价', '大包最低价', '大包最高价']]
    visit_num = models['visit'].predict(data).flatten()

    # 预测下单人数
    data['访问人数'] = visit_num
    data = norm(data_stats, data)
    data = data[['曝光人数', '访问人数', '小包最低价', '小包最高价', '中包最低价', '中包最高价', '大包最低价', '大包最高价']]
    order_num = models['order'].predict(data).flatten()

    prediction = {'visible': visible_num,
                  'visit': visit_num,
                  'order': order_num}

    return prediction


models = load_models()
data_stats = None
try:
    data_stats = pd.read_csv('data_stats.csv', index_col=0, encoding='gbk')
except FileNotFoundError:
    data_stats = pd.read_csv('./KTV_flow_models/data_stats.csv', index_col=0, encoding='gbk')


def predict(data: dict):
    frame_data = pd.DataFrame(data, columns=['小包最低价', '小包最高价', '中包最低价', '中包最高价', '大包最低价', '大包最高价'])
    res = predict_data(models, frame_data)
    for k in res:
        res[k] = res[k].tolist()
    return res


def test_run():
    # 加载数据集的统计信息
    data_stats = pd.read_csv('data_stats.csv', index_col=0, encoding='gbk')
    # 加载模型
    # models = load_models()

    # 输入数据为DataFrame格式，既可以输入单行数据，也可以输入多行数据
    data = {'小包最低价': [32, 40], '小包最高价': [64, 75], '中包最低价': [52, 66], '中包最高价': [122, 144], '大包最低价': [55, 70],
            '大包最高价': [155, 160]}
    data = pd.DataFrame(data, columns=['小包最低价', '小包最高价', '中包最低价', '中包最高价', '大包最低价', '大包最高价'])

    res = predict_data(models, data)
    print(res)
    # 输出结果应为：{'visible': array([2319.2788, 3036.0405], dtype=float32), 'visit': array([672.054 , 821.1971], dtype=float32), 'order': array([75.604065, 78.74483 ], dtype=float32)}

    data = {'小包最低价': [32], '小包最高价': [64], '中包最低价': [52], '中包最高价': [122], '大包最低价': [55], '大包最高价': [155]}
    data = pd.DataFrame(data, columns=['小包最低价', '小包最高价', '中包最低价', '中包最高价', '大包最低价', '大包最高价'])

    res = predict_data(models, data)
    print(res)
    # 输出结果应为：{'visible': array([2319.2788], dtype=float32), 'visit': array([672.05396], dtype=float32), 'order': array([75.604065], dtype=float32)}
