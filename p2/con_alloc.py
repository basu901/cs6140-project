import queue
import collections as col
from defragmentation import defrag,timeToDefrag

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

    def __init__(self,frames,t_memory,process_list,t_mem_move, method):
		# t_memory = Size of total memory
        self.process_list = process_list 	#Storing the number of processes to be assigned memory				
        self.t_memory = t_memory
        self.frames_line = frames
        self.defrag_time=0  
        self.t_mem_move = t_mem_move 
        if(method == 0):
            self.end_time = self.start_fit(frames, self.check_space)
        if(method == 1):
            self.end_time = self.start_fit(frames, self.next_fit)
        if(method == 2):
            self.end_time = self.start_fit(frames, self.best_fit)
     

    def show_output(self,total_frames,f_per_line,q):
        #Prints the output in the specified format
#        k = 1
#        for i in range(0,len(q)):
#            if i==k*f_per_line:
#               k = k+1
#               print('')
#            
#            print(q[i],end="")
#        print('')
        q = q[f_per_line:len(q) - f_per_line]
        print('=' * f_per_line)
        for start_frame in range(0,total_frames,f_per_line):
            print(q[start_frame:min(start_frame + f_per_line, total_frames)])
        print('=' * f_per_line)
      
	
	
  
    def start_fit(self,frames_per_line, fit_method):					
	
        time = 0
        n = len(self.process_list)
        #print("Length of process_list",n)

        mem = '='*frames_per_line+'.'*self.t_memory+'='*frames_per_line
        #print(mem)

        active_processes=list()			#List of processes that acquired main memory
        ready_processes=list()			#List of processes competing for main memory at time t
        done = list()					#List of processes which have completed all their burst
        last = list()
        next_index = 0
        end_time = 0

        #print("time ",time+self.defrag_time,"ms: Simulator started (Contiguous -- Next-Fit)")
	
		#REMOVE PROCESSES FROM MAIN MEMORY
        while(len(done)!=n):
            i =0 
            while i<len(self.process_list):
                if self.process_list[i].leave==time:
                    #print("time:",time+self.defrag_time," Leaving",self.process_list[i].name)
                    to_remove = self.process_list[i]
                    #if to_remove in last:
                     #   last.remove(to_remove)
                    if self.process_list[i].eject==1:
                        done.append(self.process_list[i])
                        #print(sorted([i.name for i in done]))
                        #self.process_list.pop(i)
                    flag = self.process_list[i].name in mem
                    x=list(mem)
                    for j in range(0,len(x)):
                        if x[j]==to_remove.name:
                           x[j]='.'
                    mem = "".join(x)
                    del x
                    
                    if(flag):    
                        print("time %dms: Process %s removed:" % (time+self.defrag_time, to_remove.name))   
                        self.show_output(self.t_memory,self.frames_line,mem)
                i=i+1

            '''i = 0
            #print([i.name for i in active_processes]) 
            while i<len(active_processes):
                #print("Ative processes")
                #print([i.name for i in active_processes])
                if active_processes[i].leave==time:
                    print("time:",time+self.defrag_time," Leaving",active_processes[i].name)
                    to_remove = active_processes[i]
                    #print("to_remove",to_remove)
                    active_processes.remove(to_remove)
                    x=list(mem)
                    for j in range(0,len(x)):
                        if x[j]==to_remove.name:
                           x[j]='.'
                    mem = "".join(x)
                    del x
                    print("time ",time+self.defrag_time,"ms: Process ",to_remove.name," removed:")
                   
                    self.show_output(self.t_memory,self.frames_line,mem)
                i = i+1''' 
                
	    #CHECK WHICH PROCESS SHOULD ENTER MAIN MEMORY. IF IT's THE LAST BURST MARK FOR EJECTION
            i = 0
            while i<len(self.process_list):
                if(self.process_list[i].eject!=1):
                    if self.process_list[i].arrival_time[0]==time:
                       self.process_list[i].leave = self.process_list[i].arrival_time[0]+self.process_list[i].burst_duration[0]
				#Updating arrival and burst times of the process
                       self.process_list[i].arrival_time.pop(0)
                       self.process_list[i].burst_duration.pop(0)
                       ready_processes.append(self.process_list[i])
                      
                    if (len(self.process_list[i].arrival_time)==0):
                       self.process_list[i].eject=1		#Indicator that process should be shifted to done list
                       
                i = i+1
                #print(i)    
                

		#Sort the processes based on process_id
            #print("EXIT firt while")
            
            
	
            if(ready_processes):
                ready_processes.sort(key=lambda x:x.name)		
                while (ready_processes):
                    c_process = ready_processes.pop(0)

                    print("time %dms: Process %s arrived (requires %d frames)" % (time+self.defrag_time, c_process.name, c_process.mem))
                    search_mem = c_process.mem	#memory requirement of process
                    #print(mem)
                    #first = self.check_space(mem,search_mem,self.t_memory)
			              # TODO 
                    first = fit_method(mem, search_mem, self.t_memory,last,next_index)
                    if first!=-1 and first!=-2:
                        #print(first) # TODO Remove?
                        x = list(mem)
                        j = first
                        while search_mem!=0:
                            x[j] = c_process.name
                            search_mem = search_mem - 1
                            j = j+ 1
                        next_index = j
                        mem = "".join(x)
                        active_processes.append(c_process)
                        if end_time<c_process.leave:
                            end_time = c_process.leave
                        print("time %dms: Placed process %s:" % (time+self.defrag_time, c_process.name))
                        last.append(c_process)
                        del x
                        #print(mem)
                        self.show_output(self.t_memory,self.frames_line,mem)

                    else:
                        if first==-1:
                            print("time %dms: Cannot place process %s -- starting defragmentation" % (time+self.defrag_time, c_process.name))
                            t_df = timeToDefrag(mem,self.t_mem_move)
                            self.defrag_time += t_df
