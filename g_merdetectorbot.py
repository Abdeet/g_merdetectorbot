import praw
import os
import re
import hashlib
import collections

# FUNCTIONS ALLOWING MANAGEMENT OF POSTS REPLIED TO

def posts_replied_to():
    with open(os.getcwd()+"/posts_replied_to.txt","r") as list_of_posts_replied_to:
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
    with open(os.getcwd()+"/posts_replied_to.txt","w") as list_of_posts_replied_to_file:       
        list_of_posts_replied_to.append(post_id)
        list_of_posts_replied_to = ",".join(list_of_posts_replied_to)
        list_of_posts_replied_to_file.write(list_of_posts_replied_to)

# FUNCTIONS ALLOWING MANAGEMENT OF COMMENTS REPLIED TO

def comments_replied_to():
    with open(os.getcwd()+"/comments_replied_to.txt","r") as list_of_comments_replied_to:
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
    with open(os.getcwd()+"/comments_replied_to.txt","w") as list_of_comments_replied_to_file:       
        list_of_comments_replied_to.append(comment_id)
        list_of_comments_replied_to = ",".join(list_of_comments_replied_to)
        list_of_comments_replied_to_file.write(list_of_comments_replied_to)

# FUNCTION TO PULL ALL MENTIONS FROM A COMMENT

def get_mentions(comment_body):
    #Uses RegEx to get users in the u/user format. Works with /u/format as well.
    mentions_in_comment = re.finditer(r'(\s|\A|\/)u\/[a-zA-Z0-9_-]{3,20}',comment_body)
    mentions_stripped = []
    for x in mentions_in_comment:
        #Cleans up mention to make them uniform
        mentions_stripped.append(x[0].strip().strip("/"))
    return mentions_stripped

# THIS IS THE THING YOU'VE ALL BEEN WAITING FOR... THE G_MER DETECTOR CODE
# THE WORDS HAVE BEEN HASHED SO THAT YOU DON'T HAVE TO READ THE DESPICABLE THINGS THESE G_MERS WRITE 

def get_g_mer_hashes():
    with open(os.getcwd()+"/g_mer_hashes.txt","r+") as g_mer_hashes:
        return g_mer_hashes.read().split(",")

def add_to_g_mer_hashes(word):
    #This is just for fun. I made the whole comparison system run on sha256 hashes. This is the way I hash the words
    word_hashed = str(hashlib.sha256(word.lower().encode()).hexdigest())
    print(word_hashed)
    g_mer_hashes = get_g_mer_hashes()
    g_mer_hashes.append(word_hashed)
    g_mer_hashes = ",".join(g_mer_hashes)
    with open(os.getcwd() + "/g_mer_hashes.txt", "w+") as g_mer_hashes_file:
        g_mer_hashes_file.write(g_mer_hashes)

def get_g_mer_count_for_comment(comment_body):
    g_mer_hashes = get_g_mer_hashes()
    g_mer_count = 0
    #This RegEx gets all the words from the comment. The downside is it prevents me from searching for multi word phrases. I could modify it to work for that but I don't really want to.
    words = re.finditer(r'[a-zA-Z]+',comment_body.lower())
    words_list = []
    words_hashed = [] 
    g_mer_words_censored = []
    for x in words:
        #This just takes every single word in the comment and converts it to a hash
        words_list.append(x)
        words_hashed.append(str(hashlib.sha256(x[0].strip().encode()).hexdigest()))
    for x in words_hashed:
        if x in g_mer_hashes:
            g_mer_count += 1
            word = words_list[words_hashed.index(x)]
            g_mer_words_censored.append(censor_g_mer_words(word))
    return g_mer_count, g_mer_words_censored

#New functionality to list g*mer words used
def censor_g_mer_words(word):
    return str(word[0][:1] + "*" + word[0][2:])

#Previous versions of the code had another function that colculated the g_mer_count, but this method only requires looping through the comments once, which is quicker.
#This basically gets the total karma of a user on a subreddit and divides by the number of comments made. It doesn't round right now because I think it shows a fuller picture like this.
def test_g_mer(user, subreddit):
    user = user.strip("u/")
    total_g_mer_count = 0
    total_karma_in_comments_on_subreddit = 0
    comments_on_subreddit = 0
    g_mer_count_for_comment = 0
    censored_list_for_comment = []
    censored_list = []
    for comment in reddit.redditor(user).comments.new(limit = 100):
        g_mer_count_for_comment, censored_list_for_comment = get_g_mer_count_for_comment(comment.body)
        for x in censored_list_for_comment:
            censored_list.append(x)
        if comment.subreddit == subreddit:
            comments_on_subreddit += 1
            total_karma_in_comments_on_subreddit += comment.score
        print(g_mer_count_for_comment)
        total_g_mer_count += g_mer_count_for_comment
    frequency_of_g_mer_words = collections.Counter(censored_list)
    if comments_on_subreddit > 0:avg_comment_score_in_subreddit = total_karma_in_comments_on_subreddit / comments_on_subreddit 
    else: avg_comment_score_in_subreddit = 0
    return total_g_mer_count, avg_comment_score_in_subreddit, frequency_of_g_mer_words


#This is how you start the reddit instance. I might add a template praw.ini file to show how it works, but right now it is in .gitignore because it has personal info like password.
reddit = praw.Reddit('bot1')

#This is where the magic happens

