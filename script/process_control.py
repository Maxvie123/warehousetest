#!/usr/bin/env python


##############################################################################
# This file will take the initial Fetch and Freight pose list as input.
# The purpose of this file is to correctly publish current pose infomation to 
# the correspoding robot and publish robot states.
# Author: Jingwei Liu
# Date: 01/06/2020
############################################################################


import rospy
import geometry_msgs.msg
import actionlib_msgs.msg
import std_msgs.msg
from warehousetest.srv import GetGoal, GetGoalResponse
from warehousetest.srv import GetGripperGoal, GetGripperGoalResponse


picker_state = []
transporter_state = []


# return action status
def return_status(data):

	global status

	if data.status_list == []:
		status = ""
		return status
	else:
		status_size = len(data.status_list)
		status = data.status_list[status_size-1].status
		return status

def return_gripper_status(data):

	global g_status

	if data.status.list == []:
		g_status = 0
		return g_status
	else:
		status_size = len(data.status_list)
		g_status = data.status_list[status_size-1].status
		return g_status



def handle_get_gripper_goal(req):

	return GetGripperGoalResponse([req.x, req.y, req.z])



class freight_process():

	global picker_num
	global picker_state
	picker_num = 2
	picker_state = [0,0]
	picker_index = [1,2]

	def __init__(self,robotname):

		rospy.init_node(robotname+'_process_control')
		rospy.Service(robotname+'/get_goal', GetGoal, self.handle_get_goal)
		rospy.Subscriber(robotname+'/move_base/status', actionlib_msgs.msg.GoalStatusArray, return_status, queue_size = 1)
		self.state_pub = rospy.Publisher(robotname+'/state', std_msgs.msg.Float32, queue_size = 1)
		self.counter_pub = rospy.Publisher(robotname+'/counter', std_msgs.msg.Int16, queue_size = 1)
		# for picker_id in (range(picker_num)):
		# 	rospy.Subscriber('fetch'+str(picker_id+1)+'/state', std_msgs.msg.Float32, self.get_picker_state, freight_process.picker_index[picker_id])
		rospy.Subscriber('fetch1'+'/state', std_msgs.msg.Float32, self.get_picker_state, 1)
		
		# misc varibles 
		self.robotname = robotname
		self.state = 0
		self.start = 0
		self.battery = 100
		self.listsize = len(robot_list)
		self.counter = 0
		self.rate = rospy.Rate(10)


	def handle_get_goal(self, req):
		p = req.goal_index
		if p == self.counter:
			print "Get request for goal No.{}.".format(p)
			return GetGoalResponse([robot1_x_list[p], robot1_y_list[p], 0])



	def get_picker_state(self,msg, picker_id):

		picker_state[picker_id-1] = msg.data
		return	


	def state_control(self):

 		global status

 		# status = ""

 		counter = self.counter


 		while (self.start == 1):
			if status == "":
				self.state = 0

			if (self.state == 0 and status == 1):
				self.state = 1
				rospy.loginfo(self.robotname+" is moving to goal position")
			elif (self.state == 1 and status == 3):
				self.state = 2
				rospy.loginfo(self.robotname+" reached the goal position")

			if (self.state == 2 and robot_list[counter] == 0):
				self.state = 0
				rospy.loginfo(self.robotname+" is idle (ready for new task)")
				counter = counter + 1
				rospy.sleep(2)
			elif (self.state == 2 and robot_list[counter] != 0):
				self.state = 3
				picker_id = robot_list[counter]
				rospy.loginfo(self.robotname+" is waiting for the items")

			if (self.state == 3 and picker_state[picker_id-1]== 4.4):
				self.state = 4
				rospy.loginfo(self.robotname+" got the items from picker")

			if (self.state == 4):
				rospy.sleep(2)
				self.state = 0
				rospy.loginfo(self.robotname+" is idle (ready for new task)")

			self.counter = counter
			self.state_pub.publish(self.state)
			self.counter_pub.publish(self.counter)
			self.rate.sleep()




