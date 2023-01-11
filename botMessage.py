import random
import variable

# 詢問參加遊戲的訊息
async def start_message(channel):
    try:
        variable.myData.gameStatus = 1
        returnMsg = await channel.send('>>> 你要不要來一場？')
        await returnMsg.add_reaction(variable.myData.reaction["reaction_check"][0])
        await returnMsg.add_reaction(variable.myData.reaction["reaction_check"][1])
        await returnMsg.add_reaction(variable.myData.reaction["reaction_check"][2])
        variable.myData.lastMessage = returnMsg
    except Exception as e:
        print(variable.myData)


async def game_start(payload, mem):
    # 點黃色方塊 -> 參加遊戲
    if payload.emoji.name == variable.myData.reaction["reaction_check"][0]:
        variable.myData.playerName.append(payload.member.name)  # 紀錄玩家名稱
        variable.myData.saveGuildInfo[payload.member.name] = payload.member

        msg = []  # 這個玩家拿到的卡片
        msg = random_give_card(msg)
        variable.myData.player[payload.member.name] = msg
        await payload.member.send('>>> round ' + str(variable.myData.topicPlayer + 1) + ': ' + str(msg) + ' is your card')

    # 開始遊戲
    elif (payload.emoji.name == variable.myData.reaction["reaction_check"][1]) and (variable.myData.firstPlayer == payload.member.name):
        await variable.myData.lastMessage.clear_reactions()
        variable.myData.playNum = len(variable.myData.player)
        await mem.send('>>> there are ' + str(variable.myData.playNum) + ' players')
        variable.myData.gameStatus = 2
        for name in variable.myData.playerName:
            variable.myData.scoreBoard[name] = 0

##################################################################################################################################

def random_give_card(msg):
    list = variable.myData.card["myCards"]  # 所有卡片
    # 總之就是從牌堆隨機抽了幾張，牌都不會重複
    for i in range(variable.myData.NUM_PLAYER_CARD):
        x = random.randint(0, len(variable.myData.card["myCards"]) - 1)
        while variable.myData.take[x] == 1:
            x = random.randint(0, len(variable.myData.card["myCards"]) - 1)
        msg.append(list[x])
        variable.myData.take[x] = 1  # css is awesome
    return msg


async def give_one_card():
    x = random.randint(0, len(variable.myData.card["myCards"]) - 1)
    while variable.myData.take[x] == 1:
        x = random.randint(0, len(variable.myData.card["myCards"]) - 1)
    variable.myData.take[x] = 1  # css is awesome
    return x


async def remove_and_give(name):
    newCard = await give_one_card()
    if name in variable.myData.saveAnswerInfo:
        pos = variable.myData.saveAnswerInfo[name]
        variable.myData.player[name][pos] = variable.myData.card["myCards"][newCard]

##################################################################################################################################

async def display_topic(mem):
    variable.myData.numAnswered = 0  # 已選擇答案的人數
    num = random.randint(0, len(variable.myData.card["topic"]) - 1)
    while variable.myData.take_topic[num] == 1:
        num = random.randint(0, len(variable.myData.card["topic"]) - 1)
    
    variable.myData.take_topic[num] = 1
    variable.myData.topic = variable.myData.card["topic"][num]
    totalMessage = '>>> Round ' + str(variable.myData.topicPlayer + 1) + '\n' + '\n 由 ' + str(
        variable.myData.playerName[variable.myData.topicPlayer]) + ' 擔任裁判\n 題目是： ' + str(variable.myData.card["topic"][num])
    
    replyAct = await mem.send(totalMessage)
    for i in range(variable.myData.NUM_PLAYER_CARD):
        await replyAct.add_reaction(variable.myData.reaction["reaction_number"][i])# 給玩家的選項
    variable.myData.lastMessage = replyAct

    variable.myData.gameStatus = 3


