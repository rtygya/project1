# Reety Gyawali 1001803756
# Rakshav Patel – 10011941754

import copy
import os

# Get input file and store it in a variable
input_file = "Input 1.txt"
# input_file = input("Enter input file name: ")

output_file = "Output " + input_file[6] + ".txt"

# Function to write text to output file
def write_file(file, text):
    with open(file, 'a') as output:
        if text:
            output.write(text)
        

#array that will hold diffrent state of transaction
input_operation = []
A = "active"
B = "abort"
C = "committed"
E = "abort"
W = "Waiting"

#array that will hold transaction table items 
transTableItem = []

#array to hold lock item
locTableItem = []

#will hold write and read transaction
RW_transaction = []
W = "write"
R = "Read"

# this will hav waiting transaction values
W_Transaction = []

# Variable to track timestamp for transaction
timestamp = 1

# lock class this will hold diffrent elements of the lock tabel
class lock_table():
    def __init__(self, lock_sate, lock_item, t_id):
        self.lock_state = lock_sate # if its active or locked
        self.lock_item = lock_item  # if the item is already locked
        self.RW_transaction = []    # this is read or write transaction
        self.lockHoldBy = []        # holding lock for read or write
        self.lockHoldBy.append(t_id)
    def ChangeLock_State(self, lock_state):
        self.lock_state = lock_state
    def add_locking_trxn(self, t_id):
        self.lockHoldBy.append(t_id)
    def waiting_transaction(self, t_id):
        self.RW_transaction.append(t_id) # waitinmg for items to be unlocked 
    
# Readlock function
def readlock(i, X):
    item = find_lock_item(X)
    if not item:
        locTableItem.append(lock_table("read-locked", X, i))
        modified_line = ' ' + locTableItem[-1].lock_item + ' is read-locked by' + ' T' + str(i) + '. \n'
        write_file(output_file, modified_line)
        return 1
    elif item.lock_state == "read-locked" and i in item.lockHoldBy:
        modified_line = ' T' + i + ' already has write lock on ' + X + '. \n'
        write_file(output_file, modified_line)
        return 1
    elif item.lock_state == "read-locked" and i not in item.lockHoldBy:
        item.add_locking_trxn(i)
        modified_line = ' ' + item.lock_item + ' is read-locked by' + ' T' + str(i) + '. \n'
        write_file(output_file, modified_line)
        return 1
    elif item.lock_state == "write-locked" and item.lockHoldBy[0] == i:
        item.lockHoldBy.clear()
        item.add_locking_trxn(i)
        item.ChangeLock_State("read-locked")
        modified_line = ' ' + item.lock_item + ' is read-locked by' + ' T' + str(i) + '. \n'
        write_file(output_file, modified_line)
        return 1
    elif item.lock_state == "write-locked" and item.lockHoldBy[0] != i:  
        find_transaction(i).wait_die(find_transaction(item.lockHoldBy[0]), item)
        return 0
        
# Writelock function
def writelock(i, X):
    item = find_lock_item(X)
    if not item:
        locTableItem.append(lock_table("write-locked", X, i))
        modified_line = ' T' + i + ' write-locked. \n'
        write_file(output_file, modified_line) 
        return 1
    elif item.lock_state == "write-locked" and item.lockHoldBy[0] == i:
        modified_line = ' T' + i + ' already has write lock on ' + X + "\n"
        write_file(output_file, modified_line) 
        return 1
    elif item.lock_state == "read-locked" and len(item.lockHoldBy) == 1 and item.lockHoldBy[0] == i:
        item.lockHoldBy.clear()
        item.add_locking_trxn(i)
        item.ChangeLock_State("write-locked")
        modified_line = ' read lock on ' + item.lock_item + ' by T' + i + ' is upgraded to write lock. \n'
        write_file(output_file, modified_line) 
        return 1
    elif item.lock_state == "read-locked" and len(item.lockHoldBy) >= 1:
        for tid in item.lockHoldBy:
            if tid != i:
                find_transaction(i).wait_die(find_transaction(tid), item)
    elif item.lock_state == "write-locked" and item.lockHoldBy[0] != i:
        find_transaction(i).wait_die(find_transaction(item.lockHoldBy[-1]), item)
        return 0

# Unlock function         
def unlock(item):
    if item in locTableItem:
        wt = item.RW_transaction
        locTableItem.remove(item)
        for transaction in wt:
            if transaction:
                transaction.state = "active"
                resume(transaction)

# Resume function
def resume(transaction):
        # process all blocked operations
        for op in transaction.blocked_operations:
            write_file(output_file, op + ' T' + op[1] + ' is released from operation list.')
            process_operation(op, timestamp)
            
