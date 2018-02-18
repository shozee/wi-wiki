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

MARKDOWN_BIN=subsh/markdown
#MARKDOWN_BIN=subsh/discount

WIKI_PATH=/home/shoji/public_html/wish/wiki
WIKI_URL=/~shoji/wish/wiki
DATA_PATH=/home/shoji/public_html/wish/data
CGI_URL=/~shoji/wish/wi.cgi

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
  echo '[&mdash; Home &mdash;]('$CGI_URL'?cmd=get&page=Home)'
  for file in $(cd $WIKI_PATH; find . -name \*.md)
  do
    page=${file#./}
    page=${page%%.md}
    if [[ $page != Home ]]
    then
      echo '['$page']('$CGI_URL'?cmd=get&page='$page')'
    fi
  done
}

function show_static_pages_list
{
  typeset file
  typeset page
  echo '[&mdash; Home &mdash;]('$WIKI_URL'/Home.html)'
  for file in $(cd $WIKI_PATH; find . -name \*.md)
  do
    page=${file#./}
    page=${page%%.md}
    if [[ $page != Home ]]
    then
      echo '['$page']('$WIKI_URL'/'$page.html')'
    fi
  done
}

function show_search
{
  echo "<form action='$CGI_URL' method='get'>"
  echo '<input type="hidden" name="cmd" value="search">'
  echo '<input type="text" name="pattern" size="20" maxlength="100">'
  echo '<input type="submit" value="Search"></form>'
}

function show_search_results
{
  typeset result
  echo '#' Search: $1
  (cd $WIKI_PATH; egrep --include=*.md -r -i "$1") | while read result
  do
    echo "$result" | sed -e "s%\\(.*\\).md:%[\1]($CGI_URL?cmd=get\&page=\1): %g"
    echo
  done
}

function relative_path
{
  # set the URL prefix to $WIKI_URL if : is not contained, then
  #   pass it to cgi if the URL postfix matches .md
  D=`dirname  $1`
  sed -e "s%\\[\\(.*\\)\\](\\([^:]*\\))%[\\1]($WIKI_URL/$D/\\2)%g" \
      -e "s%]($WIKI_URL/$D/\\(.*\\).md)%](${CGI_URL}?cmd=get\&page=$D/\\1)%g"
}

function static_relative_path
{
  D=`dirname  $1`
  sed -e "s%\\[\\(.*\\)\\](\\([^:]*\\))%[\\1]($WIKI_URL/$D/\\2)%g" \
      -e "s%]($WIKI_URL/$D/\\(.*\\).md)%](${WIKI_URL}/\\1.html)%g"
}


function show_page_content
{
  if [[ -r $WIKI_PATH/$1.md ]]
  then
    print_rule
    show_page_controls $1
    print_rule
    echo '#' $1
    eval "$2" | relative_path $1
    print_rule
  else
    print_error_page $1
  fi
}

function show_static_page_content
{
  if [[ -r $WIKI_PATH/$1.md ]]
  then
    print_rule
    echo '#' $1
    cat $WIKI_PATH/$1.md | static_relative_path $1
    print_rule
  fi
}

function show_page_editor
{
  print_rule
  echo '#' $1
  echo "<form action='$CGI_URL' method='post'>"
  echo '<input type="hidden" name="cmd" value="publish">'
  echo '<input type="hidden" name="page" value="'$1'">'
  echo '<textarea name="content" id="content" cols="100" rows="30" onkeydown="if(event.ctrlKey&&event.keyCode==13){document.getElementById('\''submit'\'').click();return false};">'
  (cd $WIKI_PATH; cat $1.md)
  echo '</textarea><hr />'
  echo '<input type="submit" id="submit" value="Publish"></form>'
  echo '<script> document.getElementById("content").focus(); </script>'
  (cd $WIKI_PATH; cat $1.md)
}

function show_create_page
{
  print_rule
  echo '#' Create new page:
  echo "<form action='$CGI_URL' method='post'>"
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
        show_page_content ${page:-Home} 'cat $WIKI_PATH/$1.md'
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
      show_page_content Home 'cat $WIKI_PATH/Home.md'
      ;;
    POST+publish)
      page=$(get_value "$2" page)
      content=$(get_value "$2" content)
      publish_content $page "$content"
      show_pages_list
      show_page_content $page 'cat $WIKI_PATH/$1.md'
      ;;
    POST+create)
      page=$(get_value "$2" page)
      create_page $page
      show_pages_list
      show_page_content $page 'cat $WIKI_PATH/$1.md'
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
  show_search
  echo '</td><td>'
  echo "<form action='$CGI_URL' method='get'>"
  echo '<input type="hidden" name="cmd" value="get">'
  echo '<input type="hidden" name="page" value="New">'
  echo '<input type="submit" value="New"></form>'
  echo '</td><td>'
  echo "<form action='$CGI_URL' method='get'>"
  echo '<input type="hidden" name="cmd" value="edit">'
  echo '<input type="hidden" name="page" value="'$1'">'
  echo '<input type="submit" value="Edit"></form>'
  echo '</td><td>'
  echo "<form action='$CGI_URL' method='get'>"
  echo '<input type="hidden" name="cmd" value="history">'
  echo '<input type="hidden" name="page" value="'$1'">'
  echo '<input type="submit" value="History"></form>'
  echo '</td><td>'
  echo "<form action='$CGI_URL' method='post'>"
  echo '<input type="hidden" name="cmd" value="delete">'
  echo '<input type="hidden" name="page" value="'$1'">'
  echo '<input type="submit" value="Delete"></form>'
  echo '</tr></td></table>'
}

function create_page
{
  D=`dirname  $1`
  F=`basename $1`.md
  (cd $WIKI_PATH; test -d $D || mkdir -p $D ; touch $D/$F; git add $D/$F; git commit -m "Create $1") >/dev/null
}

function publish_content
{
  (cd $WIKI_PATH; echo "$2" >$1.md; git add $1.md; git commit -m "Publish $1") >/dev/null
}

function print_history
{
  typeset line
  (cd $WIKI_PATH; git log -p -n 10 $1.md) | while read line
  do
    echo -e "\t$line"
  done
}

function delete_page
{
  (cd $WIKI_PATH; git rm -f $1.md; git commit -m "Delete $1") >/dev/null
}

function run_CGI
{
  typeset cmd
  typeset query
  echo Content-Type: text/html
  echo
  cat $DATA_PATH/HEADER
  if [[ $REQUEST_METHOD == GET ]]
  then
    cmd=$(get_value "$QUERY_STRING" cmd)
    cmd=${cmd:-get}
  else
    query=`cat` # get stdin
    cmd=$(get_value "$query" cmd)
  fi
  show_page $REQUEST_METHOD+$cmd "$query" | $MARKDOWN_BIN
  cat $DATA_PATH/FOOTER
}

function generate_static
{
  typeset page
  typeset file_markdown
  typeset file_html
  for file_markdown in $(cd $WIKI_PATH ; find . -name \*.md)
  do
    page=${file_markdown#./}
    page=${page%%.md}
    file_html=$page.html
    cat $DATA_PATH/HEADER > $WIKI_PATH/$file_html
    show_static_pages_list | $MARKDOWN_BIN >> $WIKI_PATH/$file_html
    show_static_page_content $page | $MARKDOWN_BIN >> $WIKI_PATH/$file_html
    cat $DATA_PATH/FOOTER >> $WIKI_PATH/$file_html
    echo $file_html generated
  done
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
