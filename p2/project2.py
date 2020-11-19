# CS 6140 - Computer Operating Systems
# Project 2
# 
# Shaunak Basu     (basus6)
# Michael Giancola (giancm)
# Farhad  Mohsin   (mohsif)

#  argv[1]: The first command-line argument specifies the number of frames to show on a line.
#The examples show 32 frames per line. Note that this value might not be a power of two.
#  argv[2]: The second command-line argument specifies the size of the memory, i.e., how many
#frames make up the physical memory. The examples show a memory consisting of 256 frames.
#Note that this value might not be a power of two.
#  argv[3]: The third command-line argument specifies the name of the input file to read in
#for your simulation.
#  argv[4]: The fourth command-line argument defines tmemmove, which is the time, in milliseconds, 
#that it takes to move one frame of memory during defragmentation

import sys
import non_con
import con_alloc

if __name__=='__main__':
    
  # Argument Checks

  if(len(sys.argv) < 4):
    print("Usage: python3 project2.py <num_frames> <mem_size> <input_file> <move_time>", file=sys.stderr)
    exit()

  if(int(sys.argv[1]) < 0 or int(sys.argv[2]) < 0 or int(sys.argv[4]) < 0):
    print("ERROR: Numerical inputs should all be positive numbers.", file=sys.stderr)
    exit()

  try:
    fp = open(sys.argv[3], 'r')
  except IOError:
    print("ERROR: File \"" + sys.argv[3] + "\" does not exist.", file=sys.stderr)
    exit()
  
  txt = fp.read()
  
  con_alloc.contiguous_memory_alloc(txt, int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[4]))
  non_con.non_contiguous_alloc( [int(sys.argv[1]), int(sys.argv[2]), txt] )
  
  fp.close()