import argparse
import time
import json
import csv
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs
import sys

# with open('facebook_credentials.txt') as file:
#     EMAIL = file.readline().split('"')[1]
#     PASSWORD = file.readline().split('"')[1]


def _extract_post_text(item):
    actualPosts = item.find_all(attrs={"data-testid": "post_message"})
    text = ""
    if actualPosts:
        for posts in actualPosts:
            paragraphs = posts.find_all('p')
            text = ""
            for index in range(0, len(paragraphs)):
                text += paragraphs[index].text
    return text

def _extract_post_date(item):
    dateContainer = item.find_all(attrs={"class": "_5ptz"})
    date = ""
    for dateObj in dateContainer:
        date = dateObj.get('title')
    return date


def _extract_link(item):
    postLinks = item.find_all(class_="_6ks")
    link = ""
    for postLink in postLinks:
        link = postLink.find('a').get('href')
    return link


def _extract_post_id(item):
    postIds = item.find_all(class_="fsm fwn fcg")
    post_id = ""
    for postId in postIds:
        children = postId.findChildren("a" , recursive=False)
        for a in children:
            segments = a.get('href').split("?")
            post_id = segments[0]
            # if len(segments)>2:
            #     if "?" in segments[3]:
            #         segments[3] = segments[3].split("?")[0]
                # post_id = segments[2]+"/"+segments[3]
            # else:
            #     post_id = a.get('href')
    return post_id


def _extract_image(item):
    postPictures = item.find_all(class_="scaledImageFitWidth img")
    image = ""
    for postPicture in postPictures:
        image = postPicture.get('src')
    return image


def _extract_shares(item):
    postShares = item.find_all(class_="_4vn1")
    shares = {"comments":0, "shares":0}
    for postShare in postShares:
        childrenSpan = postShare.findChildren("span" , recursive=False)
        spanCount = 1
        for span in childrenSpan:
            childrensA = span.findChildren("a" , recursive=False)
            for childrenA in childrensA:
                if spanCount==1:
                    shares['comments'] = childrenA.text.split(" ")[0]
                else:
                    shares['shares'] = childrenA.text.split(" ")[0]
            spanCount +=1
    # for postShare in postShares:
    #     shares = postShare.text.split(" veces")[0]
    return shares


