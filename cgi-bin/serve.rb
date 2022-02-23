#!/usr/bin/env ruby
require 'webrick'
WEBrick::HTTPServer.new(:DocumentRoot => "./", :Port => 3000).start