# Transaction class
class Transaction:
    def __init__(self, id, ts, state):
        self.id = id                    # transaction id
        self.ts = ts                    # timestamp (integer)
        self.state = state              # "active", "blocked", "committed", "aborted"
        self.locked_items = []          # items locked by this transaction
        self.blocked_operations = []    # if transaction is blocked, further operations from input file go here to be resumed later
        
    def lock_item(self, item):
        self.locked_items.append(item)
            
    def add_blocked_op(self, op):
        self.blocked_operations.append(op)
        if (op[0] == 'r'):
            item = op[3]
            write_file(output_file, ' T' + self.id + ' reading ' + item + ' is added to operation list. \n')
        elif (op[0] == 'w'):
            item = op[3]
            write_file(output_file, ' T' + self.id + ' writing ' + item + ' is added to operation list. \n')
        elif (op[0] == 'e'):
            write_file(output_file, ' Committing T' + self.id + ' is added to operation list. \n')
        else:
            write_file(output_file, 'Operation added to list. ')
    
    def read(self, item):
        if readlock(self.id, item):
            if find_lock_item(item) not in self.locked_items:
                self.lock_item(find_lock_item(item))
        
    def write(self, item):
        if writelock(self.id, item):
            if find_lock_item(item) not in self.locked_items:
                self.lock_item(find_lock_item(item))
                    
    def commit(self): 
        for item in self.locked_items:
            unlock(item)    
        self.state = C  # state is now committed
        modified_line = ' T' + self.id + ' is ' + self.state + '. \n'
        write_file(output_file, modified_line)
        
                
    def abort(self):
        for item in self.locked_items:
            unlock(item)
        self.state = "aborted"  # state is now aborted
        
    def wait_die(self, t2, item):
        # this transaction currently requests an item locked by t2
        if self.ts < t2.ts:
            modified_line = ' T' + self.id + ' is blocked/waiting due to wait-die. \n'
            write_file(output_file, modified_line)
            self.state = "blocked"  # block if older
            item.waiting_transaction(find_transaction(self.id))
        else:
            modified_line = ' T' + self.id + ' is aborted due to wait-die. \n'
            write_file(output_file, modified_line)
            self.abort()            # abort if younger
            
        
# Begin function
def begin(ts, t_id):
    transTableItem.append(Transaction(t_id, ts, A)) 
    modified_line = ' T' + t_id + ' begins. Id=' + transTableItem[-1].id + '. TS=' + str(transTableItem[-1].ts) + '. state=' + A + '. \n'
    write_file(output_file, modified_line)        

    
# Function to easily find transaction with specific id
def find_transaction(target_id):
    for t in transTableItem:
        if t.id == target_id:
            return t   # Return transaction object
    return None 

# Function to easily find item with name
def find_lock_item(name):
    for l in locTableItem:
        if l.lock_item == name:
            return l   # Return lock item
    return None  

        
# Process each input sequence              
def process_operation(line, timestamp):
    # Store transaction ID and operation in variables
    t_id = line[1]
    op = line[0]
    transaction = find_transaction(t_id)
    modified_line = '\n'
    if transaction:
        if transaction.state == "aborted":  # If transaction is not aborted
            modified_line = ' T' + t_id + ' is already aborted. \n'
            write_file(output_file, modified_line)
        else:
            if (op == 'r'):
            # Transaction reads item 
                item = line[3]
                if transaction.state == "blocked":
                    # Blocked transaction, add operation to waiting list      
                    transaction.add_blocked_op(line.strip())
                else:                    
                    # aquire a read lock for this item by this transaction
                    transaction.read(item)
                    #modified_line = ' T' + t_id + ' reads item ' + item  + '\n'
            
            elif (op == 'w'):
            # Transaction writes item 
                item = line[3]
                if transaction.state == "blocked":
                    # Blocked transaction, add operation to waiting list      
                    transaction.add_blocked_op(line.strip())
                else:                    
                    # aquire a write lock for this item by this transaction
                    transaction.write(item)
                    #modified_line = ' T' + t_id + ' writes item ' + item  + '\n'  
            
            elif (op == 'e'):
            # Commit transaction 
                if transaction.state == "blocked":
                    # Blocked transaction, add operation to waiting list      
                    transaction.add_blocked_op(line.strip())
                else:           
                    transaction.commit()        
    elif (line[0] == 'b'):    
        # Begin new transaction
        begin(timestamp, t_id)    

# Reading and parsing each line in file 
try:
    with open(input_file, 'r') as input:
        lines = input.readlines()
        
    open(output_file, "w")
            
    for line in lines:
        write_file(output_file, line.strip())
        process_operation(line.strip(), timestamp)
        if line[0] == 'b':
            timestamp += 1
        
    # Write the final states of each transaction at the very end
    final_line = "\nFinal state:\n"
    write_file(output_file, final_line)
    for tr in transTableItem:
        final_line = 'T' + tr.id + ': ' + tr.state + '. '
        write_file(output_file, final_line)
    write_file(output_file, '\n')
        
    print("Output file created:", output_file)
except FileNotFoundError:
        print("Error: Input file not found.")
