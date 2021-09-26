from data_apis.data_tools import *


class Solution(APIComponent):
    url = 'https://e.dianping.com/fun/ktv/solutionlist'

    def get_solution_id(self):
        resp = self.request_func(self.url)
        if resp is None:
            raise GBKLoginError("需要登录")
        # print(resp)
        # with open("solution.html", 'w', encoding='utf8') as f:
        #     f.write(resp)
        if '没有权限' in resp:
            raise GBKPermissionError("没有权限")
        try:
            # html = etree.HTML(resp)
            # try:
            #     data = html.xpath('/html/body/div[1]/div/div/table/tbody/tr/td[4]/a')[0]
            # except IndexError:
            #     raise GBKPermissionError("没有权限")
            # href = data.attrib['href']
            # solution_id = int(href.split('=')[-1])

            result = re.findall(r'data-solutionid="[0-9]*"', resp)
            if len(result) == 0:
                raise GBKPermissionError("没有权限")
            solution_id = int(result[0][17:-1])
            return solution_id
        except GBKPermissionError as e:
            logger.warning(e)
            raise e
        except Exception as e:
            logger.warning(e)
            raise GBKError("未知错误")
