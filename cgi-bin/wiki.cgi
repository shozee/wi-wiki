#!/bin/bash -pevx

# Copyright (C) 2010-2011 Ricardo Catalinas Jimenez <jimenezrick@gmail.com>
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

function git_cmd
{
  case $1 in
    add)
      chmod 644 $2
      git add -f $2
      ;;
    rm)
      git rm -f $2
      ;;
  esac
  set +e
  git commit -m "$3"
  set -e
}

function decode_query
{
  sed 's/%\([[:alnum:]][[:alnum:]]\)/\\x\1/g' | nkf -w --numchar-input | xargs --null printf
}

function escape_equation
{
  #  '\{' to '\\{', '\}' to '\\}'
  #  '\' to '\\'
  #  '_'  to '\_'
  ## '*'  to '\*'
#  sed -r 's%\\\\%\\\\\\\\%g;s%\\\{%\\\\\{%g;s%\\\}%\\\\\}%g;s%[*]%\\*%g'
  sed -r 's%\\\\%\\\\\\\\%g;s%\\\{%\\\\\{%g;s%\\\}%\\\\\}%g'
}

function get_value
{
  if [[ -n $1 ]]; then
    query=$(echo -n "$1" | sed 's/\+/ /g' | sed -n "s/.*$2=\([^\&]*\).*/\1/p")
    if [ -n "$query" ]; then
      echo "$query" | decode_query
    else
      echo ''
    fi
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
  echo $1
  print_rule
}

function print_error_query
{
  print_rule
  echo '# ERROR: invalid query'
  print_rule
}

