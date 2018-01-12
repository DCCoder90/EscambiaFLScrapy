#Name: spider.py
#Desc: Scrapes county jailview and stores data in json format
#Date: 12/12/2016
#Author: Ernest Mallett
from scrapy.spiders import CrawlSpider, Rule
from escambiaflpublic.items import EscambiaflpublicItem, ChargeItem, FinanceItem, RecieptsItem, DocketItem, PartyItem, CaseItem
import logging
import string
import json
import hashlib
import scrapy
import urllib
from scrapy.selector import Selector
from pprint import pprint
from scrapy import signals
from scrapy.mail import MailSender

class EscambiaSpider(CrawlSpider):
    name = "escambiafl"
    start_urls=["http://74.174.28.52/BMWeb/CourtCase.aspx/CaseThumbnail/1"]
    #global start, limit, baseurl
    global baseurl
    #start = 54261 #Where to start the crawler           
    #limit = 100000 #How many records to grab
    baseurl = "http://74.174.28.52"
        
    def __init__(self, *args, **kwargs):
        super(EscambiaSpider, self).__init__(*args, **kwargs)
        self.start=int(kwargs['start'])
        self.limit=int(kwargs['limit'])
        self.identifier=str(kwargs['identifier'])
        
    #Ensure's data isn't left null and strips out unneeded characters
    def fixdata(self, resp,xpth):
        hxs = Selector(text=resp)
        if hxs.xpath(xpth).extract():
            data=hxs.xpath(xpth).extract()[0].encode('utf-8')
            d=data.replace("\t","").replace("\r","").replace("\n","").replace("\xc2","").replace("\xa0","")
            dd = d.strip()
            return dd
        else:
            return ""
    
    #Checks if the party is a person or an agency
    def check_party(self,response,xpath):
        purl = self.fixdata(response,xpath)
        if purl == "":
            return False
        else:
            return True
    
    def parse_party(self,response):
        defendant_path = ".//*[@id='gridParties']/tbody/tr[1]/td[2]/div[1]"
        plaintiff_path = ".//*[@id='gridParties']/tbody/tr[2]/td[2]/div[1]"
        #logging.debug("Parse Party")
        if self.check_party(response,defendant_path+"/a/@href"):
            tid = self.fixdata(response,defendant_path+"/a/@href")
            ttid = string.split(tid,"Index/")
            tttid = string.split(ttid[1],"?")
            defendantid = tttid[0]
            defendantlink = self.fixdata(response,defendant_path+"/a/@href")
        else:
            defendantid = self.fixdata(response,defendant_path+"/text()")
            defendantlink = ""
        
        if self.check_party(response,plaintiff_path+"/a/@href"):
            tid = self.fixdata(response,plaintiff_path+"/a/@href")
            ttid = string.split(tid,"Index/")
            tttid = string.split(ttid[1],"?")
            plaintiffid = tttid[0]
            plaintifflink = self.fixdata(response,plaintiff_path+"/a/@href")
        else:
            plaintiffid = self.fixdata(response,plaintiff_path+"/text()")
            plaintifflink = ""
        
        if defendantlink != "":
            defendantresp = urllib.urlopen(baseurl+defendantlink).read()
            defendant = self.get_part_details(defendantresp,defendantid)
        else:
            defendant = self.create_blank_party(defendantid)
            
            
        if plaintifflink != "":
            plaintiffresp = urllib.urlopen(baseurl+plaintifflink).read()
            plaintiff = self.get_part_details(plaintiffresp,plaintiffid)
        else:
            plaintiff = self.create_blank_party(plaintiffid)
            
        logging.debug("DID: "+defendantid)
        logging.debug("PID: "+plaintiffid)
            
        return [defendant,plaintiff]
        
    def get_part_details(self,response,id):
        name = self.fixdata(response,".//table[@class='casedetailSectionTable']/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr[1]/td[2]/text()")
        name = self.split_name(name.strip())
        party = PartyItem()
        
        party['lname'] = name[0]
        party['fname'] = name[1]
        party['mname'] = name[2]
        
        party['address'] = self.fixdata(response,".//table[@class='casedetailSectionTable']/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr[2]/td[2]/text()")
        party['dob'] = self.fixdata(response,".//table[@class='casedetailSectionTable']/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr[4]/td[2]/text()")
        party['ssn'] = self.fixdata(response,".//table[@class='casedetailSectionTable']/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr[5]/td[2]/text()")
        party['gender'] = self.fixdata(response,".//table[@class='casedetailSectionTable']/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr[6]/td[2]/text()")
        party['race'] = self.fixdata(response,".//table[@class='casedetailSectionTable']/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr[7]/td[2]/text()")
        party['id'] = self.fixdata(response,".//table[@class='casedetailSectionTable']/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr[8]/td[2]/text()")
        party['driverlicense'] = self.fixdata(response,".//table[@class='casedetailSectionTable']/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr[1]/td[4]/text()")
        
        #TODO: Split hight and weight
        party['height'] = self.fixdata(response,".//table[@class='casedetailSectionTable']/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr[2]/td[4]/text()")
        party['weight'] = self.fixdata(response,".//table[@class='casedetailSectionTable']/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr[2]/td[4]/text()")
        
        #TODO: Split eye and hair
        party['eye'] = self.fixdata(response,".//table[@class='casedetailSectionTable']/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr[3]/td[2]/text()")
        party['hair'] = self.fixdata(response,".//table[@class='casedetailSectionTable']/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr[3]/td[2]/text()")
        
        party['phone'] = self.fixdata(response,".//table[@class='casedetailSectionTable']/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr[4]/td[4]/text()")
        party['other'] = self.fixdata(response,".//table[@class='casedetailSectionTable']/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr[6]/td[4]/text()")
        return party

    def split_name(self,name):
        #logging.debug("NAME: "+name)
        if "," in name:
            name = string.split(name,",")
            fname = name[0]
            lmname = string.split(name[1].strip()," ")
            lname = lmname[0]
            try:
                mname = lmname[1]
            except IndexError:
                mname = ""
        else:
            fname = name
            lname = name
            mname = name
        #logging.debug(fname)
        #logging.debug(lname)
        return [fname,lname,mname]
    
    def create_blank_party(self,id):
        try:
            output = []
            i = 0
            for character in id:
                number = ord(character)
                output.append(number)    
                if i > 3:
                    break  
                i +=1  
            numericid=''.join(str(e) for e in output)
            negid=int(((int(numericid)-96)*0.1)*-1)
        except ValueError:
            negid=0
            
        party = PartyItem()
        party['lname'] = id
        party['fname'] = id
        party['mname'] = id
        party['address'] = ""
        party['dob'] = ""
        party['ssn'] = ""
        party['gender'] = ""
        party['race'] = ""
        party['id'] = negid #Hash to ensure unique
        party['driverlicense'] = ""
        party['height'] = ""
        party['weight'] = ""
        party['eye'] = ""
        party['hair'] = ""
        party['phone'] = ""
        party['other'] = ""
        return party 
    
    def parse_charges(self,response):
        charges = []
        hxs = Selector(text=response)
        charge_table = hxs.xpath(".//table[@id='gridCharges']/tbody/tr").extract()
        for cc in charge_table:
            c = ChargeItem()
            c['count'] = self.fixdata(cc,".//tr/td[2]/text()")
            c['description'] = self.fixdata(cc,".//tr/td[3]/text()")
            c['level'] = self.fixdata(cc,".//tr/td[4]/text()")
            c['degree'] = self.fixdata(cc,".//tr/td[5]/text()")
            c['plea'] = self.fixdata(cc,".//tr/td[6]/text()")
            c['disposition'] = self.fixdata(cc,".//tr/td[7]/text()")
            c['dispositiondate'] = self.fixdata(cc,".//tr/td[8]/text()")
            charges.append(c)
        return charges
    
    def parse_finances(self,response):
        finances = []
        hxs = Selector(text=response)
        finance_table = hxs.xpath(".//*[@id='feesAccordionCollapse']/div/table/tbody/tr").extract()
        for cc in finance_table:
            c = FinanceItem()
            c['code'] = self.fixdata(cc,".//tr/td[2]/text()")
            c['description'] = self.fixdata(cc,".//tr/td[3]/text()")
            c['assessment'] = self.fixdata(cc,".//tr/td[4]/text()")
            c['paid'] = self.fixdata(cc,".//tr/td[5]/text()")
            c['waived'] = self.fixdata(cc,".//tr/td[6]/text()")
            c['balance'] = self.fixdata(cc,".//tr/td[7]/text()")
            c['judgement'] = self.fixdata(cc,".//tr/td[8]/text()")
            c['duedate'] = self.fixdata(cc,".//tr/td[9]/text()")
            finances.append(c)
        return finances
    
    def parse_reciepts(self,response):
        reciepts = []
        hxs = Selector(text=response)
        reciepts_table = hxs.xpath(".//*[@id='transactionsAccordion']/div/div/div/table/tbody/tr").extract()
        for cc in reciepts_table:
            c = RecieptsItem()
            c['date'] = self.fixdata(cc,".//tr/td[1]/text()")
            c['number'] = self.fixdata(cc,".//tr/td[2]/text()")
            c['amount'] = self.fixdata(cc,".//tr/td[3]/text()")
            reciepts.append(c)
        return reciepts
    
    def parse_dockets(self,id):
        response = urllib.urlopen(baseurl+"/BMWeb/CourtCase.aspx/CaseDockets/"+str(id)).read()
        hxs = Selector(text=response)
        dockets = []
        dockets_table = hxs.xpath(".//*[@id='gridDockets']/tbody/tr").extract()
        for cc in dockets_table:
            c = DocketItem()
            c['date'] = self.fixdata(cc,".//tr/td[2]/text()")
            c['entry'] = self.fixdata(cc,".//tr/td[3]/text()")
            dockets.append(c)
        return dockets
    
    def parse_case(self,id):
        response = urllib.urlopen(baseurl+"/BMWeb/CourtCase.aspx/DetailsSummary/"+str(id)).read()
        
        case = CaseItem()
        logging.debug("Parse case")
        case['id'] = id
        case['judge'] = self.fixdata(response,".//div[@id='summaryAccordionCollapse']/div/table/tr/td[1]/dl/dd[1]/text()")
        case['casenum'] = self.fixdata(response,".//div[@id='summaryAccordionCollapse']/div/table/tr/td[1]/dl/dd[2]/text()")
        case['clerkfiledate'] = self.fixdata(response,".//div[@id='summaryAccordionCollapse']/div/table/tr/td[1]/dl/dd[3]/text()")
        case['totalfeesdue'] = self.fixdata(response,".//div[@id='summaryAccordionCollapse']/div/table/tr/td[1]/dl/dd[4]/text()")
        case['agencyreportnum'] = self.fixdata(response,".//div[@id='summaryAccordionCollapse']/div/table/tr/td[1]/dl/dd[5]/text()")
        case['courttype'] = self.fixdata(response,".//div[@id='summaryAccordionCollapse']/div/table/tr/td[2]/dl/dd[1]/text()")
        case['uniformcasenum'] = self.fixdata(response,".//div[@id='summaryAccordionCollapse']/div/table/tr/td[2]/dl/dd[2]/text()")
        case['statusdate'] = self.fixdata(response,".//div[@id='summaryAccordionCollapse']/div/table/tr/td[2]/dl/dd[3]/text()")
        case['casetype'] = self.fixdata(response,".//div[@id='summaryAccordionCollapse']/div/table/tr/td[3]/dl/dd[1]/text()")
        case['status'] = self.fixdata(response,".//div[@id='summaryAccordionCollapse']/div/table/tr/td[3]/dl/dd[2]/text()")
        case['agency'] = self.fixdata(response,".//div[@id='summaryAccordionCollapse']/div/table/tr/td[3]/dl/dd[4]/text()")
        
        charges = self.parse_charges(response)
        case['charges'] = charges
        finances = self.parse_finances(response)
        case['finances'] = finances
        reciepts = self.parse_reciepts(response)
        case['reciepts'] = reciepts
        dockets = self.parse_dockets(id)
        case['dockets'] = dockets
        return case
        
    def gather_info(self,id):
        logging.debug("Gathering info on "+str(id))
        item = EscambiaflpublicItem()

        summary = urllib.urlopen(baseurl+"/BMWeb/CourtCase.aspx/DetailsSummary/"+str(id)).read()

        party=self.parse_party(summary)
        item['defendant'] = party[0]
        item['plaintiff'] = party[1]
                
        case = self.parse_case(id)
        item['case'] = case
        return item
             
    def parse(self,response):
        i = self.start
        bad = 0
        breaklimit = (self.start+self.limit)-1
        self.tcount = 0
        while True:
            self.tcount += 1
            logging.debug(i)
            thumburl = baseurl+"/BMWeb/CourtCase.aspx/CaseThumbnail/"+str(i)
            response=urllib.urlopen(thumburl).read()   
            thumbdate = self.fixdata(response,".//table[@class='thumbSummary']/tr[6]/td[2]/text()")   
            if thumbdate == "1/1/0001":
                bad += 1
            else:
                yield self.gather_info(i)
            if i == breaklimit:
                break
            i += 1
        logging.debug("Got total of "+str(self.tcount)+" records!")

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(*args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        mailer = MailSender(mailfrom="MYEMAIL@gmail.com",smtphost="smtp.gmail.com",smtpport=587,smtpuser="MYEMAIL@gmail.com",smtppass="SMTP_PASSWORD")
        return mailer.send(to=["MYEMAIL@gmail.com"],subject="Spider "+self.identifier+" Finished",body="EscambiaFL Spider "+self.identifier+" has completed running. \n\n Started at: "+str(self.start)+"\n Ended at: "+str(self.start+self.tcount)+"\n Total Items: "+str(self.tcount))
    
    def spider_opened(self, spider):
        mailer = MailSender(mailfrom="MYEMAIL@gmail.com",smtphost="smtp.gmail.com",smtpport=587,smtpuser="MYEMAIL@gmail.com",smtppass="SMTP_PASSWORD")
        return mailer.send(to=["MYEMAIL@gmail.com"],subject="Spider "+self.identifier+" Started",body="EscambiaFL Spider "+self.identifier+" has started running. \n\n Started at: "+str(self.start)+"\n Limit: "+str(self.limit))
 