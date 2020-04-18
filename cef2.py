# Tutorial example. Doesn't depend on any third party GUI framework.
# Tested with CEF Python v57.0+

from cefpython3 import cefpython as cef
import base64
import platform
import sys
import threading
import pdb
import traceback




# HTML code. Browser will navigate to a Data uri created
# from this html code.


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
    #browser = cef.CreateBrowserSync(url="http://www.zhaopin.com")
    browser = cef.CreateBrowserSync(url="http://www.baidu.com")

    js_binding(browser)
    bs4_visitor = Bs4Visitor()
    browser.SetClientHandler(LoadHandler(bs4_visitor))
    # browser.SetClientHandler(ResourceHandler())
    browser.SetClientHandler(RequestHandler())

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

def js_binding(browser):
    bindings = cef.JavascriptBindings()
    bindings.SetFunction("py_function", py_print)
    bindings.SetFunction("py_callback", py_callback)
    browser.SetJavascriptBindings(bindings)

# *args变长值参数，**kwargs 变长关键字参数
def py_print(value, js_callback):
    print("Value sent from Javascript: " + value)
    js_callback.Call("I am a Python string #2", py_callback)

def _py_print(*args, **kwargs):
    if args:
        print(args)
    if kwargs:
        print(kwargs)

def py_callback(value):
    print("Value sent from Javascript: "+value)

# 使用bs4解析 Visitor
class Bs4Visitor(object):

    def Visit(self, value):
        try:
            self._visit(value)
        except:
            print(traceback.print_exc())
            self._close()
        finally:
            pass


    def _visit(self, value):
        pass


class RequestHandler(object):
    def __init__(self):
        self.getcount = 0
        self.setcount = 0
        self.resHandler = None

    '''
        def GetResourceHandler(self, browser, frame, request):
        #print(kwargs)
        #request = kwargs.get("request")
        print("GetResourceHandler(): url = %s" % request.GetUrl())
        resHandler = ResourceHandler()
        resHandler._clientHandler = self
        resHandler._browser = browser
        resHandler._frame = frame
        resHandler._request = request
        self._AddStrongReference(resHandler)
        return resHandler

    '''
    def OnBeforeResourceLoad(self, browser, frame, request):
        print("OnBeforeResourceLoad", request.GetUrl())
        return False


    def OnQuotaRequest(self, browser, origin_url, new_size, callback):
        print(origin_url, new_size, callback)
        return True

    def CanGetCookies(self, frame, request, **_):
        # There are multiple iframes on that website, let's log
        # cookies only for the main frame.
        if frame.IsMain():
            self.getcount += 1
            print("-- CanGetCookies #" + str(self.getcount))
            print("url=" + request.GetUrl()[0:80])
            print("")
        # Return True to allow reading cookies or False to block
        return True

    def CanSetCookie(self, frame, request, cookie, **_):
        # There are multiple iframes on that website, let's log
        # cookies only for the main frame.
        if frame.IsMain():
            self.setcount += 1
            print("-- CanSetCookie @" + str(self.setcount))
            print("url=" + request.GetUrl()[0:80])
            print("Name=" + cookie.GetName())
            print("Value=" + cookie.GetValue())
            print("")

        # Return True to allow setting cookie or False to block
        return True

    _resourceHandlers = {}
    _resourceHandlerMaxId = 0

    def _AddStrongReference(self, resHandler):
        self._resourceHandlerMaxId += 1
        resHandler._resourceHandlerId = self._resourceHandlerMaxId
        self._resourceHandlers[resHandler._resourceHandlerId] = resHandler

    def _ReleaseStrongReference(self, resHandler):
        if resHandler._resourceHandlerId in self._resourceHandlers:
            del self._resourceHandlers[resHandler._resourceHandlerId]
        else:
            print("_ReleaseStrongReference() FAILED: resource handler " \
                  "not found, id = %s" % (resHandler._resourceHandlerId))


