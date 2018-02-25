cgi :
	XUID=`id -u`
	XGID=`id -g`
	cc -DUID=$(XUID) -DGID=$(XGID) wiki.c -o wiki.cgi
	chmod u+s wiki.cgi
	mv wiki.cgi ../cgi-bin/