async def choose_answer(payload, mem):  # 答題者選擇答案編號
    # 出題者在這個階段按按鈕無效
    if payload.member.name == variable.myData.playerName[variable.myData.topicPlayer]:
        return

    for i in variable.myData.reaction["reaction_check"]:  # 不是這個階段的選項
        if payload.emoji.name == i:
            return

    if payload.member.name in variable.myData.playerName:  # 有參加遊戲的人才會考慮
        if payload.member.name not in variable.myData.saveAnswerInfo:  # 還沒回答過的人
            variable.myData.numAnswered += 1
            x = 0
            for i in variable.myData.reaction["reaction_number"]:
                if i == payload.emoji.name:
                    break
                x += 1

            if x != variable.myData.playNum:  # 有找到的情況
                variable.myData.saveAnswerInfo[payload.member.name] = x
            if variable.myData.numAnswered >= (variable.myData.playNum - 1):
                await variable.myData.lastMessage.clear_reactions()
                variable.myData.gameStatus = 4


async def display_pair_info(payload, mem):  # 所有回答者的東西，輸出成句子
    n = 1
    totalMessage = '>>> ```ansi\n 選項：\n'
    for name in variable.myData.saveAnswerInfo.keys():
        sentance = variable.myData.topic
        # 第?個player的第??張牌
        pos = variable.myData.saveAnswerInfo[name]
        word = variable.myData.player[name][pos]
        sentance = sentance.replace(
            "___", '\u001b[1;34m' + str(word) + '\u001b[0m')

        totalMessage += str(n) + '. ' + str(sentance) + '\n'
        n = n + 1

    totalMessage += '\n最不喜歡哪個答案？```'
    replyAct = await mem.send(totalMessage)
    for i in range(1, variable.myData.playNum):
        await replyAct.add_reaction(variable.myData.reaction["reaction_number"][i])
    variable.myData.lastMessage = replyAct
    variable.myData.gameStatus = 5


async def round_result(payload, mem):  # "player ? lose."
    n = 1
    if (payload.member.name == variable.myData.playerName[variable.myData.topicPlayer]) and (not variable.myData.lock):
        await variable.myData.lastMessage.clear_reactions()
        variable.myData.lock = True
        for name in variable.myData.saveAnswerInfo.keys():
            if payload.emoji.name == variable.myData.reaction["reaction_number"][n]:
                variable.myData.scoreBoard[name] += 1
                await mem.send('>>> ' + name + ' 扣1分.\n')

            n += 1
        variable.myData.topicPlayer += 1

        if variable.myData.topicPlayer == variable.myData.playNum:
            variable.myData.gameStatus = 6
        else:
            await reset_data()       # 更新現在的手牌並私訊給玩家
            await display_topic(mem) # 顯示下個題目
        variable.myData.lock = False


async def reset_data(): # 更新現在的手牌並私訊給玩家
    for name in variable.myData.playerName:
        await remove_and_give(name)
        await variable.myData.saveGuildInfo[name].send('>>> round ' + str(variable.myData.topicPlayer + 1) + ': ' + str(variable.myData.player[name]) + ' is your card')
    variable.myData.saveAnswerInfo.clear()


async def finalResult(payload, mem):
    loser = []
    losePoint = 0
    totalMessage = '>>> '
    for name in variable.myData.playerName:
        if losePoint <= variable.myData.scoreBoard[name]:
            if losePoint < variable.myData.scoreBoard[name]:
                loser.clear()
            losePoint = variable.myData.scoreBoard[name]
            loser.append(name)

        totalMessage += name + ' 扣了 ' + \
            str(variable.myData.scoreBoard[name]) + '分\n'

    await mem.send(totalMessage)

    totalMessage = ''
    for name in loser:
        totalMessage += (name + ' ')
    replyAct = await mem.send(totalMessage + '是輸家\n↓離開遊戲並刪除頻道')
    await replyAct.add_reaction(variable.myData.reaction["reaction_check"][2])


async def clear_all(): 
    for i in range(len(variable.myData.card["myCards"])):
        variable.myData.take[i] = 0

    for i in variable.myData.card["topic"]:
        variable.myData.take_topic.append(0)

    variable.myData.player.clear()
    variable.myData.playerName.clear()
    variable.myData.saveGuildInfo.clear()
    variable.myData.saveAnswerInfo.clear()

    variable.myData.numAnswered = 0
    variable.myData.topicPlayer = 0
    variable.myData.gameStatus = 0
    variable.myData.playNum = 0
    variable.myData.lastMessage = ''
