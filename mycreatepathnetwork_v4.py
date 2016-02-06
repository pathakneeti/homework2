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

def findClosestUnobstructedModified(p, nodes, worldLines):
	best = None
	dist = INFINITY
	for n in nodes:
		if rayTraceWorldNoEndPoints(p, n, worldLines) == None:
			d = distance(p, n)
			if best == None or d < dist:
				best = n
				dist = d
	return best

def generateTriangleMesh(point, triList, anchorpoints, obstructionLines, obstacle, indexPt2, indexPt3):
	if len(triList) == 3 and isConvex(triList):
		print "success"
		return triList

	if len(triList) ==1:
		# if len(anchorpoints) == 0:
		# 	return None
		if indexPt2 >= len(anchorpoints):
			return None
		# try the last item in anchorpoints
		# cases where it is ok: doesn't intersect with obstructionLines unless line in obstruction lines
		#index = len(anchorpoints) -1
		triPt2 = anchorpoints[indexPt2]
		hit = rayTraceWorldNoEndPoints(point,triPt2,obstructionLines) 
		tempLine1 = (point, triPt2)
		tempLine2 = (triPt2, point)
		obsPts = obstacle.getPoints()

		# if (obsPts.count(triPt2) >0):
		# 	if (obstructionLines.count(tempLine1) >0 or obstructionLines.count(tempLine2) >0):
		# 		#anchorpoints.remove(triPt2)
		# 		triList.append(triPt2)
		# 		generateTriangleMesh(triPt2, triList, anchorpoints, obstructionLines, obstacle, indexPt2 + 1, indexPt3)
		# 	else:
		# 		#anchorpoints.remove(triPt2)
		# 		generateTriangleMesh(point, triList, anchorpoints, obstructionLines, obstacle, indexPt2 + 1, indexPt3)
		if (obstructionLines.count(tempLine1) >0 or obstructionLines.count(tempLine2) >0):
				#anchorpoints.remove(triPt2)
				triList.append(triPt2)
				generateTriangleMesh(triPt2, triList, anchorpoints, obstructionLines, obstacle, indexPt2 + 1, indexPt3)
		elif hit == None: 
			#anchorpoints.remove(triPt2)
			triList.append(triPt2)
			generateTriangleMesh(triPt2, triList, anchorpoints, obstructionLines, obstacle, indexPt2 + 1, indexPt3)
		else: 
			#anchorpoints.remove(triPt2)
			generateTriangleMesh(point, triList, anchorpoints, obstructionLines, obstacle, indexPt2 + 1, indexPt3)

	if len(triList)==2:
		#if len(anchorpoints) == 0:
		if indexPt3 >= len(anchorpoints):
			# we need another Pt2 so increment that in recursion and remove it from the triList 
			print "go here"
			print triList
			removept = triList[1]
			triList.remove(removept)
			print triList
			generateTriangleMesh(triList[0], triList, anchorpoints, obstructionLines, obstacle, indexPt2 +1, 0)
		else:
			# try the last item in anchorpoints
			# cases where it is ok: doesn't intersect with obstructionLines unless line in obstruction lines
			#index = len(anchorpoints) -1
			print str(len(anchorpoints))
			print "pt3 " + str(indexPt3)
			print "pt2 " + str(indexPt2)
			triPt3 = anchorpoints[indexPt3]
			hit1 = rayTraceWorldNoEndPoints(point,triPt3,obstructionLines) 
			tempLine11 = (point, triPt3)
			tempLine12 = (triPt3, point)
			hit2 = rayTraceWorldNoEndPoints(triList[0],triPt3,obstructionLines) 
			tempLine21 = (triList[0], triPt3)
			tempLine22 = (triPt3, triList[0])
			obsPts = obstacle.getPoints()

			# # if its on the polygon, then it should be a line 
			# condition11 = (obsPts.count(triPt3) >0) and (obstructionLines.count(tempLine11) >0 or obstructionLines.count(tempLine12) >0)
			# condition21 = (obsPts.count(triList[0]) >0) and (obstructionLines.count(tempLine21) >0 or obstructionLines.count(tempLine22) >0)

			# #if its not on the polygon then it should not collide with other obstructions
			# condition12 = (obsPts.count(triPt3) <=0) and (hit1 == None)
			# condition22 = (obsPts.count(triList[0]) <=0) and (hit2 == None)

			# point should not be in the triangle already
			condition0 = (triList.count(triPt3) <=0)

			# if its on the polygon, then it should be a line 
			condition11 = (obstructionLines.count(tempLine11) >0 or obstructionLines.count(tempLine12) >0)
			condition21 = (obstructionLines.count(tempLine21) >0 or obstructionLines.count(tempLine22) >0)

			#if its not on the polygon then it should not collide with other obstructions
			condition12 = (hit1 == None)
			condition22 = (hit2 == None)
			print "count pt3 " + str(obsPts.count(triPt3))
			print "obstacle line? " + str(obstructionLines.count(tempLine11))
			print "obstacle line? " + str(obstructionLines.count(tempLine12))

			if condition0 and (condition11 or condition12) and (condition21 or condition22):
				#anchorpoints.remove(triPt3)
				print "should be success"
				triList.append(triPt3)
				print triList
				return triList
				generateTriangleMesh(triPt3, triList, anchorpoints, obstructionLines, obstacle, indexPt2, indexPt3 +1)
			else:
				print condition11
				print condition12
				print condition21
				print condition22
				#anchorpoints.remove(triPt3)
				generateTriangleMesh(triList[1], triList, anchorpoints, obstructionLines, obstacle, indexPt2, indexPt3 +1)

		# if hit1 == None and hit2 == None: 
		# 	anchorpoints.remove(triPt3)
		# 	triList.append(triPt3)
		# 	generateTriangleMesh(triPt3, triList, anchorpoints, obstructionLines, obstacle)
		# elif (obstructionLines.count(tempLine1) >0 or obstructionLines.count(tempLine2) >0) and (obstructionLines.count(tempLine21) >0 or obstructionLines.count(tempLine22) >0):
		# 	anchorpoints.remove(triPt3)
		# 	triList.append(triPt3)
		# 	generateTriangleMesh(triPt3, triList, anchorpoints, obstructionLines, obstacle)
		# else: 
		# 	anchorpoints.remove(triPt3)
		# 	generateTriangleMesh(triList[1], triList, anchorpoints, obstructionLines, obstacle)

	#return triList