def _extract_comments(item):
    postComments = item.findAll("div", {"class": "_4eek"})
    comments = dict()
    for comment in postComments:
        if comment.find(class_="_6qw4") is None:
            continue

        commenter = comment.find(class_="_6qw4").text
        comments[commenter] = dict()
        comments[commenter]['commenter'] = commenter
        # comments[commenter]['postid'] = postId

        comment_text = comment.find("span", class_="_3l3x")

        if comment_text is not None:
            comments[commenter]["text"] = comment_text.text.encode('utf-8').decode()

        comment_id = comment.find("a", class_="_6qw7")
        if comment_id is not None:
            comments[commenter]["commentid"] = comment_id.get('href').split("comment_id=")[1].encode('utf-8').decode()
            for children in comment_id:
                comments[commenter]["date"] = children.get("data-tooltip-content").encode('utf-8').decode()

        # comment_link = comment.find(class_="_ns_")
        # if comment_link is not None:
        #     comments[commenter]["link"] = comment_link.get("href")

        # comment_pic = comment.find(class_="_2txe")
        # if comment_pic is not None:
        #     comments[commenter]["image"] = comment_pic.find(class_="img").get("src")

        commentList = item.find('ul', {'class': '_7791'})
        if commentList:
            comments = dict()
            comment = commentList.find_all('li')
            if comment:
                for litag in comment:
                    aria = litag.find("div", {"class": "_4eek"})
                    if aria:
                        commenter = aria.find(class_="_6qw4").text
                        comments[commenter] = dict()
                        comments[commenter]['commenter'] = commenter
                        comment_text = litag.find("span", class_="_3l3x")
                        if comment_text:
                            comments[commenter]["text"] = comment_text.text.encode('utf-8').decode()

                        comment_id = comment.find("span", class_="_6qw7")
                        if comment_id is not None:
                            comments[commenter]["commentid"] = comment_id.get('href').split("comment_id=")[1].encode('utf-8').decode()
                            for children in comment_id:
                                comments[commenter]["date"] = children.get("data-tooltip-content").encode('utf-8').decode()

                        # comment_link = litag.find(class_="_ns_")
                        # if comment_link is not None:
                        #     comments[commenter]["link"] = comment_link.get("href")

                        # comment_pic = litag.find(class_="_2txe")
                        # if comment_pic is not None:
                        #     comments[commenter]["image"] = comment_pic.find(class_="img").get("src")

                        # repliesList = litag.find(class_="_2h2j")
                        # if repliesList:
                        #     reply = repliesList.find_all('li')
                        #     if reply:
                        #         comments[commenter]['reply'] = dict()
                        #         for litag2 in reply:
                        #             aria2 = litag2.find("div", {"class": "_4efk"})
                        #             if aria2:
                        #                 replier = aria2.find(class_="_6qw4").text
                        #                 if replier:
                        #                     comments[commenter]['reply'][replier] = dict()

                        #                     reply_text = litag2.find("span", class_="_3l3x")
                        #                     if reply_text:
                        #                         comments[commenter]['reply'][replier][
                        #                             "reply_text"] = reply_text.text

                        #                     r_link = litag2.find(class_="_ns_")
                        #                     if r_link is not None:
                        #                         comments[commenter]['reply']["link"] = r_link.get("href")

                        #                     r_pic = litag2.find(class_="_2txe")
                        #                     if r_pic is not None:
                        #                         comments[commenter]['reply']["image"] = r_pic.find(
                        #                             class_="img").get("src")
    return comments


def _extract_reaction(item):
    reactionBar = item.findAll("span", {"class": "_1n9k"})
    reactionTypes = {"0":"totalreactions", "1":"like", "2":"love", "3":"wow", "4":"haha", "7":"sorry", "8":"angry", "16":"care"}
    reactions = {"like":0, "love":0, "wow":0, "haha":0, "sorry":0, "angry":0, "care":0, "totalreactions":0}
    if not reactionBar:  # pretty fun
        return reactions
    # reaction = dict()
    reactions['totalreactions'] = item.findAll("span", {"class": "_81hb"})[0].text
    for reactionBar_child in reactionBar:
        reactionA = reactionBar_child.findAll("a", {"class": "_1n9l"})[0]
        reactionType = str(reactionA.get("ajaxify").split("reaction_type=")[1].split("&")[0])
        reactions[reactionTypes[reactionType]] = reactionA.get("aria-label").split(" ")[0]
        # str = toolBar_child['data-testid']
        # reaction = str.split("UFI2TopReactions/tooltip_")[1]

        # reaction[reaction] = 0

        # for toolBar_child_child in toolBar_child.children:

        #     num = toolBar_child_child['aria-label'].split()[0]

        #     # fix weird ',' happening in some reaction values
        #     num = num.replace(',', '.')

        #     if 'K' in num:
        #         realNum = float(num[:-1]) * 1000
        #     else:
        #         realNum = float(num)

        #     reaction[reaction] = realNum
    return reactions


def _extract_html(bs_data):

    #Add to check
    with open('./bs.html',"w", encoding="utf-8") as file:
        file.write(str(bs_data.prettify()))

    k = bs_data.find_all(class_="_5pcr userContentWrapper")
    postBigDict = list()

    for item in k:
        postDict = dict()
        # postDict['Link'] = _extract_link(item)
        postDict['postid'] = _extract_post_id(item)
        postDict['text'] = _extract_post_text(item)
        postDict['date'] = _extract_post_date(item) #_5ptz timestamp livetimestamp
        # postDict['Image'] = _extract_image(item)
        sharesComments = _extract_shares(item)
        postDict['shares'] = sharesComments['shares']
        postDict['totalComments'] = sharesComments['comments']
        postDict['featuredComments'] = _extract_comments(item)
        reactions = _extract_reaction(item)
        for reaction in reactions:
            postDict[reaction]=reactions[reaction]

        #Add to check
        postBigDict.append(postDict)
    
    with open('./postBigDict_'+datetime.date.today().strftime("%Y-%m-%d-H-i-s")+'.json','w', encoding='utf-8') as file:
            file.write(json.dumps(postBigDict, ensure_ascii=False).encode('utf-8').decode())

    return postBigDict


