import json
from typing import Any, MutableSequence
from urllib.parse import quote, quote_plus
from urllib.request import Request, urlopen


DataDictionary = {
    "한영번역": ["ko", "Korean", "en", "English"],
    "영한번역": ["en", "English", "ko", "Korean"],
    "한일번역": ["ko", "Korean", "ja", "Japanese"],
    "일한번역": ["ja", "Japanese", "ko", "Korean"],
    "한중번역": ["ko", "Korean", "zh-CN", "Chinese"],
    "중한번역": ["zh-CN", "Chinese", "ko", "Korean"],
    "일영번역": ["ja", "Japanese", "en", "English"],
    "영일번역": ["en", "English", "ja", "Japanese"],
    "영중번역": ["en", "English", "zh-CN", "Chinese"],
    "중영번역": ["zh-CN", "Chinese", "en", "English"],
    "중일번역": ["zh-CN", "Chinese", "ja", "Japanese"],
    "일중번역": ["ja", "Japanese", "zh-CN", "Chinese"],
}


class dataProcessStream(object):
    def __init__(self, client_id, client_secret):
        self.baseurl = "https://openapi.naver.com/v1/papago/n2mt"
        self.translateDict = dict()
        self.InitiateData()
        self.client_id = client_id
        self.client_secret = client_secret

    def InitiateData(self) -> None:
        for y in list(DataDictionary.keys()):
            self.translateDict[y] = {
                "ntl": {
                    "queryParam": DataDictionary[y][0],
                    "languageName": DataDictionary[y][1]
                },
                "tl": {
                    "queryParam": DataDictionary[y][2],
                    "languageName": DataDictionary[y][3]
                }
            }

    def returnQuery(self, message, translateType) -> MutableSequence:
        needTranslate = message
        basicQuery = f"source={self.translateDict[translateType]['ntl']['queryParam']}&target={self.translateDict[translateType]['tl']['queryParam']}&text={quote_plus(needTranslate)}"
        return self.buildRequestInstane(basicQuery, needTranslate, self.translateDict[translateType]['ntl']['languageName'], self.translateDict[translateType]['tl']['languageName'])

    def buildRequestInstane(self, Query, needTranslate, ntl, tl) -> MutableSequence:
        req = Request(self.baseurl)
        req.add_header("X-Naver-Client-Id", self.client_id)
        req.add_header("X-Naver-Client-Secret", self.client_secret)
        response = urlopen(req, data=Query.encode("utf-8"))
        return self.checkResponseReturnDataBox(response, needTranslate, ntl, tl)

    def checkResponseReturnDataBox(self, response, needTranslate, ntl, tl) -> MutableSequence:
        dataBox = {
            "status": {
                "code": None
            },
            "data": {
                "ntl": {
                    "text": needTranslate,
                    "name": ntl
                },
                "tl": {
                    "text": None,
                    "name": tl
                }
            }
        }
        if response.getcode() < 300:
            dataBox["status"]["code"] = response.getcode()
            response = response.read()
            apiResult = response.decode('utf-8')
            apiResult = json.loads(apiResult)
            translated = apiResult['message']['result']["translatedText"]
            dataBox["data"]["tl"]["text"] = translated
            return dataBox
        else:
            dataBox["status"]["code"] = response.getcode()
            return dataBox
