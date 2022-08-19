XUID=$(shell id -u)
XGID=$(shell id -g)
CGI_BIN=$(PWD)/../cgi-bin
HTACS=$(CGI_BIN)/.htaccess
HTPWD=$(CGI_BIN)/.htpasswd

all : cgi htpasswd

cgi :
	cc -DUID=${XUID} -DGID=${XGID} wiki_edit.c -o wiki_edit.cgi
	chmod u+s wiki_edit.cgi
	mv wiki_edit.cgi $(CGI_BIN)/

htpasswd:
	echo "<Files wiki_edit.cgi>"  >  $(HTACS)
	echo "AuthType Basic"         >> $(HTACS)
	echo "AuthUserFile $(HTPWD)"  >> $(HTACS)
	echo 'AuthName "auth"'        >> $(HTACS)
	echo "require valid-user"     >> $(HTACS)
	echo "</Files>"               >> $(HTACS)