def _login(browser, email, password):
    browser.get("http://facebook.com")
    browser.maximize_window()
    browser.find_element_by_name("email").send_keys(email)
    browser.find_element_by_name("pass").send_keys(password)
    browser.find_element_by_id('u_0_b').click()
    time.sleep(3)


def _count_needed_scrolls(browser, infinite_scroll, numOfPost):
    if infinite_scroll:
        lenOfPage = browser.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;"
        )
    else:
        # roughly 8 post per scroll kindaOf
        lenOfPage = int(numOfPost / 2)
    print("Number Of Scrolls Needed " + str(lenOfPage))
    return lenOfPage


def _scroll(browser, infinite_scroll, lenOfPage):
    lastCount = -1
    match = False

    progressStep = 10
    progessPercent = lenOfPage/progressStep
    progressCount = 10
    while not match:
        if infinite_scroll:
            lastCount = lenOfPage
        else:
            lastCount += 1

        # wait for the browser to load, this time can be changed slightly ~3 seconds with no difference, but 5 seems
        # to be stable enough
        time.sleep(3)

        if infinite_scroll:
            lenOfPage = browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return "
                "lenOfPage;")
        else:
            browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return "
                "lenOfPage;")
        if lastCount>=progessPercent:
            print(str(progressCount)+"%.....")
            progressCount +=progressStep
            progessPercent += lenOfPage/progressStep

        if lastCount == lenOfPage:
            match = True