def reply_to_comment(message, mentions):
    if "u/g_merdetectorbot" in mentions:
        #Removes u/g_merdetectorbot from the mentions
        mentions.pop(mentions.index("u/g_merdetectorbot"))
        g_mer_score = 0
        avg_karma_in_subreddit = 0
        g_mer_name = ""
        frequency_of_g_mer_words = None
        #Checks if another user is mentioned in the comment, and if so makes them the test subject. Otherwise checks who the comment was a reply to and makes them the test subject
        if len(mentions) == 1:
            g_mer_score , avg_karma_in_subreddit , frequency_of_g_mer_words = test_g_mer(mentions[0],message.subreddit)
            g_mer_name = mentions[0]
        elif len(mentions) == 0:
            parent_author = str(message.parent().author).lower()
            g_mer_score , avg_karma_in_subreddit , frequency_of_g_mer_words = test_g_mer(parent_author,message.subreddit)
            g_mer_name = "u/" + parent_author
        #Creates table using markdown if there are words to make table with
        g_mer_word_table_string = ""
        if(g_mer_score > 0):
            g_mer_word_table_string = "| Word | Count |\n|-----|-----|\n"
            g_mer_words = list(frequency_of_g_mer_words.keys())
            g_mer_frequencies = list(frequency_of_g_mer_words.values())
            for x in range(len(g_mer_words)):
                g_mer_word_table_string += f"| {g_mer_words[x]} | {g_mer_frequencies[x]} |\n"
        #If test subject is u/g_merdetectorbot it replies with a custom message
        if g_mer_name == "u/g_merdetectorbot":
            message.reply(f"**u/G_merDetectorBot** \n\n Check out the new subreddit: r/G_merDetectorBot \n\n [^How ^the ^bot ^works ](https://www.reddit.com/user/G_merDetectorBot/comments/gowq2d/) \n\n [^Words ^the ^bot ^detects ](https://www.reddit.com/user/G_merDetectorBot/comments/gowikd/) \n\n [^Message ^the ^creator ](https://www.reddit.com/message/compose/?to=abdeet) \n\n [^Github ^link](https://github.com/Abdeet/g_merdetectorbot)")
        #Same with if test subject is u/Abdeet
        elif g_mer_name == "u/abdeet":
            message.reply(f"u/Abdeet created this bot. \n\n God says all g\*mers will rot. \n\n G\*ming is a sin, \n\n Anti-g\*ming will win, \n\n This limerick sure hits the spot. \n\n ^Check ^out ^the ^subreddit: ^r/G_merDetectorBot \n\n [Github link](https://github.com/Abdeet/g_merdetectorbot)")
        #Standard message
        
        else:
            message.reply(f"**Suspected G\*mer: {g_mer_name}**\n\n  **G\*mer Score: _{g_mer_score}_** \n\n **Average Comment Score in r/{message.subreddit}: _{avg_karma_in_subreddit}_** \n\n Words Used: \n\n{g_mer_word_table_string} \n\n Check out the subreddit: r/G_merDetectorBot \n\n ^Calculated ^using ^user's ^last ^100 ^comments, ^searching ^for [^these ^words ](https://www.reddit.com/user/G_merDetectorBot/comments/gowikd/) \n\n [^Send ^a ^private ^message ](https://www.reddit.com/message/compose/?to=abdeet) ^to ^suggest ^more ^words ^to ^add. \n\n ^Created ^to ^rid ^the ^world ^of ^the ^evils ^of ^g\*ming.")

#Runs the code
def main():
    for message in reddit.inbox.unread():
        all_mentions = get_mentions(message.body.lower())
        reply_to_comment(message, all_mentions)
        message.mark_read()

#Calls main, and basically all the other code
main()



#Regex from u/HDMemes. It isn't currently compatible with the way detection is done right now, but if I decide to streamline the bot this is definitely going to be useful
#(\b((g+[\W_]*)+(a+[\W_]*)+(m+[\W_]*)+(((e+[\W_]*)+(r+[\W_]*)*(s+[\W_]*)*)|((i+[\W_]*)+(n+[\W_]*)+(g+[\W_]*)+)))\b|\b((k+[\W_]*)+(a+[\W_]*)+(r+[\W_]*)+(e+[\W_]*)+(n+[\W_]*)+)\b|\b((b+[\W_]*)+(o+[\W_]*){2,}(m+[\W_]*)+(e+[\W_]*)+(r+[\W_]*)+)\b|\b((n+[\W_]*)+(i+[\W_]*)+(g+[\W_]*){2,}(((e+[\W_]*)+(r+[\W_]*)+)|(a+[\W_]*)+))\b|\b((f+[\W_]*)+(a+[\W_]*)+(g+[\W_]*){2,}(o+[\W_]*)+(t+[\W_]*)+)\b|\b((x+[\W_]*)+(b+[\W_]*)+(o+[\W_]*)+(x+[\W_]*)+)\b|\b((p+[\W_]*)+(l+[\W_]*)+(a+[\W_]*)+(y+[\W_]*)+(s+[\W_]*)+(t+[\W_]*)+(a+[\W_]*)+(t+[\W_]*)+(i+[\W_]*)+(o+[\W_]*)+(n+[\W_]*)+)\b|\b((n+[\W_]*)+(i+[\W_]*)+(n+[\W_]*)+(t+[\W_]*)+(e+[\W_]*)+(n+[\W_]*)+(d+[\W_]*)+(o+[\W_]*)+)\b)