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
	# firstPoints = world.getPoints()
	# firstPoints.remove((0, 0))
	# firstPoints.remove((world.getDimensions()[0], 0))
	# firstPoints.remove((world.getDimensions()[0], world.getDimensions()[1]))
	# firstPoints.remove((0, world.getDimensions()[1]))
	ManualObstacleList = []

	for triPoint1 in anchorpoints:
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
						obsInTri = obsInTri and (o.pointInside(point) or trianglePoly.count(point)>0)
					if obsInTri == True:
						obstacleInTriangle = True
						break
				if obstacleInTriangle:
					continue

				# check if we are repeating a polygon 
				repeatTri = False
				for manObs in ManualObstacleList: 
					if (triPoint1 in manObs.getPoints()) and (triPoint2 in manObs.getPoints()) and (triPoint3 in manObs.getPoints()):
						repeatTri = True
						break
				if repeatTri:
					continue


				edge1 = (triPoint1,triPoint2)
				#appendLineNoDuplicates(edge1,edges)
				appendLineNoDuplicates(edge1,obstructionLines)
				edge2 = (triPoint2,triPoint3)
				#appendLineNoDuplicates(edge2,edges)
				appendLineNoDuplicates(edge2,obstructionLines)
				edge3 = (triPoint1,triPoint3)
				#appendLineNoDuplicates(edge3,edges)
				appendLineNoDuplicates(edge3,obstructionLines)
				
				(ManualObstacleList).append(o)

	# Merge Triangles
	merged = [] # mark merged polygons
	visited = [] # mark comparisonObj that we dont want to remerge 			
	for manualObj in ManualObstacleList:
		for comparisonObj in ManualObstacleList:
			newPolygon = []
			if (manualObj != comparisonObj) and (comparisonObj not in visited) and (manualObj not in visited): # 1. cannot be same object and cannot be visited
				mindex=0
				cindex=0
				shareLineClockwise = False
				shareLineCounterclock = False
				for line in manualObj.getLines():
					counterline = (line[1], line[0])
					if line in comparisonObj.getLines(): # 2. share a same line in same counterclockwise order
						print str(line) + " :matchyoo: " + str(comparisonObj.getLines())
						shareLineCounterclock = True
						shareLineClockwise = False
						cindex = comparisonObj.getLines().index(line) # where does the manualObj line exist in the comparisonObj
					# elif counterline in comparisonObj.getLines(): # 3. share a same line in clockwise order
					# 	print str(line) + " :matchpoo: " + str(comparisonObj.getLines())
					# 	shareLineCounterclock = False
					# 	shareLineClockwise = True
					# 	cindex = comparisonObj.getLines().index(counterline) # where does the manualObj counterline exist in the comparisonObj

					if shareLineClockwise or shareLineCounterclock:
						break
					else:
						mindex+=1
						continue
				# merge polygons clockwise or counterclockwise
				if shareLineClockwise:
					manualIndex=0
					for manualPoint in manualObj.getPoints():
						if manualIndex != mindex:
							newPolygon.append(manualObj.getPoints()[manualIndex])
						elif manualIndex >= len(manualObj.getPoints()):
							break
						else:
							if cindex == len(comparisonObj.getPoints()) -1:
								counter = 0
								while counter < len(comparisonObj.getPoints()):
									newPolygon.append(comparisonObj.getPoints()[counter])
									counter+=1
							else:
								counter = cindex +1 # finish in increasing order
								while counter < len(comparisonObj.getPoints()):
									newPolygon.append(comparisonObj.getPoints()[counter])
									counter+=1
								counter = 0 # finish in increase order
								while counter < cindex -1:
									print "boo"
									newPolygon.append(comparisonObj.getPoints()[counter])
									counter+=1
						manualIndex+=1
				elif shareLineCounterclock:
					manualIndex=0
					for manualPoint in manualObj.getPoints():
						if manualIndex != mindex:
							newPolygon.append(manualObj.getPoints()[manualIndex])
						elif manualIndex >= len(manualObj.getPoints()):
							break
						else:
							if cindex == len(comparisonObj.getPoints()) -1:
								print "here"
								counter = cindex
								while counter > 0:
									newPolygon.append(comparisonObj.getPoints()[counter])
									counter-=1
							else:
								counter = cindex # finish in decreasing order
								while counter >=  0:
									print "poo"
									newPolygon.append(comparisonObj.getPoints()[counter])
									counter-=1
								counter =  len(comparisonObj.getPoints()) - 1# finish in decreasing order
								while counter > cindex +1 :
									print "issue"
									newPolygon.append(comparisonObj.getPoints()[counter])
									counter-=1
						manualIndex+=1
				# if newPoly is not an empty list, check convexity 
				if (len(newPolygon) >0) and isConvex(newPolygon):
					print isConvex(newPolygon)
					print "obj points: " + str(manualObj.getPoints())
					print "comp points: " + str(comparisonObj.getPoints())
					print "final POLY: " + str(newPolygon)
					newP = ManualObstacle(tuple(newPolygon))
					merged.append(newP)
					visited.append(manualObj)
					visited.append(comparisonObj)
					break

	# remove visited polys and add merged polys to the final list 
	for visit in visited:
		#print "visited points"
		#print visit.getPoints()
		ManualObstacleList.remove(visit)
	ManualObstacleList.extend(merged)

	for obs in ManualObstacleList:
		polys.append(obs.getPoints())
	#polys.extend(ManualObstacleList)
	# Place Waypoints

	# Form Path Newtwork
	### YOUR CODE GOES ABOVE HERE ###
	return nodes, edges, polys
	
