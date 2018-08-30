#/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import urllib2,re, json
import datetime, time
from dateutil.parser import parse
try:
    from bs4 import BeautifulSoup
except ImportError:
    from BeautifulSoup import BeautifulSoup

reload(sys)
sys.setdefaultencoding( "utf-8" )

#2015年07月21日15:05
def parseStrDate(dateString):
    try:
        #print dateString
        if dateString.find(u"月")>0 and dateString.find(u"年")<0:
            dateString = u"%s年%s" % (datetime.datetime.now().year, dateString)
        dateString = dateString.replace(u"年","/").replace(u"月","/").replace(u"日"," ")
        #print dateString
        m = re.search(r'((19|20)\d{2})[\./\-_]{0,1}([0-3]{0,1}[0-9])[\./\-_]{0,1}([0-3]{0,1}[0-9])(\s|T)+([0-9]{0,2}[:]{0,1}[0-9]{0,2}[:]{0,1}[0-9]{0,2})', dateString)
        if m:
            #print m.group(0)
            dateTimeObj = parse(m.group(0), fuzzy=True)
            return dateTimeObj

        m = re.search(r'((19|20)\d{2})[\./\-_]{0,1}([0-3]{0,1}[0-9])[\./\-_]{0,1}([0-3]{0,1}[0-9])', dateString)
        if m:
            #print m.group(0)
            dateTimeObj = parse(m.group(0), fuzzy=True)
            return dateTimeObj
    except Exception,ex:
        #print ex
        pass
    return None

# Try to extract from the article URL - simple but might work as a fallback
def _extractFromURL(url):

    #Regex by Newspaper3k  - https://github.com/codelucas/newspaper/blob/master/newspaper/urls.py
    #m = re.search(r'([\./\-_]{0,1}(19|20)\d{2})[\./\-_]{0,1}(([0-3]{0,1}[0-9][\./\-_])|(\w{3,5}[\./\-_]))([0-3]{0,1}[0-9][\./\-]{0,1})?', url)
    m = re.search(r'((19|20)\d{2})[\./\-_]{0,1}([0-1][0-9])[\./\-_]{0,1}([0-3][0-9])', url)
    if m:
        return parseStrDate(m.group(0))
    return  None

    m = re.search(r'((19|20)\d{2})[\./\-_]{0,1}([0-1]{0,1}[0-9])[\./\-_]{0,1}([0-3]{0,1}[0-9])', url)
    if m:
        return parseStrDate(m.group(0))
    return  None

def _extractFromHtml(html):
    try:
        m = re.search(r'发表于\s*?((19|20)\d{2})[\./\-_]{0,1}([0-3]{0,1}[0-9])[\./\-_]{0,1}([0-3]{0,1}[0-9])\s+([0-9]{0,2}[:]{0,1}[0-9]{0,2}[:]{0,1}[0-9]{0,2})', html)
        if m:
            #print m.group(0)
            dateTimeObj = parse(m.group(0), fuzzy=True)
            return dateTimeObj

        m = re.search(r'发表于\s*?((19|20)\d{2})[\./\-_]{0,1}([0-3]{0,1}[0-9])[\./\-_]{0,1}([0-3]{0,1}[0-9])', html)
        if m:
            #print m.group(0)
            dateTimeObj = parse(m.group(0), fuzzy=True)
            return dateTimeObj
    except Exception,ex:
        #print ex
        pass
    return None


def _extractFromLDJson(parsedHTML):
    jsonDate = None
    try:
        script = parsedHTML.find('script', type='application/ld+json')

        if script is None:
            return None

        data = json.loads(script.text)

        try:
            jsonDate = parseStrDate(data['datePublished'])
        except Exception, e:
            pass

        try:
            jsonDate = parseStrDate(data['dateCreated'])
        except Exception, e:
            pass


    except Exception, e:
        return None

    return jsonDate


