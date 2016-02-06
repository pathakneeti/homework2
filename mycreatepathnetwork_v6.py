'''
 * Copyright (c) 2014, 2015 Entertainment Intelligence Lab, Georgia Institute of Technology.
 * Originally developed by Mark Riedl.
 * Last edited by Mark Riedl 05/2015
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
'''

import sys, pygame, math, numpy, random, time, copy, operator
from pygame.locals import *

from constants import *
from utils import *
from core import *

# Creates a pathnode network that connects the midpoints of each navmesh together
def myCreatePathNetwork(world, agent = None):
	nodes = []
	edges = []
	polys = []
	### YOUR CODE GOES BELOW HERE ###
	obstructionLines = world.getLines()
	anchorpoints = world.getPoints()
	firstPoints = world.getPoints()
	firstPoints.remove((0, 0))
	firstPoints.remove((world.getDimensions()[0], 0))
	firstPoints.remove((world.getDimensions()[0], world.getDimensions()[1]))
	firstPoints.remove((0, world.getDimensions()[1]))
	ManualObstacleList = []

	# anchorpoints, check that allpoints in all obs not in the triangle
	for triPoint1 in firstPoints:
		for triPoint2 in anchorpoints:
			templine1 = (triPoint1,triPoint2)
			templine2 = (triPoint2, triPoint1)
			midpoint12 = ((triPoint1[0]+triPoint2[0])/2, (triPoint1[1]+triPoint2[1])/2)
			hit12 = rayTraceWorldNoEndPoints(triPoint1,triPoint2,obstructionLines)
			inside12 = False
			for obstacle in world.getObstacles():
				if obstacle.pointInside(midpoint12):
					inside12 = True
			for obstacle in ManualObstacleList:
				if obstacle.pointInside(midpoint12):
					inside12 = True

			if triPoint1 == triPoint2: # 1. cannot be equal as pt1
				continue
			elif ((obstructionLines.count(templine1) >0) or (obstructionLines.count(templine2) >0)): # 2. can be an obstacle line
				pass
			elif hit12 == None and inside12 == True: # 3. cannot by inside a polygon or triangle
				continue 
			else:
				continue
			# elif hit12 != None and inside12 == False: #4. can by a line outside polygon with no collision
			# 	pass
			# else:
			# 	continue

			for triPoint3 in anchorpoints:
				#check midpoint
				midpoint13 = ((triPoint1[0]+triPoint3[0])/2, (triPoint1[1]+triPoint3[1])/2)
				midpoint23 = ((triPoint3[0]+triPoint2[0])/2, (triPoint3[1]+triPoint2[1])/2)
				inside23 = False
				inside13 = False
				for obstacle in world.getObstacles():
					if obstacle.pointInside(midpoint13):
						inside13 = True
					if obstacle.pointInside(midpoint23):
						inside23 = True
				for obstacle in ManualObstacleList:
					if obstacle.pointInside(midpoint13):
						inside13 = True
					if obstacle.pointInside(midpoint23):
						inside23 = True
				templine23 = (triPoint2,triPoint3)
				templine32 = (triPoint3,triPoint2)
				templine13 = (triPoint1, triPoint3)
				templine31 = (triPoint3,triPoint1)

				hit13 = rayTraceWorldNoEndPoints(triPoint1,triPoint3,obstructionLines)
				hit23 = rayTraceWorldNoEndPoints(triPoint2,triPoint3,obstructionLines)

				if triPoint1 == triPoint3 or triPoint2 == triPoint3: # 1. cannot be another point 
					continue
				elif (hit13 != None and (obstructionLines.count(templine13)==0 and obstructionLines.count(templine31)==0)) or (hit23 != None and (obstructionLines.count(templine23)==0 and obstructionLines.count(templine32)==0)):
					continue # 7. either collides and not obsline
				elif (hit13== None and inside13 == True ) or (hit23 == None and inside23 == True ):
					continue #and (obstructionLines.count(templine13)==0 and obstructionLines.count(templine31)==0) and (obstructionLines.count(templine23)==0 and obstructionLines.count(templine32)==0)
				
				trianglePoly = (triPoint1,triPoint2,triPoint3)
				o = ManualObstacle(trianglePoly)
				
				# check if the triangle is inside the obstacle 
				triangleInObstacle = False
				for obstacle in world.getObstacles():
					if obstacle.pointInside(triPoint1) and obstacle.pointInside(triPoint2) and obstacle.pointInside(triPoint3):
						triangleInObstacle = True
						break
				if triangleInObstacle:
					continue

				# check if the obstacle is inside the triangle
				obstacleInTriangle = False
				for obstacle in world.getObstacles():
					obsInTri = True
					for point in obstacle.getPoints():
						obsInTri = obsInTri and o.pointInside(point)
					if obsInTri = True:
						obstacleInTriangle = True
						break
				if obstacleInTriangle:
					continue



				# elif (obstructionLines.count(templine23)>0 or obstructionLines.count(templine32)>0) and (inside13 == False and hit13 == None): # 2. 23 is obsline and 13 is outside line
				# 	pass
				# elif (obstructionLines.count(templine13)>0 or obstructionLines.count(templine31)>0) and (inside23 == False and hit23 == None): # 3. 13 is obsline and 23 is outside line 
				# 	pass
				# elif (obstructionLines.count(templine23)>0 or obstructionLines.count(templine32)>0) and (obstructionLines.count(templine13)>0 or obstructionLines.count(templine31)>0):
				# 	pass # 4. 13 and 23 are obsline 
				# elif (hit13==None and inside13 == False) and (hit23 == None and inside23 == False):
				# 	pass #5. either inside polys no collision


				edge1 = (triPoint1,triPoint2)
				appendLineNoDuplicates(edge1,edges)
				appendLineNoDuplicates(edge1,obstructionLines)
				edge2 = (triPoint2,triPoint3)
				appendLineNoDuplicates(edge2,edges)
				appendLineNoDuplicates(edge2,obstructionLines)
				edge3 = (triPoint3,triPoint1)
				appendLineNoDuplicates(edge3,edges)
				appendLineNoDuplicates(edge3,obstructionLines)
				
				(ManualObstacleList).append(o)

				#drawPolygon(o, surface, color, width, center):
				#drawPolygon(0, surface, (0, 255, 0), 5, False)

	### YOUR CODE GOES ABOVE HERE ###
	return nodes, edges, polys

				# if triPoint1 == triPoint2: 
				# 	accept2 = False
				# 	accept3 = False
				# 	break
				# 	#if same point, need new pt2
				# elif rayTraceWorldNoEndPoints(triPoint1,triPoint2, obstructionLines) != None:
				# 	#print rayTraceWorldNoEndPoints(triPoint1,triPoint2, obstructionLines)
				# 	if ((obstructionLines.count(templine1) >0) or (obstructionLines.count(templine2) >0)):
				# 		print "line 1-2 on obstacle? " + str(obstructionLines.count(templine1))
				# 		print "line 1-2 on obstacle? " + str(obstructionLines.count(templine2))
				# 		print templine1
				# 		print templine2
				# 		accept2 = True #accept pt2, check pt3
				# 		if triPoint3 == triPoint1 or triPoint3 == triPoint2: 
				# 			accept3 = False
				# 			continue
				# 			#reject pt3
				# 		elif hit13 != None or hit23 !=None:
				# 			if (obstructionLines.count(templine23)>0 or obstructionLines.count(templine32)>0) and inside13 == False:
				# 				accept3 = True
				# 			elif (obstructionLines.count(templine13)>0 or obstructionLines.count(templine31)>0) and inside23 == False:
				# 				accept3 = True
				# 			elif (obstructionLines.count(templine23)>0 or obstructionLines.count(templine32)>0) and (obstructionLines.count(templine13)>0 or obstructionLines.count(templine31)>0):
				# 				accept3 = True
				# 			else:
				# 				accept3 = False
				# 				continue
				# 		elif (hit13==None and inside13 == False) and (hit23 == None and inside23 == False):
				# 			accept3 = True
				# 		elif hit13 != None or hit23 != None: 
				# 			accept3 = False
				# 			continue #reject pt3
				# 		elif hit13 == None and hit23 == None:
				# 			if( ((obstructionLines.count(templine23)>0 or obstructionLines.count(templine32)>0) or (inside23==False)) and ((obstructionLines.count(templine13)>0 or obstructionLines.count(templine31)>0) or (inside13==False)) ):
				# 				accept3 = True #accept pt3
				# 			else:
				# 				accept3 = False
				# 				continue
				# 	else:
				# 		print "collision point 1-2" + str(rayTraceWorldNoEndPoints(triPoint1,triPoint2, obstructionLines))
				# 		accept2 = False
				# 		accept3 = False
				# 		break 
				# 	#collides reject, need new pt2
				# elif rayTraceWorldNoEndPoints(triPoint1,triPoint2, obstructionLines) == None:
				# 	if inside12 == False: #accept pt2, check pt3
				# 		accept2 = True
				# 		if triPoint3 == triPoint1 or triPoint3 == triPoint2: 
				# 			accept3 = False
				# 			continue
				# 			#reject pt3
				# 		elif hit13 != None or hit23 !=None:
				# 			if (obstructionLines.count(templine23)>0 or obstructionLines.count(templine32)>0) and inside13 == False:
				# 				accept3 = True
				# 			elif (obstructionLines.count(templine13)>0 or obstructionLines.count(templine31)>0) and inside23 == False:
				# 				accept3 = True
				# 			elif (obstructionLines.count(templine23)>0 or obstructionLines.count(templine32)>0) and (obstructionLines.count(templine13)>0 or obstructionLines.count(templine31)>0):
				# 				accept3 = True
				# 			else:
				# 				accept3 = False
				# 				continue
				# 		elif (hit13==None and inside13 == False) and (hit23 == None and inside23 == False):
				# 			accept3 = True
				# 		elif hit13 != None or hit23 != None: 
				# 			accept3 = False
				# 			continue #reject pt3
				# 		elif hit13 == None and hit23 == None:
				# 			if( ((obstructionLines.count(templine23)>0 or obstructionLines.count(templine32)>0) or (inside23==False)) and ((obstructionLines.count(templine13)>0 or obstructionLines.count(templine31)>0) or (inside13==False)) ):
				# 				accept3 = True #accept pt3
				# 			else:
				# 				accept3 = False
				# 				continue
				# 	else:
				# 		accept2 = False
				# 		accept3 = False
				# 		continue
				# else:
				# 	continue
				# if accept2 == False:
				# 	break
				# elif accept2 == True and accept3 == True:
				# 	edge1 = (triPoint1,triPoint2)
				# 	appendLineNoDuplicates(edge1,edges)
				# 	appendLineNoDuplicates(edge1,obstructionLines)
				# 	edge2 = (triPoint2,triPoint3)
				# 	appendLineNoDuplicates(edge2,edges)
				# 	appendLineNoDuplicates(edge2,obstructionLines)
				# 	edge3 = (triPoint3,triPoint1)
				# 	appendLineNoDuplicates(edge3,edges)
				# 	appendLineNoDuplicates(edge3,obstructionLines)
				# 	tuple1 = (triPoint1,triPoint2,triPoint3)
				# 	o = ManualObstacle(tuple1)
				# 	(ManualObstacleList).append(o)
				# else:
				# 	continue
	
