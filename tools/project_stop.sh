
ps aux | grep scrapyd | awk '{print $2}' | xargs kill -9
