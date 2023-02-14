# coding:utf-8
#导入库,初始化pygame环境3步
import pygame, sys, random, time, easygui
from pygame.locals import *
pygame.init()
# 创建一个长宽分别为480/650窗口
canvas = pygame.display.set_mode((480,650))
canvas.fill((255,255,255))#窗口填充为白色
pygame.display.set_caption("飞机大战")# 设置窗口标题
#加载图片
bg = pygame.image.load("images/bg1.png")#背景图片
enemy1 = pygame.image.load("images/enemy1.png")#小飞机
enemy2 = pygame.image.load("images/enemy2.png")#中飞机
enemy3 = pygame.image.load("images/enemy3.png")#大飞机
b = pygame.image.load("images/bullet1.png")#子弹图片
h = pygame.image.load("images/hero.png")#英雄机图片
startgame=pygame.image.load("images/startGame.png")#开始游戏图片
logo=pygame.image.load("images/LOGO.png")#logo图片
pause = pygame.image.load("images/game_pause_nor.png")#暂停图片
# 定义Sky类,为了创建背景图
class Sky():
    def __init__(self):
        self.width = 480
        self.height = 852
        self.img = bg
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = -self.height
    # 创建paint方法
    def paint(self):
        canvas.blit(self.img, (self.x1, self.y1))
        canvas.blit(self.img, (self.x2, self.y2))
    # 创建step方法
    def step(self):
        self.y1 = self.y1 + 1
        self.y2 = self.y2 + 1
        #实现飞机的持续移动
        if self.y1 > self.height:
            self.y1 = -self.height
        if self.y2 > self.height:
            self.y2 = -self.height     
# 定义父类FlyingObject
class FlyingObject(object):
    def __init__(self, x, y, width, height, life, img):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.life = life
        self.img = img
        # 控制敌飞机移动的时间间隔
        self.lastTime = 0
        self.interval = 0.01
        # 添加删除属性
        self.canDelete = False
    # 定义paint方法
    def paint(self):
        canvas.blit(self.img, (self.x, self.y))
    # 定义step方法
    def step(self):
        # 判断是否到了移动的时间间隔
        if not isActionTime(self.lastTime, self.interval):
            return
        self.lastTime = time.time()
        # 控制移动速度
        self.y = self.y + 2
    # 定义hit方法判断两个对象之间是否发生碰撞
    def hit(self, c):
        #发生碰撞时x,y的范围
        return c.x > self.x - c.width and c.x < self.x + self.width and \
               c.y > self.y - c.height and c.y < self.y + self.height
    # 定义bang方法处理对象之间碰撞后的处理
    def bang(self, bangsign):
        # 敌机和英雄机碰撞之后的处理
        if bangsign:
            self.canDelete = True  # 设置删除属性为True
            if hasattr(self,'score'):  #判断对象是否有'score'属性
                GameVar.score += self.score
            if bangsign == 2:  #bangsign == 2,处理英雄机要做的事情
                self.life -= 1           
        # 敌机和子弹碰撞之后的处理
        else:
            self.life -= 1
            if self.life == 0:
                self.canDelete = True # 设置删除属性为True
                if hasattr(self,'score'):
                    GameVar.score += self.score 
    # 定义outOfBounds方法判断敌机对象是否越界
    def outOfBounds(self):
        return self.y > 650    
# 重构Enemy类
class Enemy(FlyingObject):
    def __init__(self, x, y, width, height, type, life, score, img):
        #继承父类6个属性
        FlyingObject.__init__(self, x, y, width, height, life, img)
        self.type = type
        self.score = score    
# 重构Hero类 牧童
class Hero(FlyingObject):
    def __init__(self, x, y, width, height, life, img):
        FlyingObject.__init__(self, x, y, width, height, life, img)
        #英雄机的初始位置位于屏幕正中间
        self.x = 480 / 2 - self.width / 2
        self.y = 650 - self.height - 30
        #发射子弹的时间间隔
        self.shootLastTime = 0
        self.shootInterval = 0.3
    #定义发射子弹的方法
    def shoot(self):
        if not isActionTime(self.shootLastTime, self.shootInterval):
            return
        self.shootLastTime = time.time()
        #添加子弹对象
        GameVar.bullets.append(Bullet(self.x + self.width / 2 - 5, self.y - 10, 10, 10, 1, b))
