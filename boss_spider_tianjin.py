from cefpython3 import cefpython as cef

import sys
import traceback
#import time
import random
#import _thread
from bs4 import BeautifulSoup
from io import StringIO
import platform
import time



def gen_file_name():
    return "{}.json".format(time.strftime('%Y%m%d%H%M%S', time.localtime()))


class RequestHandler(object):
    def OnBeforeResourceLoad(self, browser, frame, request):
        url = request.GetUrl()
        print("OnBeforeResourceLoad", url)
        try:
            print("headers", request.GetHeaderMap())
            print('postdata', request.GetPostData())

        except Exception as ex:
            print(ex)

        return False

    def CanGetCookies(self, frame, request, **_):
        # There are multiple iframes on that website, let's log
        # cookies only for the main frame.
        if frame.IsMain():
            pass
            #print("-- CanGetCookies #" )
            #print("url=" + request.GetUrl())
            #print("")

        # Return True to allow reading cookies or False to block
        return True

    def CanSetCookie(self, frame, request, cookie, **_):
        # There are multiple iframes on that website, let's log
        # cookies only for the main frame.
        if frame.IsMain():
            pass
            #print("-- CanSetCookie @" )
            #print("url=" + request.GetUrl())
            #print("Name=" + cookie.GetName())
            #print("Value=" + cookie.GetValue())
            #print("")

        # Return True to allow setting cookie or False to block
        return True


def print_dir(o):
    for item in dir(o):
        print(item)

def check_versions():
    ver = cef.GetVersion()
    print("CEF Python {ver}".format(ver=ver["version"]))
    print("Chromium {ver}".format(ver=ver["chrome_version"]))
    print("CEF {ver}".format(ver=ver["cef_version"]))
    print("Python {ver} {arch}".format(
           ver=platform.python_version(),
           arch=platform.architecture()[0]))
    assert cef.__version__ >= "57.0", "CEF Python v57.0+ required to run this"

def main():
    check_versions()
    sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
    # To change user agent use either "product_version"
    # or "user_agent" options. Explained in Tutorial in
    # "Change user agent string" section.
    settings = {
        #"debug": True
        # "product_version": "MyProduct/10.00",
        # "user_agent": "MyAgent/20.00 MyProduct/10.00",
    }
    cef.Initialize(settings=settings)
    #set_global_handler()
    browser = cef.CreateBrowserSync(url="https://www.zhipin.com/beijing",
                                    window_title="zhipin spider")

    print_dir(browser)
    set_javascript_bindings(browser)
    bs4_visitor = Bs4Visitor(browser)
    browser.SetClientHandler(LoadHandler(bs4_visitor))
    browser.SetClientHandler(RequestHandler())

    cef.MessageLoop()
    cef.Shutdown()

def py_print(content):
    print(content)

def set_javascript_bindings(browser):
    #external = External(browser)
    bindings = cef.JavascriptBindings(
            bindToFrames=False, bindToPopups=False)
    #bindings.SetProperty("python_property", "This property was set in Python")
    #bindings.SetProperty("cefpython_version", cef.GetVersion())
    bindings.SetFunction("py_print", py_print)
    #bindings.SetObject("external", external)
    browser.SetJavascriptBindings(bindings)