class ResourceHandler(object):
    '''
    2020.4.3
    试图拦截分析后台请求内容，分析出json数据
    '''

    _resourceHandlerId = None
    _clientHandler = None
    _browser = None
    _frame = None
    _request = None
    _responseHeadersReadyCallback = None
    _webRequest = None
    _webRequestClient = None
    _offsetRead = 0

    def ProcessRequest(self, request, callback):
        '''

        :param request:
        :param callback:
        :return:
        '''
        print("ProcessRequest, 发起请求")
        print("GetUrl", request.GetUrl())
        print("GetFirstPartyForCookies", request.GetFirstPartyForCookies())
        #print("GetTransitionType", request.GetTransitionType())
        print("GetFlags", request.GetFlags())
        print("GetMethod", request.GetMethod())
        print("headers",request.GetHeaderMap())
        print('postdata', request.GetPostData())
        callback.Continue()

        print("ProcessRequest()")
        # 1. Start the request using WebRequest
        # 2. Return True to handle the request
        # 3. Once response headers are ready call
        #    callback.Continue()
        self._responseHeadersReadyCallback = callback
        self._webRequestClient = WebRequestClient()
        self._webRequestClient._resourceHandler = self
        # Need to set AllowCacheCredentials and AllowCookies for
        # the cookies to work during POST requests (Issue 127).
        # To skip cache set the SkipCache request flag.
        request.SetFlags(cef.Request.Flags["AllowCachedCredentials"] \
                         | cef.Request.Flags["AllowCookies"])
        # A strong reference to the WebRequest object must kept.
        self._webRequest = cef.WebRequest.Create(
            request, self._webRequestClient)
        return True

    def GetResponseHeaders(self, response, responseLengthOut, redirectUrlOut):
        '''

        :param response:
        :param response_length_out:list[int]
        :param redirect_url_out:list[string]
        :return:
        '''
        #print("GetResponseHeaders， 请求返回")
        #print("GetStatus", response.GetStatus())
        #print("GetStatusText", response.GetStatusText())
        #print("GetMimeType", response.GetMimeType())
        # 返回某个特定的header
        #print("GetHeader", response.GetHeader(header))
        #print("GetHeaderMap", response.GetHeaderMap())
        #print("GetHeaderMultimap", response.GetHeaderMultimap())

        #print("GetResponseHeaders()")
        # 1. If the response length is not known set
        #    responseLengthOut[0] to -1 and ReadResponse()
        #    will be called until it returns False.
        # 2. If the response length is known set
        #    responseLengthOut[0] to a positive value
        #    and ReadResponse() will be called until it
        #    returns False or the specified number of bytes
        #    have been read.
        # 3. Use the |response| object to set the mime type,
        #    http status code and other optional header values.
        # 4. To redirect the request to a new URL set
        #    redirectUrlOut[0] to the new url.
        #assert self._webRequestClient._response, "Response object empty"
        #wrcResponse = self._webRequestClient._response
        #response.SetStatus(wrcResponse.GetStatus())
        #response.SetStatusText(wrcResponse.GetStatusText())
        #response.SetMimeType(wrcResponse.GetMimeType())
        #if wrcResponse.GetHeaderMultimap():
        #    response.SetHeaderMultimap(wrcResponse.GetHeaderMultimap())
        #print("headers: ")
        #print(wrcResponse.GetHeaderMap())
        #responseLengthOut[0] = self._webRequestClient._dataLength
        #if not responseLengthOut[0]:
            # Probably a cached page? Or a redirect?
        #    pass

        #pass


    def ReadResponse(self,dataOut, bytesToRead, bytesReadOut, callback):
        #print(data_out, bytes_to_read, bytes_read_out, callback)
        # print("ReadResponse()")
        # 1. If data is available immediately copy up to
        #    bytesToRead bytes into dataOut[0], set
        #    bytesReadOut[0] to the number of bytes copied,
        #    and return true.
        # 2. To read the data at a later time set
        #    bytesReadOut[0] to 0, return true and call
        #    callback.Continue() when the data is available.
        # 3. To indicate response completion return false.
        if self._offsetRead < self._webRequestClient._dataLength:
            dataChunk = self._webRequestClient._data[ \
                        self._offsetRead:(self._offsetRead + bytesToRead)]
            self._offsetRead += len(dataChunk)
            dataOut[0] = dataChunk
            bytesReadOut[0] = len(dataChunk)
            return True
        self._clientHandler._ReleaseStrongReference(self)
        print("no more data, return False")
        return False

    def CanGetCookie(self, cookie):
        return True

    def CanSetCookie(self, cookie):
        return True

    def Cancel(self):
        pass


class WebRequestClient:

    _resourceHandler = None
    _data = ""
    _dataLength = -1
    _response = None

    def OnUploadProgress(self, webRequest, current, total):
        print('WebRequestClient.OnUploadProgress')
        pass

    def OnDownloadProgress(self, webRequest, current, total):
        print('WebRequestClient.OnDownloadProgress')
        pass

    def OnDownloadData(self, webRequest, data):
        print('WebRequestClient.OnDownloadData')
        self._data += data

    def OnRequestComplete(self, webRequest):
        print("WebRequestClient.OnRequestComplete()")
        # cefpython.WebRequest.Status = {"Unknown", "Success",
        #         "Pending", "Canceled", "Failed"}
        statusText = "Unknown"
        if webRequest.GetRequestStatus() in cef.WebRequest.Status:
            statusText = cef.WebRequest.Status[\
                    webRequest.GetRequestStatus()]
        print("status = %s" % statusText)
        print("error code = %s" % webRequest.GetRequestError())
        # Emulate OnResourceResponse() in ClientHandler:
        self._response = webRequest.GetResponse()
        # Are webRequest.GetRequest() and
        # self._resourceHandler._request the same? What if
        # there was a redirect, what will GetUrl() return
        # for both of them?
        self._data = self._resourceHandler._clientHandler._OnResourceResponse(
                self._resourceHandler._browser,
                self._resourceHandler._frame,
                webRequest.GetRequest(),
                webRequest.GetRequestStatus(),
                webRequest.GetRequestError(),
                webRequest.GetResponse(),
                self._data)
        self._dataLength = len(self._data)
        # ResourceHandler.GetResponseHeaders() will get called
        # after _responseHeadersReadyCallback.Continue() is called.
        self._resourceHandler._responseHeadersReadyCallback.Continue()




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

    def OnLoadEnd(self, browser, **_):
        #browser.ExecuteFunction("py_funtion", "I am a Python string #1")
        browser.ExecuteJavascript("alert('加载完成')")


class DisplayHandler(object):
    def OnConsoleMessage(self, browser, message, **_):
        print(message)


def print_dir(o):
    for item in dir(o):
        print(item)

if __name__ == '__main__':
    #pdb.run('main()')
    try:
        main()
    except Exception as ex:
        print(traceback.extract_stack())
