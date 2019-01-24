# Requirements

1. Retrieve item identifier and search terms from a record view (stored in a regularly-formatted text file)
2. Apply these search terms to the current portal
3. Loop through results until item URL found. Store identifier, position 
4. Repeat steps 2-3 on the test portal (through BM25f handler)
5. Calculate nDCG on legacy, portal, and test sites

