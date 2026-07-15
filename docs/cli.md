# cli

## description

copycat is a command line tool for copying text, files, and images cross-device.

## subcommands

### copy | cp

Send content from local OS clipboard to the copycat server. 
Use options `-f`, `-t`, `-m` to set certain content types first before sending, using these options by default will clear other existing content types.

usage:
```sh
copycat cp [options] 
```

options:
```
-f | --file <filepath>      Set file uri to clipboard and send.
-t | --text <plain-text>    Set plain text content (mimetype: text/plain) to clipboard and send.
-m | --html <html-content>  Set HTML content(mimetype: text/html) to clipboard and send.
-k | --keep                 Used in combination with -f, -t, -m to set certain content types while keeping other existing content types.
-h | --help                 Show help information
```

### paste | ps

Get content from copycat server to local OS clipboard. Use options `-f`, `-t`, `-m` to only get certain content types.

usage:
```sh
copycat ps [options]
```

options:
```
-f | --file      Download file to local cache folder and set file url to local OS clipboard.
-t | --text      Get plain text content from server and set to local OS clipboard.
-m | --html      Get HTML content from server and set to local OS clipboard.
-h | --help      Show help information
```

## configuration

By default, read config from `${XDG_CONFIG_HOME}/copycat/config.yaml` or `${HOME}/.config/copycat/config.yaml`.
Config can also be set by environment variables.

```yaml
---
# Mandatory fields, must be set in config file or environment variables.
# base server url, can also be set by environment variable COPYCAT_SERVER_URL
server_url:  

# user id, used for authentication, must match the user-id in DB user table, can also be set by environment variable COPYCAT_USER_ID
user_id:

# api key, used in combination with COPYCAT_USER_ID for basic authentication, can also be set by environment variable COPYCAT_API_KEY
api_key:
```
