from os import link, name
import flask
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
import html5lib
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
from flask_wtf.csrf import CSRFProtect

# Global variables
# total number of reviews per page
num = 30
flag_prev = 0
flag_next = 0
pageReviews = {}
page = 1
pt = 1
nextLink = ''
searchString = ''
searchResult = []
ratingFilter = -1

app = Flask(__name__)
csrf = CSRFProtect(app)
app.config['SECRET_KEY'] = 'ty4425hk54a21eee5719b9s9df7sdfklx'
csrf.init_app(app)


@app.route('/', methods=['POST', 'GET'])  # route to display the home page
@cross_origin()
def homePage():
    global num
    global flag_prev
    global flag_next
    global pageReviews
    global page
    global pt
    global nextLink
    global searchString
    global searchResult
    num = 30
    flag_prev = 0
    flag_next = 0
    pageReviews = {}
    page = 1
    pt = 1
    nextLink = ''
    searchString = ''
    searchResult = []
    return render_template("index.html")


@app.route('/search', methods=['POST', 'GET'])
@cross_origin()
def search():
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
        names = flipkart_html.findAll(class_=["_4rR01T", "s1Q9rs", "IRpwTa"])
        prices = flipkart_html.findAll(class_="_30jeq3")
        ratings = flipkart_html.find_all(class_="_3LWZlK")
        links = flipkart_html.findAll(
            "a", class_=["_1fQZEK", "_2rpwqI", "_2UzuFa"])
        searchResult = []
        for i in range(0, len(names)):

            products = {}

            try:
                products.update({"ProductName": names[i].get_text().strip()})
            except:
                products.update({"ProductName": "Unkown"})

            try:
                products.update({"Rating": ratings[i].get_text().strip()}),
            except:
                products.update({"Rating": "No Rating Given"})

            try:
                products.update({"Price": prices[i].get_text().strip()}),
            except:
                products.update({"Price": "No Price Mentioned"})

            products.update({"Purchase Link": links[i].get("href")})
            print(products)
            searchResult.append(products)
        context = {"Name": searchString.replace(
            "+", " "), "ProductList": searchResult}
    return render_template('search.html', context=context)


@app.route('/backtoSearch', methods=['POST', 'GET'])
@cross_origin()
def backtoSearch():
    global pageReviews
    global num
    global pt
    global page
    num = 30
    pageReviews = {}
    pt = 1
    page = 1
    return flask.redirect('/search', code=307)


@app.route('/searchNew', methods=['POST', 'GET'])
@cross_origin()
def searchNew():
    global pageReviews
    global num
    global pt
    global page
    global searchString
    num = 30
    pageReviews = {}
    pt = 1
    page = 1
    if searchString != request.form['content']:
        searchString = ''
    return flask.redirect('/search', code=307)


# route to show the review comments in a web UI
@app.route('/review', methods=['POST', 'GET'])
@cross_origin()
def index():
    global num
    global flag_prev
    global flag_next
    global pageReviews
    global page
    global pt
    global nextLink
    global searchString
    global ratingFilter

    reviews = []

    # ratingFilter = -1
    # # ratingFilter to be given value via html form in results html (maybe drop down menu)
    # # ratingFilter=1
    # # make sure to reset pageReviews = {}

    if request.method == 'POST':
        commentsLink = ''
        commRes = ''
        comm_html = ''
        prodName = ''
        try:
            if pageReviews == {} and page == 1:
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
                productLink = "https://www.flipkart.com" + \
                    request.form['link']  # box.div.div.div.a['href']
                prodRes = requests.get(productLink)
                prodRes.encoding = 'utf-8'
                prod_html = bs(prodRes.text, "html.parser")
                prodName = prod_html.findAll(
                    "span", {"class": "B_NuCI"})[0].text
                prodImage = prod_html.find(class_="_396cs4")
                prodPrice = prod_html.find(class_="_30jeq3")
                prodRating = prod_html.find(class_="_2d4LTz")
                comms = prod_html.findAll("div", {"class": "col JOpGWq"})
                commentsLink = "https://www.flipkart.com" + \
                    comms[0].find_all('a')[-1]['href']
                print(comms[0].find_all('a')[-1]['href'])
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
            pages = int(comm_html.find_all('div', {'class': '_2MImiq _1Qnn1K'})[
                        0].span.text.split()[-1].replace(',', ''))
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
                return render_template('results.html', reviews=pageReviews[page], flag_prev=flag_prev, flag_next=flag_next, page=page, prodName=prodName, prodImage=prodImage.get("src"), price=prodPrice.get_text().strip(), rating=prodRating.get_text().strip())

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
            return render_template('results.html', reviews=reviews, flag_prev=flag_prev, flag_next=flag_next, page=page, prodName=prodName, prodImage=prodImage.get("src"), price=prodPrice.get_text().strip(), rating=prodRating.get_text().strip())
        except Exception as e:
            print('The Exception message is: ', e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')


@app.route('/prev', methods=['POST', 'GET'])
def prev():
    global page
    #print('hello prev')
    page -= 1
    return flask.redirect('/review', code=307)


@app.route('/next', methods=['POST', 'GET'])
def next():
    global page
    global num
    num = 30
    #print('hello next')
    page += 1
    return flask.redirect('/review', code=307)


@app.route('/filterReviews', methods=['POST', 'GET'])
@cross_origin()
def filterReviews():
    global pageReviews
    global num
    global pt
    global page
    global searchString
    global filterReviews
    num = 30
    pageReviews = {}
    pt = 1
    page = 1
    filterReviews = request.args.get('filter')
    return flask.redirect('/review', code=307)


if __name__ == "__main__":
    #app.run(host='127.0.0.1', port=8001, debug=True)
    app.run(debug=True)
