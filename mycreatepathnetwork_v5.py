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

						hit13 = rayTraceWorldNoEndPoints(triPoint1,triPoint3,obstructionLines)
						hit23 = rayTraceWorldNoEndPoints(triPoint2,triPoint3, obstructionLines)

						if triPoint3 == triPoint1 or triPoint3 == triPoint2: 
							reject pt3
						elif hit13 != None or hit23 != None: 
							x= 5 #reject pt3
						elif hit13 == None and hit23 == None:
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
	#return nodes, edges, polys