#                            alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
#                            proc = [a for a in alphabet if a in mem]
                            mem, proc = defrag(mem)
                            print("time %dms: Defragmentation complete (moved %d frames: %s)" % (time+self.defrag_time, t_df/self.t_mem_move, ', '.join(proc)))
                            
                            second = self.check_space(mem, search_mem, self.t_memory,last,next_index)

                        else:
                            print("time %dms: Cannot place process %s -- skipped!" % (time+self.defrag_time, c_process.name))
                            continue

                        if second!=-1:
                            j = second
                            x = list(mem)
                            while search_mem!=0:
                                x[j] = c_process.name
                                search_mem -= 1
                                j = j+1
                            next_index = j
                            mem = "".join(x)
                            if end_time<c_process.leave:
                                end_time = c_process.leave
                            active_processes.append(c_process)
                            last.append(c_process)
                            print("time %dms: Placed process %s:" % (time+self.defrag_time, c_process.name))
                            del x

                            self.show_output(self.t_memory,self.frames_line,mem)

                        #else:
                         #   print("time ",time+self.defrag_time,"ms : Cannot place process ",c_process.name," -- skipped!")
                

            time = time+1
        #print("time ",time+self.defrag_time-1,"ms: Simulator ended (Contiguous -- Next Fit)")
        return end_time+self.defrag_time

    #THIS METHOD SHOULD BE MODIFIED FOR DIFFERENT PLACEMENT ALGOS
    def check_space(self,m,space,total,dummy,dummy2):
        #-1 is after defragment, -2 is no need to defragment as memory was empty
        count = 0
        for c in m:
            if c=='.':
                count = count+1
        #print("Space left:",count)
        if count<space:
            return -2
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
                else:
                    return -1
           
    # Returns the index where a block of memory of size space
    # can be inserted into m, and returns -1 if there isn't space
    # Returns -2 if impossible to fit, even if defragmented
    def best_fit(self, m, space, total,dummy,dummy2):
        if (m.count('.') < space): return -2

        smallest = inf # Size of smallest free space (>= space)
        idx = -1       # Index of above

        i = m.find('.')            # Find the first free space
        while(i < len(m)):
            tmpLen = 0

            while(i < len(m) and m[i] == '.'):    # Count the size of the free space
                tmpLen += 1        # Track the length
                i += 1

            # If this space is smaller than the current smallest,
            # but still bigger than the required space, its the
            # new smallest
            if(tmpLen < smallest and tmpLen >= space):
                idx = i - tmpLen
                smallest = tmpLen

            while(i < len(m) and m[i] != '.'): # Find the next free space
                i += 1

        return idx

    def next_fit(self,m,space,total,last,n_index):
        #print("In next fit!!!!!!!!!!!")
        #print (n_index)
        count = 0
        passed = 0
        for c in m:
            if c=='.':
                count = count+1
        #print("Space left:",count)
        if count<space:
            return -2
        
        if count==total:
            if n_index == 0:
                first = m.find('.')
            else:
                count = 0
                i = n_index
                while m[i]!='=':
                    #print("HERE")
                    count = count+1
                    i = i+1
                if space <= count:
                    first = n_index
                else:
                    first = m.find('.',0)
                    #print("HERE")           
            return first

        letter = last[-1].name
        #print("Letter is :",letter)
        start = m.find(letter)
        if start==-1:
            i =n_index
            start = n_index
        else:
            i = start
        while m[i]!='.':
            if i ==(len(m)-1):
                i= 0
                passed = 1
                break
            i = i+1
            #print(i,len(m))
        i = m.find('.',i)
        if i==-1:
            return -1
        else:
            first = i
            #print("HERE",first)
        #print("Check i value",i)
        while(True):
            if passed:
                #print("HERE2",i)
                while i<start:
                    #print("HERE3")
                    if i == -1:
                        return -1
                    while m[i]=='.':
                        i = i+1
                    if space<=(i-first):
                        #print("HERE4")
                        return first
                    else:
                        i = m.find('.',i)
                        first = i
                return -1

            else:
                while m[i]=='.':
                    i = i+1
                if space<=(i-first):
                    return first
                if m[i]=='=':
                    passed = 1
                    i = m.find('.',0)
                    first=i
                else:
                    i = m.find('.',i)
                    first = i
                if i == -1:
                    passed = 1
                    i = m.find('.',0)
                    first=i
               

