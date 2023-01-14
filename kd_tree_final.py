from typing import List
from collections import namedtuple
import time
import math
import sys
import matplotlib.pyplot as plt

class Point(namedtuple("Point", "x y")):
  def __repr__(self) -> str:
    return f'Point{tuple(self)!r}'


class Rectangle(namedtuple("Rectangle", "lower upper")):
  def __repr__(self) -> str:
    return f'Rectangle{tuple(self)!r}'

  def is_contains(self, p: Point) -> bool:
    return self.lower.x <= p.x <= self.upper.x and self.lower.y <= p.y <= self.upper.y


'''
class Node(namedtuple("Node", "location left right")):
  """
  location: Point
  left: Node
  right: Node
  """

  def __repr__(self):
    return f'{tuple(self)!r}'
'''

class Node(object):

  def __init__(self, location, left = None, right = None):
    self.location = location
    self.left = left
    self.right = right

class KDTree:

  def __init__(self):
    self._root = None
    self._n = 0
  # insert a series of points
  def insert(self, p: List[Point]):
    if self._root is None:
      self._root = Node(p[0])

    for _p in p[1:]:
      self._insertNode(self._root, _p, self._n)

  def _insertNode(self, currentNode, p, depth):
    #print(currentNode, p, depth)
    axis = depth % 2
    next_depth = depth + 1

    if p[axis] <= currentNode.location[axis]:
      if currentNode.left is None:
        currentNode.left = Node(p)
      else:
        self._insertNode(currentNode.left, p, next_depth)

    elif p[axis] > currentNode.location[axis]:
      if currentNode.right is None:
        currentNode.right = Node(p)
      else:
        self._insertNode(currentNode.right, p, next_depth)
    
  # check whether the points in kd tree is in the rectangle
  def range(self, rectangle: Rectangle) -> List[Point]:
    res = []
    self._checkPoint(self._root, rectangle, self._n, res)
    return res

  def _checkPoint(self, cNode, rect, depth, res):
    axis = depth % 2
    next_depth = depth + 1

    if cNode is None:
      return

    if cNode.location[axis] > rect.upper[axis]:
      self._checkPoint(cNode.left, rect, next_depth, res)

    elif cNode.location[axis] < rect.lower[axis]:
      self._checkPoint(cNode.right, rect, next_depth, res)
      
    elif rect.lower[axis] <= cNode.location[axis] <= rect.upper[axis]:  # 这只判断了一个维度，若要在矩形区域内，则还要另一个维度也在区域内才能说明。
      if rect.lower[1 - axis] <= cNode.location[1 - axis] <= rect.upper[1 - axis]:
        res.append(cNode.location)
      self._checkPoint(cNode.left, rect, next_depth, res)
      self._checkPoint(cNode.right, rect, next_depth, res)

  # Implement the Nearest Neighbor Query
  def nearestNeighbor(self, x1, y1):
    qryPoint = (x1, y1)
    bestNode = self._root
    best_dst = self._calDist(self._root.location, qryPoint)
    p1 = self._findNearest(qryPoint, self._root.left, best_dst, self._n, bestNode)
    p2 = self._findNearest(qryPoint, self._root.right, best_dst, self._n, bestNode)
    d1 = self._calDist(p1.location, qryPoint)
    d2 = self._calDist(p2.location, qryPoint)
    if d1 > d2:
      return p2.getInfo()
    else:
      return p1.getInfo()


  def _findNearest(self, qryPoint, cNode, best_dst, depth, bestNode):
    axis = depth % 2
    next_depth = depth + 1

    if cNode is None:
      return bestNode

    if best_dst > self._calDist(qryPoint, cNode.location):
      best_dst = self._calDist(qryPoint, cNode.location)
      bestNode = cNode

    # compare best distance with distance between current node and query point
    if best_dst > abs(qryPoint[axis] - cNode.location[axis]):
      self._findNearest(qryPoint, cNode.left, best_dst, next_depth, bestNode)
      self._findNearest(qryPoint, cNode.right, best_dst, next_depth, bestNode)
    else:
      if qryPoint[axis] <= cNode.location[axis]:
        self._findNearest(qryPoint, cNode.left, best_dst, next_depth, bestNode)
      else:
        self._findNearest(qryPoint, cNode.right, best_dst, next_depth, bestNode)

    return bestNode

  def _calDist(self, point1, point2):
    x1 = point1[0]
    y1 = point1[1]
    x2 = point2[0]
    y2 = point2[1]
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
# test
def range_test():
  points = [Point(7, 2), Point(5, 4), Point(9, 6), Point(4, 7), Point(8, 1), Point(2, 3)]
  kd = KDTree()
  kd.insert(points)
  result = kd.range(Rectangle(Point(0, 0), Point(6, 6)))
  assert sorted(result) == sorted([Point(2, 3), Point(5, 4)])


def performance_test():
  points = [Point(x, y) for x in range(100) for y in range(100)]

  lower = Point(500, 500)
  upper = Point(504, 504)
  rectangle = Rectangle(lower, upper)
  #  naive method
  start = int(round(time.time() * 1000))
  result1 = [p for p in points if rectangle.is_contains(p)]
  end = int(round(time.time() * 1000))
  print(f'Naive method: {end - start}ms')

  kd = KDTree()
  kd.insert(points)
  # k-d tree
  start = int(round(time.time() * 1000))
  result2 = kd.range(rectangle)
  end = int(round(time.time() * 1000))
  print(f'K-D tree: {end - start}ms')

  assert sorted(result1) == sorted(result2)


if __name__ == '__main__':
  sys.setrecursionlimit(5000)
  range_test()
  performance_test()

# Visualize the Time Performance Between K-D Tree Method and Naive Method
  x1 = []
  y1 = []
  x2 = []
  y2 = []

  lower = Point(500, 500)
  upper = Point(504, 504)
  rectangle = Rectangle(lower, upper)

  for i in range(1, 10):
      points = [Point(x, y) for x in range(400) for y in range(400)]
      #  naive method
      start = int(round(time.time() * 1000))
      result1 = [p for p in points if rectangle.is_contains(p)]
      end = int(round(time.time() * 1000))
      x = end - start
      x1.append(i)
      y1.append(x)

      # kd tree method
      kd = KDTree()
      kd.insert(points)
      # k-d tree
      start = int(round(time.time() * 1000))
      result2 = kd.range(rectangle)
      end = int(round(time.time() * 1000))
      x = end - start
      x2.append(i)
      y2.append(x)

  # draw the picture
  plt.plot(x1, y1, color="lightsteelblue", linewidth=3.0, linestyle="-", label="naive method")
  plt.plot(x2, y2, color="mediumpurple", linewidth=3.0, linestyle="--", label="kd tree method")
  plt.xlabel('number of trials', fontsize=10)
  plt.ylabel('run time', fontsize=10)
  plt.legend(loc="best")
  plt.title(r'naive and kd tree method', fontsize=15)