def _extractFromScript(parsedHTML):
    for script in parsedHTML.findAll('script'):
        #print script.text
        try:
            m = re.search(r'create.{0,20}((19|20)\d{2})[\./\-_]{0,1}([0-3]{0,1}[0-9])[\./\-_]{0,1}([0-3]{0,1}[0-9])\s+([0-9]{0,2}[:]{0,1}[0-9]{0,2}[:]{0,1}[0-9]{0,2})', script.text)
            if m:
                #print m.group(0)
                dateTimeObj = parse(m.group(0), fuzzy=True)
                return dateTimeObj

            m = re.search(r'publish.{0,20}((19|20)\d{2})[\./\-_]{0,1}([0-3]{0,1}[0-9])[\./\-_]{0,1}([0-3]{0,1}[0-9])\s+([0-9]{0,2}[:]{0,1}[0-9]{0,2}[:]{0,1}[0-9]{0,2})', script.text)
            if m:
                #print m.group(0)
                dateTimeObj = parse(m.group(0), fuzzy=True)
                return dateTimeObj

            m = re.search(r'create.{0,20}((19|20)\d{2})[\./\-_]{0,1}([0-3]{0,1}[0-9])[\./\-_]{0,1}([0-3]{0,1}[0-9])', script.text)
            if m:
                #print m.group(0)
                dateTimeObj = parse(m.group(0), fuzzy=True)
                return dateTimeObj

            m = re.search(r'publish.{0,20}((19|20)\d{2})[\./\-_]{0,1}([0-3]{0,1}[0-9])[\./\-_]{0,1}([0-3]{0,1}[0-9])', script.text)
            if m:
                #print m.group(0)
                dateTimeObj = parse(m.group(0), fuzzy=True)
                return dateTimeObj
        except:
            pass

    return None


def _extractFromMeta(parsedHTML):

    metaDate = None
    for meta in parsedHTML.findAll("meta"):
        metaName = meta.get('name', '').lower()
        itemProp = meta.get('itemprop', '').lower()
        httpEquiv = meta.get('http-equiv', '').lower()
        metaProperty = meta.get('property', '').lower()


        #<meta name="pubdate" content="2015-11-26T07:11:02Z" >
        if 'pubdate' == metaName:
            metaDate = meta['content'].strip()
            break


        #<meta name='publishdate' content='201511261006'/>
        if 'publishdate' == metaName:
            metaDate = meta['content'].strip()
            break

        #<meta name="timestamp"  data-type="date" content="2015-11-25 22:40:25" />
        if 'timestamp' == metaName:
            metaDate = meta['content'].strip()
            break

        #<meta name="DC.date.issued" content="2015-11-26">
        if 'dc.date.issued' == metaName:
            metaDate = meta['content'].strip()
            break

        #<meta property="article:published_time"  content="2015-11-25" />
        if 'article:published_time' == metaProperty:
            metaDate = meta['content'].strip()
            break
            #<meta name="Date" content="2015-11-26" />
        if 'date' == metaName:
            metaDate = meta['content'].strip()
            break

        #<meta property="bt:pubDate" content="2015-11-26T00:10:33+00:00">
        if 'bt:pubdate' == metaProperty:
            metaDate = meta['content'].strip()
            break
            #<meta name="sailthru.date" content="2015-11-25T19:56:04+0000" />
        if 'sailthru.date' == metaName:
            metaDate = meta['content'].strip()
            break

        #<meta name="article.published" content="2015-11-26T11:53:00.000Z" />
        if 'article.published' == metaName:
            metaDate = meta['content'].strip()
            break

        #<meta name="published-date" content="2015-11-26T11:53:00.000Z" />
        if 'published-date' == metaName:
            metaDate = meta['content'].strip()
            break

        #<meta name="article.created" content="2015-11-26T11:53:00.000Z" />
        if 'article.created' == metaName:
            metaDate = meta['content'].strip()
            break

        #<meta name="article_date_original" content="Thursday, November 26, 2015,  6:42 AM" />
        if 'article_date_original' == metaName:
            metaDate = meta['content'].strip()
            break

        #<meta name="cXenseParse:recs:publishtime" content="2015-11-26T14:42Z"/>
        if 'cxenseparse:recs:publishtime' == metaName:
            metaDate = meta['content'].strip()
            break

        #<meta name="DATE_PUBLISHED" content="11/24/2015 01:05AM" />
        if 'date_published' == metaName:
            metaDate = meta['content'].strip()
            break


        #<meta itemprop="datePublished" content="2015-11-26T11:53:00.000Z" />
        if 'datepublished' == itemProp:
            metaDate = meta['content'].strip()
            break


        #<meta itemprop="datePublished" content="2015-11-26T11:53:00.000Z" />
        if 'datecreated' == itemProp:
            metaDate = meta['content'].strip()
            break




        #<meta property="og:image" content="http://www.dailytimes.com.pk/digital_images/400/2015-11-26/norway-return-number-of-asylum-seekers-to-pakistan-1448538771-7363.jpg"/>
        if 'og:image' == metaProperty or "image" == itemProp:
            url = meta['content'].strip()
            #print url
            possibleDate = _extractFromURL(url)
            if possibleDate is not None:
                return  possibleDate


        #<meta http-equiv="data" content="10:27:15 AM Thursday, November 26, 2015">
        if 'date' == httpEquiv:
            metaDate = meta['content'].strip()
            break

    if metaDate is not None:
        return parseStrDate(metaDate)

    return None

