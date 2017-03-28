import os

idir = "fields_used"
odir = "facet_comparison"
cwd = os.getcwd()

with open('proposed_fields.txt') as prop:
    proposed_fields = [line.strip() for line in prop.readlines() if line.strip != ""]

for f in os.listdir(os.path.join(cwd, idir)):
    fieldcounts = {}
    with open(os.path.join(cwd, idir, f)) as infile:
        for line in infile.readlines():
            (fieldname, sourcefields, count) = line.split("\t")
            sourcefields = sourcefields.replace(fieldname + ".*", fieldname)
            if("--" in sourcefields):
                relfields = [fieldname]
            else:
                relfields = sourcefields.split(",")
            relfields = [r.strip() for r in relfields if r not in proposed_fields]
            for r in relfields:
                try:
                    fieldcounts[r] += int(count)
                except KeyError:
                    fieldcounts[r] = int(count)
    newfile = "filtered_" + f
    with open(os.path.join(cwd, odir, newfile), 'w') as outfile:
        for r in sorted(fieldcounts, key=fieldcounts.get, reverse=True):
            msg = r + "\t" + str(fieldcounts[r]) + "\n"
            outfile.write(msg)