class fetch_process():

	global transporter_num
	global transporter_state
	transporter_num = 3
	transporter_state = []

	# initialize the node and create two services for 2d navigation goal and gripper goal. create a subscriber for 
	def __init__(self,robotname):

		rospy.init_node(robotname+'_process_control')
		rospy.Service(robotname+'/get_goal', GetGoal, self.handle_get_goal)
		rospy.Service(robotname+'/get_gripper_goal', GetGripperGoal, handle_get_gripper_goal)
		rospy.Subscriber(robotname+'/move_base/status', actionlib_msgs.msg.GoalStatusArray, return_status, queue_size = 1)
		rospy.Subscriber(robotname+'/move_group/status', actionlib_msgs.msg.GoalStatusArray, return_gripper_status, queue_size = 1)
		self.state_pub = rospy.Publisher(robotname+'/state', std_msgs.msg.Float32, queue_size = 1)
		self.counter_pub = rospy.Publisher(robotname+'/counter', std_msgs.msg.Int16, queue_size = 1)
		for transporter_id in (range(transporter_num)):
			rospy.Subscriber('freight'+str(transporter_id+1)+'/state', std_msgs.msg.Float32, self.get_transporter_state, transporter_id)

		# misc varibles 
		self.robotname = robotname
		self.state = 0
		self.start = 0
		self.battery = 100
		self.listsize = len(robot_list)
		self.counter = 0
		self.rate = rospy.Rate(10)	


	def handle_get_goal(self, req):
		p = req.goal_index
		if p == self.counter:
			print "Get request for goal No.{}.".format(p)
			return GetGoalResponse([robot1_x_list[p], robot1_y_list[p], 0])


	def get_transporter_state(self, msg, transporter_id):

		transporter_state[transporter_id+1] = msg.data
		return


	def state_control(self):

 		global status
 		global g_status

 		# status = ""

 		counter = self.counter


 		while (self.start == 1):
			if status == "":
				self.state = 0

			if (self.state == 0 and status == 1):
				self.state = 1
				print "state1"
				rospy.loginfo(self.robotname+" is moving to goal position")
			elif (self.state == 1 and status == 3):
				self.state = 2
				print "state2"
				rospy.loginfo(self.robotname+" reached the goal position")

			if (self.state == 2 and robot_list[counter] == 0):
				self.state = 0
				rospy.loginfo(self.robotname+" is idle (ready for new task)")
				counter = counter + 1
				rospy.sleep(2)
			elif (self.state == 2 and robot_list[counter] != 0):
				transporter_id = robot_list[counter]
				self.state = 3

			if (self.state == 3 and g_status == 1):
				self.state = 3.1
				rospy.loginfo(self.robotname+" is picking the items")
			elif (self.state == 3.1 and g_status == 3):
				self.state = 3.2
				rospy.loginfo(self.robotname+" got the item")
			elif (self.state == 3.2 and g_status == 1):
				self.state = 3.3
				rospy.loginfo(self.robotname+" back to default arm position")
			elif (self.state == 3.2 and g_status == 3 and transporter_state[transporter_id-1] == 3):
				self.state = 4
				rospy.loginfo(self.robotname+" is ready to place item to transporter")


			if (self.state == 4 and status == 1):
				self.state = 4.1
				rospy.loginfo(self.robotname+" is moving to transporter")
			elif (self.state == 4.1 and status == 3):
				self.state = 4.2
				rospy.loginfo(self.robotname+" reach cooperation position")
			elif (self.state == 4.2 and g_status == 1):
				self.state = 4.3
				rospy.loginfo(self.robotname+" is placing the item")
			elif (self.state == 4.3 and g_status == 3):
				self.state = 4.4
				rospy.loginfo(self.robotname+" has placed the item")
			elif (self.state == 4.4 and g_status == 1):
				self.state = 4.5
				rospy.loginfo(self.robotname+" back to default arm position")
			elif (self.state == 4.5 and g_status == 3):
				self.state = 0
				rospy.loginfo(self.robotname+" is idle (ready for new task)")
				rospy.sleep(2)

			self.counter = counter
			self.state_pub.publish(self.state)
			self.counter_pub.publish(self.counter)
			self.rate.sleep()



if __name__ == "__main__":


	robot1_x_list = [-4,-4]
	robot1_y_list = [-7,5]
	robot_list =[1,1]



	robot1 = freight_process("freight2")

	rospy.sleep(2)

	robot1.start = 1
	
	robot1.state_control()