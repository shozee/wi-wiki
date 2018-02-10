#!/bin/bash

# Copyright (C) 2010-2011 Ricardo Catalinas Jiménez <jimenezrick@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENT_ROOT=/home/shoji/public_html/wish
MARKDOWN_BIN=subsh/markdown
WIKI_PATH=/wiki
DATA_PATH=data
CGI_URL=/~shoji/wish

function decode_query
{
  sed 's/%\([[:alnum:]][[:alnum:]]\)/\\x\1/g' | nkf -w --numchar-input | xargs --null printf
}

function get_value
{
  if [ -n "$1" ]; then
    echo -n "$1" | sed 's/\+/ /g' | sed -n "s/.*$2=\([^\&]*\).*/\1/p" | decode_query
  else
    echo ''
  fi
}

function print_rule
{
  echo
  echo '---'
}

function print_error_page
{
  print_rule
  echo '# ERROR: page' $1 'not found'
  print_rule
}

function print_error_query
{
  print_rule
  echo '# ERROR: invalid query'
  print_rule
}

function show_pages_list
{
  typeset file
  typeset page
  echo '[&mdash; Home &mdash;]('$CGI_URL'/wi.cgi?cmd=get&page=Home)'
  echo '[&mdash; New &mdash;]('$CGI_URL'/wi.cgi?cmd=get&page=New)'
  for file in $(cd $DOCUMENT_ROOT$WIKI_PATH; find . -name \*.md)
  do
    page=${file#./}
    page=${page%%.md}
    if [[ $page != Home ]] && [[ $page != New ]]
    then
      echo '['$page']('$CGI_URL'/wi.cgi?cmd=get&page='$page')'
    fi
  done
}

function show_static_pages_list
{
  typeset file
  typeset page
  echo '[&mdash; Home &mdash;]('$WIKI_PATH'/Home.html)'
  for file in *.md
  do
    page=${file%%.md}
    if [[ $page != Home ]] && [[ $page != New ]]
    then
      echo '['$page']('$WIKI_PATH'/'$page.html')'
    fi
  done
}

function show_search
{
  echo "<form action='$CGI_URL/wi.cgi' method='get'>"
  echo '<input type="hidden" name="cmd" value="search">'
  echo '<input type="text" name="pattern" size="20" maxlength="100">'
  echo '<input type="submit" value="Search"></form>'
}

function show_search_results
{
  typeset result
  echo '#' Search: $1
  (cd $DOCUMENT_ROOT$WIKI_PATH; egrep -i "$1" *.md) | while read result
  do
    echo "$result" | sed "s%\(.*\)\..*:%[\1]($CGI_URL/wi.cgi?cmd=get\&page=\1): %g"
    echo
  done
}

function show_page_content
{
  if [[ -r $DOCUMENT_ROOT$WIKI_PATH/$1.md ]]
  then
    print_rule
    show_page_controls $1
    print_rule
    echo '#' $1
    eval "$2"
    print_rule
  else
    print_error_page $1
  fi
}

function show_static_page_content
{
  print_rule
  echo '#' $1
  cat $1.md
  print_rule
}

function show_page_editor
{
  print_rule
  echo '#' $1
  echo "<form action='$CGI_URL/wi.cgi' method='post'>"
  echo '<input type="hidden" name="cmd" value="publish">'
  echo '<input type="hidden" name="page" value="'$1'">'
  echo '<textarea name="content" id="content" cols="100" rows="30" onkeydown="if(event.ctrlKey&&event.keyCode==13){document.getElementById('\''submit'\'').click();return false};">'
  (cd $DOCUMENT_ROOT$WIKI_PATH; cat $1.md)
  echo '</textarea><hr />'
  echo '<input type="submit" id="submit" value="Publish"></form>'
  echo '<script> document.getElementById("content").focus(); </script>'
  (cd $DOCUMENT_ROOT$WIKI_PATH; cat $1.md)
}

function show_create_page
{
  print_rule
  echo '#' Create new page:
  echo "<form action='$CGI_URL/wi.cgi' method='post'>"
  echo '<input type="hidden" name="cmd" value="create">'
  echo '<input type="text" name="page" size="20" maxlength="30">'
  echo '<input type="submit" value="Create"></form>'
  print_rule
}

