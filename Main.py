# -*- coding:utf-8 -*-

import Akinator
import choice



def main():
    print(
        '''在脑海中猜想一个真实或虚构的人物,我将猜出TA是谁
    [提示:尽量选择精确的答案,除非该问题真的未被提及过,才选择模糊答案]
    [服务器响应缓慢,请耐心等待]
    ''')

    game = Akinator.Akinator()
    game.AskQuestion()
    progression = game.GetNextQuestion()
    print('')

    while True:
        ansID = game.AskQuestion()
        print('')

        if ansID == 5:  # 选择 6.查看当前猜测
            problAns = game.GetProblAns()
            print('')
            for i in problAns:
                print('[{}%]{}'.format(
                    round(float(i['element']['proba']) * 100), i['element']['name']))
                print(i['element']['description'] + '\n')
        elif ansID == 6:  # 选择 7.上一步
            game.CancelLastAnswer()
        else:
            progression = game.GetNextQuestion()

        if float(progression) >= 95:
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
