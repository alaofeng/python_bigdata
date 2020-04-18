# Tutorial example. Doesn't depend on any third party GUI framework.
# Tested with CEF Python v57.0+

from cefpython3 import cefpython as cef
import base64
import platform
import sys
import threading
import pdb
import traceback
import time
import random
import _thread

import atexit
import signal


from bs4 import BeautifulSoup
from io import StringIO


# HTML code. Browser will navigate to a Data uri created
# from this html code.
HTML_code = """
<!DOCTYPE html>
<html>
<head>
    <style type="text/css">
    body,html { font-family: Arial; font-size: 11pt; }
    div.msg { margin: 0.2em; line-height: 1.4em; }
    b { background: #ccc; font-weight: bold; font-size: 10pt;
        padding: 0.1em 0.2em; }
    b.Python { background: #eee; }
    i { font-family: Courier new; font-size: 10pt; border: #eee 1px solid;
        padding: 0.1em 0.2em; }
    </style>
    <script>
    function js_print(lang, event, msg) {
        msg = "<b class="+lang+">"+lang+": "+event+":</b> " + msg;
        console = document.getElementById("console")
        console.innerHTML += "<div class=msg>"+msg+"</div>";
    }
    function js_callback_1(ret) {
        js_print("Javascript", "html_to_data_uri", ret);
    }
    function js_callback_2(msg, py_callback) {
        js_print("Javascript", "js_callback", msg);
        py_callback("String sent from Javascript");
    }
    window.onload = function(){
        js_print("Javascript", "window.onload", "Called");
        js_print("Javascript", "python_property", python_property);
        js_print("Javascript", "navigator.userAgent", navigator.userAgent);
        js_print("Javascript", "cefpython_version", cefpython_version.version);
        html_to_data_uri("test", js_callback_1);
        external.test_multiple_callbacks(js_callback_2);
    };
    </script>
</head>
<body>
    <h1>Tutorial example</h1>
    <div id="console"></div>
</body>
</html>
"""


def main():
    check_versions()
    sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
    # To change user agent use either "product_version"
    # or "user_agent" options. Explained in Tutorial in
    # "Change user agent string" section.
    settings = {
        # "product_version": "MyProduct/10.00",
        # "user_agent": "MyAgent/20.00 MyProduct/10.00",
    }
    cef.Initialize(settings=settings)
    #set_global_handler()
    #browser = cef.CreateBrowserSync(url=html_to_data_uri(HTML_code),
    #                                window_title="Tutorial")
    browser = cef.CreateBrowserSync(url="http://www.zhipin.com")
    print_dir(browser)
    #browser = cef.CreateBrowserSync(url="http://www.zhipin.com")
    #set_client_handlers(browser)
    #set_javascript_bindings(browser)
    bs4_visitor = Bs4Visitor(browser)

    browser.SetClientHandler(LoadHandler(bs4_visitor))

    cef.MessageLoop()
    cef.Shutdown()


def check_versions():
    ver = cef.GetVersion()
    print("CEF Python {ver}".format(ver=ver["version"]))
    print("Chromium {ver}".format(ver=ver["chrome_version"]))
    print("CEF {ver}".format(ver=ver["cef_version"]))
    print("Python {ver} {arch}".format(
           ver=platform.python_version(),
           arch=platform.architecture()[0]))
    assert cef.__version__ >= "57.0", "CEF Python v57.0+ required to run this"


def html_to_data_uri(html, js_callback=None):
    # This function is called in two ways:
    # 1. From Python: in this case value is returned
    # 2. From Javascript: in this case value cannot be returned because
    #    inter-process messaging is asynchronous, so must return value
    #    by calling js_callback.
    html = html.encode("utf-8", "replace")
    b64 = base64.b64encode(html).decode("utf-8", "replace")
    ret = "data:text/html;base64,{data}".format(data=b64)
    if js_callback:
        js_print(js_callback.GetFrame().GetBrowser(),
                 "Python", "html_to_data_uri",
                 "Called from Javascript. Will call Javascript callback now.")
        js_callback.Call(ret)
    else:
        return ret


def set_global_handler():
    # A global handler is a special handler for callbacks that
    # must be set before Browser is created using
    # SetGlobalClientCallback() method.
    # GlobalHandler 是自定义的
    global_handler = GlobalHandler()
    #可以设置一些全局的函数
    cef.SetGlobalClientCallback("OnAfterCreated",
                                global_handler.OnAfterCreated)


# 绑定一些浏览器事件
def set_client_handlers(browser):
    #client_handlers = [LoadHandler(), DisplayHandler()]
    #for handler in client_handlers:
    #    browser.SetClientHandler(handler)
    #browser.SetClientHandler(LoadHandler())
    pass


def set_javascript_bindings(browser):
    external = External(browser)
    bindings = cef.JavascriptBindings(
            bindToFrames=False, bindToPopups=False)
    bindings.SetProperty("python_property", "This property was set in Python")
    bindings.SetProperty("cefpython_version", cef.GetVersion())
    bindings.SetFunction("html_to_data_uri", html_to_data_uri)
    bindings.SetObject("external", external)
    browser.SetJavascriptBindings(bindings)

# 执行一个js函数
def js_print(browser, lang, event, msg):
    # Execute Javascript function "js_print"
    #browser.ExecuteFunction("js_print", lang, event, msg)
    pass


