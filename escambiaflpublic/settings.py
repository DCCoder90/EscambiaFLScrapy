BOT_NAME = 'escambiaflpublic'

SPIDER_MODULES = ['escambiaflpublic.spiders']
NEWSPIDER_MODULE = 'escambiaflpublic.spiders'

DBU = 'DATABASEUSERNAME'
DBP = 'DATABASEPASSWORD'
DB = 'DATABASENAME'
DBH = 'DATABASEHOST'
DBPORT = 3306


USER_AGENT = 'IntelNexus Spider (USER@EXAMPLE.COM)'

ITEM_PIPELINES = {
    'escambiaflpublic.pipelines.MySQLPipeline': 300,
}
