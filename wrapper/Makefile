XUID=$(shell id -u)
XGID=$(shell id -g)
cgi :
	cc -DUID=${XUID} -DGID=${XGID} wiki.c -o wiki.cgi
	chmod u+s wiki.cgi
	mv wiki.cgi ../cgi-bin/
