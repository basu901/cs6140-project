import queue
import collections as col
from defragmentation import defrag,timeToDefrag
import non_con

inf = float('inf')

class m_proc(object):
	
    def __init__(self,name,mem,arrival_time,burst_duration):
        self.name = name			#Name of the process		
        self.mem = mem				#Size of memory required by the process
        self.arrival_time = arrival_time     #This is a dequeue
        self.burst_duration = burst_duration #This is a dequeue
        self.leave = -1		     #When should the process be taken out of memory
        self.eject = 0			     #Should process be removed from queue of ready processes after completing present burst


class fit(object):

    def __init__(self,t_memory,frames,process_list):
		# t_memory = Size of total memory
        self.process_list = process_list 	#Storing the number of processes to be assigned memory				
        self.t_memory = t_memory
        self.frames_line = frames
        self.start_fit(frames)

    def show_output(self,total_frames,f_per_line,q):
        #Prints the output in the specified format
        print("In PRINT")
        k = 1
        for i in range(0,len(q)):
            if i==k*f_per_line:
               k = k+1
               print('')
            
            print(q[i],end="")
        print('')

      
	
	
  
    def start_fit(self,frames_per_line):					
	
        time = 0
        n = len(self.process_list)
        #print("Length of process_list",n)

        mem = '='*frames_per_line+'.'*self.t_memory+'='*frames_per_line

        active_processes=list()			#List of processes that acquired main memory
        ready_processes=list()			#List of processes competing for main memory at time t
        done = list()					#List of processes which have completed all their burst


        print("time ",time,"ms: Simulator started (Contiguous -- First-Fit)")
	
		#REMOVE PROCESSES FROM MAIN MEMORY
        while(len(done)!=n):

            i =0 
            while i<len(self.process_list):
                #print(i)
                #print(len(self.process_list))
                if self.process_list[i].leave==time:
                    print("time:",time," Leaving",self.process_list[i].name)
                    to_remove = self.process_list[i].name
                    if self.process_list[i].eject==1:
                        done.append(self.process_list[i])
                        self.process_list.pop(i)
                    x=list(mem)
                    for j in range(0,len(x)):
                        if x[j]==to_remove:
                           x[j]='.'
                    mem = "".join(x)
                    del x
                    print("After process left:")
                    #print(mem)
                i = i+1    
                
	    #CHECK WHICH PROCESS SHOULD ENTER MAIN MEMORY. IF IT's THE LAST BURST MARK FOR EJECTION
            i = 0
            while i<len(self.process_list):
                #print(i)
                #print(self.process_list[i].name)
                if(self.process_list[i].eject!=1):
                    if self.process_list[i].arrival_time[0]==time:
                        print("ARRIVED",self.process_list[i].name)
                        self.process_list[i].leave = self.process_list[i].arrival_time[0]+self.process_list[i].burst_duration[0]
				#Updating arrival and burst times of the process
                        self.process_list[i].arrival_time.pop(0)
                        self.process_list[i].burst_duration.pop(0)
                        ready_processes.append(self.process_list[i])
                        print("READY PROCESS",ready_processes)
                        if len(self.process_list[i].arrival_time)==0:
                            self.process_list[i].eject=1		#Indicator that process should be shifted to done list
                       
                i = i+1
                #print(i)    
                

		#Sort the processes based on process_id
            #print("EXIT firt while")
            
            
	
            if(ready_processes):
                ready_processes.sort(key=lambda x:x.name)		
                while (ready_processes):
                    c_process = ready_processes.pop(0)
                    print("current",c_process.name)
                    
                    print("time ",time,"ms: Process ",c_process.name," arrived (requires ",c_process.mem," frames)")
                    search_mem = c_process.mem	#memory requirement of process
		
                    print("Search mem",search_mem)
                    #print(mem)
                    #first = self.check_space(mem,search_mem,self.t_memory)
			              # TODO 
                    first = self.best_fit(mem, search_mem, self.t_memory)
                    if first!=-1 and first!=-2:
                        x = list(mem)
                        j = first
                        while search_mem!=0:
                            x[j] = c_process.name
                            search_mem = search_mem - 1
                            j = j+ 1
                        mem = "".join(x)
                        del x
                        #print(mem)
                        self.show_output(self.t_memory,self.frames_line,mem)

                    else:
                        if first==-1:
                            #time_defrag = (mem,) 
                            defrag(mem)
                            #second = self.check_space(mem,search_mem,self.t_memory)
                            # TODO 
                            second = self.best_fit(mem, search_mem, self.t_memory)

                        else:
                            continue

                        if second!=-1:
                            j = second+1
                            while search_mem!=0:
                                mem[j] = c_process.name
                                search_mem -= 1
                                j = j+1

                            self.show_output(self.t_memory,self.frames_line,mem)

                        else:
                            print("time ",time,"ms : Cannot place process ",c_process.name," -- skipped!")
                

            time = time+1
 


    #THIS METHOD SHOULD BE MODIFIED FOR DIFFERENT PLACEMENT ALGOS
    def check_space(self,m,space,total):
        #-1 is after defragment, -2 is no need to defragment as memory was empty
        first = m.find('.')
        #print("INDEX of .",first)
        i = first
        while(True):
            while m[i]=='.':
                i = i+1
            if m[i]!='=':    
                if space<=(i-first):
                    return first
                else:
                    first = m.find('.',i+1)
                    i = first
                    if first==-1:
                        return first
            else:
                if space<=(i-first):
                    return first

    # Returns the index where a block of memory of size space
    # can be inserted into m, and returns -1 if there isn't space
    def best_fit(self, m, space, total):
        smallest = inf # Size of smallest free space (>= space)
        idx = -1       # Index of above
        tmpLen = 0

        i = m.find('.')            # Find the first free space
        while(i < len(m)):

            while(m[i] == '.'):    # Count the size of the free space
                tmpLen += 1        # Track the length
                i += 1

            # If this space is smaller than the current smallest,
            # but still bigger than the required space, its the
            # new smallest
            if(tmpLen < smallest and tmpLen >= space):
                idx = i - tmpLen
                smallest = tmpLen
                tmpLen = 0

            while(i < len(m) and m[i] != '.'): # Find the next free space
                i += 1

        return idx

def create_processes(txt):
    lines = txt.split('\n')
   
    P = []
    for line in lines:
        bursts = list()
        arrival = list()
        #print("line is",line)
        words = line.split(' ')
        #print(words)
        arr_dur = list()
        for i in range(2,len(words)):
            arr_dur.append([int(x) for x in words[i].split('/')])
        #print("arr_dur",arr_dur)
        i=0
        while i<(len(arr_dur)):
            arrival.append(arr_dur[i][0])
            #print("ARRIVAL:",arrival)
            bursts.append(arr_dur[i][1])
            #print("BURSTS:",bursts)
            i = i+1
        process = m_proc(words[0],int(words[1]),arrival,bursts)
        #print("BURSTS:",bursts)
        P.append(process)
        del arr_dur
        del arrival
        del bursts

    for i in P:
        print(i.name,i.mem,i.arrival_time,i.burst_duration)
    return P




if __name__=='__main__':

    txt = '''A 28 350/2650
B 50 0/350 400/50
C 20 0/250 300/60'''
    
    #create the processes from the text file        
    


    P = create_processes(txt)
    print("CHECKING THE ARRIVAL AND BURST LISTS OF PROCESSES	")
    for i in P:
        print(i.name,i.arrival_time,i.burst_duration)
    
    fit(100,50,P)



	


					
					
				
	
	