class GlobalHandler(object):
    def OnAfterCreated(self, browser, **_):
        """Called after a new browser is created."""
        # DOM is not yet loaded. Using js_print at this moment will
        # throw an error: "Uncaught ReferenceError: js_print is not defined".
        # We make this error on purpose. This error will be intercepted
        # in DisplayHandler.OnConsoleMessage.
        js_print(browser, "Python", "OnAfterCreated",
                 "This will probably never display as DOM is not yet loaded")
        # Delay print by 0.5 sec, because js_print is not available yet
        args = [browser, "Python", "OnAfterCreated",
                "(Delayed) Browser id="+str(browser.GetIdentifier())]
        threading.Timer(0.5, js_print, args).start()

# 使用bs4解析 Visitor
class Bs4Visitor(object):

    def __init__(self, browser, next_page_delay = 20):
        self.browser = browser
        self.delay = next_page_delay
        self.file_handle = open("jobs.txt", 'a')

   #
    def _close(self):
        self.file_handle.close()


    def quit(self, signum, frame):
        print('catched singal: %d' % signum)
        self._close()

    # 点击下一页
    def _click_next_page(self):
        random.randint(5, self.delay)
        time.sleep(self.delay)
        # <a href = "javascript:;" ka = "page-next" class ="next disabled" > < / a >
        if self.browser.ExecuteJavascript:
            self.browser.ExecuteJavaScript('''
            next_page = document.getElementsByClassName("next");            
            alert(next_page);
            next_page.click();    
            ''')

    # 点击下一页
    def click_next_page(self, soup):
        print('click_next_page')

        #soup.find('div', class_="page")
        # ka="page-next"
        # <a href="javascript:;" ka="page-next" class="next disabled"></a>
        # <a href="/c101030100-p100109/?page=2" ka="page-next" class="next"></a>
        next_page = soup.find('a', attrs={"ka":"page-next"})
        if not next_page:
            # 关闭资源
            self.browser.CloseBrowser(True)
            self._close()
            cef.QuitMessageLoop()
            sys.exit(0)


        href = next_page['href']
        print('next_page', href)
        if href == 'javascript:;':
            self.browser.CloseBrowser(True)
            self._close()
            #关闭资源
            sys.exit(1)
        else:
            sleep = random.randint(5, self.delay)
            time.sleep(sleep * 1000)

            #Navigate
            print( 'self.browser.LoadUrl("http://www.zhipin.com" + href)')
            #_thread.start_new_thread(self.browser.LoadUrl, ("http://www.zhipin.com" + href,))
            _thread.start_new_thread(self.browser.LoadUrl, ("http://www.baidu.com",))



    def get_tag_value(self, tag):
        if tag and hasattr(tag, 'get_text'):
            return tag.get_text()
        else:
            return None

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

    def Visit(self, value):
        try:
            self._visit(value)
        except:
            print(traceback.print_exc())
            self._close()
        finally:
            pass


    def _visit(self, value):
        soup = BeautifulSoup(value, 'html.parser')
        # 所有页面都有这个main方法
        #
        #tags = soup.find_all(id='main')
        #<class 'bs4.element.ResultSet'>，这个是一个列表类
        #print(type(tag))

        tag = soup.find('div', class_="job-list")
        # 如果找不到 返回None


        if tag:
            #bs4.element.Tag
            '''
            find、findAll、findAllNext、findAllPrevious、findChild、findChildren、findNext、findNextSibling、findNextSiblings、findParent
            findParents
            findPrevious
            findPreviousSibling
            findPreviousSiblings
            find_all
            find_all_next
            find_all_previous
            find_next
            find_next_sibling
            find_next_siblings、find_parent、find_parents、find_previous、find_previous_sibling、find_previous_siblings
            '''
            #print(type(tag))
            #print_dir(tag)
            #print(tag)
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










# 加载完成事件
class LoadHandler(object):

    def __init__(self, bs4_visitor):
        self.visitor = bs4_visitor


    def OnLoadingStateChange(self, browser, is_loading, **_):
        """Called when the loading state has changed."""
        #print('OnLoadingStateChange')
        frame = browser.GetFocusedFrame()
        #print(frame)
        #print_dir(frame)
        #mainFrame = browser.GetMainFrame()
        frame.GetSource(self.visitor)
        #print(frame.GetName())

        if not is_loading:
            # 由此获取document模型，进一步获取文档信息
            print(is_loading)
            # Loading is complete. DOM is ready.
            #js_print(browser, "Python", "OnLoadingStateChange",
            #         "Loading is complete")
            #print(**_)


class DisplayHandler(object):
    def OnConsoleMessage(self, browser, message, **_):
        """Called to display a console message."""
        # This will intercept js errors, see comments in OnAfterCreated
        if "error" in message.lower() or "uncaught" in message.lower():
            # Prevent infinite recurrence in case something went wrong
            if "js_print is not defined" in message.lower():
                if hasattr(self, "js_print_is_not_defined"):
                    print("Python: OnConsoleMessage: "
                          "Intercepted Javascript error: "+message)
                    return
                else:
                    self.js_print_is_not_defined = True
            # Delay print by 0.5 sec, because js_print may not be
            # available yet due to DOM not ready.
            args = [browser, "Python", "OnConsoleMessage",
                    "(Delayed) Intercepted Javascript error: <i>{error}</i>"
                    .format(error=message)]
            threading.Timer(0.5, js_print, args).start()


def print_dir(o):
    for item in dir(o):
        print(item)


class External(object):
    def __init__(self, browser):
        self.browser = browser

    def test_multiple_callbacks(self, js_callback):
        """Test both javascript and python callbacks."""
        js_print(self.browser, "Python", "test_multiple_callbacks",
                 "Called from Javascript. Will call Javascript callback now.")

        def py_callback(msg_from_js):
            js_print(self.browser, "Python", "py_callback", msg_from_js)
        js_callback.Call("String sent from Python", py_callback)




if __name__ == '__main__':
    #pdb.run('main()')
    main()