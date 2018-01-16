#!/usr/bin/env python
# -*- coding:utf-8 -*-

import Akinator_new as Akinator
import choice

def AskQuestion(prompt):
    print(prompt)
    print('1.是 2.否 3.不知道 4.或许是 5.或许不是 [6.查看Akinator当前猜测 7.返回上一步]')
    ans_id = choice.choice('你的回答是:', '1234567')
    return ans_id

def main():
    print(
        '''在脑海中猜想一个真实或虚构的人物,我将猜出TA是谁
    [提示:尽量选择精确的答案,除非该问题真的未被提及过,才选择模糊答案]
    [服务器响应缓慢,请耐心等待]
    ''')

    game = Akinator.Akinator()
    ans_id = AskQuestion(game.GetQuestion())
    progess = game.SendAnswer(ans_id)
    print('')

    while True:
        ans_id = AskQuestion(game.GetQuestion())
        print('')

        if ans_id == 5:  # 选择 6.查看当前猜测
            problAns = game.GetProblAns()
            print('')
            for i in problAns:
                print('[{}%]{}'.format(
                    round(float(i['element']['proba']) * 100), i['element']['name']))
                print(i['element']['description'] + '\n')
        elif ans_id == 6:  # 选择 7.上一步
            game.CancelLastAnswer()
        else:
            progess = game.SendAnswer(ans_id)

        if float(progess) >= 95:
            problAns = game.GetProblAns()[0]['element']
            print(
                '我想:{}--{}\n'.format(problAns['name'], problAns['description']))

            ansIsTrue = choice.choice('我猜对了吗?(Y/N):', 'yYnN')

            if ansIsTrue >= 2:
                game.ExcludeAns()
                bContinue = choice.choice('继续?(Y/N)', 'yYnN')
                if bContinue >= 2:
                    break
            else:
                AnsInfo = game.SendChoice(problAns['id'])[
                    'parameters']['element_informations']
                game.CancelSession()
                print('\n该人物已被使用{}次\n上一次使用是{}\n'.format(
                    AnsInfo['times_selected'], AnsInfo['previous']))
                
                onceAgain = choice.choice('再来一次吗?(Y/N)', 'yYnN')

                if onceAgain < 2:
                    print('')
                    main()

                break

if __name__ == '__main__':
    main()