# Creates a pathnode network that connects the midpoints of each navmesh together
def myCreatePathNetwork(world, agent = None):
	nodes = []
	edges = []
	polys = []
	### YOUR CODE GOES BELOW HERE ###

	obstructionLines = world.getLines()
	anchorpoints = world.getPoints()

	for triPoint1 in anchorpoints:
		for triPoint2 in anchorpoints:
			for triPoint3 in anchorpoints:
				templine1 = (triPoint1,triPoint2)
				templine2 = (triPoint2, triPoint1)
				accept2 = False
				accept3 = False
				if triPoint1 == triPoint2: 
					break
					#if same point, need new pt2
				elif rayTraceWorldNoEndPoints(triPoint1,triPoint2, obstructionLines) != None:
					break 
					#collides reject, need new pt2
				elif rayTraceWorldNoEndPoints(triPoint1,triPoint2, obstructionLines) == None:
					#check midpoint
					midpoint12 = ((triPoint1[0]+triPoint2[0])/2, (triPoint1[1]+triPoint2[1])/2)
					midpoint13 = ((triPoint1[0]+triPoint3[0])/2, (triPoint1[1]+triPoint3[1])/2)
					midpoint23 = ((triPoint3[0]+triPoint2[0])/2, (triPoint3[1]+triPoint2[1])/2)
					inside12 = False
					inside23 = False
					inside13 = False
					for obstacle in world.getObstacles():
						if obstacle.pointInside(midpoint12):
							inside12 = True
						if obstacle.pointInside(midpoint13):
							inside13 = True
						if obstacle.pointInside(midpoint23):
							inside23 = True

					if ((obstructionLines.count(templine1) >0) or (obstructionLines.count(templine2) >0)) or (inside12 == False): #accept pt2, check pt3
						accept2 = True
						templine23 = (triPoint2,triPoint3)
						templine32 = (triPoint3,triPoint2)
						templine13 = (triPoint1, triPoint3)
						templine31 = (triPoint3,triPoint1)
						if triPoint3 == triPoint1 or triPoint3 == triPoint2: 
							#reject pt3
						elif rayTraceWorldNoEndPoints(triPoint1,triPoint3,obstructionLines) != None or rayTraceWorldNoEndPoints(triPoint2, triPoint3, obstructionLines) != None:
						    #reject pt3
						elif rayTraceWorldNoEndPoints(triPoint1,triPoint3, obstructionLines) == None and rayTraceWorldNoEndPoints(triPoint2,triPoint3, obstructionLines) == None:
							if( ((obstructionLines.count(templine23)>0 or obstructionLines.count(templine32)>0) or (inside23==False)) and ((obstructionLines.count(templine13)>0 or obstructionLines.count(templine31)>0) or (inside13==False)) ):
								accept3 = True #accept pt3
						else:				
				if accept2 == False:
					break
				else:
					if accept3 == True: #accept the triangle!
						edge1 = (triPoint1,triPoint2)
						appendLineNoDuplicates(edge1,edges)
						appendLineNoDuplicates(edge1,obstructionLines)
						edge2 = (triPoint2,triPoint3)
						appendLineNoDuplicates(edge2,edges)
						appendLineNoDuplicates(edge2,obstructionLines)
						edge3 = (triPoint3,triPoint1)
						appendLineNoDuplicates(edge3,edges)
						appendLineNoDuplicates(edge3,obstructionLines)
	
	print "edges " + str(len(edges))
	### YOUR CODE GOES ABOVE HERE ###
	return nodes, edges, polys


	
