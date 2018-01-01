# -*- coding:utf-8 -*-

import urllib.request
import time
import json
import choice

# TODO: __baseURL可以包含session和signature
class Akinator(object):

    def __init__(self):
        Session = self.__NewSession()
        self.__SessionInfo = Session['parameters']['identification']
        self.__stepInfo    = Session['parameters']['step_information']

    def __baseURL(self, func, param=''):
        return 'http://api-cn1.akinator.com/ws/' + func + '?session={}&signature={}&_={}&'.format(
            self.__SessionInfo['session'], self.__SessionInfo['signature'], round(time.time() * 1000)
        ) + param

    def __getBytesFromURL(self, URL):
        while True:
            try:
                return urllib.request.urlopen(URL, timeout=5).read()
            except:
                pass

    def __NewSession(self):
        url = "http://api-cn1.akinator.com/ws/new_session?partner=1&player=desktopPlayer&constraint=ETAT<>'AV'&_={}"
        res = self.__getBytesFromURL(url.format(round(time.time() * 1000)))
        return json.loads(res.decode())

    def CancelSession(self):
        url = self.__baseURL('cancel_game')
        self.__getBytesFromURL(url)

    def ExcludeAns(self):
        url = self.__baseURL('exclusion', 'step={}&forward_answer=1'.format(self.__stepInfo['step']))
        self.__getBytesFromURL(url) #不需要返回值
        self.__stepInfo['step'] = str(int(self.__stepInfo['step']) - 1)
        self.GetNextQuestion()

    def SendChoice(self, eleID):
        url = self.__baseURL('choice', 'step={}&element={}&duel_allowed=1'.format(
            self.__stepInfo['step'], eleID
        ))
        return json.loads(self.__getBytesFromURL(url))

    def GetNextQuestion(self):
        url = self.__baseURL('answer', 'step={}&answer={}'.format(self.__stepInfo['step'], self.__ansID))
        res = self.__getBytesFromURL(url)
        self.__stepInfo = json.loads(res.decode())['parameters']
        return self.__stepInfo['progression']

    def CancelLastAnswer(self):
        url = self.__baseURL('cancel_answer', 'step={}&answer=-1'.format(self.__stepInfo['step']))
        res = self.__getBytesFromURL(url)
        self.__stepInfo = json.loads(res.decode())['parameters']
        return self.__stepInfo['progression']

    # FIXME: 第一个问题不能有 6 7 选项
    def AskQuestion(self):
        print('[{}%]{}.{}'.format(
            round(float(self.__stepInfo['progression'])),
            str(int(self.__stepInfo['step'])+1),
            self.__stepInfo['question']
        ))
        print('1.是 2.否 3.不知道 4.或许是 5.或许不是 [6.查看Akinator当前猜测 7.返回上一步]')
        self.__ansID = choice.choice('你的回答是:', '1234567')
        return self.__ansID

    def GetProblAns(self):
        url = self.__baseURL('list', 'step={}'.format(self.__stepInfo['step']))
        res = self.__getBytesFromURL(url)
        return json.loads(res.decode())['parameters']['elements']
