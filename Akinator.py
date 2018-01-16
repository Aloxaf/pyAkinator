# -*- coding:utf-8 -*-

import requests
import time
import choice

# TODO: __baseURL可以包含session和signature


class Akinator(object):

    host = 'http://api-cn1.akinator.com/ws'

    def __init__(self):
        session = self.NewSession()
        self.session_info = session['parameters']['identification']
        self.step_info = session['parameters']['step_information']

    def post(self, URL, params={}):
        params.update({
            'session': self.session_info['session'],
            'signature': self.session_info['signature'],
            '_': round(time.time() * 1000)
        })
        while True:
            try:
                return requests.get(URL, timeout=5, params=params)
            except:
                pass

    def NewSession(self):
        url = f"{self.host}/new_session?partner=1&player=desktopPlayer&constraint=ETAT<>'AV'&_={{}}"
        res = requests.get(url.format(round(time.time() * 1000)))
        return res.json()

    def CancelSession(self):
        self.post(f'{self.host}/cancel_game')

    def ExcludeAns(self):
        self.post(f'{self.host}/exclusion', params={
            'step': self.step_info['step'],
            'forward_answer': '1'
        })
        self.step_info['step'] = str(int(self.step_info['step']) - 1)
        self.GetNextQuestion()

    def SendChoice(self, eleID):
        res = self.post(f'{self.host}/choice', params={
            'step': self.step_info['step'],
            'element': eleID,
            'duel_allowed': '1'
        })
        return res.json()

    def SendAnswer(self, ans_id):
        res = self.post(f'{self.host}/answer', params={
            'step': self.step_info['step'],
            'answer': ans_id
        })
        self.step_info = res.json()['parameters']
        return self.step_info['progression']

    def CancelLastAnswer(self):
        res = self.post(f'{self.host}/cancel_answer', params={
            'step': self.step_info['step'],
            'answer': '-1'
        })
        self.step_info = res.json()['parameters']
        return self.step_info['progression']

    # FIXME: 第一个问题不能有 6 7 选项
    def GetQuestion(self):
        return '[{}%]{}.{}'.format(
            round(float(self.step_info['progression'])),
            str(int(self.step_info['step']) + 1),
            self.step_info['question']
        )

    def GetProblAns(self):
        res = self.post(f'{self.host}/list', params={
            'step': self.step_info['step'],
        })
        return res.json()['parameters']['elements']
