# -*- coding: utf-8 -*-
import time, cv2
import json, os
import numpy as np
import random
from dm.MainCommucation import MainCommucation
from presetAction.Buyequip.Buyequip import Main as equip_action

THRESHOLD = 0.5


class operater(MainCommucation):
	def __init__(self, op_id=1, img_path='', test=False):
		self.id = op_id
		self.test = test
		self.img_path = r"dm/screen1/0.bmp"
		if img_path is not '':
			self.img_path = img_path
		self.commandCahe = {
			'time': 0,
			'commandList': []
		}



		if not test:
			super(operater, self).__init__()
			self.start()

		self.equip_action = equip_action(self)

	def get_game_img(self):
		ret = self.Capture(0, 0, 2000, 2000, self.img_path)
		if ret == 0:
			print('capture fail')
			return None
		img = cv2.imread(self.img_path)
		return img

	def randomChooseTargetAction(self: any, action: dict):
		"""
		根据softmax得出的值，随机选择一个动作
		:param action:动作字典，key为动作名 value为动作未指数前概率
		:return:动作名称
		"""
		keys = np.array(list(action.keys()))
		values = np.array(list(action.values()))
		values = np.e ** values

		randomTarget = random.random() * np.sum(values)

		s = 0
		targetActionIndex = 0
		for i in range(len(values)):
			s += values[i]
			if randomTarget < s:
				targetActionIndex = i
				break
		targetAction = keys[targetActionIndex]
		return targetAction

	def init_action(self):
		self.equip_action.INIT()
		self.equip_action.Buy('多兰之刃')

	def goHome(self):
		"""
		返回泉水
		:return:无
		"""
		self.MoveToPostion([1105, 707], False)
		time.sleep(5)
		self.keyboardCommand('B')
		time.sleep(9)

	def moveto_center_of_soldier(self, params):
		mat = params['mat'][0]
		all_pos = np.where(mat > THRESHOLD)
		all_pos = np.array(all_pos)
		print(all_pos.shape)
		print(all_pos)
		exit()

	def attack_nearest_enemy_soldier(self, params):
		pass


	def actionExcute(self: any, action: dict, params: dict):
		"""
		根据字典随机选择动作并执行动作
		:param action:动作字典
		:param params:参数字典
		:return:
		"""

		# 回家并买装备
		if action == 0:
			self.goHome()
			# self.equip_action.auto_buy_equip(params['MONEY'])
			self.equip_action.Buy('多兰之刃')

		# 前进
		elif action == 1:
			targetPostion = params.get('go', None)
			if targetPostion is not None:
				self.MoveToPostion(targetPostion, False)

		# 后退
		elif action == 2:

			targetPostion = params.get('back', None)
			if targetPostion is not None:
				self.MoveToPostion(targetPostion, False)

		# 原地A
		elif action == 3:
			targetPostion = [590, 358]
			self.MoveToPostion(targetPostion, True)

		# 走到己方小兵的中心位置
		elif action == 4:
			self.moveto_center_of_soldier(params)

		# 攻击最近的敌方小兵
		elif action == 5:
			self.attack_nearest_enemy_soldier(params)

		else:
			print('未实现动作 待实现：[{}]'.format(action))
			raise

	def MoveToPostion(self, postionOnMap, attack=True):
		'''
		攻击移动前往坐标
		:param postionOnMap:
		:return:
		'''
		if attack:
			key = 'A'
			self.keyboardCommand(key, Down=True)
			self.mouseCommand(postionOnMap[0], postionOnMap[1], liftClick=True)
			self.keyboardCommand(key, Up=True)
		else:
			self.mouseCommand(postionOnMap[0], postionOnMap[1], rightClick=True)

	def keyboardCommand(self, keyChar, delay=100, Down=False, Up=False):
		mathodName = 'KeyPressChar'

		if Down:
			mathodName = 'KeyDownChar'
		if Up:
			mathodName = 'KeyUpChar'

		# print('keyboardCommand mathod:{} key:{} delay={}'.format(mathodName,keyChar,delay))
		command = {
			'name': mathodName,
			'key': keyChar,
			'delay': delay
		}
		self.excuteCommand(command)

	def mouseCommand(self, x=-1, y=-1, liftClick=False, rightClick=False, delay=100):
		'''
		:param x: -1==NoMove
		:param y: -1==NoMove
		:param liftClick:
		:param rightClick:
		:param delay:
		:return:
		'''
		# print('mouseCommand x:{} y:{} liftClick:{} rightClick:{} delay={}'.format(x,y,liftClick,rightClick,delay))
		if x != -1 and y != -1:
			mathodName = 'MoveTo'
			command = {
				'name': mathodName,
				'x': int(x),
				'y': int(y),
				'delay': delay
			}
			self.excuteCommand(command)

		mathodName = ''
		if liftClick:
			mathodName = 'LeftClick'
		if rightClick:
			mathodName = 'RightClick'
		if mathodName == '':
			return
		command = {
			'name': mathodName,
			'delay': delay
		}
		self.excuteCommand(command)

	def excuteCommand(self, commandDict):
		# print(commandDict)
		if self.test:
			return
		# 执行命令模块
		key = commandDict.get('key', '')
		x = commandDict.get('x', '')
		y = commandDict.get('y', '')
		delay = commandDict.get('delay', 100)
		name = commandDict.get('name', '')
		if name == '':
			return
		mathod = 'self.{}'.format(name)
		args = ''
		for arg in [key, x, y]:
			if arg != '':
				if args == '':
					args += '('
				else:
					args += ','
				args += '\'' + str(arg) + '\''
		if args == '':
			args = '()'
		else:
			args += ')'
		command = mathod + args
		try:
			print('excute command:{}'.format(command))
			eval(command)
		# time.sleep(delay / 1000)
		except Exception as e:
			print(e)
		finally:
			pass


if __name__ == "__main__":
	p = operater(1)
	p.keyboardCommand('a', Down=True)
	p.mouseCommand(619, 425, liftClick=True)
	p.keyboardCommand('a', Up=True)
	p.sendCommand()
