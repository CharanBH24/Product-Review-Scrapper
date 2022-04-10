import flask
from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq

#Global variables
# total number of reviews per page
num = 30
flag_prev = 0
flag_next = 0
pageReviews = {}
page = 1
pt=1
nextLink = ''
searchString = ''
searchResult = []
ratingFilter = -1

app = Flask(__name__)

@app.route('/',methods=['POST','GET'])  # route to display the home page
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

@app.route('/search', methods=['POST','GET'])
@cross_origin()
def search():
    print(1)
    global pageReviews
    global searchString
    global searchResult
    global num
    global pt
    num=30
    pageReviews={}
    pt=1
    if searchString=='':
        searchString= request.form['content']
        flipkart_url = "https://www.flipkart.com/search?q=" + searchString.replace(" ","")
        uClient = uReq(flipkart_url)
        flipkartPage = uClient.read()
        uClient.close()
        flipkart_html = bs(flipkartPage, "html.parser")
        names = flipkart_html.findAll("div", {"class": "_4rR01T"})
        prices = flipkart_html.findAll("div", {"class": "_30jeq3 _1_WHN1"})
        features = flipkart_html.findAll("ul", {"class": "_1xgFaf"})
        links = flipkart_html.findAll("div", {"class": "_2kHMtA"})
        searchResult=[]
        for i in range(24):
            searchResult.append({'name':names[i].text,'price':prices[i].text,'features':[i.text for i in features[i].findAll("li")],'link':links[i].a['href']})
    return render_template('search.html', searchResult=searchResult, searchString=searchString)

@app.route('/backtoSearch', methods=['POST','GET'])
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

@app.route('/searchNew', methods=['POST','GET'])
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

@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
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
        prodName=''
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
                productLink = "https://www.flipkart.com" + request.args.get('link')#box.div.div.div.a['href']
                prodRes = requests.get(productLink)
                prodRes.encoding='utf-8'
                prod_html = bs(prodRes.text, "html.parser")
                prodName=prod_html.findAll("span", {"class": "B_NuCI"})[0].text
                comms=prod_html.findAll("div", {"class": "col JOpGWq"})
                commentsLink = "https://www.flipkart.com" + comms[0].find_all('a')[-1]['href']
                print(comms[0].find_all('a')[-1]['href'])
                commRes = requests.get(commentsLink)
                commRes.encoding='utf-8'
                comm_html = bs(commRes.text, "html.parser")

            else:
                commentsLink=nextLink
                commRes = requests.get(commentsLink)
                commRes.encoding = 'utf-8'
                comm_html = bs(commRes.text, "html.parser")

            # Total number of pages in reviews
            print('1')
            pages = int(comm_html.find_all('div', {'class': '_2MImiq _1Qnn1K'})[0].span.text.split()[-1].replace(',',''))
            currPage=int(comm_html.find_all('div', {'class': '_2MImiq _1Qnn1K'})[0].span.text.split()[1].replace(',',''))
            if pages==currPage:
                flag_next = 0
            else:
                flag_next = 1

            if page == 1:
                flag_prev = 0
            else:
                flag_prev = 1

            print('2')
            if page in pageReviews.keys():
                return render_template('results.html', reviews=pageReviews[page], flag_prev=flag_prev, flag_next=flag_next, page=page, prodName=prodName)

            while num > 0 and pages > 1:
                print('3')
                #commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})
                commentboxes = comm_html.find_all('div', {'class': "col"})
                print(len(commentboxes))

                for i in range(pt,len(commentboxes),2):
                    commentbox=commentboxes[i]
                    try:
                        #name.encode(encoding='utf-8')
                        name = commentbox.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text


                    except:
                        name = 'No Name'

                    try:
                        #rating.encode(encoding='utf-8')
                        #rating = commentbox.div.div.div.div.text
                        rating = commentbox.div.div.div.text


                    except:
                        rating = 'No Rating'

                    try:
                        #commentHead.encode(encoding='utf-8')
                        #commentHead = commentbox.div.div.div.p.text
                        commentHead = commentbox.div.div.p.text

                    except:
                        commentHead = 'No Comment Heading'
                    try:
                        comtag = commentbox.div.find_all('div', {'class': ''})
                        #custComment.encode(encoding='utf-8')
                        custComment = comtag[0].div.text
                    except Exception as e:
                        print("Exception while creating dictionary: ",e)

                    mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                              "Comment": custComment}

                    #filtering outliers or as according to rating filter
                    if (mydict["Rating"] != 'No Rating' and ratingFilter==-1) or mydict["Rating"] == str(ratingFilter):
                        reviews.append(mydict)
                        num-=1 #number of reviews to be limited to 30 per page
                    pt=i
                    if num == 0:
                        break

                if pt<len(commentboxes)-1:
                    nextLink=commentsLink
                    print(nextLink)
                #code for going next reviews page
                commentsLink = "https://www.flipkart.com" + comm_html.find_all('a', {'class': '_1LKTO3'})[-1]['href']
                commRes = requests.get(commentsLink)
                commRes.encoding = 'utf-8'
                comm_html = bs(commRes.text, "html.parser")
                pages-=1
                if pt == len(commentboxes)-1:
                    pt=1
                    nextLink=commentsLink
                    print(nextLink)

            if pageReviews != {} and page != 1:
                reviews=reviews[1:]
            pageReviews[page]=reviews
            return render_template('results.html', reviews=reviews, flag_prev=flag_prev, flag_next=flag_next, page=page, prodName=prodName)
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')

@app.route('/prev',methods=['POST','GET'])
def prev():
    global page
    #print('hello prev')
    page-=1
    return flask.redirect('/review', code=307)

@app.route('/next',methods=['POST','GET'])
def next():
    global page
    global num
    num=30
    #print('hello next')
    page+=1
    return flask.redirect('/review', code=307)

@app.route('/filterReviews', methods=['POST','GET'])
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
    filterReviews=request.args.get('filter')
    return flask.redirect('/review', code=307)

if __name__ == "__main__":
    #app.run(host='127.0.0.1', port=8001, debug=True)
    app.run(debug=True)
