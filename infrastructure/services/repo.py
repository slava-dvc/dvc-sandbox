import git

repo = git.Repo('../')  # Initialize the repo object. Replace '.' with your repo path if needed
head_commit = repo.head.commit
sha = head_commit.hexsha
short_sha = head_commit.hexsha[:7]
