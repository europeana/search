
with open('dm2e_severity.tidy', 'w') as out:
    with open('dm2e_severity', 'r') as sevs:
        highest_count = 0
        total_count = 0
        for line in sevs:
            (orig, orig_count, ours, our_count, total) = line.strip().split("\t")
            total_count += int(total)
            if(int(orig_count) > 0): out.write(line)
            if(int(orig_count) > highest_count): highest_count = int(orig_count)
        out.write("Highest collision count: " + str(highest_count) + "\tTotal Collisions: " + str(total_count))
