#!/usr/bin/env ruby
require 'webrick' 
WEBrick::HTTPServer.new(:DocumentRoot => "./", :Port => 8000).start
