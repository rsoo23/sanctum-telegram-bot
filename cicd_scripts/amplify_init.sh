#!/bin/bash
set -e
IFS='|'

AWSCLOUDFORMATIONCONFIG="{\
\"configLevel\":\"project\",\
\"useProfile\":false,\
\"profileName\":\"default\",\
\"accessKeyId\":\"$ACCESS_KEY_ID\",\
\"secretAccessKey\":\"$SECRET_ACCESS_KEY\",\
\"region\":\"us-east-1\"\
}"
AMPLIFY="{\
\"projectName\":\"sanctum-telegram-bot\",\
\"envName\":\"myenvname\",\
\"defaultEditor\":\"code\"\
}"
PROVIDERS="{\
\"awscloudformation\":$AWSCLOUDFORMATIONCONFIG\
}"

amplify init \
--amplify $AMPLIFY \
--providers $PROVIDERS \
--yes
