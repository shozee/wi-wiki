#!/bin/bash -pvx

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

DATA_PATH=../data
WIKI_PATH=../contents

export PATH=${PWD}/subsh:${PATH} # put nkf in subsh/ if you haven't got it
MARKDOWN_BIN="md2html --github --ftables"

CGI_URL=$SCRIPT_NAME  # given by http server
WIKI_URL=${SCRIPT_NAME%/*/*}/contents
AUTHOR=${REMOTE_USER:-wiki user}

function decode_query
{
  sed 's/%\([[:alnum:]][[:alnum:]]\)/\\x\1/g' | nkf -w --numchar-input | xargs --null printf
}

function get_value
{
  if [[ -n $1 ]]; then
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

function get_pages_list
{
  list=''
  dir=`echo $1 | sed 's%/$%%g'`
  for file in $(cd $WIKI_PATH/$dir; ls -1 | grep '.md$') \
              $(cd $WIKI_PATH/$dir; ls -F -1 | grep '/$')
  do
    page=${file#./}
    page=${page%%.md}
    if [[ $page != Home ]]
    then
      list="$list "'['$page']('$CGI_URL'?cmd=get&page='$dir/$page')'
    fi
  done
  echo "$list"
}

function show_pages_list
{
  typeset file
  typeset page
  echo '[&mdash; Home &mdash;]('$CGI_URL'?cmd=get&page=Home)'
  get_pages_list .
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

function show_page_content
{
  if [[ -r $WIKI_PATH/$1.md ]]
  then
    print_rule
    show_page_controls $1
    print_rule
    eval "$2" | relative_path $1
    print_rule
  elif [[ -d $WIKI_PATH/$1 ]]
  then
    print_rule
    show_page_controls $1
    print_rule
    get_pages_list $1 | sed 's/ /\n- /g'
    print_rule
  else
    print_error_page $1
  fi
}

function show_attachments
{
  line=''
  d=`dirname $1.md`
  for file in $(cd $WIKI_PATH/$d; find . -maxdepth 1 -type f)
  do
    f=${file##*/}
    ext=${f##*.}
    if [[ $ext != md ]] && [[ $ext != html ]]
    then
      line=$line'<tr><td><input type="checkbox" name="files2del" value="'$f'" /></td><td><a href="'$WIKI_URL/$d/$f'">'$f'</td></tr>'
    fi
  done
  if [[ -n $line ]] ; then
    echo 'Attatchments: '
    echo "<form action='$CGI_URL' method='post' enctype='multipart/form-data'>"
    echo '<input type="hidden" name="cmd" value="delattach">'
    echo '<input type="hidden" name="page" value="'$1'">'
    echo '<table>'$line'</table>'
    echo '<input type="submit" value="delete"/></form>'
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
  # Note: commonmark treats a blank line as a closing html tag. To avoid the parser converting .md contents inside the textarea, \n needs to be replaced with &#010; .
  (cd $WIKI_PATH; cat $1.md | tr -d '\r' | sed -e ':loop; N; $!b loop; s/\n/\&#010;/g')
  echo '</textarea><br />'
  echo '<input type="submit" id="submit" value="Publish"></form>'
  echo '<script> document.getElementById("content").focus(); </script>'

  echo '<hr />'
  echo '<table><tr><td>'
  echo "<form action='$CGI_URL' method='get'>"
  echo '<input type="hidden" name="cmd" value="history">'
  echo '<input type="hidden" name="page" value="'$1'">'
  echo '<input type="submit" value="History"></form>'
  echo '</td><td>'
  echo "<form action='$CGI_URL' method='post'>"
  echo '<input type="hidden" name="cmd" value="delete">'
  echo '<input type="hidden" name="page" value="'$1'">'
  echo '<input type="submit" value="Delete"></form>'
  echo '</td><td>'
  echo "<form action='$CGI_URl' method='post' enctype='multipart/form-data'>"
  echo '<input type="hidden" name="cmd" value="attach">'
  echo '<input type="hidden" name="page" value="'$1'">'
  echo '<input type="file"   name="attachfile">'
  echo '<input type="submit" value="Attach"></form>'
  echo '</td></tr></table>'
  echo '<hr />'

  show_attachments $1
  print_rule
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
    POST+attach|POST+delattach)
      page=$(get_value "$2" page)
      show_pages_list
      show_page_editor $page
      ;;
    POST+publish)
      page=$(get_value "$2" page)
      content=$(get_value "$2" content | tr -d '\r')
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
      echo "$1" 
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
  echo '</td></tr></table>'
}

function create_page
{
  D=`dirname  $1`
  F=`basename $1`.md
  (cd $WIKI_PATH; test -d $D || mkdir -p $D ; touch $D/$F; chmod 644 $1.md ; git add $D/$F; git commit --author="$AUTHOR" -m "Create $1") >/dev/null
}

function publish_content
{
  (cd $WIKI_PATH; echo "$2" >$1.md; chmod 644 $1.md ; git add $1.md; git commit --author="$AUTHOR" -m "Publish $1") >/dev/null
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
  (cd $WIKI_PATH; git rm -f $1.md; git commit --author="$AUTHOR" -m "Delete $1") >/dev/null
}

function run_CGI
{
  typeset cmd
  typeset query
  echo Content-Type: text/html
  echo
  cat $DATA_PATH/HEADER
  if [[ $REQUEST_METHOD == GET ]] ; then
    cmd=$(get_value "$QUERY_STRING" cmd)
    cmd=${cmd:-get}
  elif [[ $CONTENT_TYPE =~ multipart ]] ; then
    tmpfile=$(mktemp)
    cat > $tmpfile
    line=`cat $tmpfile | wc -l | cut -d' ' -f1`
    cmd=$(sed -n 4p $tmpfile | tr -d '\r')
    page=$(sed -n 8p $tmpfile | tr -d '\r')
    dir=`dirname $page`
    if [[ $cmd = attach ]]
    then
      if [ $line -ge 15 ]; then
        filename=$(sed -n 10p $tmpfile | sed 's%.*filename="\(.*\)".*%\1%g')
        sed -n 13,$((line-2))p $tmpfile > $WIKI_PATH/$dir/$filename
        sed -n $((line-1))p $tmpfile | tr -d '\r' >> $WIKI_PATH/$dir/$filename
        chmod 644 $WIKI_PATH/$dir/$filename
        echo "attached :  $filename"
      fi
    elif [[ $cmd = delattach ]]
    then
      i=12
      while [ $i -le $line ]; do
        filename=$(sed -n ${i}p $tmpfile | tr -d '\r')
        rm -f $WIKI_PATH/$dir/$filename
        echo "deleted :  $filename"
        i=$(( i + 4 ))
      done
    fi
    rm -f $tmpfile
    query="page=$page"
  else
    query=`cat | tr -d '\r'` # get stdin
    cmd=$(get_value "$query" cmd)
  fi
  show_page $REQUEST_METHOD+$cmd "$query" | $MARKDOWN_BIN
  cat $DATA_PATH/FOOTER
}

# main 
run_CGI 2> error.log
#run_CGI | tee tmp.html 2> error.log # debug
