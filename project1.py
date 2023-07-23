# Reety Gyawali 1001803756
# Rakshav Patel – 10011941754

# Get input file and store it in a variable
input_file = "Input 2.txt"
# input_file = input("Enter input file name: ")

output_file = "Output " + input_file[6] + ".txt"

#array that will hold diffrent state of transaction
input_operation = []
A = "active"
B = "abort"
C = "committed"
E = "abort"

#array that will hold transaction table items 
transTableItem = []

#array to hold lock item
locTableItem = []

#will hold write and read transaction
RW_transaction = []
W = "write"
R = "Read"

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
    def lockHoldBy(self, t_id):
        self.lockHoldBy.append(t_id)
    def waiting_transaction(self, t_id):
        self.RW_transaction.append(t_id) # waitinmg for items to be unlocked
        
# Variable to track timestamp for transaction
timestamp = 1

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
                    
    def commit(self): 
        for i in self.locked_items:     # unlock all items locked by this transaction
            locTableItem.unlock(i)      
        self.state = C  # state is now committed
                
    def abort(self):
        for i in self.locked_items:     # unlock all items locked by this transaction
            locTableItem.unlock(i)      
        self.state = "aborted"  # state is now aborted
        
    def block(self):
        self.state = "blocked"
        
# Wait-die function
def wait_die(t1, t2):
    # t1 currently requests an item locked by t2
    if t1.ts < t2.ts:
        t1.block()  # block if t1 older
    else:
        t1.abort()  # abort if t1 younger
    
# Function to easily find transaction with specific id
def find_transaction(target_id):
    for t in transTableItem:
        if t.id == target_id:
            return t   # Return transaction object
    return None  

# Reading and parsing each line in file 
try:
    with open(input_file, 'r') as input:
        lines = input.readlines()

    with open(output_file, 'w') as output:
        for line in lines:
            # Store transaction ID and operation in variables
            t_id = line[1]
            op = line[0]
            transaction = find_transaction(t_id)
            
            if transaction:
                if not transaction.state == "aborted":  # Process operations only if transaction is not aborted
                    if transaction.state == "blocked":
                        # Blocked transaction, add operation to waiting list      
                        transaction.add_blocked_op(op)  
                    elif (op == 'r'):
                        # Transaction readlocks item 
                        item = line[3]
                        modified_line = line.strip() + ' T' + t_id + ' reads item ' + item  + '\n'
                    elif (op == 'w'):
                        # Transaction writelocks item 
                        item = line[3]
                        modified_line = line.strip() + ' T' + t_id + ' writes item ' + item  + '\n'
                    elif (op == 'e'):
                        # Commit transaction 
                        transaction.commit()
                        modified_line = line.strip() + ' T' + t_id + ' is ' + transaction.state + '\n'
            elif (op == 'b'):
                # Begin transaction
                transTableItem.append(Transaction(t_id, timestamp, A)) 
                modified_line = line.strip() + ' T' + t_id + ' begins. TS=' + str(timestamp) + '. Id=' + t_id + '. state=' + A + '.\n'
                timestamp += 1
            
            output.write(modified_line)
        
        # Write the final states of each transaction at the very end
        final_line = "Final state:\n"
        output.write(final_line)
        for tr in transTableItem:
            final_line = 'T' + tr.id + ': ' + tr.state + '. '
            output.write(final_line)
        output.write('\n')
        
    print("Output file created:", output_file)
except FileNotFoundError:
        print("Error: Input file not found.")
