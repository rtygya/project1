# Reety Gyawali 1001803756
# Rakshav Patel – 10011941754

# Get input file and store it in a variable
input_file = "Input 1.txt"
# input_file = input("Enter input file name: ")

output_file = "Output " + input_file[6] + ".txt"

# Reading and parsing each line in file 
try:
    with open(input_file, 'r') as input:
        lines = input.readlines()

    with open(output_file, 'w') as output:
        for line in lines:
            # Store transaction ID in variable
            t_id = line[1]
    
            if (line[0] == 'b'):
                # Begin transaction   
                modified_line = line.strip() + ' T' + t_id + ' begins.\n'
            elif (line[0] == 'e'):
                # Commit transaction 
                modified_line = line.strip() + ' T' + t_id + ' is committed.\n'
            elif (line[0] == 'r'):
                # Transaction readlocks item 
                item = line[3]
                modified_line = line.strip() + ' T' + t_id + ' reads item ' + item  + '\n'
            elif (line[0] == 'w'):
                # Transaction writelocks item 
                item = line[3]
                modified_line = line.strip() + ' T' + t_id + ' writes item ' + item  + '\n'
            
            output.write(modified_line)

    print("Output file created:", output_file)
except FileNotFoundError:
        print("Error: Input file not found.")


