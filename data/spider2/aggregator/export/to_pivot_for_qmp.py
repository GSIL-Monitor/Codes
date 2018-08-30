
import pandas as pd
import numpy as np
from math import isnan
import openpyxl
import requests


class Make_Qmp_Pivot(object):

    def __init__(self):
        self.df_excel = pd.read_excel('/Users/hush/Desktop/export.xlsx', index_col=0)  # 不要重新建立索引
        self.df = pd.DataFrame(self.df_excel[self.df_excel['country'] == 'CN']).reset_index()
        self.df2 = pd.read_excel('/Users/hush/Desktop/export2.xlsx', index_col=0)

    def compare_keyi_count(self):
        """
        根据可疑的情况进行统计 各种情况的公司数

        """
        piv1 = self.df.groupby('可疑')['country'].count().to_frame()
        piv1.loc['总计'] = piv1.values.sum()
        piv1 = pd.pivot_table(piv1, index=['可疑']).sort_values(by='country')
        piv1.rename(columns={'country': 'Count'}, inplace=True)
        piv1.to_excel('/Users/hush/Desktop/1.xlsx', index=1)  # index=1 保留原有索引
        return piv1

    def compare_queshi_count(self):
        """
        根据 '匹配不到公司','烯牛无融资' 这两种缺失情况 按阶段轮次统计

        """

        piv2 = self.df.groupby(['可疑', 'jieduan'])['country'].aggregate('count').unstack().loc[['匹配不到公司', '烯牛无融资']]
        for i in piv2.columns:
            lis = list(piv2[i].values)
            if list(map(isnan, lis)) == [True, True]:
                piv2.drop(i, axis=1, inplace=True)

        piv2.fillna(0, inplace=True)
        piv2 = piv2.astype(np.int)
        piv2 = piv2.T
        piv2 = pd.pivot_table(piv2, index=['jieduan'])
        piv2['总计'] = piv2.apply(lambda x: x.sum(), axis=1)
        piv2.loc['总计'] = piv2.apply(lambda x: x.sum())
        piv2.to_excel('/Users/hush/Desktop/2.xlsx', index=1)
        return piv2

    def compare_dujia_count(self):
        """
        统计烯牛独家在各阶段的公司数量

        """
        piv3 = self.df.groupby(['可疑', 'roundDesc'])['country'].aggregate('count').unstack().loc['烯牛独家']
        piv3.fillna(0, inplace=True)
        piv3 = piv3.astype(np.int)
        piv3['总计'] = piv3.sum()
        piv3 = pd.DataFrame(piv3).sort_values(by='烯牛独家')
        piv3 = pd.pivot_table(piv3, index=['roundDesc']).sort_values(by='烯牛独家')
        piv3.to_excel('/Users/hush/Desktop/3.xlsx', index=1)
        return piv3

    def compare_total_count(self):
        """
        统计 企名片 和 烯牛 阶段分布的公司数量比较

        """
        self.df2.fillna(0, inplace=True)
        df = self.df2.astype(np.int)
        df.loc['总计'] = df.apply(lambda x: x.sum())
        piv4 = pd.pivot_table(df, index=['轮次']).sort_values(by=['烯牛', '企名片'])
        piv4.to_excel('/Users/hush/Desktop/4.xlsx', index=1)
        return piv4



if __name__ == '__main__':
    pass

    # qmp_pivot = Make_Qmp_Pivot()
    # pivot1 = qmp_pivot.compare_keyi_count()
    # print(pivot1)
    # print('-------------------------------')
    # pivot2 = qmp_pivot.compare_queshi_count()
    # print(pivot2)
    # print('-------------------------------')
    # pivot3 = qmp_pivot.compare_dujia_count()
    # print(pivot3)
    # print('-------------------------------')
    # pivot4 = qmp_pivot.compare_total_count()
    # print(pivot4)