# 重构Bullet类 
class Bullet(FlyingObject):
    def __init__(self, x, y, width, height, life, img):
        FlyingObject.__init__(self, x, y, width, height, life, img)
    def step(self):
        self.y = self.y - 2
    # 重写outOfBounds方法判断子弹是否越界
    def outOfBounds(self):
        return self.y < -self.height
# 创建componentEnter方法
def componentEnter():
    # 随机生成坐标
    x = random.randint(0,480 - 57)
    x1 = random.randint(0,480 - 50)
    x2 = random.randint(0,480 - 100)
    #产生随机整数0~9
    n = random.randint(0, 9)
    # 判断是否到了产生敌飞机的时间
    if not isActionTime(GameVar.lastTime, GameVar.interval):
        return
    GameVar.lastTime = time.time()
    #根据随机数n的值控制3种敌机的数量
    if n <= 7:
        GameVar.enemies.append(Enemy(x, 0, 57, 45, 1, 1, 1, enemy1))
    elif n == 8:
        GameVar.enemies.append(Enemy(x1, 0, 50, 68, 2, 3, 5, enemy2))
    elif n == 9: 
        if len(GameVar.enemies) == 0 or GameVar.enemies[0].type != 3: 
            GameVar.enemies.insert(0, Enemy(x2, 0, 100, 153, 3, 10, 20, enemy3)) 
# 创建画组件方法
def componentPaint():
    # 判断是否到了飞行物重绘的时间
    if not isActionTime(GameVar.paintLastTime,GameVar.paintInterval):
        return
    GameVar.paintLastTime = time.time()
    # 调用sky对象的paint方法
    GameVar.sky.paint()
    for enemy in GameVar.enemies:
        enemy.paint()
    # 画出英雄机
    GameVar.hero.paint()
    # 画出子弹对象
    for bullet in GameVar.bullets:
        bullet.paint()
    # 写出分数和生命值
    fillText('SCORE:' + str(GameVar.score), (0, 0))
    fillText('LIFE:' + str(GameVar.heroes), (380, 0))
# 创建组件移动的方法 
def componentStep():
    # 调用sky对象的step方法
    GameVar.sky.step()
    for enemy in GameVar.enemies:
        enemy.step()
    # 使子弹移动
    for bullet in GameVar.bullets:
        bullet.step()   
#创建定时器(最近一次的时间,时间间隔)
def isActionTime(lastTime, interval):
    if lastTime == 0:
        return True
    currentTime = time.time()#time.time()获取当前时间
    return currentTime - lastTime >= interval
# 创建checkHit方法,碰撞检测 
def checkHit():
    # 判断英雄机是否与每一架敌飞机发生碰撞
    for enemy in GameVar.enemies:
        if GameVar.hero.hit(enemy):
            # 敌机和英雄机调用bang方法
            enemy.bang(1)
            GameVar.hero.bang(2)
        # 判断每一架敌飞机是否与每一颗子弹发生碰撞
        for bullet in GameVar.bullets:
            if enemy.hit(bullet):
                # 敌机和子弹调用bang方法
                enemy.bang(0)
                bullet.bang(0)
# 创建鼠标移入画布的方法
def isMouseOver(x, y):
    if x > 1 and x < 479 and y > 1 and y < 649:
        return True
    else:
        return False
# 创建鼠标移出画布的方法
def isMouseOut(x, y):
    if x >= 479 or x <= 0 or y >= 649 or y <= 0:
        return True
    else:
        return False
