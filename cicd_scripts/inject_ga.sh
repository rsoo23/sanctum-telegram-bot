#!/bin/bash

# Define the path to your index.html file
FILE="Game/build-templates/web-mobile/index.ejs"

# Check the environment variable
if [ "$ENV" == "production" ]; then
  sed -i '' "s/G-XXXXXXXXXX/$GA_ID_PRODUCTION/g" $FILE
  echo "Injected Google Analytics ID ($GA_ID_PRODUCTION) into index.ejs"
else
  sed -i '' "s/G-XXXXXXXXXX/$GA_ID_STAGING/g" $FILE
  echo "Injected Google Analytics ID ($GA_ID_STAGING) into index.ejs"
fi


