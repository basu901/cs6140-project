# CS 6140 - Computer Operating Systems
# Project 2
# 
# Shaunak Basu     (basus6)
# Michael Giancola (giancm)
# Farhad  Mohsin   (mohsif)

# no need to implement page table to exact specs
#   take liberty, maybe just use a dict
#   page_no:(memory,offset)

# <num_frames> <mem_size>
class memory(object):
    def __init__(self, num_frames, mem_size):
        self.mem_size = mem_size
        self.state = '.' * mem_size
        self.num_frames = num_frames
        self.free = mem_size
        self.end_time = -1
    
    def find_free_mem(self):
        # find first free memory
        start = self.state.find('.')
        # find end of that memory stretch
        end_list = [i for i in range(start,len(self.state)) if self.state[i] != '.']
        if(len(end_list) == 0):
            end = len(self.state)
        else:
            end = end_list[0]
        return start,end
    
    def edit_mem(self, p_name, start, end):
        x = self.state
        self.state = x[:start] + p_name*(end - start) + x[end:]
    
    # try to insert arriving process into memory
    # return True if success, otherwise False    
    def insert_process(self, p):
        if(p.memory > self.free):
            print("time %dms: Cannot place process %s -- skipped!"%(p.current_proc_start(), p.name))
            self.end_time = p.current_proc_start()
            p.cur_burst += 1
            return False
        
        # keep inserting process memory in non-contagious spaces as long 
        #   as there is memory left to insert
        # also add to the page table
        # page table structure: page_no:(frame_loc, offset)
        
        print("time %dms: Placed process %s:"%(p.current_proc_start(), p.name))
        
        mem_left = p.memory
        page_cnt = 0
        while(mem_left > 0):
            start,end = self.find_free_mem()
            stretch = end - start
            if(stretch > mem_left):
                self.edit_mem(p.name, start, start + mem_left)
                mem_left = 0
                p.page_table.append({page_cnt: (start, mem_left)})
            else:
                self.edit_mem(p.name, start, end)
                mem_left -= stretch
                p.page_table.append({page_cnt: (start, stretch)})
            page_cnt += 1
        
        p.ongoing = True
        self.free -= p.memory
        self.print_()
        return True
    
    # remove a process from memory once a burst is done
    #   also increment process burst_no and clear page_table
    def remove_process(self, p):
        if(p.ongoing):
            p.ongoing = False
            print("time %dms: Process %s removed:"%(p.current_proc_end(), p.name))
            self.end_time = p.current_proc_end()
            p.cur_burst += 1
            p.page_table = []   
            self.state = self.state.replace(p.name, '.')
            self.print_()
            self.free += p.memory
        
    def print_(self):
        print('=' * self.num_frames)
        for start_frame in range(0,self.mem_size,self.num_frames):
            print(self.state[start_frame:min(start_frame + self.num_frames, self.mem_size)])
        print('=' * self.num_frames)
        
class process(object):
    def __init__(self, name, memory, bursts):
        self.name = name
        self.memory = memory
        # bursts are a 2-lenght list, indicating the start time and burst_lenght
        self.bursts = bursts
        self.cur_burst = 0
        # page_table will be a list of dicts, only necessary for non-contigouos memory
        # dict structure would be of type {page_no:(frame_loc, offset)}
        self.page_table = []
        self.ongoing = False
    
    def current_proc_start(self):
        return self.bursts[self.cur_burst][0]
    
    def current_proc_end(self):
        return self.bursts[self.cur_burst][0] + self.bursts[self.cur_burst][1]
    
    def print_(self):
        print("Process %s: memory = %d"%(self.name, self.memory))
        print(self.bursts)
    
class PQueue(object): 
    def __init__(self): 
        self.queue = [] 
  
    def __str__(self): 
        return ' '.join([str(i) for i in self.queue]) 
  
    # for inserting an element in the queue
    # data is of type (time, process, 'start'/'end')
    def insert(self, data): 
        if(len(self.queue) == 0):
            self.queue.append(data)
        else:
            flag = False
            for i , q_dat in enumerate(self.queue):
                # place burst in appropriate time
                if(data[0] < q_dat[0]):
                    self.queue.insert(i, data)
                    flag = True
                    break
                elif(data[0] == q_dat[0]):
                    # for tasks at same time, 'end' takes precedent 
                    if(data[2] == 'end' and q_dat[2] == 'start'):
                        self.queue.insert(i, data)
                        flag = True
                        break
                    else:
                        if(data[1].name < q_dat[1].name):
                            self.queue.insert(i, data)
                            flag = True
                            break
            if(not(flag)):
                self.queue.append(data)
    
    # return the length of the queue
    def length(self):
        return len(self.queue)
        
    # for popping an element based on Priority 
    def pop(self): 
        item = self.queue.pop(0)
        return item
    
    def print_(self):
        for q_dat in self.queue:
            print(q_dat[0],q_dat[1].name,q_dat[2])
            
# gets rid of blank lines (if any)            
def get_lines(txt):
    lines = txt.split('\n')
    new_lines = []
    for line in lines:
        if(line.rstrip()):
            new_lines.append(line)
    return new_lines
            
def create_processes(txt):
#    lines = txt.split('\n')
    lines = get_lines(txt)
    P = []
    for line in lines:
        words = line.split()
        if(words[0][0] == '#'):
           continue
        bursts = []
        for i in range(2,len(words)):
            bursts.append([int(x) for x in words[i].split('/')])
        new_p = process(words[0], int(words[1]), bursts)
        P.append(new_p)
    return P
        
def non_contiguous_alloc(args):
    
    # Sample test case
    # Will change this part to work with argvs
    M = memory(args[0], args[1])
    txt = args[2]
    
    print('time 0ms: Simulator started (Non-Contiguous)')
    #create the processes from the text file        
    P = create_processes(txt)
    
    #add all the times in a priority queue
    time_queue = PQueue()
    for p_ in P:
        for burst in p_.bursts:
            # data is of type (time, process_name, 'start'/'end')
            data = (burst[0], p_, 'start')
            time_queue.insert(data)
            data = (burst[0] + burst[1], p_, 'end')
            time_queue.insert(data)
    
    #time_queue.print_()
    
    while (time_queue.length() > 0):
        # event is of type(time, process, start/end)
        event = time_queue.pop()
        if(event[2] == 'start'):
            print("time %dms: Process %s arrived (requires %d frames)"%(event[0], event[1].name, event[1].memory))
            M.insert_process(event[1])
        elif(event[2] == 'end'):
            M.remove_process(event[1])
#        if(time_queue.length() == 0):
#            end_time = event[0]
    
    end_time = M.end_time
    print('time %dms: Simulator ended (Non-Contiguous)'%end_time)
    
    return P