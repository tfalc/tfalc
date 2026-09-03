import re

def commit_callback(commit):
    # set author and committer to Thiago
    name = "Thiago Falc\xc3\xa3o da Silva"
    email = "thiago.falcao86@gmail.com"
    commit.author_name = name.encode('utf-8')
    commit.author_email = email.encode('utf-8')
    commit.committer_name = commit.author_name
    commit.committer_email = commit.author_email
    # remove Co-authored-by trailers (case-insensitive)
    commit.message = re.sub(b'(?im)^co-authored-by:.*\n?', b'', commit.message)
