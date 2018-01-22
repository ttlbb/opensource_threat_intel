# opensource_threat_intelligence


## project install

1. install mongodb
	
	https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/

2. install requirements

	sudo pip install  -r requirements.txt

3. install scrapy
	
	https://doc.scrapy.org/en/latest/intro/install.html

4. install scrapyd

	http://scrapyd.readthedocs.io/en/stable/install.html
	
	sudo vi  /usr/local/lib/python2.7/dist-packages/scrapyd/default_scrapyd.conf

	set bind_address = 0.0.0.0 for remote access
	
	sudo pip install scrapyd-client

## how to use
1. start crawl project
	
	./project_restart.sh
	
	![start](http://7xpyfe.com1.z0.glb.clouddn.com/Jietu20180112-191538.jpg)

	you can use crontab execute task

        0 */4 * * *  bash /../../opensource_threat_intel/tools/scrapyd_crontab_task.sh

2. scrapyd running status 

	 http://localhost:6800/

	 ![job](http://7xpyfe.com1.z0.glb.clouddn.com/Jietu20180112-191648.jpg)
3. data structure
```	
      {
        "indicator":"1.180.74.58",
        "data_type":0,
        "confidence":7,
        "alive":true/false,
        "updated_time":"2017-06-30T14:22:44"/"none",
        "source":"blocklist.de",
        "tag":5,
        "created_time":"2017-06-30T14:22:44"
        "description":""
     }
```

![mongodata](http://7xpyfe.com1.z0.glb.clouddn.com/Jietu20180112-191340.jpg)

## support sources

   001_abuse.sh
   
   002_alexa.com
   
   003_alienvault.com
   
   004_antispam.imp.ch
   
   005_blocklist.de
   
   006_cisco.com
   
   007_csirtg.io
   
   008_cyren.com
   
   009_danger.rulez.sk
   
   010_dataplane.org
   
   011_dragonresearchgroup.org
   
   012_emergingthreats.net
   
   013_malc0de.com
   
   014_netlab_360_com
   
   015_nothink.org
   
   016_openphish.com
   
   017_osint_bambenekconsulting_com
   
   018_phishtank_com
   
   019_public-dns.info
   
   020_spamhaus.org
   
   022_watcherlab.com
   
   023_badips.com
   
   024_blocklist.greensnow.co
   
   025_cinsscore.com
   
   026_rutgers.edu
   
   027_urlvir.com
   
   028_urlquery.net
   
   029_cybercrime-tracker.net
   
   030_malwaredomainlist.com
