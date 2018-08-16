from PIL import Image
from pandas import read_excel
from pyecharts import Bar, Pie, Geo, Map, WordCloud, Line
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import re
import jieba
import numpy as np
from wordcloud import WordCloud, ImageColorGenerator
import matplotlib.pyplot as plt

def stopwords():
    #  读取停用词库，然后是一行一行的迭代，然后line.rstrip()将 末尾的“\n”去掉，返回一个列表格式
    stopwords_list1 = [line.rstrip() for line in open("./stopwords/四川大学机器智能实验室停用词库.txt", "r", encoding="utf-8")]
    stopwords_list2 = [line.rstrip() for line in open("./stopwords/哈工大停用词表.txt", "r", encoding="utf-8")]
    stopwords_list3 = [line.rstrip() for line in open("./stopwords/中文停用词库.txt", "r", encoding="utf-8")]
    #   将上述获取的列表词库合并为一个词库，并且  去重   ---> set()  --->  list()  转化为列表格式
    stopwords_list = list(set(stopwords_list1 + stopwords_list2 + stopwords_list3))

    return stopwords_list

csvFrame = read_excel("./一出好戏.xlsx", index=False)
# print(type(csvFrame))
# print(csvFrame)

# 根据userId进行去重, 获取去重后的真实数据
data = csvFrame.drop_duplicates(['userId'])
# print(data)

# 获取基本描述信息
describe = data.describe()
print(describe)

# 根据城市进行分组
cityGroup = data.groupby("city")

# 评分人数 > 10的方为有效评分城市
countInfo = cityGroup.count()

# 筛选列中>10的每行的数据
data2 = countInfo[countInfo['userId']>10]
print(data2)
# 获取城市索引
citys = data2.index

# 从大数据中筛选合格数据, 然后拼接
frame = pd.DataFrame()

for city in citys:
    newData = data[data['city'] == city]
    if frame.empty:
        frame = newData
    else:
        # 行拼接
        frame = frame.append(newData)

# # 真实数据根据城市进行分组
cityGroup2 = frame.groupby("city")
cityScores = cityGroup2['score']

# print(cityScores)

## 全国热力图
city_com = cityScores.agg(['mean', 'count'])
citys = city_com.index
city_mean = city_com["mean"].values
city_count = city_com["count"].values

# 对打分数据进行优化处理
city_mean = np.array(city_mean)
city_score = np.round(city_mean, 2)

# 主城市打分柱状图
bar = Bar("《一出好戏》部分城市评分", "猫眼均分")
bar.add("Score", citys, city_score)
bar.show_config()
bar.render(path="./signs/评分柱状图.html")

# 主城市打分折线图 和 人员分布图
line = Line("观众分布折线图")
# line.add("评分", citys, city_score, line_opacity=0.2, area_opacity=0.4, symbol=None)
line.add("观众数", citys, city_count, is_fill=True, area_opacity=0.3, is_smooth=True)
line.show_config()
line.render(path='./signs/观众分布折线图.html')

# 全国观看热力图
geo = Geo('《一出好戏》观众分布图', title_color="#fff",
          title_pos="center", width=1200, height=600, background_color='#404a59')
geo.add("", citys, city_count, type='heatmap', visual_range=[0, 35],
        visual_text_color="#fff", symbol_size=10, is_visualmap=True,
        is_roam=False)
geo.render('./signs/观众分布图.html')


# 全国评分图
geo = Geo('《一出好戏》全国评分图', title_color="#fff",
          title_pos="center", width=1200, height=600, background_color='#404a59')
geo.add("", citys, city_score, visual_range=[3, 5],
        visual_text_color="#fff", symbol_size=10, is_visualmap=True,
        is_roam=False)
geo.render('./signs/全国评分图.html')

# 观看占比饼图
pie = Pie()
pie.add("", citys, city_count, is_label_show=True)
pie.render(path="./signs/观众占比饼图.html")


# 绘制词云
# 连接所有评论，去除特殊字符(去除特殊无用字符：因为，所以，虽然等等和人名)

comments = data['comment']

wash_signature=[]
for item in comments:
    #去除emoji表情等非文字
    if "emoji" in item:
        continue
    rep = re.compile("1f\d+\w*|[<>/=【】『』♂ω]")
    item=rep.sub("", item)
    wash_signature.append(item)


words="".join(wash_signature)

# 用jieba切片
wordlist = jieba.cut(words, cut_all=True)
word_space_split = " ".join(wordlist)

# 统计单词占比
# 这里可以使用stopwords  之所以没用是因为对电影的评价有 一般
# stopwords = stopwords()

tfidf = TfidfVectorizer(stop_words=['张艺兴', '黄渤', '绵阳', '电影', '王宝强'])
data2 = tfidf.fit_transform([word_space_split])

indexs = tfidf.get_feature_names()
narray = data2.toarray()

ser = pd.Series(narray[0], index = indexs)

# 大于指定数值
# print(ser[ser.values > 0.05])

print("^^" * 30)
# 排序，选择前n个
ser2 = ser.sort_values(ascending=False)
# 获取排名靠前的100个单词
worlds = ser2[0:100].index
# print(worlds)

new_worlds = " ".join(worlds)

coloring = np.array(Image.open("./signs/huangbo.jpg"))

# simkai.ttf 必填项 识别中文的字体，例：simkai.ttf，
my_wordcloud = WordCloud(background_color="white", max_words=800,
                         mask=coloring, max_font_size=120, random_state=30, scale=2,font_path="./signs/simkai.ttf").generate(new_worlds)

image_colors = ImageColorGenerator(coloring)
plt.imshow(my_wordcloud.recolor(color_func=image_colors))
plt.imshow(my_wordcloud)
plt.axis("off")
plt.show()

# 保存图片
my_wordcloud.to_file('./signs/关键词.png')







