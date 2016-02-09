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

# Creates the pathnetwork as a list of lines between all pathnodes that are traversable by the agent.
def myBuildPathNetwork(pathnodes, world):
	lines = []
	nodes = []
	radius= world.getAgent().getRadius()
	for pointStart in pathnodes:
		match = False
		for pointEnd in pathnodes:
			if pointStart != pointEnd and rayTraceWorld(pointStart,pointEnd, world.getLinesWithoutBorders()) == None:
				if(pointStart[1] > pointEnd[1]):
					pSleft = (pointStart[0] - radius*1.5, pointStart[1] + radius*1.5)
					pSright = (pointStart[0] + radius*1.5, pointStart[1] + radius*1.5)
					pEleft = (pointEnd[0] - radius*1.5, pointEnd[1] - radius*1.5)
					pEright = (pointEnd[0] + radius*1.5, pointEnd[1] - radius*1.5)
				else:
					pSleft = (pointStart[0] - radius*1.5, pointStart[1] - radius*1.5)
					pSright = (pointStart[0] + radius*1.5, pointStart[1] - radius*1.5)
					pEleft = (pointEnd[0] - radius*1.5, pointEnd[1] + radius*1.5)
					pEright = (pointEnd[0] + radius*1.5, pointEnd[1] + radius*1.5)
				if rayTraceWorld(pSleft,pEleft, world.getLinesWithoutBorders()) == None and rayTraceWorld(pSleft,pEright, world.getLinesWithoutBorders()) == None and rayTraceWorld(pSright,pEleft, world.getLinesWithoutBorders()) == None and rayTraceWorld(pSright,pEright, world.getLinesWithoutBorders()) == None:
					match = True
					tempLine = (pointStart,pointEnd)
					appendLineNoDuplicates(tempLine,lines)
		if match:
			nodes.append(pointStart)
	return nodes,lines
def mergeTriangles(ManualObstacleList):
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
						shareLineCounterclock = True
						shareLineClockwise = False
						cindex = comparisonObj.getLines().index(line) # where does the manualObj line exist in the comparisonObj
					elif counterline in comparisonObj.getLines(): # 3. share a same line in clockwise order
						shareLineCounterclock = False
						shareLineClockwise = True
						cindex = comparisonObj.getLines().index(counterline) # where does the manualObj counterline exist in the comparisonObj

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
								while counter < len(comparisonObj.getPoints()) -1:
									newPolygon.append(comparisonObj.getPoints()[counter])
									counter+=1
							else:
								counter = cindex +1 # finish in increasing order
								while counter < len(comparisonObj.getPoints()):
									newPolygon.append(comparisonObj.getPoints()[counter])
									counter+=1
								counter = 0 # finish in increase order
								while counter < cindex -1:
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
								counter = cindex
								while counter > 0:
									newPolygon.append(comparisonObj.getPoints()[counter])
									counter-=1
							else:
								counter = cindex # finish in decreasing order
								while counter >=  0:
									newPolygon.append(comparisonObj.getPoints()[counter])
									counter-=1
								counter =  len(comparisonObj.getPoints()) - 1# finish in decreasing order
								while counter > cindex +1 :
									newPolygon.append(comparisonObj.getPoints()[counter])
									counter-=1
						manualIndex+=1
				# if newPoly is not an empty list, check convexity 
				if (len(newPolygon) >0) and isConvex(newPolygon):
					print "final POLY: " + str(newPolygon)
					newP = ManualObstacle(tuple(newPolygon))
					print "final POLY Lines: " + str(newP.getLines())
					merged.append(newP)
					visited.append(manualObj)
					visited.append(comparisonObj)
					break

	# remove visited polys and add merged polys to the final list 
	mergeOccured = False
	for visit in visited:
		ManualObstacleList.remove(visit)
	if len(merged) >0:
		mergeOccured = True
	ManualObstacleList.extend(merged)

	return mergeOccured, ManualObstacleList
# Creates a pathnode network that connects the midpoints of each navmesh together
def myCreatePathNetwork(world, agent = None):
	nodes = []
	edges = []
	polys = []
	### YOUR CODE GOES BELOW HERE ###
	obstructionLines = world.getLines()
	anchorpoints = world.getPoints()
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
			elif hit12 != None and not ((obstructionLines.count(templine1) >0) or (obstructionLines.count(templine2) >0)):
				continue
			#else:
			#	continue

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
				elif (hit13 != None and not (obstructionLines.count(templine13)>0 or obstructionLines.count(templine31)>0)) or (hit23 != None and not (obstructionLines.count(templine23)>0 or obstructionLines.count(templine32)>0)):
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
				appendLineNoDuplicates(edge1,obstructionLines)
				edge2 = (triPoint2,triPoint3)
				appendLineNoDuplicates(edge2,obstructionLines)
				edge3 = (triPoint3,triPoint1)
				appendLineNoDuplicates(edge3,obstructionLines)
				
				(ManualObstacleList).append(o)

	
	keepMerge = True
	polyList = ManualObstacleList
	while keepMerge == True:
		returnVal = mergeTriangles(polyList)
		keepMerge = returnVal[0]
		polyList = returnVal[1]

	for obs in polyList:
		polys.append(obs.getPoints())
	
	# Place Waypoints

	# for every line in the polygons, if it is not an obstruction (obstacle or border) temp place waypoint
	allPolyLines = []
	for poly in polyList:
		allPolyLines.extend(poly.getLines())
	tempnodes = []
	obstructionLines = world.getLinesWithoutBorders()
	for poly in polyList:
		for line in poly.getLines():
			counterline = (line[1],line[0])
			if line not in obstructionLines and counterline not in obstructionLines and (allPolyLines.count(line) + allPolyLines.count(counterline) > 1):
				midpoint = ((line[0][0]+line[1][0])/2, (line[0][1]+line[1][1])/2)
				tempnodes.append(midpoint) 
		#compute the centroid
		sumX =0
		sumY=0
		for point in poly.getPoints():
			sumX+= point[0]
			sumY+= point[1]
		centroid = ((sumX/len(poly.getPoints())),(sumY/len(poly.getPoints())))
		tempnodes.append(centroid)

	# make an edge of a waypoint can reach another waypoint 
	nodesEdges = myBuildPathNetwork(tempnodes,world)
	edges.extend(nodesEdges[1]) 
	nodes.extend(nodesEdges[0])
	# Form Path Newtwork
	### YOUR CODE GOES ABOVE HERE ###
	return nodes, edges, polys
	
