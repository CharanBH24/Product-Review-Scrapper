import sys
import flask
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
from requests_html import HTMLSession
import html5lib
import re
import os
from flask_wtf.csrf import CSRFProtect
import requests
# Global variables
# total numAber of reviews per page
numA = 10
flagA = 0
pageReviewsA = {}
pageA = 1
ptA = 1
nextLinkA = ''
searchString = ''
num = 30
flag_prev = 0
flag_next = 0
pageReviews = {}
page = 1
pt = 1
nextLink = ''
searchResult = []
ratingFilter = -1
ratingFlag = 0
prodNameFlipkart = ''
prodImageFlipkart = ''
prodPriceFlipkart = ''
prodRatingFlipkart = ''
pages = 0
productLink = ''
prodImage = ''

app = Flask(__name__)
tracker = -1
# links = []
res = []

app = Flask(__name__)
csrf = CSRFProtect(app)
app.config['SECRET_KEY'] = 'ty4425hk54a21eee5719b9s9df7sdfklx'
csrf.init_app(app)


@app.route('/', methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    global numA
    global flagA
    global pageReviewsA
    global pageA
    global ptA
    global nextLinkA
    numA = 10
    flagA = 0
    pageReviewsA = {}
    pageA = 1
    ptA = 1
    nextLinkA = ''
    searchString = ''
    return render_template("index.html")


@app.route('/searchAmazon', methods=['POST', 'GET'])
@cross_origin()
def searchAmazon():
    filetest = open("test.txt", "w")
    global pageReviews
    global searchString
    pageReviews = {}
    cookies = {"location": "Vellore"}
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36"}
    searchString = request.form['content'].replace(" ", "+")
    url = "https://www.amazon.in/s?k=" + searchString
    # flipkart_url = "https://www.flipkart.com/search?q=" + searchString
    page = requests.get(url, headers=headers, cookies=cookies)
    soup1 = bs(page.content, "html5lib")
    soup2 = bs(soup1.prettify(), features="lxml")
    # filetest.write(str(soup2))
    names_price = soup2.find_all("a", class_=[re.compile(
        "a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"), "a-link-normal a-text-normal"])
    while names_price == []:
        page = requests.get(url, headers=headers, cookies=cookies)
        soup1 = bs(page.content, "html5lib")
        soup2 = bs(soup1.prettify(), features="lxml")
        # filetest.write(str(soup2))
        names_price = soup2.find_all("a", class_=[re.compile(
            "a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"), "a-link-normal a-text-normal"])
    names = []
    prices = []
    for name_t in names_price:
        # print(name_t.find("span",class_="a-offscreen"))
        if name_t.find("span", class_="a-offscreen") != None:
            # name_t.find("span",class_="a-offscreen")
            prices.append(name_t.find("span", class_="a-offscreen"))
        else:
            names.append(name_t.span)

    # prices = flipkart_html.findAll("div", {"class": "_30jeq3 _1_WHN1"})
    ratingA = []
    mainboxes = soup2.findAll("div", {"class": "s-asin"})
    for subbox in mainboxes:
        try:
            ratingA.append(
                (subbox.find("span", {"class": "a-icon-alt"}).text.strip())[0:3:])
        except:
            ratingA.append("No rating")
    links = []
    for subbox in mainboxes:
        link = subbox.find_all("a", {"class": "a-link-normal"})
        if len(link[0]['href']) > 80:  # warning value 80 experimental
            # print("--0--")
            productLink = "https://www.amazon.in" + link[0]['href']
        elif len(link[1]['href']) > 80:
            # print("--1--")
            productLink = "https://www.amazon.in" + link[1]['href']
        elif len(link[2]['href']) > 80:
            # print("--2--")
            productLink = "https://www.amazon.in" + link[2]['href']
        else:
            # print("--3--")
            productLink = "https://www.amazon.in" + link[3]['href']
        links.append(productLink)
    # links=[]
    global res
    # res=[]
    for i in range(24):
        try:
            # res.append({'name':names[i].text.strip(),'price':prices[i].text.strip(),'rating':ratingA[i].strip(),'link':links[i],'tracker':i})
            res.append({'name': names[i].text.strip(), 'price': prices[i].text.strip(
            ), 'rating': ratingA[i].strip(), 'link': links[i], 'tracker': i})
            filetest.write("-----"+str(res)+"-------")
        except:
            print("ending=", i, "\n")
            break
    filetest.close()
    context = {'Name': searchString.replace("+", " "), 'ProductList': res}
    return render_template('search.html', context=context)

# route to show the review comments in a web UI


@app.route('/searchFlipkart', methods=['POST', 'GET'])
@cross_origin()
def searchFlipkart():
    print(1)
    global pageReviews
    global searchString
    global searchResult
    global num
    global pt
    num = 30
    pageReviews = {}
    pt = 1
    try:
        if searchString == '':
            searchString = request.form['content']
        flipkart_url = "https://www.flipkart.com/search?q=" + \
            searchString.replace(" ", "+")
        flipkartPage = requests.get(flipkart_url)
        flipkart_html = bs(flipkartPage.content, "html5lib")
        names = flipkart_html.find(class_=["_1YokD2 _3Mn1Gg"]).find_all(
            class_=["_4rR01T", "s1Q9rs", "IRpwTa"])
        prices = flipkart_html.find(
            class_=["_1YokD2 _3Mn1Gg"]).find_all(class_="_30jeq3")
        ratings = flipkart_html.find(
            class_=["_1YokD2 _3Mn1Gg"]).find_all(class_="_3LWZlK")
        links = flipkart_html.find(class_=["_1YokD2 _3Mn1Gg"]).find_all(
            "a", class_=["_1fQZEK", "_2rpwqI", "_2UzuFa"])
        searchResult = []
        for i in range(0, len(names)):

            products = {}

            try:
                products.update({"name": names[i].get_text().strip()})
            except:
                products.update({"name": "Unkown"})

            try:
                products.update({"rating": ratings[i].get_text().strip()}),
            except:
                products.update({"rating": "No Rating Given"})

            try:
                products.update({"price": prices[i].get_text().strip()}),
            except:
                products.update({"price": "No Price Mentioned"})

            products.update(
                {"link": "https://flipkart.com"+links[i].get("href")})
            print(products)
            searchResult.append(products)
        context = {"Name": searchString.replace(
            "+", " "), "ProductList": searchResult}
        return render_template('search1.html', context=context)
    except Exception as e:
        print('The Exception message is: ', e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        return 'something is wrong'


@app.route('/reviewAmazon', methods=['POST', 'GET'])
@cross_origin()
def indexAmazon():
    global numA
    global flagA
    global pageReviewsA
    global pageA
    global ptA
    global nextLinkA
    global searchString
    global tracker
    # global links
    global res

    reviews = []

    ratingFilter = -1
    # ratingFilter to be given value via html form in results html (maybe drop down menu)
    # ratingFilter=1
    # make sure to reset pageReviewsA = {}

    if request.method == 'POST':
        # print(links)
        filetest = open("test.txt", "w")
        commentsLinkA = ''
        commResA = ''
        comm_htmlA = ''
        cookies = {"location": "Vellore"}
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36"}
        # print(pageReviewsA,pageA)
        try:
            if pageReviewsA == {} and pageA == 1:
                # productLink = request.args.get('link')
                productLink = request.args.get('tracker')
                print(productLink)
                # print(res[int(productLink)]['name'])
                # productLink = res[int(productLink)]['link']
                productLink = request.form['link']
                # productLink="https://www.amazon.in"+productLink
                # filetest.write("----",request.args.get('tracker'),"  ",res[int(productLink)]['name'],"  ",productLink,"----")
                redo = 1
                while(redo > 0 and redo < 10):
                    try:
                        prodRes = requests.get(
                            productLink, headers=headers, cookies=cookies)
                        soup3 = bs(prodRes.content, "html5lib")
                        soup4 = bs(soup3.prettify(), features="lxml")
                        prodImage = soup4.find("img",
                                               class_=["a-dynamic-image"])
                        prodPrice = soup4.find("span",
                                               class_=["a-price"]).find("span", class_=["a-offscreen"])
                        prodRating = soup4.find("span",
                                                class_=["a-icon-alt"]
                                                )
                        # print(prod_html)
                        print("point-4")
                # commsA=soup4.findAll("div", {"id": "reviews-medley-footer"})
                        commsA = soup4.find(
                            "a", {"data-hook": "see-all-reviews-link-foot"}).get('href')
                        commentsLinkA = "https://www.amazon.in" + commsA
                        redo = 0
                        break
                    except:
                        redo += 1
                print("new-point-4")
                # print("--------------------------",commentsLinkA,"---------------------------","\n")
                commResA = requests.get(
                    commentsLinkA, headers=headers, cookies=cookies)
                soup3 = bs(commResA.content, "html5lib")
                comm_htmlA = bs(soup3.prettify(), features="lxml")

            else:
                commentsLinkA = nextLinkA
                commResA = requests.get(
                    commentsLinkA, headers=headers, cookies=cookies)
                soup3 = bs(commResA.content, "html5lib")
                comm_htmlA = bs(soup3.prettify(), features="lxml")

            print("new-point-5")
            # Total numAber of pages in reviews
            # pages = int(comm_htmlA.find_all('div', {'class': '_2MImiq _1Qnn1K'})[0].span.text.split()[-1])            #cannot solve in amazon, skipping it

            if pageA == 1:
                flagA = 0
            else:
                flagA = 1

            if pageA in pageReviewsA.keys():
                return render_template('results.html', reviews=pageReviewsA[pageA], flag=flagA, page=pageA, prodName=searchString.replace("+", " "), prodImage=prodImage.get("src"), rating=prodRating.get_text().strip()[0:3], price=prodPrice.get_text().strip(), link=productLink)

            print("--------------------------", commentsLinkA,
                  "---------------------------", "\n")  # debug
            while numA > 0:  # and pages > 1
                commentboxes = comm_htmlA.findAll(
                    "div", {"data-hook": "review"})
                # if pageA==2:
                # if numA==10:
                # filename = searchString + ".csv"
                # fw = open(filename, "w")
                # headers = "Product, Customer Name, Rating, Heading, Comment \n"
                # fw.write(headers)
                reviews = []
                print("point-5")
                # print("-----------------------------------------------------------------\n")
                for i in range(ptA-1, len(commentboxes), 1):
                    # for commentbox in commentboxes:
                    commentbox = commentboxes[i]
                    # if i == 1:
                    # print("--------------------------", commentbox,"---------------------------", "\n")
                    try:
                        # name.encode(encoding='utf-8')
                        name = commentbox.find(
                            'span', {'class': 'a-profile-name'}).text

                    except:
                        name = 'No Name'

                    try:
                        # rating.encode(encoding='utf-8')
                        # rating = commentbox.find('span', {'class': 'a-profile-name'}).text
                        rating = commentbox.find(
                            'a', {'class': 'a-link-normal'}).get('title')[0:3]
                        # rating=rating[0:3]
                        # rating = commentbox.div.div.div[1].title

                    except:
                        rating = 'No Rating'

                    try:
                        # commentHead.encode(encoding='utf-8')
                        commentHead = commentbox.find(
                            'a', {'data-hook': 'review-title'}).span.text
                        # commentHead = commentbox.div.div.div[1].a[1].span.text

                    except:
                        commentHead = 'No Comment Heading'
                    try:
                        # comtag = commentbox.find('div', {'class': 'review-text-content'})
                        comtag = commentbox.find(
                            'span', {'data-hook': 'review-body'})
                        custComment = comtag.span.text
                    except Exception as e:
                        custComment = "No comment found"
                        print("Exception while creating dictionary: ", e)

                    mydict = {"Name": name, "Rating": rating,
                              "CommentHead": commentHead, "Comment": custComment}
                    reviews.append(mydict)
                    numA -= 1  # numAber of reviews to be limited to 10 per pageA
                    ptA = i
                    if numA == 0:
                        break

                print("new-point-6")
                if ptA < len(commentboxes)-1:
                    nextLinkA = commentsLinkA
                # code for going next reviews pageA

                try:
                    commentsLinkA = comm_htmlA.find(
                        "ul", {"class": "a-pagination"})
                    print("new-point-7")
                    commentsLinkA = commentsLinkA.find(
                        "li", {"class": "a-last"}).a['href']
                    print("new-point-8")
                    # print("--------------------------",commentsLinkA,"---------------------------","\n")
                    commentsLinkA = "https://www.amazon.in" + commentsLinkA

                    commResA = requests.get(
                        commentsLinkA, headers=headers, cookies=cookies)
                    soup3 = bs(commResA.content, "html5lib")
                    comm_htmlA = bs(soup3.prettify(), features="lxml")
                except:
                    print("\nNumber of reviews less then 11\n")
                # pages-=1
                if ptA == len(commentboxes)-1:
                    ptA = 1
                    nextLinkA = commentsLinkA

            if pageReviewsA != {} and pageA != 1:
                reviews = reviews[0:]
            pageReviewsA[pageA] = reviews
            print("point-6")
            # print("-----------------------------------------------------------------\n")
            return render_template('results.html', reviews=reviews[0:(len(reviews))], prodName=searchString.replace("+", " "), prodImage=prodImage.get("src"), rating=prodRating.get_text().strip()[0:3], price=prodPrice.get_text().strip(), link=productLink)
        except Exception as e:
            print('The Exception message is: ', e)
            return 'something is wrong'
        filetest.close()
    # return render_template('results.html')

    else:
        return render_template('index.html')


@app.route('/reviewFlipkart', methods=['POST', 'GET'])
@cross_origin()
def indexFlipkart():
    global num
    global flag_prev
    global flag_next
    global pageReviews
    global page
    global pt
    global nextLink
    global searchString
    global ratingFilter
    global ratingFlag
    global prodNameFlipkart
    global prodPriceFlipkart
    global prodRatingFlipkart
    global prodImageFlipkart
    global pages
    global productLink

    reviews = []

    # ratingFilter = -1
    # # ratingFilter to be given value via html form in results html (maybe drop down menu)
    # # ratingFilter=1
    # # make sure to reset pageReviews = {}
    commentsLink = ''
    commRes = ''
    comm_html = ''
    try:
        if pageReviews == {} and page == 1 and ratingFlag == 0:
            '''searchString = request.form['content'].replace(" ","")

            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            print(box)'''
            print(request.form["link"])
            productLink = request.form['link']  # box.div.div.div.a['href']
            print(productLink)
            prodRes = requests.get(productLink)
            prodRes.encoding = 'utf-8'
            prod_html = bs(prodRes.text, "html.parser")
            prodNameFlipkart = prod_html.findAll(
                "span", {"class": "B_NuCI"})[0].text
            prodImageFlipkart = prod_html.find(class_=["_396cs4", "_2r_T1I"])
            prodPriceFlipkart = prod_html.find(class_="_30jeq3")
            prodRatingFlipkart = prod_html.find(class_=["_2d4LTz", "_3LWZlK"])
            comms = prod_html.findAll(
                class_=["col JOpGWq", "_16PBlm _2RzJ9n"])
            commentsLink = "https://www.flipkart.com" + \
                comms[0].find_all('a')[-1]['href']
            print(comms[0].find_all('a')[-1]['href'])
            commRes = requests.get(commentsLink)
            commRes.encoding = 'utf-8'
            comm_html = bs(commRes.text, "html.parser")
        elif pageReviews == {} and page == 1 and ratingFlag == 1:
            ratingFlag = 0
            pt = 1
            commentsLink = nextLink[:-nextLink[::-1].find('&') - 1]
            print(commentsLink)
            if ratingFilter == 5:
                commentsLink += '&aid=overall&certifiedBuyer=true&sortOrder=POSITIVE_FIRST'
            elif ratingFilter == -1:
                commentsLink += '&aid=overall&certifiedBuyer=true&sortOrder=MOST_RECENT'
            else:
                commentsLink += '&aid=overall&certifiedBuyer=true&sortOrder=NEGATIVE_FIRST'
            print(commentsLink)
            commentsLink = getLoc(commentsLink, ratingFilter)
            commRes = requests.get(commentsLink)
            commRes.encoding = 'utf-8'
            comm_html = bs(commRes.text, "html.parser")
        else:
            commentsLink = nextLink
            commRes = requests.get(commentsLink)
            commRes.encoding = 'utf-8'
            comm_html = bs(commRes.text, "html.parser")

        # Total number of pages in reviews
        print('1')
        if pages == 0:
            pages = int(
                comm_html.find_all('div', {'class': '_2MImiq _1Qnn1K'})[0].span.text.split()[-1].replace(',', ''))
            if pages > 999:
                pages = 999
        currPage = int(comm_html.find_all('div', {'class': '_2MImiq _1Qnn1K'})[
                       0].span.text.split()[1].replace(',', ''))
        if pages == currPage:
            flag_next = 0
        else:
            flag_next = 1

        if page == 1:
            flag_prev = 0
        else:
            flag_prev = 1

        print('2')
        if page in pageReviews.keys():
            return render_template('results1.html', reviews=pageReviews[page], flag_prev=flag_prev, flag_next=flag_next, page=page, prodName=prodNameFlipkart, prodImage=prodImageFlipkart.get("src"), price=prodPriceFlipkart.get_text().strip(), rating=prodRatingFlipkart.get_text().strip(), link=productLink)

        while num > 0 and pages > 1:
            print('3')
            #commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})
            commentboxes = comm_html.find_all('div', {'class': "col"})
            print(len(commentboxes))

            for i in range(pt, len(commentboxes), 2):
                commentbox = commentboxes[i]
                try:
                    # name.encode(encoding='utf-8')
                    name = commentbox.div.find_all(
                        'p', {'class': '_2sc7ZR _2V5EHH'})[0].text

                except:
                    name = 'No Name'

                try:
                    # rating.encode(encoding='utf-8')
                    #rating = commentbox.div.div.div.div.text
                    rating = commentbox.div.div.div.text

                except:
                    rating = 'No Rating'

                try:
                    # commentHead.encode(encoding='utf-8')
                    #commentHead = commentbox.div.div.div.p.text
                    commentHead = commentbox.div.div.p.text

                except:
                    commentHead = 'No Comment Heading'
                try:
                    comtag = commentbox.div.find_all('div', {'class': ''})
                    # custComment.encode(encoding='utf-8')
                    custComment = comtag[0].div.text
                except Exception as e:
                    print("Exception while creating dictionary: ", e)

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}

                # filtering outliers or as according to rating filter
                if (mydict["Rating"] != 'No Rating' and ratingFilter == -1) or mydict["Rating"] == str(ratingFilter):
                    reviews.append(mydict)
                    num -= 1  # number of reviews to be limited to 30 per page
                pt = i
                if num == 0:
                    break

            if pt < len(commentboxes)-1:
                nextLink = commentsLink
                print(nextLink)
            # code for going next reviews page
            commentsLink = "https://www.flipkart.com" + \
                comm_html.find_all('a', {'class': '_1LKTO3'})[-1]['href']
            commRes = requests.get(commentsLink)
            commRes.encoding = 'utf-8'
            comm_html = bs(commRes.text, "html.parser")
            pages -= 1
            if pt == len(commentboxes)-1:
                pt = 1
                nextLink = commentsLink
                print(nextLink)

        if pageReviews != {} and page != 1:
            reviews = reviews[1:]
        pageReviews[page] = reviews
        return render_template('results1.html', reviews=reviews, flag_prev=flag_prev, flag_next=flag_next, page=page, prodName=prodNameFlipkart, prodImage=prodImageFlipkart.get("src"), price=prodPriceFlipkart.get_text().strip(), rating=prodRatingFlipkart.get_text().strip(), link=productLink)
    except Exception as e:
        print('The Exception message is: ', e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        return 'something is wrong'


@app.route('/prev', methods=['POST', 'GET'])
def prev():
    global page
    #print('hello prev')
    page -= 1
    return flask.redirect('/reviewFlipkart', code=307)


@app.route('/next', methods=['POST', 'GET'])
def next():
    global page
    global num
    num = 30
    #print('hello next')
    page += 1
    return flask.redirect('/reviewFlipkart', code=307)


@app.route('/backtoSearch', methods=['POST', 'GET'])
@cross_origin()
def backtoSearch():
    global pageReviews
    global num
    global pt
    global page
    global ratingFilter
    global ratingFlag
    num = 30
    pageReviews = {}
    pt = 1
    page = 1
    ratingFilter = -1
    ratingFlag = 0
    return flask.redirect('/searchFlipkart', code=307)


@app.route('/searchNew', methods=['POST', 'GET'])
@cross_origin()
def searchNew():
    global pageReviews
    global num
    global pt
    global page
    global searchString
    global searchResult
    num = 30
    pageReviews = {}
    pt = 1
    page = 1
    searchResult = []
    if searchString != request.form['content']:
        searchString = ''
    return flask.redirect('/searchFlipkart', code=307)


@app.route('/filterReviews', methods=['POST', 'GET'])
@cross_origin()
def filterReviews():
    global pageReviews
    global num
    global pt
    global page
    global searchString
    global filterReviews
    global ratingFlag
    global ratingFilter
    num = 30
    pageReviews = {}
    pt = 1
    page = 1
    try:
        ratingFilter = int(request.args.get('filter'))
        print(ratingFilter)
    except:
        ratingFilter = -1
    ratingFlag = 1
    return flask.redirect('/reviewFlipkart', code=307)


def getLoc(commentsLink, ratingFilter):
    global pages
    if ratingFilter in [1, 5, -1]:
        print(commentsLink)
        return commentsLink
    else:
        reqRating = ratingFilter - 0.5
        # '&aid=overall&certifiedBuyer=true&sortOrder=POSITIVE_FIRST&page=' + str(pages // 2)
        print('Fiktering ', ratingFilter, reqRating)
        start, end = 1, pages
        while start < end:
            mid = (start + end) // 2
            commentsLink += '&page=' + str(mid)
            uClient = uReq(commentsLink)
            commRes = uClient.read()
            uClient.close()
            comm_html = bs(commRes, "html.parser")
            commentbox = comm_html.find_all('div', {'class': "_27M-vq"})
            while commentbox == []:
                print('again')
                uClient = uReq(commentsLink)
                commRes = uClient.read()
                uClient.close()
                comm_html = bs(commRes, "html.parser")
                commentbox = comm_html.find_all('div', {'class': "_27M-vq"})
            rating = int(commentbox[1].div.div.div.div.text)
            if rating < reqRating:
                start = mid + 1
            else:
                end = mid - 1
        print("https://www.flipkart.com" +
              comm_html.find_all('a', {'class': '_1LKTO3'})[1]['href'])
        return "https://www.flipkart.com" + comm_html.find_all('a', {'class': '_1LKTO3'})[1]['href']


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8001, debug=True)
    # app.run(debug=True)
