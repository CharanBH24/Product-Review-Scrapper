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
    global searchString
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

            products.update({"link": links[i].get("href")})
            print(products)
            searchResult.append(products)
        context = {"Name": searchString.replace(
            "+", " "), "ProductList": searchResult}
    return render_template('search.html', context=context)


@app.route('/review', methods=['POST', 'GET'])
@cross_origin()
def index():
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
                        prodRating = soup4.find("i",
                                                class_=["a-icon-star"]
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


@app.route('/prev', methods=['POST', 'GET'])
def prev():
    global pageA
    #print('hello prev')
    pageA -= 1
    return flask.redirect('/review', code=307)


@app.route('/next', methods=['POST', 'GET'])
def next():
    global pageA
    global numA
    numA = 10
    #print('hello next')
    pageA += 1
    return flask.redirect('/review', code=307)


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8001, debug=True)
    # app.run(debug=True)