function show_page
{
  typeset page
  typeset pattern
  typeset line
  typeset content
  case $1 in
    GET+get)
      page=$(get_value "$QUERY_STRING" page)
      if [[ $page == New ]]
      then
        show_pages_list
        show_create_page
      else
        show_pages_list
        show_page_content ${page:-Home} 'cat $DOCUMENT_ROOT$WIKI_PATH/$1.md'
      fi
      ;;
    GET+search)
      pattern=$(get_value "$QUERY_STRING" pattern)
      show_pages_list
      print_rule
      show_search
      print_rule
      show_search_results "$pattern"
      print_rule
      ;;
    GET+history)
      page=$(get_value "$QUERY_STRING" page)
      show_pages_list
      show_page_content $page "print_history $page"
      ;;
    GET+edit)
      page=$(get_value "$QUERY_STRING" page)
      show_pages_list
      show_page_editor $page
      ;;
    POST+delete)
      page=$(get_value "$2" page)
      delete_page $page
      show_pages_list
      show_page_content Home 'cat $DOCUMENT_ROOT$WIKI_PATH/Home.md'
      ;;
    POST+publish)
      page=$(get_value "$2" page)
      content=$(get_value "$2" content)
      publish_content $page "$content"
      show_pages_list
      show_page_content $page 'cat $DOCUMENT_ROOT$WIKI_PATH/$1.md'
      ;;
    POST+create)
      page=$(get_value "$2" page)
      create_page $page
      show_pages_list
      show_page_content $page 'cat $DOCUMENT_ROOT$WIKI_PATH/$1.md'
      ;;
    *)
      show_pages_list
      print_error_query
      ;;
  esac
}

function show_page_controls
{
  echo '<table><tr><td>'
  echo "<form action='$CGI_URL/wi.cgi' method='get'>"
  echo '<input type="hidden" name="cmd" value="edit">'
  echo '<input type="hidden" name="page" value="'$1'">'
  echo '<input type="submit" value="Edit"></form>'
  echo '</td>'
  echo '<td>'
  echo "<form action='$CGI_URL/wi.cgi' method='get'>"
  echo '<input type="hidden" name="cmd" value="history">'
  echo '<input type="hidden" name="page" value="'$1'">'
  echo '<input type="submit" value="History"></form>'
  echo '</td>'
  echo '<td>'
  echo "<form action='$CGI_URL/wi.cgi' method='post'>"
  echo '<input type="hidden" name="cmd" value="delete">'
  echo '<input type="hidden" name="page" value="'$1'">'
  echo '<input type="submit" value="Delete"></form>'
  echo '</td>'
  echo '<td>'
  show_search
  echo '</tr></td></table>'
}

function create_page
{
  D=`dirname  $1`
  F=`basename $1`.md
  (cd $DOCUMENT_ROOT$WIKI_PATH; test -d $D || mkdir -p $D ; touch $D/$F; git add $D/$F; git commit -m 'Wi!: create page') >/dev/null
}

function publish_content
{
  (cd $DOCUMENT_ROOT$WIKI_PATH; echo "$2" >$1.md; git add $1.md; git commit -m 'Wi!: publish content') >/dev/null
}

function print_history
{
  typeset line
  (cd $DOCUMENT_ROOT$WIKI_PATH; git log -p -n 10 $1.md) | while read line
  do
    echo -e "\t$line"
  done
}

function delete_page
{
  (cd $DOCUMENT_ROOT$WIKI_PATH; git rm -f $1.md; git commit -m 'Wi!: delete page') >/dev/null
}

function run_CGI
{
  typeset cmd
  typeset query
  echo Content-Type: text/html
  echo
  cat $DOCUMENT_ROOT/$DATA_PATH/HEADER
  if [[ $REQUEST_METHOD == GET ]]
  then
    cmd=$(get_value "$QUERY_STRING" cmd)
    cmd=${cmd:-get}
  else
    read query
    cmd=$(get_value "$query" cmd)
  fi
  show_page $REQUEST_METHOD+$cmd "$query" | $MARKDOWN_BIN
  cat $DOCUMENT_ROOT/$DATA_PATH/FOOTER
}

function generate_static
{
  typeset page
  typeset file_markdown
  typeset file_html
  for file_markdown in *.md
  do
    page=${file_markdown%%.md}
    file_html=$page.html
    cat $DOCUMENT_ROOT/$DATA_PATH/HEADER >$file_html
    show_static_pages_list | $MARKDOWN_BIN >>$file_html
    show_static_page_content $page | $MARKDOWN_BIN >>$file_html
    cat $DOCUMENT_ROOT/$DATA_PATH/FOOTER >>$file_html
    echo $file_html generated
  done
  ln -sf Home.html Home.html
}

if [[ $# == 0 ]]
then
  run_CGI
elif [[ $1 == --generate-static ]]
then
  generate_static
else
  echo 'Usage: wi.cgi --generate-static (or run as CGI)'
  exit 1
fi
