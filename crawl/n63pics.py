from tool.GetHtml import hp
from tool.ProxyMantenance import ProxyUse, MongoPro
from pymongo import MongoClient
from lxml import etree
from multiprocessing.dummy import Pool
import queue, re, os, requests

TARGET_URL = 'http://www.n63.com/photodir/chinam.htm'