# 使用bs4解析 Visitor
class Bs4Visitor(object):

    def __init__(self, browser, next_page_delay = 20):
        self.browser = browser
        self.current_url = browser.GetUrl()
        self.next_url = None
        self.delay = next_page_delay
        self.file_handle = open(gen_file_name(), 'a')
        self.keywords = iter((u'大数据',u'大数据架构师',u'大数据技术总监',u'技术总监',u'cto',u'技术合伙人',u'大数据讲师',u'python',u'java',u'前端',u'架构师',))
        self.citys = iter(('tianjin','beijing','shanghai','guangzhou','shenzhen','chengdu','chongqing',))


    def next_keyword(self):
        try:
            return next(self.keywords)
        except StopIteration as stop:
            print("遍历关键字结束")
            return None


    def _close(self):
        if self.file_handle:
            self.file_handle.close()

    def Visit(self, value):
        try:
            self._visit(value)
        except:
            print(traceback.print_exc())
            self._close()
        finally:
            pass

    def clean(self, job):
        new_job = {}
        for k, v in job.items():
            v = v.strip()
            v = ''.join([line.strip() for line in StringIO(v).readlines() if line.strip()])
            new_job[k] = v
        return new_job

    def parse_job(self, tag):
        try:
            return self._parse_job(tag)
        except :
            if hasattr(tag, 'prettify'):
                print(traceback.print_exc())
                #print(tag.prettify())

    def _parse_job(self, tag):

        #print(tag.prettify())
        job = {}
        primary_box = tag.find('div', 'primary-box')
        # href="/job_detail/ba4ffd2a1c13f2d903V6092-FVY~.html"
        job['url'] = primary_box['href']
        # data-jobid="41080354"
        job['id'] = primary_box['data-jobid']
        job_title = tag.find('div', class_='job-title')
        # print(job_title.prettify())

        job_name = job_title.find('span', 'job-name')
        job['title'] = job_name.get_text()

        job['area'] = job_title.find("span", 'job-area').get_text()

        job_limit = tag.find("div", class_=["job-limit", "clearfix"])
        job['salary'] = job_limit.find('span', 'red').string
        job['requirements'] = job_limit.find('p').get_text()

        company = tag.find('div', 'company-text')
        job['company'] = company.find('h3', 'name').get_text()
        job['company_desc'] = company.find('p').get_text()

        other = tag.find('div', class_=["info-append"])
        tags = other.find_all('span', 'tag-item')
        job['job_desc'] = ",".join([t.get_text() for t in tags])
        job['welfare'] = other.find('div', 'info-desc').get_text()
        return job

    def _visit(self, value):
        soup = BeautifulSoup(value, 'html.parser')
        # 所有页面都有这个main div
        #
        #tags = soup.find_all(id='main')
        #<class 'bs4.element.ResultSet'>，这个是一个列表类
        #print(type(tag))

        tag = soup.find('div', class_="job-list")
        # 如果找不到 返回None


        if tag:
            #bs4.element.Tag
            ul = tag.find('ul')
            #print(ul.prettify())
            if ul:
                li_arr = tag.findChildren('li')
                if len(li_arr) > 0:
                    for li in li_arr:
                        job = self.parse_job(li)
                        print(job, file=self.file_handle)
            self.click_next_page(soup)
            return True
        else:
            return False

            # 点击下一页

    def click_next_page(self, soup):
        print('click_next_page')
        # soup.find('div', class_="page")
        # ka="page-next"
        # <a href="javascript:;" ka="page-next" class="next disabled"></a>
        # <a href="/c101030100-p100109/?page=2" ka="page-next" class="next"></a>
        next_page = soup.find('a', attrs={"ka": "page-next"})
        if not next_page:
            pass
            # 关闭资源
            # self.browser.CloseBrowser(True)
            #self._close()
            #cef.QuitMessageLoop()
            #sys.exit(0)
        else:
            href = next_page['href']
            print('next_page', href)
            if href == 'javascript:;':
                # 手动输入下一个关键字进行查询
                keyword = self.next_keyword()
                print("下一个关键字是：%s" % (keyword,))
                if keyword:
                    self.browser.ExecuteJavascript('''
                        function next_keyword(){
                          try {
                            py_print($('.ipt-search').html());
                            $('.ipt-search').val('%s');
                            $('.position-sel>.label-text>b').text('职位类型');
                            $('.industry-sel>.label-text>b').text('公司行业');
                            $('input[type=hidden].industry-code').val('');
                            $('input[type=hidden].position-code').val('');                            
                            $('button.btn.btn-search').click();                                                                                         
                          }catch(err){
                            py_print("error:" + err)
                          }  
                        }
                        //delay 1 minus
                        setTimeout(next_keyword, 60000);
                        '''%(keyword,))
                else:
                    # exit
                    print("finished !!!")


                #self.browser.CloseBrowser(True)
                #self._close()
                #cef.Shutdown()
                # 关闭资源
                #sys.exit(1)
            else:
                # Navigate
                next_url = "http://www.zhipin.com" + href
                current_url = self.browser.GetUrl()
                #print('next_url', next_url, 'current_url', current_url)
                if current_url != next_url:
                    sleep = random.randint(5, self.delay)
                    #self.browser.ExecuteJavascript("alert('cefpython running!');")
                    js = """                      
                      function next_page() {
                        try {
                          //alert(location.href);
                          location.href = '%s';                          
                        } catch(err){
                          alert(err); // 可执行
                        }
                      }
                      //delay 10second
                      setTimeout(next_page, 10000);
                    """ % next_url
                    #print(js)
                    self.browser.ExecuteJavascript(js)
                    self.browser.ExecuteJavascript('''
                       try {
                         py_print($('.next').html());            
                         //alert(next_page);
                         //next_page.click();
                       }catch(err){
                         
                         alert("error:" + err)
                       }  ''')

                # _thread.start_new_thread(self.browser.LoadUrl, ("http://www.zhipin.com" + href,))
                #_thread.start_new_thread(self.browser.LoadUrl, ("http://www.baidu.com",))




# 加载完成事件
class LoadHandler(object):

    def __init__(self, bs4_visitor):
        self.visitor = bs4_visitor

    def OnLoadingStateChange(self, browser, is_loading, **_):
        #https://www.zhipin.com/tianjin/
        if not is_loading:
            #print(is_loading)
            print('加载完成', browser.GetUrl())
            #browser.ExecuteJavascript("""document.write("<script src='https://cdn.bootcss.com/jquery/3.4.1/jquery.min.js'></script>");""")
            #browser.ExecuteFunction("alert","加载完b成")
            #https://cdn.bootcss.com/jquery/3.4.1/jquery.min.js
            #browser.ExecuteFunction("alert","加载完成")
            frame = browser.GetFocusedFrame()
            frame.GetSource(self.visitor)

    def OnLoadEnd(self,browser, frame, http_code):
        print(frame, http_code)
        #frame = browser.GetFocusedFrame()
        #frame.GetSource(self.visitor)

if __name__ == '__main__':
    #pdb.run('main()')
    main()