import discord
from botMessage import start_message, game_start, choose_answer, display_pair_info, round_result, display_topic, clear_all, finalResult
import json
import variable
import boto3

# 主要執行的函式

TOKEN = 'YOUR_TOKEN'
intent = discord.Intents.all()
client = discord.Client(intents=intent)


@client.event
async def on_ready():  # 機器人開機
    try:
        s3 = boto3.client('s3')
        s3.download_file('yellowcarddata', 'card.json',
                         '/home/ubuntu/card.json')
    except Exception as e:
        print(e)
        return
    print(f'{client.user} is running!')
    variable.myData.topicPlayer = 0
    with open("card.json") as f:
        variable.myData.card = json.load(f)

    for i in variable.myData.card["myCards"]:
        variable.myData.take.append(0)

    for i in variable.myData.card["topic"]:
        variable.myData.take_topic.append(0)

    with open("reaction.json", encoding="utf-8") as f:
        variable.myData.reaction = json.load(f)


@client.event
async def on_message(message):  # 當傳送訊息
    if message.author == client.user:
        return

    username = str(message.author)
    user_message = str(message.content)
    channel = str(message.channel)

    msg = user_message.split(' ')

    if variable.myData.gameStatus == 0:
        if user_message == '?game':
            variable.myData.firstPlayer = message.author.name
            guild = message.author.guild
            _channel = await guild.create_text_channel('遊戲頻道')
            await _channel.set_permissions(guild.default_role, send_messages=False)
            await start_message(_channel)  # 傳送遊戲邀請

        elif (msg[0] == '?new') and (len(msg) == 2) and (msg[1] not in variable.myData.card["myCards"]):
            with open("card.json", 'r') as f:
                variable.myData.card = json.load(f)
                variable.myData.card["myCards"].append(msg[1])
            with open('card.json', 'w') as f:
                json.dump(variable.myData.card, f)
            await message.channel.send('>>> ' + msg[1] + '已成功加入牌庫')
            variable.myData.take.append(0)

        elif user_message == '?savedata':
            s3 = boto3.client('s3')
            s3.upload_file('檔案路徑',
                           'yellowcarddata', 'card.json')
            await message.channel.send('>>> 牌庫資料已永久保存到雲端')

        elif user_message == '?help':
            with open("welcome.json", encoding="utf-8") as f:
                variable.myData.intro = json.load(f)
            await message.channel.send(variable.myData.intro["welcome"])

        elif (msg[0] == '?setting') and (len(msg) == 2) and (msg[1].isdigit() and int(msg[1]) <= 8 and int(msg[1]) >= 3):
            variable.myData.NUM_PLAYER_CARD = int(msg[1])
            await message.channel.send('>>> 手牌數量設定為：' + msg[1] + '張')


@client.event
async def on_raw_reaction_add(payload):  # 按下反應時
    # 不要的情況
    if payload.member.bot:
        return
    if (payload.emoji.name not in variable.myData.reaction["reaction_check"] and payload.emoji.name not in variable.myData.reaction["reaction_number"]):
        return

    if payload.emoji.name == variable.myData.reaction["reaction_check"][2]:
        if variable.myData.firstPlayer == payload.member.name:
            existing_channel = discord.utils.get(
                payload.member.guild.channels, name='遊戲頻道')
            if existing_channel is not None:
                await existing_channel.delete()
                await clear_all()

    if variable.myData.gameStatus == 0:
        return

    channel = payload.channel_id  # recupere le numero du canal
    mem = client.get_guild(payload.guild_id).get_channel(channel)

    if variable.myData.gameStatus == 1:
        await game_start(payload, mem)         # "🟨", "✔️"的偵測
    
    ############################################ >> 以下指令將重複執行 #
    if variable.myData.gameStatus == 2:
        await display_topic(mem)               # 顯示題目
    if variable.myData.gameStatus == 3:
        await choose_answer(payload, mem)      # 玩家各自選擇要出哪張
    if variable.myData.gameStatus == 4:  
        await display_pair_info(payload, mem)  # 玩家回答的東西和題目組合
    elif variable.myData.gameStatus == 5:
        await round_result(payload, mem)       # 裁判選擇一個人扣分
    ###################################################################
    
    if variable.myData.gameStatus == 6:
        await finalResult(payload, mem)        # 結束遊戲，誰輸了
        await clear_all()                      # 重設資料

client.run(TOKEN)
