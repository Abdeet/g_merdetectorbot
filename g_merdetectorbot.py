import praw
import os
import re
import hashlib

# FUNCTIONS ALLOWING MANAGEMENT OF POSTS REPLIED TO

def posts_replied_to():
    with open(os.getcwd()+"\posts_replied_to.txt","r") as list_of_posts_replied_to:
        list_of_posts_replied_to = list_of_posts_replied_to.read()
        list_of_posts_replied_to = list_of_posts_replied_to.split(",")
        list_of_posts_replied_to = list(filter(None, list_of_posts_replied_to))
        return list_of_posts_replied_to

def in_posts_replied_to(post_id):
    if post_id in posts_replied_to():
        return True
    else: return False

def add_to_posts_replied_to(post_id):
    list_of_posts_replied_to = posts_replied_to()
    with open(os.getcwd()+"\posts_replied_to.txt","w") as list_of_posts_replied_to_file:       
        list_of_posts_replied_to.append(post_id)
        list_of_posts_replied_to = ",".join(list_of_posts_replied_to)
        list_of_posts_replied_to_file.write(list_of_posts_replied_to)

# FUNCTIONS ALLOWING MANAGEMENT OF COMMENTS REPLIED TO

def comments_replied_to():
    with open(os.getcwd()+"\comments_replied_to.txt","r") as list_of_comments_replied_to:
        list_of_comments_replied_to = list_of_comments_replied_to.read()
        list_of_comments_replied_to = list_of_comments_replied_to.split(",")
        list_of_comments_replied_to = list(filter(None, list_of_comments_replied_to))
        return list_of_comments_replied_to

def in_comments_replied_to(comment_id):
    if comment_id in comments_replied_to():
        return True
    else: return False

def add_to_comments_replied_to(comment_id):
    list_of_comments_replied_to = comments_replied_to()
    with open(os.getcwd()+"\comments_replied_to.txt","w") as list_of_comments_replied_to_file:       
        list_of_comments_replied_to.append(comment_id)
        list_of_comments_replied_to = ",".join(list_of_comments_replied_to)
        list_of_comments_replied_to_file.write(list_of_comments_replied_to)

# FUNCTION TO PULL ALL MENTIONS FROM A COMMENT

def get_mentions(comment_body):
    mentions_in_comment = re.finditer(r'(\s|\A|\/)u\/[a-zA-Z0-9_-]{3,20}(\s|\Z)',comment_body)
    mentions_stripped = []
    for x in mentions_in_comment:
        mentions_stripped.append(x[0].strip().strip("/"))
    return mentions_stripped

# THIS IS THE THING YOU'VE ALL BEEN WAITING FOR... THE G_MER DETECTOR CODE
# THE WORDS HAVE BEEN HASHED SO THAT YOU DON'T HAVE TO READ THE DESPICABLE THINGS THESE G_MERS WRITE 

def get_g_mer_count_for_comment(comment_body):
    g_mer_hashes = ['cec8478d2feedfa7bda5501face1aab64368b9876ea5149ec11b2b9df4a2e568','904294d8c54b1c63e40832fa1d95bcde534b310df6d42882ce4baf28f3e0184a',
    'ab6b786aa204199a39492078eab36895cfa6b650d969c79f85a0055d461a0c52','120f6e5b4ea32f65bda68452fcfaaef06b0136e1d0e4a6f60bc3771fa0936dd6','08a841e996781e9e77d30a4e4420a8f501a280b00624e6d1224bf54aaff73eba']
    g_mer_count = 0
    words = re.finditer(r'[a-zA-Z]+',comment_body.lower())
    words_hashed = [] 
    for x in words:
        words_hashed.append(hashlib.sha256(x[0].strip().encode()).hexdigest())
    for x in words_hashed:
        if x in g_mer_hashes:
            g_mer_count += 1
    return g_mer_count


def compute_g_mer_score(user):
    user = user.strip("u/")
    total_g_mer_count  = 0
    for comment in reddit.redditor(user).comments.new(limit = 100):
        total_g_mer_count += get_g_mer_count_for_comment(comment.body)
    return total_g_mer_count




#START OF CODE

reddit = praw.Reddit('bot1')

for message in reddit.inbox.unread():
    all_mentions = get_mentions(message.body.lower())
    if "u/g_merdetectorbot" in all_mentions:
        all_mentions.pop(all_mentions.index("u/g_merdetectorbot"))
        g_mer_score = 0
        g_mer_name = ""
        if len(all_mentions) == 1:
            g_mer_score = compute_g_mer_score(all_mentions[0])
            g_mer_name = all_mentions[0]
        elif len(all_mentions) == 0:
            parent_author = str(message.parent().author).lower()
            g_mer_score = compute_g_mer_score(parent_author)
            g_mer_name = "u/" + parent_author
        if(parent_author == "g_merdetectorbot"):
            message.reply(f"**u/G_merDetectorBot** \n\n By *u/Abdeet* \n\n ")
        else:
            message.reply(f"**Suspected G\*mer: {g_mer_name}**\n\n  **G\*mer Score: _{g_mer_score}_** \n\n ^Calculated ^using ^user's ^last ^100 ^comments, ^searching ^for [^these ^words](https://www.reddit.com/user/G_merDetectorBot/comments/gowikd/) \n\n ^Send ^a ^private ^message ^to ^suggest ^more ^words ^to ^add. \n\n ^Created ^by ^u/Abdeet ^to ^rid ^the ^world ^of ^the ^evils ^of ^g\*ming.")
        message.mark_read()
