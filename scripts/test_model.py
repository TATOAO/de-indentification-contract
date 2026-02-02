# python scripts/test_model.py 
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks


semantic_cls = pipeline(
    'rex-uninlu', 
    model='./models/modelscope/iic/nlp_deberta_rex-uninlu_chinese-base', model_revision='v1.2.1',
    )

# 命名实体识别 {实体类型: None}
result = semantic_cls(
    input='1944年毕业于北大的名古屋铁道会长谷口清太郎等人在日本积极筹资，共筹款2.7亿日元，参加捐款的日本企业有69家。', 
    schema={
        '人物': None,
        '地理位置': None,
        '组织机构': None
    }
) 
print(result) 

# 关系抽取 {主语实体类型: {关系(宾语实体类型): None}}
result = semantic_cls(
  input='1987年首播的央视版《红楼梦》是中央电视台和中国电视剧制作中心根据中国古典文学名著《红楼梦》摄制的一部古装连续剧', 
    schema={
        '组织机构': {
            '注册资本(数字)': None,
            '创始人(人物)': None,
            '董事长(人物)': None,
            '总部地点(地理位置)': None,
            '代言人(人物)': None,
            '成立日期(时间)': None, 
            '占地面积(数字)': None, 
            '简称(组织机构)': None
        }
    }
) 
print(result) 