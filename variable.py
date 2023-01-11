class myData:
    card = {}           # 題目跟手牌
    take = []           # 哪些牌已經發給玩家了
    take_topic = []     # 哪些題目用過
    topic = ''          # 目前題目
    player = {}         # "author" : ["cards"]
    playerName = []     # 紀錄玩家名稱
    playNum = 0         # 玩家數量
    reaction = {}       # 紀錄反應的種類
    gameStatus: int = 0  # 遊戲狀態
    numAnswered = 0     #
    topicPlayer = 0     #
    saveGuildInfo = {}
    saveAnswerInfo = {}
    lastMessage = ''
    scoreBoard = {}

    lock = False
    firstPlayer = ''
    intro = {}

    NUM_PLAYER_CARD = 3