def _extractFromHTMLTag(parsedHTML):
    #<time>
    for t in parsedHTML.findAll("time"):
        dt = t.get('datetime', '')
        if len(dt) > 0:
            return parseStrDate(dt)

        dt = t.get('class', '')
        if len(dt) > 0 and dt[0].lower() == "timestamp":
            return parseStrDate(t.string)


    tag = parsedHTML.find("span", {"itemprop": "datePublished"})
    if tag is not None:
        dateText = tag.get("content")
        if dateText is None:
            dateText = tag.text
        if dateText is not None:
            return parseStrDate(dateText)

    #class=
    for tag in parsedHTML.find_all(['span', 'p','div', 'abbr', 'strong', 'article'], class_=re.compile("pubdate|timestamp|article_date|articledate|date|time|pubtime|article-source|article_info|tm|article",re.IGNORECASE)):
        dateText = tag.string
        if dateText is None:
            dateText = tag.text
        #print "str1: %s" % dateText.strip()
        possibleDate = parseStrDate(dateText)

        if possibleDate is not None:
            return  possibleDate

        for key,value in tag.attrs.items():
            if key.lower().find("date") >=0 or key.lower().find("time") >=0:
                #print value
                try:
                    d = int(value)
                    if d > 100000000 * 1000:
                        d = d / 1000
                    possibleDate = datetime.datetime(*tuple(time.localtime(d))[:6])
                    if possibleDate.year > 1990 and possibleDate.year < 2099:
                        return possibleDate
                except:
                    pass

    for tag in parsedHTML.find_all(['span', 'p','div', 'abbr','strong', 'article'], id=re.compile("pubdate|timestamp|article_date|articledate|date|time|pubtime|article-source|article_info|tm|article",re.IGNORECASE)):
        dateText = tag.string
        if dateText is None:
            dateText = tag.text
        #print "str2: %s" % dateText.strip()
        possibleDate = parseStrDate(dateText)

        if possibleDate is not None:
            return  possibleDate

        for key,value in tag.attrs.items():
            if key.lower().find("date") >=0 or key.lower().find("time") >=0:
                #print value
                try:
                    d = int(value)
                    if d > 100000000 * 1000:
                        d = d / 1000
                    possibleDate = datetime.datetime(*tuple(time.localtime(d))[:6])
                    if possibleDate.year > 1990 and possibleDate.year < 2099:
                        return possibleDate
                except:
                    pass

    return None



def extractArticlePublishedDate(articleLink, html = None):

    #print "Extracting date from " + articleLink

    articleDate = None

    try:
        articleDate = _extractFromURL(articleLink)
        #print "from url: %s" % articleDate

        if html is None:
            request = urllib2.Request(articleLink)
            # Using a browser user agent, decreases the change of sites blocking this request - just a suggestion
            request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36')
            html = urllib2.build_opener().open(request).read()

        parsedHTML = BeautifulSoup(html,"lxml")

        possibleDate = _extractFromLDJson(parsedHTML)
        #print "1"

        if possibleDate is None:
            #print "2"
            possibleDate = _extractFromMeta(parsedHTML)

        if possibleDate is None:
            #print "3"
            possibleDate = _extractFromHTMLTag(parsedHTML)
        if possibleDate is None:
            #print "4"
            possibleDate = _extractFromHtml(html)
        if possibleDate is None:
            #print "5"
            possibleDate = _extractFromScript(parsedHTML)

        #print "possibleDate: ", possibleDate
        if possibleDate is not None:
            articleDate = possibleDate
            #print "from html: %s" % articleDate

    except Exception as e:
        print "Exception in extractArticlePublishedDate for " + articleLink
        print e



    return articleDate


if __name__ == '__main__':
    d = extractArticlePublishedDate(sys.argv[1])
    print d