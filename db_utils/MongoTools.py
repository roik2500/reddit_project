# # fields = []
# # with open(r"G:\.shortcut-targets-by-id\1Zr_v9ggL0ZP7j6DJeTQggwxX7BPmEJ-d\final_project\outputs\filter_fields.txt") as f:
# #     line = f.readline()
# #     while not line.__contains__("pushshift_api:"):
# #         line = f.readline()
# #         continue
# #     line = f.readline()
# #     while not line.__contains__("pushshift_api:"):
# #         fields.append(line.split('":')[0].strip(' "'))
# #         line = f.readline()
# #
import pymongo
from pymongo import WriteConcern
from pymongo.errors import BulkWriteError
from tqdm import tqdm

# # good_fields = ["can_mod_post",
# # "is_crosspostable",
# # "is_original_content",
# # "is_robot_indexable",
# # "locked",
# # "num_comments",
# # "num_crossposts",
# # "retrieved_on",
# # "selftext",
# # "title"]
# # bed_fields = [field for field in fields if field not in good_fields ]
# # bed_fields.remove('e')
# # bed_fields.remove('t')
# # bed_fields.remove('}],\n')
# #
#
client = pymongo.MongoClient(
    'mongodb://132.72.66.126:27017/?readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false')
db = client["reddit"]


#
# for collection_name in db.list_collection_names():
#     if collection_name == "mensrights":
#         continue
#     print(collection_name)
#     colc = db[collection_name]
#     collection_name_comments = "{}_comments".format(collection_name)
#     db.create_collection(collection_name_comments)
#     colc_comments = db[collection_name_comments]
#
#     curs = colc.find({}, {"reddit_api.comments": 1})
#     colc_comments.insert_many([y for x in tqdm(curs) for y in x["reddit_api"]["comments"]])
#     colc.update_many({}, {"$unset": {"reddit_api.comments": ""}})
#
def remove_dup(collection_name):
    colc = db[collection_name]
    curs = colc.find({}, {"data.id": 1}, no_cursor_timeout=True)
    index = set()
    for x in tqdm(curs):
        _id = x["data"]["id"]
        if _id in index:
            print("delete")
            colc.delete_one({"data.id": _id})
        else:
            index.add(_id)


def comments_to_lists(comments, link_id):  # link_id = post_id
    results = []  # create list for results
    for comment in comments:  # iterate over comments
        # if 'created_utc' in comment['data']:
        #     created = self.convert_time_format(comment['data']['created_utc'])[0]
        # id = comment['data']['id']
        # is_removed = self.is_removed(comment, "comment", "Removed")
        # text = ''
        # if "body" in comment["data"] and not comment['data']['body'] == "[removed]" \
        #         and comment['data']['body'] != "[deleted]":  # we comment text from reddit. Not Removed content
        #     text = comment['data']['body']
        #
        # elif "body" in comment["data"] and comment['data'][
        #     'body'] == "[removed]":  # the comment was removed by mods
        #     text = comment['data']['body']
        #     # print('comment_id',  comment['data']['id'])
        #     # print('reddit comment content', comment['data']['body'])
        #     # print('reddit user', comment['data']['author'])
        #     # pushshift_comment = self.pushshift_api.get_comments_by_comments_ids(ids_list=[id])
        #     # text = [c for c in pushshift_comment][0]['body']
        #     # if text != '[removed]' and comment['data']['author'] != '[deleted]':
        #     #     all_user_commnets = self.reddit_api.get_user_commnets(reddit_user_name=comment['data']['author'])
        #     #     text = self.reddit_api.get_removed_comment_from_reddit(user_comments=all_user_commnets, removed_comment_id=id)
        #     # print('retrived comment from user profile', text)
        # text = self.parser.remove_URL(text)
        # item = [[text, created, id, link_id, is_removed]]  # create list from comment

        item = [
            {"kind": "t1", "data": {item[0]: item[1] for item in dict(comment["data"]).items() if item[1] is not None}}]
        if 'replies' in comment["data"] and len(comment['data']['replies']) > 0:
            replies = comment['data']['replies']['data']['children']
            item[0]["data"].pop('replies')
            item += comments_to_lists(replies,
                                      link_id=link_id)  # convert replies using the same function item["replies"] = k4lz6m

        results += item  # add converted item to results
    return results  # return all converted comments


for collection_name in db.list_collection_names():
    if collection_name.__contains__("comments"):
        print(collection_name)
        colc = db[collection_name].with_options(write_concern=WriteConcern(w=0))
        replies_lst = []
        curs = colc.find({"data.replies": {"$ne": ""}})
        replies_lst = []
        counter = 0
        for x in tqdm(curs):
            if "replies" in x["data"].keys():
                comments = comments_to_lists(x["data"]["replies"]["data"]["children"], x["data"]["id"])
                print(counter, x["data"]["id"])
                replies_lst.extend(comments)
                counter += 1
            if counter == 100000:
                print("writing!")
                colc.insert_many(replies_lst)
                replies_lst = []
                counter = 0
        if counter > 0:
            print("last writing!")
            colc.insert_many(replies_lst)
            replies_lst = []
            counter = 0
# remove_dup("cryptocurrency_comments")

#     if "replies" in x["data"].keys():
#         replies_lst.append(x)
# while len(replies_lst) > 0:
#     children = [y for x in tqdm(replies_lst) for y in x["data"]["replies"]["data"]["children"]]
#     colc.insert_many(children)
#
#     curs = colc.find({"data.replies": {"$ne": ""}}, {"data.replies.data.children": 1})
#     replies_lst = []
#     for x in curs:
#         if "replies" in x["data"].keys():
#             replies_lst.append(x)