def extract(page, numOfPost, infinite_scroll=False, scrape_comment=True):
    option = Options()
    option.add_argument("--disable-infobars")
    option.add_argument("start-maximized")
    option.add_argument("--disable-extensions")

    # Pass the argument 1 to allow and 2 to block
    option.add_experimental_option("prefs", {
        "profile.managed_default_content_settings.images":2,
        "profile.default_content_setting_values.notifications":2,
        "profile.managed_default_content_settings.stylesheets":2,
        "profile.managed_default_content_settings.cookies":2,
        "profile.managed_default_content_settings.javascript":1,
        "profile.managed_default_content_settings.plugins":1,
        "profile.managed_default_content_settings.popups":2,
        "profile.managed_default_content_settings.geolocation":2,
        "profile.managed_default_content_settings.media_stream":2,
    })

    # chromedriver should be in the same folder as file
    browser = webdriver.Chrome(executable_path="./scrapper/chromedriver", options=option)
    #_login(browser, EMAIL, PASSWORD)
    browser.get(page)
    lenOfPage = _count_needed_scrolls(browser, infinite_scroll, numOfPost)
    _scroll(browser, infinite_scroll, lenOfPage)

    # click on all the comments to scrape them all!
    # TODO: need to add more support for additional second level comments
    # TODO: ie. comment of a comment

    if scrape_comment:
        #first uncollapse collapsed comments
        unCollapseCommentsButtonsXPath = '//a[contains(@class,"_666h")]'
        unCollapseCommentsButtons = browser.find_elements_by_xpath(unCollapseCommentsButtonsXPath)
        for unCollapseComment in unCollapseCommentsButtons:
            action = webdriver.common.action_chains.ActionChains(browser)
            try:
                # move to where the un collapse on is
                action.move_to_element_with_offset(unCollapseComment, 5, 5)
                action.perform()
                unCollapseComment.click()
            except:
                # do nothing right here
                pass

        #second set comment ranking to show all comments
        rankDropdowns = browser.find_elements_by_class_name('_2pln') #select boxes who have rank dropdowns
        rankXPath = '//div[contains(concat(" ", @class, " "), "uiContextualLayerPositioner") and not(contains(concat(" ", @class, " "), "hidden_elem"))]//div/ul/li/a[@class="_54nc"]/span/span/div[@data-ordering="RANKED_UNFILTERED"]'
        for rankDropdown in rankDropdowns:
            #click to open the filter modal
            action = webdriver.common.action_chains.ActionChains(browser)
            try:
                action.move_to_element_with_offset(rankDropdown, 5, 5)
                action.perform()
                rankDropdown.click()
            except:
                pass

            # if modal is opened filter comments
            ranked_unfiltered = browser.find_elements_by_xpath(rankXPath) # RANKED_UNFILTERED => (All Comments)
            if len(ranked_unfiltered) > 0:
                try:
                    ranked_unfiltered[0].click()
                except:
                    pass    

        # moreComments = browser.find_elements_by_xpath('//a[@class="_4sxc _42ft"]')
        # lfg = str(len(moreComments))
        # print("Scrolling through to click on more comments: "+lfg)
        # #while len(moreComments) != 0:
        # for moreComment in moreComments:
        #     # action = webdriver.common.action_chains.ActionChains(browser)
        #     try:
        #         # move to where the comment button is
        #         # action.move_to_element_with_offset(moreComment, 5, 5)
        #         # action.perform()
        #         moreComment.click()
        #     except:
        #         # do nothing right here
        #         pass

           # moreComments = browser.find_elements_by_xpath('//a[@class="_4sxc _42ft"]')

    # Now that the page is fully scrolled, grab the source code.
    source_data = browser.page_source

    # Throw your source into BeautifulSoup and start parsing!
    bs_data = bs(source_data, 'html.parser')

    postBigDict = _extract_html(bs_data)
    browser.close()

    return postBigDict


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Facebook Page Scraper")
#     required_parser = parser.add_argument_group("required arguments")
#     required_parser.add_argument('-page', '-p', help="The Facebook Public Page you want to scrape", required=True)
#     required_parser.add_argument('-len', '-l', help="Number of Posts you want to scrape", type=int, required=True)
#     optional_parser = parser.add_argument_group("optional arguments")
#     optional_parser.add_argument('-infinite', '-i',
#                                  help="Scroll until the end of the page (1 = infinite) (Default is 0)", type=int,
#                                  default=0)
#     optional_parser.add_argument('-usage', '-u', help="What to do with the data: "
#                                                       "Print on Screen (PS), "
#                                                       "Write to Text File (WT) (Default is WT)", default="CSV")

#     optional_parser.add_argument('-comments', '-c', help="Scrape ALL Comments of Posts (y/n) (Default is n). When "
#                                                          "enabled for pages where there are a lot of comments it can "
#                                                          "take a while", default="No")
#     args = parser.parse_args()

#     infinite = False
#     if args.infinite == 1:
#         infinite = True

#     scrape_comment = False
#     if args.comments == 'y':
#         scrape_comment = True

#     postBigDict = extract(page=args.page, numOfPost=args.len, infinite_scroll=infinite, scrape_comment=scrape_comment)


#     #TODO: rewrite parser
#     if args.usage == "WT":
#         with open('output.txt', 'w') as file:
#             for post in postBigDict:
#                 file.write(json.dumps(post))  # use json load to recover

#     elif args.usage == "CSV":
#         with open('data.csv', 'w',) as csvfile:
#            writer = csv.writer(csvfile)
#            #writer.writerow(['Post', 'Link', 'Image', 'Comments', 'Reaction'])
#            writer.writerow(['Post', 'Link', 'Image', 'Comments', 'Shares'])

#            for post in postBigDict:
#               writer.writerow([post['Post'], post['Link'],post['Image'], post['Comments'], post['Shares']])
#               #writer.writerow([post['Post'], post['Link'],post['Image'], post['Comments'], post['Reaction']])

#     else:
#         for post in postBigDict:
#             print(post)

#     print("Finished")