function print_pages_link
{
  list=''
  dir=`echo $1 | sed 's%/$%%g'`
  for file in $(cd $WIKI_PATH/$dir; ls -1 | grep '.md$') \
              $(cd $WIKI_PATH/$dir; ls -F -1 | grep '/$')
  do
    page=${file#./}
    page=${page%%.md}
    if [ $page = Home ]; then
      continue
    else
      list="$list "'['$page']('$CGI_URL'?cmd=get&page='$dir/$page')'
    fi
  done
  echo "$list"
}

function get_parent_dir
{
  page=$1
  parent_dir=${page%/*}
  test -d $WIKI_PATH/$parent_dir || parent_dir=$(dirname "$parent_dir")
  echo "$parent_dir"
}

function print_tree_link
{
  if [ -f $WIKI_PATH/$1.md ]; then
    page=$(basename $1)
  else
    page=''
  fi

  list=''
  pdir=$1
  for I in `seq 10` ; do          # maxdepth=10
    [ -z "$pdir"  ] && break
    pdir=$(get_parent_dir $pdir)
    [ $pdir = "." ] && break
    cdir=$(basename $pdir)
    list='['$cdir'/]('$CGI_URL'?cmd=get&page='$pdir')'" $list "
    [ $pdir = $cdir ] && break
  done
  echo "$list $page"
}

function print_url_resetter
{
  echo '<script type="text/javascript"> window.location.href=window.location.href+"?cmd=get&page='$1'"; </script>'
}

function show_pages_list
{
  typeset file
  typeset page
  echo '[&mdash; Home &mdash;]('$CGI_URL'?cmd=get&page=Home)'
  print_pages_link .
  page=$(get_value "$QUERY_STRING" page)
  echo "<br /> at: "
  print_tree_link $page
}

function show_search_bar
{
  echo "<form action='$CGI_URL' method='get'>"
  echo '<input type="hidden" name="cmd" value="search">'
  echo '<input type="text" name="pattern" size="20">'
  echo '<input type="submit" value="Search"></form>'
}

function show_search_results
{
  typeset result
  echo '#' Search: $1
  # file content
  (cd $WIKI_PATH; egrep --include=*.md -r -i "$1") | while read result
  do
    echo "$result" | sed -e "s%\\(.*\\).md:%[\1]($CGI_URL?cmd=get\&page=\1): %g"
    echo
  done
  # file name
  (cd $WIKI_PATH; find . -name *$1*) | while read result
  do
    echo "$result" | sed -e "s%./\\(.*\\).md%[\1]($CGI_URL?cmd=get\&page=\1)%g"
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
    echo "<div class='printable'>"
    echo
    eval "$2" | relative_path $1
    echo "</div>"
    print_rule
  elif [[ -d $WIKI_PATH/$1 ]]
  then
    print_rule
    show_page_controls $1
    print_rule
    print_pages_link $1 | sed 's/ /\n- /g'
    print_rule
  else
    print_error_page "# ERROR: page $1 not found"
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
    if [[ $ext != md ]]
    then
      line=$line'<tr><td><input type="checkbox" name="files2del" value="'$f'" /></td>'
      line=$line'<td><a href="'$WIKI_URL/$d/$f'">'$f'</td></tr>'
    fi
  done
  if [[ -n $line ]] ; then
    echo 'Attatchments: '
    echo '<form action='$CGI_URL' method='post' enctype='multipart/form-data' name="delattach">'
    echo '<input type="hidden" name="cmd" value="delattach">'
    echo '<input type="hidden" name="page" value="'$1'">'
    echo '<table>'$line'</table>'
    echo '<input type="submit" onclick="delattach_async(); return false;" value="delete"/></form>'
  fi
}

function show_ajax_js
{
  formname=$1
  domname=$2
  cat <<EOF
<script>
function ${formname}_async() {
  var form = document.forms.namedItem("$formname");
  oData = new FormData(form);
  var oReq = new XMLHttpRequest();
  oReq.open("POST", '$CGI_URL', true);
  oReq.onload = function(oEvent) {
    if (oReq.status == 200) {
      document.getElementById('$domname').innerHTML = oReq.responseText;
      MathJax.Hub.Queue(["Typeset",MathJax.Hub]);
    } else {
      document.getElementById('$domname').innerHTML = "process failed";
    }
  };
  oReq.send(oData);
}
</script>
EOF
}
function show_print_js
{
  cat<<EOF
<script>
  function PrintScript(){
  htmlcode = window.document.body.innerHTML;
  prnhtml  = document.getElementsByClassName("printable")[0].innerHTML;
  window.document.body.innerHTML = prnhtml;
  window.print();
  window.document.body.innerHTML = htmlcode;
  }
</script>
EOF

}

function show_page_editor
{
  print_rule
  echo '#' $1
  echo "<form action='$CGI_URL' method='post' name='publish'>"
  echo '<table><tr><td valign="top">'
  echo '<input type="hidden" name="cmd" value="publish">'
  echo '<input type="hidden" name="page" value="'$1'">'
  # Top-Left: textarea
  echo '<textarea name="content" id="content" rows=20 style="overflow-y:scroll; width:95%;" onkeydown="if(event.ctrlKey&&event.keyCode==13){publish_async();return false}else if(event.altKey&&event.keyCode==13){document.getElementById('\''submit'\'').click();return false}">'
  # Note: commonmark treats a blank line as a closing html tag.
  #  To avoid the parser converting .md contents inside the textarea,
  #   \n needs to be replaced with &#010; .
  (cd $WIKI_PATH; cat $1.md | tr -d '\r' | sed -e ':loop; N; $!b loop; s/\n/\&#010;/g ; s/\\/\&#x5c;/g ')
  echo '</textarea><br />'
  echo '<script> document.getElementById("content").focus(); </script>'

  echo '</td></tr><tr><td valign="top">'
  # Top-Right: preview pane
  echo '<div id="preview" style="overflow:auto; height:20em">'
  (cd $WIKI_PATH; cat $1.md)
  echo '</div>'
  echo '</td></tr><tr><td>'
  # Top-Left: preview button
  echo "<input type="submit" id="preview" onclick='publish_async(); return false;' value='Preview'>"
  echo '( press the button or Ctrl-Enter to preview )'
  echo '<input type="submit" id="submit" value="Publish">'
  echo '( press the button or Alt-Enter to publish )'
  echo '</td></tr></table>'
  echo '</form>'

  echo '<hr />'

  # buttons
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
  echo "<form action='$CGI_URl' method='post' enctype='multipart/form-data' name='attach'>"
  echo '<input type="hidden" name="cmd" value="attach">'
  echo '<input type="hidden" name="page" value="'$1'">'
  echo '<input type="file"   name="attachfile">'
  echo "<input type="submit" onclick='attach_async(); return false;' value='Attach'></form>"
  echo '</td></tr></table>'
  echo '<hr />'

  echo '<div id="attachments">'
  show_attachments $1
  echo '</div>'

  show_ajax_js "publish"   "preview"
  show_ajax_js "attach"    "attachments"
  show_ajax_js "delattach" "attachments"

}

function show_create_page
{
  print_rule
  echo "Create new page under $1/:"
  echo "<form action='$CGI_URL' method='post'>"
  echo '<input type="hidden" name="cmd" value="create">'
  echo "<input type='hidden' name='parent_dir' value='$1'>"
  echo "<input type='text' name='page' size='20'>"
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
        previous_page=$(get_value "$QUERY_STRING" previous_page | sed 's|%2F|/|g')
        parent_dir=$(get_parent_dir "$previous_page")
        show_pages_list
        show_create_page ${parent_dir}
      else
        show_pages_list
        show_page_content ${page:-Home} 'cat $WIKI_PATH/$1.md'
      fi
      ;;
    GET+search)
      pattern=$(get_value "$QUERY_STRING" pattern)
      show_pages_list
      print_rule
      show_search_bar
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
      print_url_resetter Home
      ;;
    POST+publish)
      page=$(get_value "$2" page)
      content=$(get_value "$2" content | tr -d '\r')
      publish_content $page "$content"
      show_pages_list
      show_page_content $page 'cat $WIKI_PATH/$1.md'
      print_url_resetter $page
      ;;
    POST+create)
      parent_dir=$(get_value "$2" parent_dir)
      page=$(get_value "$2" page)
      create_page $parent_dir $page
      show_pages_list
      show_page_content $parent_dir/$page 'cat $WIKI_PATH/$1.md'
      print_url_resetter $parent_dir/$page
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
  show_search_bar
  echo '</td><td>'

  echo "<form action='$CGI_URL' method='get'>"
  echo '<input type="hidden" name="cmd" value="get">'
  echo '<input type="hidden" name="previous_page" value="'$1'">'
  echo '<input type="hidden" name="page" value="New">'
  echo '<input type="submit" value="New"></form>'
  echo '</td><td>'
  echo "<form action='$CGI_URL' method='get'>"
  echo '<input type="hidden" name="cmd" value="edit">'
  echo '<input type="hidden" name="page" value="'$1'">'
  echo '<input type="submit" value="Edit"></form>'

  echo '</td><td>'
  show_print_js
  echo '<input type="submit" value="Print" onclick="PrintScript();">'
  echo '</td></tr></table>'
}

function create_page
{
  D=$(dirname  $1/$2)
  F=$(basename $2).md
  (cd $WIKI_PATH; test -d $D || mkdir -p $D ; cd $D ; touch $F; git_cmd add $F "Create $1/$2") >/dev/null
}

function publish_content
{
  D=`dirname  $1`
  F=`basename $1`.md
  (cd $WIKI_PATH/$D ; echo "$2" > $F ; git_cmd add $F "Publish $1") >/dev/null
}

function print_history
{
  D=`dirname  $1`
  F=`basename $1`.md
  (cd $WIKI_PATH/$D; git log -p -n 10 $F) | while read line
  do
    echo -e "\t$line"
  done
}

function delete_page
{
  D=`dirname  $1`
  F=`basename $1`.md
  (cd $WIKI_PATH/$D; git_cmd rm $F "Delete $1") >/dev/null
}

function handle_multipart
{
  tmpfile=$1
  line=`cat $tmpfile | wc -l | cut -d' ' -f1`
  cmd=$(sed -n 4p $tmpfile | tr -d '\r')
  page=$(sed -n 8p $tmpfile | tr -d '\r')
  dir=`dirname $page`

  case $cmd in
    attach)
      if [ $line -ge 15 ]; then
        filename=$(sed -n 10p $tmpfile | sed 's%.*filename="\(.*\)".*%\1%g')
        sed -n 13,$((line-2))p $tmpfile > $WIKI_PATH/$dir/$filename
        sed -n $((line-1))p $tmpfile | tr -d '\r' >> $WIKI_PATH/$dir/$filename
        chmod 644 $WIKI_PATH/$dir/$filename
        (cd $WIKI_PATH/$dir ; git_cmd add $filename "Attach $filename")
        echo "attached :  $filename" | escape_equation | $MARKDOWN_BIN
      fi
      show_attachments $page
      ;;
    delattach)
      i=12
      while [ $i -le $line ]; do
        filename=$(sed -n ${i}p $tmpfile | tr -d '\r')
        (cd $WIKI_PATH/$dir ; git_cmd rm $filename "Delete $filename")
        echo "deleted :  $filename"
        i=$(( i + 4 ))
      done
      show_attachments $page
      ;;
    publish) # live preview
      sed -n 12,$((line-1))p $tmpfile | tr -d '\r' | escape_equation | $MARKDOWN_BIN
      ;;
  esac
}

function run_CGI
{
  echo Content-Type: text/html
  echo
  cat $DATA_PATH/HEADER
  if [[ $REQUEST_METHOD == GET ]] ; then
    cmd=$(get_value "$QUERY_STRING" cmd)
    cmd=${cmd:-get}
    cat $DATA_PATH/HEADER
    show_page GET+$cmd "" | escape_equation | $MARKDOWN_BIN
    cat $DATA_PATH/FOOTER

  elif [[ $CONTENT_TYPE =~ multipart ]] ; then
    tmpfile=$(mktemp)
    cat > $tmpfile
    handle_multipart $tmpfile
    rm -f $tmpfile

  else # POST
    query=`cat | tr -d '\r'` # get stdin
    cmd=$(get_value "$query" cmd)
    cat $DATA_PATH/HEADER
    show_page POST+$cmd "$query" | $MARKDOWN_BIN
    cat $DATA_PATH/FOOTER
  fi
}

# main
run_CGI 2>> error.log
#REQUEST_METHOD=GET run_CGI | tee tmp.html 2> error.log # debug
