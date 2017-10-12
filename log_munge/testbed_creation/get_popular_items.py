import os

# let's filter for all the queries that have interactions
# from more than ten users
# this will be useful for training the LTR plugin later

top_dir = "query_interactions"
clicks_dir = "min_ten_clicks"
users_dir = "min_ten_users"

for f in os.listdir(os.path.join(top_dir, clicks_dir)):
	with open(os.path.join(top_dir, clicks_dir, f)) as mtc:
		sessions = []
		for l in mtc.readlines():
			if("\t" in l):
				(_, session_id, _, _, _, _) = l.split("\t")
				sessions.append(session_id)
		unique_sessions = set(sessions)
		print(str(len(unique_sessions)))
		if(len(unique_sessions) >= 5):
			os.rename(os.path.join(top_dir, clicks_dir, f), os.path.join(top_dir, users_dir, f))