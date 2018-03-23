#!/bin/sh
WIKI_DIR=${SCRIPT_NAME%/*/*}
WIKI_CGI=$WIKI_DIR/wiki.cgi

echo "Content-Type: text/html"
echo "Set-Cookie: WISH_AUTHOR=${REMOTE_USER:-guest}; path=$WIKI_DIR; max-age=2592000;"
echo
echo '<html><body>'
if [ -r .htaccess ]; then
  echo '<a href="'$WIKI_CGI'">Back to wiki.</a>'
else
  echo 'Put .htaccess and .htpasswd at this directory.'
fi
echo '</body></html>'
