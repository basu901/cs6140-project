# CS 6140 - Computer Operating Systems
# Project 2
# 
# Shaunak Basu     (basus6)
# Michael Giancola (giancm)
# Farhad  Mohsin   (mohsif)

import sys

# Performs defragmentation of mem
# Assumes string is in correct format
def defrag(mem):
  ret = ""
  i = 0
  numFree = 0
  lineLen = 0

  moving = False
  moved = []

  # Copy header to return string
  while mem[i] == '=':
    ret += '='
    i += 1
    lineLen += 1

  while mem[i] != '=':

    if mem[i] == '\n': # Ignore newlines
      pass

    elif mem[i] != '.': # If memory is used
      ret += mem[i]     #   copy it to return string
      if moving: moved.append(mem[i])

    else:             # Otherwise
      numFree += 1    #   increment counter
      moving = True

    i += 1

  ret += numFree * '.' # Add free memory to end
  ret += lineLen * '=' # Add footer

  # No newlines in string
  #k = 0 # Insert newlines
  #for j in range(lineLen, len(mem), lineLen):
  #  idx = j + k
  #  ret = ret[:idx] + '\n' + ret[idx:]
  #  k += 1
  
  moved = list(dict.fromkeys(moved)) # Remove duplicates

  return ret, moved

# Given mem which HAS NOT BEEN DEFRAGMENTED YET, 
# determines the time (in ms) it will take to defragment
def timeToDefrag(mem, tMemMove):
  i = 0
  numMoving = 0 # Number of blocks which will be moved in defrag process

  # Move past first free area
  # i.e. memory which won't be moved in defrag process
  while mem[i] != '.': i += 1

  # Count block which will be
  # moved in defrag process
  while i < len(mem):
    if   mem[i] == '\n': pass          # Don't count
    elif mem[i] == '=':  break         # Done, hit footer
    elif mem[i] != '.': numMoving += 1 # Add used memory
    i += 1

  return numMoving * tMemMove

# Example

#print(timeToDefrag("================================\nAAAAAAAABBBBBBBBBBBBBBBBBBBBBBBB\nBBBBBBBBBBBBBBB.................\n...................DDDDDDDDD....\n................................\n................................\n........HHHHHHHHHHHHHHHHHHHHHHHH\nHHH.............................\n................................\n================================", 1))
#print()

#print("================================\nAAAAAAAABBBBBBBBBBBBBBBBBBBBBBBB\nBBBBBBBBBBBBBBB.................\n...................DDDDDDDDD....\n................................\n................................\n........HHHHHHHHHHHHHHHHHHHHHHHH\nHHH.............................\n................................\n================================")
#print()

#print(defrag("================================\nAAAAAAAABBBBBBBBBBBBBBBBBBBBBBBB\nBBBBBBBBBBBBBBB.................\n...................DDDDDDDDD....\n................................\n................................\n........HHHHHHHHHHHHHHHHHHHHHHHH\nHHH.............................\n................................\n================================"))
