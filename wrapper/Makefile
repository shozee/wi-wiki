wiki.cgi : wiki.c
	UID=`id -u`
	GID=`id -g`
	cc -DUID=$(UID) -DGID=$(GID) wiki.c -o wiki.cgi
	chmod u+s wiki.cgi
