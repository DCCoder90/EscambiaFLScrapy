# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class PartyItem(scrapy.Item):
    lname = scrapy.Field()
    fname = scrapy.Field()
    mname = scrapy.Field()
    address = scrapy.Field()
    dob = scrapy.Field()
    ssn = scrapy.Field()
    gender = scrapy.Field()
    race = scrapy.Field()
    id = scrapy.Field()
    driverlicense = scrapy.Field()
    height = scrapy.Field()
    weight = scrapy.Field()
    eye = scrapy.Field()
    hair = scrapy.Field()
    phone = scrapy.Field()
    other = scrapy.Field()

class CaseItem(scrapy.Item):
    id = scrapy.Field()
    judge = scrapy.Field()
    casenum = scrapy.Field()
    clerkfiledate = scrapy.Field()
    totalfeesdue = scrapy.Field()
    agencyreportnum = scrapy.Field()
    courttype = scrapy.Field()
    uniformcasenum = scrapy.Field()
    statusdate = scrapy.Field()
    casetype = scrapy.Field()
    status = scrapy.Field()
    agency = scrapy.Field()
    
    charges = scrapy.Field()
    finances = scrapy.Field()
    reciepts = scrapy.Field()
    dockets = scrapy.Field()
    
class ChargeItem(scrapy.Item):
    count = scrapy.Field()
    description = scrapy.Field()
    level = scrapy.Field()
    degree = scrapy.Field()
    plea = scrapy.Field()
    disposition = scrapy.Field()
    dispositiondate = scrapy.Field()

class FinanceItem(scrapy.Item):
    code = scrapy.Field()
    description = scrapy.Field()
    assessment = scrapy.Field()
    paid = scrapy.Field()
    waived = scrapy.Field()
    balance = scrapy.Field()
    judgement = scrapy.Field()
    duedate = scrapy.Field()

class RecieptsItem(scrapy.Item):
    date = scrapy.Field()
    number = scrapy.Field()
    amount = scrapy.Field()

class DocketItem(scrapy.Item):
    date = scrapy.Field()
    entry = scrapy.Field()

class EscambiaflpublicItem(scrapy.Item):
    plaintiff = scrapy.Field()
    defendant = scrapy.Field()
    case = scrapy.Field()
    pass

