#!/bin/sh

my_version="%(version)s"
delimiter="%(delimiter)s"
collect_url="%(collect_url)s"
version_url="%(version_url)s"
upload_url="%(upload_url)s"

check_version() {
    server_version=$(curl -s "$version_url")
    if [ "$server_version" != "$my_version" ]; then
        echo "Version mismatch, my($my_version), server($server_version). Please fetch $collect_url for update !"
        exit 1
    fi
}

upload() {
    export PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:$PATH
    (
        echo "hostname"
        hostname
        echo "$delimiter"

        echo "dmidecode"
        sudo dmidecode
        echo
    ) | curl -X POST --data-binary @- "$upload_url"
}


#### Main
check_version
upload
