"""
References -
https://www.programiz.com/python-programming/csv
https://www.programiz.com/python-programming/writing-csv-files
"""
import os
import sys
import subprocess
import math
import csv

mountFolder = "/media/ubuntu"
#path = "/media/ubuntu/ntfs"
#partition_no = 4   # For debug only


# Mount location of each partition corresponding to the partitions in 'partitions[]'
partitionLocs = ["ntfs", "ext2", "ext4", "FAT32", "xfs"]
TESTS = [150, 15, 15, 10, 30]


"""
Usage: python3 run_test.py <file_system_name>
File Systems: ntfs, ext2, ext4, FAT32, xfs
"""

# Index of provided FS name in partitionLocs
partition_no = partitionLocs.index(sys.argv[1])

#for partition_no in range(len(partitionLocs)):

# RUN TESTS[partition_no] FOR EACH FILE SYSTEM
print("----- RUNNING dd ON " + partitionLocs[partition_no] + " -----")

# Mount location
path = mountFolder + "/" + partitionLocs[partition_no]

# Recorded times for read and write operations
writeTimes = []
readTimes = []

# dd commands for read and write operations
cmdWrite = ['sudo', 'dd', 'if=/dev/urandom', 'of=' + path + '/test_out', 'bs=1M' ,'count=10', 'oflag=nocache', 'iflag=nocache']
cmdRead = ['sudo', 'dd', 'if=' + path + '/test_out', 'of=/dev/null', 'bs=1M' ,'count=10', 'oflag=nocache', 'iflag=nocache']

# Writing to and reading from mount location
for i in range(TESTS[partition_no]):
    # Write to File System
    process = subprocess.Popen(cmdWrite, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    output = err.decode("utf-8").split()

    writeTimes.append(float(output[13]))

    # Read from File System
    process = subprocess.Popen(cmdRead, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err =process.communicate()
    output = err.decode("utf-8").split()

    readTimes.append(float(output[13]))
    
    # Delete file from mount location
    os.system("sudo rm " + path + "/test_out")

print("Calculating Write parameters...")

# Calculating Standard error for write times:
totalWrite = sum(writeTimes)
meanWrite = totalWrite / TESTS[partition_no]

print("Mean of write times = ")
print(meanWrite)

# Calculating sum of (deviations)^2
sumSqDevWrite = 0
for i in range(TESTS[partition_no]):
    sumSqDevWrite = sumSqDevWrite + ((meanWrite - writeTimes[i]) ** 2)

# Standard Deviation
stdDevWrite = math.sqrt(sumSqDevWrite / (TESTS[partition_no] - 1))
# Standard Error
stdErrWrite = stdDevWrite / math.sqrt(TESTS[partition_no])

print("Standard Error for write operation = " + str(stdErrWrite) + " -> " + str((stdErrWrite / meanWrite) * 100) + " %")
print("")

print("Calculating Read parameters...")

# Calculating Standard error for read times:
totalRead = sum(readTimes)
meanRead = totalRead / TESTS[partition_no]

print("Mean of read times = ")
print(meanRead)

# Calculating sum of (deviations)^2
sumSqDevRead = 0
for i in range(TESTS[partition_no]):
    sumSqDevRead = sumSqDevRead + ((meanRead - readTimes[i]) ** 2)
# Standard Deviation
stdDevRead = math.sqrt(sumSqDevRead / (TESTS[partition_no] - 1))
# Standard Error
stdErrRead = stdDevRead / math.sqrt(TESTS[partition_no])

print("Standard Error for read operation = " + str(stdErrRead) + " -> " + str((stdErrRead / meanRead) * 100) + " %")
print("")
print("Writing data to ntfs_data.csv")

with open(partitionLocs[partition_no] + '_data.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Test #', 'Write Times', 'Read Times'])
    for i in range(TESTS[partition_no]):
        writer.writerow([i, writeTimes[i], readTimes[i]])
    writer.writerow(['', 'Avg = ' + str(meanWrite), 'Avg = ' + str(meanRead)])
    writer.writerow(['', 'stderr = ' + str(stdErrWrite), 'stderr = ' + str(stdDevRead)])
    writer.writerow(['', '       = ' + str((stdErrWrite / meanWrite) * 100) + " %", '       = ' + str((stdErrRead / meanRead) * 100) + " %"])
