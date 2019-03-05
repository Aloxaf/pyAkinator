from collections import namedtuple
from requests import Session, Response
from typing import Dict, List, Union
from time import time
import re

Param = Union[str, int]
Guess = namedtuple('Guess', 'id name description picture')
StepInfo = namedtuple('StepInfo', 'step question answers progression')
CharacterInfo = namedtuple('CharacterInfo', 'times_selected previous')


class Game:
    api: str = 'https://srv11.akinator.com:9150/ws'
    ses: Session
    # game
    session: str
    signature: str
    step_info: StepInfo

    def __init__(self) -> None:
        self.ses = Session()
        # the proxies setting doesn't seem to work 
        self.ses.proxies = {
            'http': 'socks5h://127.0.0.1:8877',
            'https': 'socks5h://127.0.0.1:8877',
        }
        self.ses.headers = {
            'DNT': '1',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
            'Accept': '*/*',
            'Referer': 'https://cn.akinator.com/game',
            'Connection': 'keep-alive',
        }
        json = self.new_session()
        self.session = json['parameters']['identification']['session']
        self.signature = json['parameters']['identification']['signature']
        self.update_step_info(json['parameters']['step_information'])

    def update_step_info(self, info: Dict) -> None:
        self.step_info = StepInfo(
            question=info['question'],
            answers=[i['answer'] for i in info['answers']],
            step=info['step'],
            progression=info['progression']
        )

    def get(self, url: str, params: Dict = None) -> Response:
        if params:
            params.update({'_': str(round(time() * 1000))})
        return self.ses.get(url, params=params, proxies={
            'https': 'socks5h://127.0.0.1:8877'
        })

    def new_session(self) -> Dict:
        """开始新游戏"""
        res = self.get('https://cn.akinator.com/game')
        params = {
            'partner': '1',
            'player': 'website-desktop',
            'uid_ext_session': re.findall(r"(?<=uid_ext_session = ').*(?=')", res.text)[0],
            'frontaddr': re.findall(r"(?<=frontaddr = ').*(?=')", res.text)[0],
            'constraint': 'ETAT<>\'AV\'',
            'soft_constraint': '',
            'question_filter': '',
        }
        return self.get(f'{self.api}/new_session', params=params).json()

    def send_answer(self, ans_id: Param) -> None:
        """发送答案序号"""
        params = {
            'session': self.session,
            'signature': self.signature,
            'step': self.step_info.step,
            'answer': ans_id,
            'question_filter': '',
        }
        json = self.get(f'{self.api}/answer', params=params).json()
        self.update_step_info(json['parameters'])

    def get_question(self) -> str:
        """获取当前问题"""
        return f"{self.step_info.step}. {self.step_info.question}"

    def get_answers(self) -> List[str]:
        """获取当前答案列表"""
        return self.step_info.answers

    def get_progression(self) -> float:
        """获取当前游戏进度(百分比)"""
        return float(self.step_info.progression)

    def cancel_answer(self) -> None:
        """返回上一题"""
        params = {
            'session': self.session,
            'signature': self.signature,
            'step': self.step_info.step,
            'answer': '-1',
            'question_filter': '',
        }
        json = self.get(f'{self.api}/cancel_answer', params=params).json()
        self.update_step_info(json['parameters'])

    def get_guess(self, size: Param = 2) -> List[Guess]:
        """获取当前猜测列表, size 为列表大小, 一般为 2/20 """
        params = {
            'session': self.session,
            'signature': self.signature,
            'step': self.step_info.step,
            'size': size,
            'max_pic_width': '246',
            'max_pic_height': '294',
            'pref_photos': 'VO-OK',
            'duel_allowed': '1',
            'mode_question': '0',
        }
        json = self.get(f'{self.api}/list', params=params).json()
        return [
            Guess(
                id=guess['element']['id'],
                name=guess['element']['name'],
                description=guess['element']['description'],
                picture=guess['element']['absolute_picture_path']
            ) for guess in json['parameters']['elements']
        ]

    def send_result(self, element: Param) -> CharacterInfo:
        """发送猜测结果"""
        params = {
            'session': self.session,
            'signature': self.signature,
            'step': self.step_info.step,
            'element': element,
            'duel_allowed': '1',
        }
        json = self.get(f'{self.api}/choice', params=params).json()
        info = json['parameters']['element_informations']
        return CharacterInfo(times_selected=info['times_selected'], previous=info['previous'])

    def exclude(self) -> None:
        """排除当前猜测"""
        params = {
            'session': self.session,
            'signature': self.signature,
            'step': self.step_info.step,
            'question_filter': '',
            'forward_answer': '1',
        }
        json = self.get(f'{self.api}/exclusion', params=params).json()
        self.update_step_info(json['parameters'])


def main():
    game = Game()

    print('''在脑海中猜想一个真实或虚构的人物,我将猜出TA是谁
[提示:尽量选择精确的答案,除非该问题真的未被提及过,才选择模糊答案]
[服务器响应缓慢,请耐心等待]
''')

    while True:
        while game.get_progression() <= 95:
            print(game.get_question())
            print('  '.join(f'{i+1}: {j}' for i, j in enumerate(game.get_answers() + ['返回上一步'])))
            choice = int(input())
            if choice == 6:
                game.cancel_answer()
            else:
                game.send_answer(choice - 1)

        guess = game.get_guess()[0]
        print(f'我猜: {guess.name} —— {guess.description}')

        if input('我猜对了吗? (Y/N): ').upper() == 'Y':
            info = game.send_result(guess.id)
            print(f'太棒了!\n该人物已被使用 {info.times_selected} 次, 上一次使用是 {info.previous}')
            return
        else:
            if input('要继续吗? (Y/N): ').upper() == 'Y':
                game.exclude()
            else:
                print('很好, 你打败我了')
                print('PS 后面的API就没解析了, 因为懒')


if __name__ == '__main__':
    main()
