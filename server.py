from twisted.application.internet import TCPServer
from twisted.application.service import Application
from twisted.web.resource import Resource
from twisted.web.server import Site
from json import dumps

import scrape


class PathPage(Resource):
    def render_GET(self, request):
        request.setHeader("Content-Type", "application/json; charset=utf-8")
        args = {arg: request.args[arg].pop() for arg in request.args}
        if not args:
            return dumps('Expecting: start, end, [date], [time], [resource]')
        return dumps(scrape.get_path(**args))

class DetailPage(Resource):
    def render_GET(self, request):
        request.setHeader("Content-Type", "application/json; charset=utf-8")
        args = {arg: request.args[arg].pop() for arg in request.args}
        if not args:
            return dumps('Expecting: resource')
        return dumps(scrape.get_detail(**args))


root = Resource()
root.putChild("path", PathPage())
root.putChild("detail", DetailPage())
application = Application("IDOS mobile scraper")
TCPServer(8880, Site(root)).setServiceParent(application)
