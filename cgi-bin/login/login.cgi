#!/bin/sh
WIKI_DIR=${SCRIPT_NAME%/*/*}
WIKI_CGI=$WIKI_DIR/wiki.cgi

echo "Content-Type: text/html"
echo "Set-Cookie: WISH_AUTHOR=${REMOTE_USER:-guest}; path=$WIKI_DIR; max-age=2592000;"
echo
echo '<html><body>'
if [ -r .htaccess ]; then
  echo "You Logged in as : ${REMOTE_USER:-guest}"
  echo '<a href="'$WIKI_CGI'">Back to wiki.</a><br />'
  echo '<a href=''javascript:document.cookie="WISH_AUTHOR=;max-age=0;"''>Back to wiki.</a>'
else
  echo 'Put .htaccess and .htpasswd at this directory.'
fi
echo '</body></html>'