# 创建删除组件的方法 
def componentDelete():
    for enemy in GameVar.enemies:
        if enemy.canDelete or enemy.outOfBounds(): #如果敌机可以删除或移出屏幕
            GameVar.enemies.remove(enemy) #从列表中删除元素
    for bullet in GameVar.bullets:
        if bullet.canDelete or bullet.outOfBounds():
            GameVar.bullets.remove(bullet)
    # 如果英雄机的canDelete属性为True
    if GameVar.hero.canDelete == True:
        GameVar.heroes -= 1 #英雄机的数量减1
        if GameVar.heroes == 0: #当英雄机的数量为0时，游戏结束
            GameVar.state = 4
        #否则,重新添加英雄机对象
        else:
            GameVar.hero = Hero(0,0,60,75,1,h)
#创建游戏事件处理方法 
def handleEvent(): 
    for event in pygame.event.get(): #获取事件对象
        #如果是鼠标按下事件同时按的是左键
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            #如果当前状态是开始状态，就转化为运行状态
            if GameVar.state == 1:
                GameVar.state = 2
        #如果是QUIT退出事件或键盘按下ESC
        if event.type == pygame.QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
            #关闭窗口
            pygame.quit()
            #退出程序
            sys.exit()  
        #如果是鼠标移动事件       
        if event.type == MOUSEMOTION:
            if GameVar.state == 2: #如果游戏状态为RUNNING运行状态
                #英雄机跟随鼠标移动
                GameVar.hero.x = event.pos[0] - GameVar.hero.width / 2
                GameVar.hero.y = event.pos[1] - GameVar.hero.height / 2 
            #鼠标移出画布,如果是运行状态转化为暂停状态
            if isMouseOut(event.pos[0],event.pos[1]):
                if GameVar.state == 2:
                    GameVar.state = 3
            #鼠标移入画布,如果是暂停状态就转化为运行状态
            if isMouseOver(event.pos[0],event.pos[1]):
                if GameVar.state == 3:
                    GameVar.state = 2
            
                   
# 定义fillText方法,写文字的方法
def fillText(text, position):
    my_font = pygame.font.SysFont("微软雅黑", 40) #设置字体样式和大小
    newText = my_font.render(text, True, (255, 255, 255)) #渲染要写的文字内容,字体白色
    canvas.blit(newText, position)  #画出文字         
#创建controlState方法控制游戏4种状态下要做的事情
def controlState():
    #游戏开始状态
    if GameVar.state == GameVar.STATES['START']:
        #背景持续移动
        GameVar.sky.paint()
        GameVar.sky.step()
        #画出logo、游戏开始图片
        canvas.blit(logo,(-40,200))
        canvas.blit(startgame,(150,400))
    #游戏运行状态
    elif GameVar.state == GameVar.STATES['RUNNING']:       
        componentEnter()  #创建敌机对象     
        componentPaint() #画出所有对象      
        componentStep() #对象移动       
        checkHit() #碰撞检测
        GameVar.hero.shoot() #英雄机发射子弹
        componentDelete() #删除对象
    #游戏暂停状态
    elif GameVar.state == GameVar.STATES['PAUSE']:
        componentPaint()  #画出所有对象
        GameVar.sky.step() #背景移动
        canvas.blit(pause,(0,0)) #画出暂停图片
    #游戏结束状态
    elif GameVar.state == GameVar.STATES['GAME_OVER']:
        componentPaint() #画出所有对象
        GameVar.sky.step() #背景移动
        fillText('gameOver',(180,320)) #写文字'gameOver'
# 定义GameVar类,保存变量,便于维护,类的属性
class GameVar():
    sky = Sky()
    enemies = []
    # 产生敌飞机的时间间隔
    lastTime = 0
    interval = 1.5
    # 重绘飞行物的时间间隔
    paintLastTime = 0
    paintInterval = 0.04
    # 创建英雄机对象
    hero = Hero(0, 0, 60, 75, 1, h)
    # 创建列表存储子弹对象
    bullets = []
    # 添加分数和生命值
    score = 0
    heroes = 3
    #创建字典存储游戏状态
    STATES = {'START':1,'RUNNING':2,'PAUSE':3,'GAME_OVER':4}
    state = STATES['START']
while True:
    #调用控制游戏状态的方法
    controlState()
    # 刷新屏幕
    pygame.display.update()
    # 调用handleEvent方法
    handleEvent()
    # 延迟处理
    pygame.time.delay(15)
    
    
  
    
    
    
