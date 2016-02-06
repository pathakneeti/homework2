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

def generateTriangleMesh(point, triList, anchorpoints, obstructionLines, obstacle):
	if len(triList) == 3 and isConvex(triList):
		return triList

	if len(triList) ==1:
		# try the last item in anchorpoints
		# cases where it is ok: doesn't intersect with obstructionLines unless line in obstruction lines
		index = len(anchorpoints) -1
		triPt2 = findClosestUnobstructedModified(point, anchorpoints, obstructionLines)
		if triPt2 == None:
			return None
		hit = rayTraceWorld(point,triPt2,obstacle.getLines()) 
		# calc midpoint and see if it is inside polygon
		midpoint = ((point[0]+triPt2[0])/2, (point[1]+triPt2[1])/2)
		if obstacle.pointInside(midpoint):
		# or (hit != None and pointOnPolygon(hit,obstacle.getLines()) != True):
			anchorpoints.remove(triPt2)
			generateTriangleMesh(point, triList, anchorpoints, obstructionLines, obstacle)
		else:
			anchorpoints.remove(triPt2)
			triList.append(triPt2)
			generateTriangleMesh(triPt2, triList, anchorpoints, obstructionLines, obstacle)

	if len(triList)==2:
		triPt3 = findClosestUnobstructedModified(point, anchorpoints, obstructionLines)
		if triPt3 == None:
			anchorpoints.remove(triList[1])
			removept = triList[1]
			triList.remove(removept)
			generateTriangleMesh(triList[0], triList, anchorpoints, obstructionLines, obstacle)
		# calc midpoint and see if it is inside polygon
		midpoint = ((point[0]+triPt3[0])/2, (point[1]+triPt3[1])/2)
		midpoint2 = (((triList[0])[0]+triPt3[0])/2, ((triList[0])[1]+triPt3[1])/2)
		hit = rayTraceWorld(point,triPt3,obstacle.getLines())
		hit2 = rayTraceWorld(triList[0],triPt3,obstacle.getLines()) 
		if obstacle.pointInside(midpoint) or obstacle.pointInside(midpoint2):
		#or  (hit != None and pointOnPolygon(hit, obstacle.getLines()) != True) or (hit2 != None and pointOnPolygon(hit2, obstacle.getLines()) != True):
			anchorpoints.remove(triPt3)
			generateTriangleMesh(point, triList, anchorpoints, obstructionLines, obstacle)
		else:
			anchorpoints.remove(triPt3)
			triList.append(triPt3)
			generateTriangleMesh(triPt3, triList, anchorpoints, obstructionLines, obstacle)

	return triList
# Creates a pathnode network that connects the midpoints of each navmesh together
def myCreatePathNetwork(world, agent = None):
	nodes = []
	edges = []
	polys = []
	### YOUR CODE GOES BELOW HERE ###

	obstructionLines = (world.getLinesWithoutBorders())
	for obstacle in world.getObstacles():
		points = obstacle.getPoints()
		for point in points:

			anchorpoints = (world.getPoints())
			anchorpoints.remove(point)

			triList = []
			triList.append(point)
			meshTri = generateTriangleMesh(point, triList, anchorpoints, obstructionLines, obstacle)

			if meshTri != None:
				# create the edges and add them 
				edge1 = (meshTri[0],meshTri[1])
				appendLineNoDuplicates(edge1,edges)
				appendLineNoDuplicates(edge1,obstructionLines)
				edge2 = (meshTri[1],meshTri[2])
				appendLineNoDuplicates(edge2,edges)
				appendLineNoDuplicates(edge2,obstructionLines)
				edge3 = (meshTri[2],meshTri[0])
				appendLineNoDuplicates(edge3,edges)
				appendLineNoDuplicates(edge3,obstructionLines)
				print meshTri
	
	print len(edges)
	### YOUR CODE GOES ABOVE HERE ###
	return nodes, edges, polys


	