def get_lines(txt):
    lines = txt.split('\n')
    new_lines = []
    for line in lines:
        if(line.rstrip()):
            new_lines.append(line)
    return new_lines
            
def create_processes(txt):
    lines = get_lines(txt)
   
    P = []
    for line in lines:
        bursts = list()
        arrival = list()
        #print("line is",line)
        words = line.split()
        if(words[0][0] == '#'):
           continue
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

    #for i in P:
    #    print(i.name,i.mem,i.arrival_time,i.burst_duration)
    return P

def contiguous_memory_alloc(txt, num_frames, mem_size, t_memmove):

    #create the processes from the text file        
    
#    print("CHECKING THE ARRIVAL AND BURST LISTS OF PROCESSES	")
#    for i in P:
#        print(i.name,i.arrival_time,i.burst_duration)
    print("time 0ms: Simulator started (Contiguous -- First-Fit)")
    P = create_processes(txt)
    memory = fit(num_frames, mem_size, P, t_memmove, 0)
    print("time %dms: Simulator ended (Contiguous -- First-Fit)\n" % memory.end_time)
    
    print("time 0ms: Simulator started (Contiguous -- Next-Fit)")
    P = create_processes(txt)
    memory = fit(num_frames, mem_size, P, t_memmove, 1)
    print("time %dms: Simulator ended (Contiguous -- Next-Fit)\n" % memory.end_time)
    
    print("time 0ms: Simulator started (Contiguous -- Best-Fit)")
    P = create_processes(txt)
    memory = fit(num_frames, mem_size, P, t_memmove, 2)
    print("time %dms: Simulator ended (Contiguous -- Best-Fit)\n" % memory.end_time)
