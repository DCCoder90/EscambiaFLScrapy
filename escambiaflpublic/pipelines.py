# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb
import hashlib
import string

class MySQLPipeline(object):

    collection_name = 'scrapy_items'

    def __init__(self, dbu, dbp, dbh, db, dbport):
        self.dbu = dbu
        self.dbp = dbp
        self.dbh = dbh
        self.db = db
        self.dbport = dbport

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            dbu=crawler.settings.get('DBU'),
            dbp=crawler.settings.get('DBP'),
            dbh=crawler.settings.get('DBH'),
            db=crawler.settings.get('DB'),
            dbport = crawler.settings.get('DBPORT')
        )

    def open_spider(self, spider):
        self.conn = MySQLdb.connect(
            host = self.dbh, 
            user = self.dbu, 
            passwd = self.dbp, 
            db = self.db, 
            port = self.dbport)
        self.c = self.conn.cursor()

    def close_spider(self, spider):
        self.conn.close()

    def process_item(self, item, spider):  
        try:
            plaintiff=item['plaintiff']
            defendant=item['defendant']
            case=item['case']
            self.insert_case(case,defendant,plaintiff)
            self.conn.commit()
        except:
            pass
        return item
    
    def insert_case(self, case,defendant,plaintiff):
        if self.case_exists(case['id']) > 0:
            return

        if self.party_exists(defendant['id']) == 0:
            self.insert_party(defendant)
        if self.party_exists(plaintiff['id']) == 0:
            self.insert_party(plaintiff)
            
        charges=case['charges']
        dockets=case['dockets']
        finances=case['finances']
        reciepts=case['reciepts']
        
        self.c.execute('''INSERT INTO '''+self.db+'''.case (id,judge,casenum,clerkfiledate,totalfeesdue,agencyreportnum,courttype,uniformcasenum,statusdate,casetype,status,agency,defendant,plaintiff) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',[case['id'],case['judge'],case['casenum'],case['clerkfiledate'],case['totalfeesdue'],case['agencyreportnum'],case['courttype'],case['uniformcasenum'],case['statusdate'],case['casetype'],case['status'],case['agency'],defendant['id'],plaintiff['id']])

        self.insert_dockets(dockets,case['id'])
        self.insert_reciepts(reciepts,case['id'])
        self.insert_charges(charges,case['id'])
        self.insert_finances(finances,case['id'])
        
    def case_exists(self,caseid):
        self.c.execute("SELECT COUNT(*) FROM "+self.db+".case WHERE id ='"+str(caseid)+"'") #Check if person is already here
        count = self.c.fetchone()
        return count[0]
            
    def party_exists(self,partyid):
        query="SELECT COUNT(*) FROM "+self.db+".party WHERE id ='"+str(partyid)+"'"
        self.c.execute(query) #Check if person is already here
        count = self.c.fetchone()   
        return count[0]
        
    def insert_dockets(self,dockets,caseid):
        for docket in dockets:
            self.c.execute('''INSERT INTO '''+self.db+'''.dockets (caseid,date,entry) VALUES (%s,%s,%s)''',[caseid,docket['date'],docket['entry']])
          
    def insert_reciepts(self,reciepts,caseid):
        for reciept in reciepts:
            self.c.execute('''INSERT INTO '''+self.db+'''.reciepts (caseid,date,number,amount) VALUES (%s,%s,%s,%s)''',[caseid,reciept['date'],reciept['number'],reciept['amount']])
        
    def insert_party(self,party):
        self.c.execute('''INSERT INTO '''+self.db+'''.party (id,lname,fname,mname,address,dob,ssn,gender,race,driverlicense,height,weight,eye,hair,phone,other) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',[party['id'],party['lname'],party['fname'],party['mname'],party['address'],party['dob'],party['ssn'],party['gender'],party['race'],party['driverlicense'],party['height'],party['weight'],party['eye'],party['hair'],party['phone'],party['other']])
        
    def insert_charges(self,charges,caseid):
        for charge in charges:
            self.c.execute('''INSERT INTO '''+self.db+'''.charges (caseid,count,description,level,degree,plea,disposition,dispositiondate) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)''',[caseid,charge['count'],charge['description'],charge['level'],charge['degree'],charge['plea'],charge['disposition'],charge['dispositiondate']])
      
    def insert_finances(self,finances,caseid):
        for finance in finances:
            self.c.execute('''INSERT INTO '''+self.db+'''.finances (caseid,code,description,assessment,paid,waived,balance,judgement,duedate) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)''',[caseid,finance['code'],finance['description'],finance['assessment'],finance['paid'],finance['waived'],finance['balance'],finance['judgement'],finance['duedate']])
            