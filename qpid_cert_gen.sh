#!/usr/bin/expect -f

#exp_internal 1

set timeout 50
spawn "/usr/bin/nss-db-gen"
#expect "Enter a directory [/tmp/rhua/qpid]:"
send "\r"
expect "password:"
send "redhat\r"
expect "DB\":"
send "redhat\r"
expect "PKCS12 file:"
send "redhat\r"
expect "password:"
send "redhat\r"
expect "Import Password:"
send "redhat\r"

expect eof
